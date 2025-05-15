import { store } from "./store";
import { initialized, callWorker } from "./bridge";
import { hiddenFeatures, note } from "./constants";
import { tryPreview } from "./preview";
import { clone } from "./utils";
import { setupFeatures } from "./vue/features.vue";
import { alert } from "./vue/modals/alert.vue";

import type { OptionType } from "./store";

const KB = 1024;

export async function tryOpenFile(file: File): Promise<void> {
	gtag("event", "open_ttf");
	try {
		await openBlob(file, file.name);
	} catch(e) {
		console.log(e);
		alert(`"${file.name}" is not a valid font file, or is corrupted. ` + note);
	}
}

export async function openBlob(blob: Blob, name: string): Promise<void> {
	store.loading = "packages";
	await initialized;
	store.loading = "font";

	let tempURL = URL.createObjectURL(blob);
	let info: FontInfo;
	try {
		info = await callWorker("open", tempURL) as FontInfo;
	} catch(e) {
		URL.revokeObjectURL(tempURL);
		store.loading = null;
		throw e;
	}

	console.log(clone(info));
	if(info.preview) {
		URL.revokeObjectURL(tempURL);
		tempURL = info.previewUrl;
	}

	info.fileName = name;
	info.fileSize = getFileSize(blob.size);
	info.gsub = info.gsub.filter(g => !hiddenFeatures.includes(g));
	store.variations = {};
	store.glyphs = "";
	store.options = createDefaultOption(info);
	setupFeatures(info.gsub);
	if(info.fvar) {
		for(const a of info.fvar.axes) store.variations[a.tag] = a.default;
	}
	store.font = info;

	// This needs to be done after we have turned on the font UI,
	// so that the browser will actually try to load the font.
	await tryPreview(tempURL, info);

	store.loading = null;
}

function createDefaultOption(info: FontInfo): OptionType {
	return {
		suffix: "Freeze",
		family: info.family,
		keepVar: false,
		subfamily: info.subfamily,
		typo_family: info.typo_family || info.family,
		typo_subfamily: info.typo_subfamily || "",
		fixContour: false,
		singleSub: true,
		customNames: false,
		lineHeight: 0,
		spacing: 0,
		target: "calt",
		format: "ttf",
	};
}

function getFileSize(size: number): string {
	if(size < KB) return size + "B"; else size /= KB;
	if(size < KB) return size.toFixed(1) + "KiB"; else size /= KB;
	return size.toFixed(1) + "MiB";
}
