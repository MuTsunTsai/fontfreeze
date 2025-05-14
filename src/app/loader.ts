import { setupFeatures, store } from "./store";
import { initialized, callWorker } from "./bridge";
import { hiddenFeatures, note } from "./constants";
import { tryPreview } from "./preview";
import { clone } from "./utils";

export async function tryOpenFile(file: File) {
	gtag("event", "open_ttf");
	try {
		await openBlob(file, file.name);
	} catch(e) {
		console.log(e);
		alert(`"${file.name}" is not a valid font file, or is corrupted. ` + note);
	}
}

export async function openBlob(blob: Blob, name: string) {
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
	store.options = {
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
	setupFeatures(info.gsub);
	if(info.fvar) {
		for(let a of info.fvar.axes) store.variations[a.tag] = a.default;
	}
	store.font = info;

	// This needs to be done after we have turned on the font UI,
	// so that the browser will actually try to load the font.
	await tryPreview(tempURL, info);

	store.loading = null;
}

function getFileSize(size: number): string {
	if(size < 1024) return size + "B"; else size /= 1024;
	if(size < 1024) return size.toFixed(1) + "KiB"; else size /= 1024;
	return size.toFixed(1) + "MiB";
}
