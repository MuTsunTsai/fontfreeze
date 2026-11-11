///<reference lib="WebWorker" />

// Built from src/rust by the gulp task "wasm".
import init, { loadFont, processFont, processLegacy } from "../../build/wasm/fontfreeze";

import type { StoreType } from "./store";

declare const WASM_SIZE: number;

const ONE_SECOND = 1000;
const PERCENTAGE = 100;

const wasmUrl = new URL("../../build/wasm/fontfreeze_bg.wasm", import.meta.url);

/** Fetches the wasm module, reporting the progress. */
async function fetchWasm(): Promise<Response> {
	const response = await fetch(wasmUrl);
	if(!response.ok) throw new Error(`Failed to load ${wasmUrl} (${response.status})`);
	if(!response.body || typeof TransformStream == "undefined") return response;

	let bytesLoaded = 0;
	let lastProgress = performance.now();
	const ts = new TransformStream<Uint8Array, Uint8Array>({
		transform(chunk, ctrl) {
			// The body is already decompressed, so WASM_SIZE (the uncompressed size) is the total.
			bytesLoaded += chunk.byteLength;
			const now = performance.now();
			if(now - lastProgress > ONE_SECOND) {
				postMessage({ progress: Math.min(PERCENTAGE, PERCENTAGE * bytesLoaded / WASM_SIZE).toFixed(1) });
				lastProgress = now;
			}
			ctrl.enqueue(chunk);
		},
	});
	// Keep the headers, so that the module can be compiled while streaming.
	return new Response(response.body.pipeThrough(ts), response);
}

async function initialize(): Promise<void> {
	try {
		await init({ module_or_path: fetchWasm() });
		postMessage("initialized");
	} catch(e) {
		if(e instanceof Error) postMessage({ error: e.message });
	}
}

initialize();

addEventListener("message", async event => {
	if(!event.ports[0]) return;
	try {
		const [command, data] = event.data;
		let result;
		if(command == "open") result = await open(data);
		if(command == "save") result = save(data, event.ports[0]);
		if(command == "legacy") result = legacy();
		event.ports[0].postMessage({
			success: true,
			data: result,
		});
	} catch(err: unknown) {
		event.ports[0].postMessage({
			success: false,
			data: err instanceof Error ? err.message : String(err),
		});
	}
});

// The font being worked on is kept on the Rust side (see wasm.rs),
// so that it is not copied into the wasm memory on each generation.

interface LoadResult {
	info: FontInfo;
	/** The converted font, for legacy CJK fonts. */
	data?: Uint8Array<ArrayBuffer>;
}

async function open(url: string): Promise<FontInfo> {
	const response = await fetch(url);
	const data = new Uint8Array(await response.arrayBuffer());
	const { info, data: converted } = loadFont(data) as LoadResult;
	if(info.preview && converted) info.previewUrl = createPreviewUrl(converted);
	return info;
}

function legacy(): string {
	return createPreviewUrl(processLegacy() as Uint8Array<ArrayBuffer>);
}

function createPreviewUrl(data: Uint8Array<ArrayBuffer>): string {
	const blob = new Blob([data], { type: "font/ttf" });
	return URL.createObjectURL(blob);
}

let saveURL: string;

function save(args: StoreType, port: MessagePort): string {
	// Called with the percentage of the compression done, for WOFF2 only.
	const onProgress = (progress: number): void => port.postMessage({ progress });
	const content = processFont(args, onProgress) as Uint8Array<ArrayBuffer>;
	const blob = new Blob([content], { type: "font/" + args.options.format });
	if(saveURL) URL.revokeObjectURL(saveURL);
	saveURL = URL.createObjectURL(blob);
	return saveURL;
}
