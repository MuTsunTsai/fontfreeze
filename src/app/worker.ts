///<reference lib="WebWorker" />

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
	const totalBytes = 16253175;

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

let pyodide: PyodideInterface;

async function initPyodide(): Promise<void> {
	pyodide = await loadPyodide({ fullStdLib: false });
	await pyodide.loadPackage("brotli");
	await pyodide.loadPackage("fonttools");
}

async function init(): Promise<void> {
	try {
		const [_, script] = await Promise.all([
			initPyodide(),
			fetchOriginal(new URL("../../build/main.py", import.meta.url)).then(r => r.text()), // exclude from totalBytes
		]);
		pyodide.runPython(script);

		// Use this to update totalBytes
		console.log("Total loaded bytes: " + bytesLoaded);

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
		if(command == "save") result = save(data);
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
	const content = pyodide.FS.readFile("input");
	const blob = new Blob([content], { type: "font/ttf" });
	return URL.createObjectURL(blob);
}

let saveURL: string;

function save(args: StoreType): string {
	pyodide.globals.get("processFont")(args);
	const content = pyodide.FS.readFile("output");
	const blob = new Blob([content], { type: "font/" + args.options.format });
	if(saveURL) URL.revokeObjectURL(saveURL);
	saveURL = URL.createObjectURL(blob);
	return saveURL;
}
