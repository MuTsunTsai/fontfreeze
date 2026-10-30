///<reference lib="WebWorker" />
///<reference types="emscripten" />

import script from "../../build/main.py?raw";
// Built with src/lib/uharfbuzz/Dockerfile; keep the version in sync with pyproject.toml.
import uharfbuzzWheel from "../lib/uharfbuzz/uharfbuzz-0.57.0-cp311-cp311-emscripten_3_1_46_wasm32.whl";

import type { PyodideInterface, loadPyodide as loadPy } from "pyodide";
import type { StoreType } from "./store";

declare global {
	const loadPyodide: typeof loadPy;
}

let bytesLoaded = 0;
const fetchOriginal = fetch;

const ONE_SECOND = 1000;
const PERCENTAGE = 100;

if(typeof TransformStream != "undefined") {
	// This number should be updated whenever Pyodide updates
	const totalBytes = 13399248;

	let lastProgress = performance.now();

	function loadProgress(delta: number): void {
		bytesLoaded += delta;
		const now = performance.now();
		if(now - lastProgress > ONE_SECOND) {
			postMessage({ progress: (PERCENTAGE * bytesLoaded / totalBytes).toFixed(1) });
			lastProgress = now;
		}
	}

	// Hack fetch
	globalThis.fetch = async url => {
		const response = await fetchOriginal(url);
		const ts = new TransformStream({
			transform(chunk, ctrl) {
				loadProgress(chunk.byteLength);
				ctrl.enqueue(chunk);
			},
		});
		return new Response(response.body?.pipeThrough(ts), response);
	};
}

// Pyodide must be loaded from CDN as there're too many files to bundle.
// Unless there's a bug that needs to be fixed,
// it is highly recommended that we stay at an older version of Pyodide to ensure supporting of older browsers,
// as Pyodide tends to focus only on the latest browsers as they develop.
importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js");

// The fonttools bundled with Pyodide 0.25.1 is outdated (4.42.1).
// Since fonttools is pure Python, we load a newer wheel from PyPI instead.
// Keep the version in sync with pyproject.toml.
const FONTTOOLS_WHEEL = "https://files.pythonhosted.org/packages/35/74/4ea331ecc65ba05a58b1e4e8ccd604c8a15565f876dfbf93fc2a2ea2e22b/fonttools-4.68.0-py3-none-any.whl";

let pyodide: PyodideInterface;

async function init(): Promise<void> {
	try {
		pyodide = await loadPyodide({ fullStdLib: false });
		await pyodide.loadPackage("brotli");
		await pyodide.loadPackage(FONTTOOLS_WHEEL);

		// Use this to update totalBytes
		console.log("Total loaded bytes: " + bytesLoaded);

		pyodide.runPython(script);
		postMessage("initialized");
	} catch(e) {
		if(e instanceof Error) postMessage({ error: e.message });
	}
}

init();

addEventListener("message", async event => {
	if(!event.ports[0]) return;
	try {
		const [command, data] = event.data;
		let result;
		if(command == "open") result = await open(data);
		if(command == "save") result = await save(data);
		if(command == "legacy") result = legacy();
		event.ports[0].postMessage({
			success: true,
			data: result,
		});
	} catch(err: unknown) {
		if(err instanceof Error) {
			event.ports[0].postMessage({
				success: false,
				data: err.message,
			});
		}
	}
});

async function open(url: string): Promise<FontInfo> {
	const response = await fetch(url);
	const buffer = await response.arrayBuffer();
	const array = new Uint8Array(buffer);
	pyodide.FS.writeFile("temp", array);
	const info: FontInfo = pyodide.runPython("loadFont('temp')")
		.toJs({ dict_converter: Object.fromEntries });
	if(info.preview) info.previewUrl = createPreviewUrl();
	return info;
}

function legacy(): string {
	pyodide.globals.get("processLegacy")();
	return createPreviewUrl();
}

function createPreviewUrl(): string {
	const content = pyodide.FS.readFile("input") as Uint8Array<ArrayBuffer>;
	const blob = new Blob([content], { type: "font/ttf" });
	return URL.createObjectURL(blob);
}

let saveURL: string;

async function save(args: StoreType): Promise<string> {
	const py = pyodide.globals;
	if(!py.get("processFont")(args)) {
		// GSUB/GPOS is too large for the pure-Python serializer of fontTools to pack efficiently,
		// so we load uharfbuzz for its repacker. It's only needed for such fonts, hence loaded on demand.
		try {
			await pyodide.loadPackage(uharfbuzzWheel);
			py.get("enableRepacker")();
		} catch(e) {
			console.warn("Failed to load uharfbuzz", e);
			py.get("useExtensionLookups")();
		}
		py.get("saveFont")();
	}
	const content = pyodide.FS.readFile("output") as Uint8Array<ArrayBuffer>;
	const blob = new Blob([content], { type: "font/" + args.options.format });
	if(saveURL) URL.revokeObjectURL(saveURL);
	saveURL = URL.createObjectURL(blob);
	return saveURL;
}
