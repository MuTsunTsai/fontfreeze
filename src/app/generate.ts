import { callWorker } from "./bridge";
import { formats } from "./meta/constants";
import { store } from "./store";
import { getUnicodes } from "./meta/unicode";
import { clone } from "./utils";
import { alert } from "./vue/modals/alert.vue";

const MESSAGE_TIMEOUT = 3000;

export async function generate(): Promise<void> {
	if(store.message || store.running) return;
	gtag("event", "save_" + store.options.format);
	try {
		if("showSaveFilePicker" in window) {
			store.message = null;
			const handle = await showSaveFilePicker({
				suggestedName: suggestedFileName(),
				types: [formats[store.options.format]],
			});
			await startAnime();
			const url = await getOutputURL();
			const response = await fetch(url);
			const content = await response.arrayBuffer();
			const blob = new Blob([content], { type: "font/" + store.options.format });
			const writable = await handle.createWritable();
			await writable.write(blob);
			await writable.close();
			store.message ||= "Generating complete!";
			setTimeout(() => store.message = null, MESSAGE_TIMEOUT);
		} else {
			await startAnime();
			const url = await getOutputURL();
			if(store) store.url = url;
			store.download = suggestedFileName();
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
	store.running = true;
	return anime;
}

function suggestedFileName(): string {
	const name = store.font!.fileName.replace(/\.[a-z0-9]+$/i, "");
	return name + "_freeze." + store.options.format;
}

const MS_CHAR_LIMIT = 32; // There's a 32-char limit in MS Word
const FEATURE_LENGTH = 4; // All valid feature names has this length

async function getOutputURL(): Promise<string> {
	try {
		if(!store.font) throw new Error();
		store.options.family = store.options.family.trim();
		store.options.typo_subfamily = store.options.typo_subfamily.trim();
		const options = clone(store.options);
		if(options.suffix) {
			if(
				options.family &&
				options.family.length + options.suffix.length < MS_CHAR_LIMIT
			) {
				options.family += " " + options.suffix;
			}
			if(options.typo_family) options.typo_family += " " + options.suffix;
		}
		const features = store.font.gsub.filter(g => store.features[g] === true);
		if(features.length && store.options.target.length != FEATURE_LENGTH) {
			throw new Error("Must specify a valid activation target.");
		}
		const args = {
			options,
			version: store.version,
			unicodes: getUnicodes(),
			variations: store.variations,
			features,
			disables: store.font.gsub.filter(g => store.features[g] === undefined),
		};
		return await callWorker("save", clone(args)) as string;
	} catch(e) {
		if(e instanceof Error) alert("An error occur: " + e.message);
		throw e;
	}
}
