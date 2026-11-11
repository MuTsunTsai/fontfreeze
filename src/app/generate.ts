import { callWorker } from "./bridge";
import { bucketFeatures } from "./features";
import i18n from "./i18n";
import { getFormats } from "./meta/constants";
import { getUnicodes } from "./meta/unicode";
import { applySuffix, suggestedFileName } from "./naming";
import { store } from "./store";
import { clone } from "./utils";
import { alert } from "./vue/modals/alert.vue";

const { t } = i18n.global;

const MESSAGE_TIMEOUT = 3000;

export async function generate(): Promise<void> {
	if(store.message || store.running) return;
	gtag("event", "save_" + store.options.format);
	try {
		if("showSaveFilePicker" in window) {
			store.message = null;
			const handle = await showSaveFilePicker({
				suggestedName: fileName(),
				types: [getFormats(store.options.format)],
			});
			await startAnime();
			const url = await getOutputURL();
			const response = await fetch(url);
			const content = await response.arrayBuffer();
			const blob = new Blob([content], { type: "font/" + store.options.format });
			const writable = await handle.createWritable();
			await writable.write(blob);
			await writable.close();
			store.message ||= t("main.generatingComplete");
			setTimeout(() => store.message = null, MESSAGE_TIMEOUT);
		} else {
			await startAnime();
			const url = await getOutputURL();
			if(store) store.url = url;
			store.download = fileName();
		}
	} catch(e) {
		console.log(e);
	}
	if(store.running) store.running = false;
}

function startAnime(): Promise<unknown> {
	const anime = new Promise(resolve => {
		addEventListener("animationstart", resolve, { once: true });
	});
	// The progress is only shown while running, so it suffices to reset it here.
	store.progress = null;
	store.running = true;
	return anime;
}

function fileName(): string {
	return suggestedFileName(store.font!.fileName, store.options.format);
}

const FEATURE_LENGTH = 4; // All valid feature names has this length

async function getOutputURL(): Promise<string> {
	try {
		if(!store.font) throw new Error();
		store.options.family = store.options.family.trim();
		store.options.typo_subfamily = store.options.typo_subfamily.trim();
		const options = applySuffix(clone(store.options));
		const { features, featureValues, disables } = bucketFeatures(store.font.gsub, store.features);
		if(features.length && store.options.target.length != FEATURE_LENGTH) {
			throw new Error(t("error.invalidTarget"));
		}
		const args = {
			options,
			version: store.version,
			unicodes: getUnicodes(store.glyphs ||= "", store.subsetMode),
			variations: store.variations,
			features,
			featureValues,
			disables,
		};
		return await callWorker("save", clone(args), p => store.progress = p) as string;
	} catch(e) {
		if(e instanceof Error) alert(t("error.errorOccur", { message: e.message }));
		throw e;
	}
}
