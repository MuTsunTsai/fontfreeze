import { callWorker } from "./bridge";
import { formats } from "./constants";
import { store } from "./store";
import { getUnicodes } from "./unicode";
import { clone } from "./utils";

export async function generate() {
	if(store.message) return; // button not ready
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
			store.message = "Generating complete!";
			setTimeout(() => store.message = null, 3000);
		} else {
			await startAnime();
			store.url = await getOutputURL();
			store.download = suggestedFileName();
		}
	} catch(e) {
		console.log(e);
	}
	store.running = false;
}

function startAnime() {
	const anime = new Promise(resolve => {
		addEventListener("animationstart", resolve, { once: true });
	});
	store.running = true;
	return anime;
}

function suggestedFileName() {
	const name = store.font!.fileName.replace(/\.[a-z0-9]+$/i, "");
	return name + "_freeze." + store.options.format;
}

async function getOutputURL(): Promise<string> {
	try {
		if(!store.font) throw new Error();
		for(let tag in store.variations) {
			// Fix bugs of petite-vue with <input type="range">
			store.variations[tag] = Number(store.variations[tag]);
		}
		store.options.family = store.options.family.trim();
		store.options.typo_subfamily = store.options.typo_subfamily.trim();
		const options = clone(store.options);
		if(options.suffix) {
			if(
				options.family &&
				options.family.length + options.suffix.length < 32 // There's a 32-char limit in MS Word
			) {
				options.family += " " + options.suffix;
			}
			if(options.typo_family) options.typo_family += " " + options.suffix;
		}
		const features = store.font.gsub.filter(g => store.features[g] === true);
		if(features.length && store.options.target.length != 4) {
			throw new Error("Must specify a valid activation target.");
		}
		const args = {
			options: options,
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
