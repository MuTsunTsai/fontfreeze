import { createApp } from "petite-vue";
import { Modal } from "bootstrap";

import { store } from "./store";
import { initialized, callWorker } from "./bridge";
import { setPreviewUnicodeRange, setPreviewFont } from "./preview";
import { buildLocalFonts } from "./localFonts";
import { getUnicodes } from "./unicode";
import { supportPlaintext, setupPlaintext } from "./plainText";

import "./style.scss";

// Features that should not be exposed to the users
const hiddenFeatures = [
	"abvm", "abvs", "akhn", "blwf", "blwm", "blws", "ccmp", "cfar", "cjct", "curs",
	"dist", "dtls", "fin2", "fin3", "fina", "flac", "half", "haln", "init", "isol",
	"ljmo", "locl", "ltra", "ltrm", "mark", "med2", "medi", "mkmk", "nukt", "pref",
	"pres", "pstf", "psts", "rclt", "rkrf", "rlig", "rphf", "rtla", "rtlm", "rvrn",
	"ssty", "stch", "tjmo", "vjmo", "DELT" // last one is special value
];

const axisNames = {
	"ital": "Italic",
	"opsz": "Optical size",
	"slnt": "Slant",
	"wdth": "Width",
	"wght": "Weight",
};

const formats = {
	"ttf": {
		description: "TTF font",
		accept: { "font/ttf": ".ttf" },
	},
	"woff2": {
		description: "WOFF2 font",
		accept: { "font/woff2": ".woff2" },
	}
};

const note =
	"Please try re-exporting the font with editors such as FontForge and see if it fixes the issue. " +
	"If it still doesn't, please submit an issue.";

const modal = selector => Modal.getOrCreateInstance(selector);

let lastValues;

// Setup dropzone
const dropzone = document.querySelector(".dropzone");
const toggle = (event, drag) => {
	event.stopPropagation();
	event.preventDefault();
	dropzone.classList.toggle("drag", drag)
};
document.body.addEventListener("dragover", event => toggle(event, true));
dropzone.addEventListener("dragleave", event => toggle(event, false));
dropzone.addEventListener("drop", event => {
	toggle(event, false);
	const items = [...event.dataTransfer.items];
	const item = items.find(i => i.kind == "file");
	if(item) tryOpenFile(item.getAsFile());
});

// Initialize Vue
createApp({
	chromiumVersion: parseInt(navigator.userAgentData?.brands.find(b => b.brand == "Chromium")?.version ?? 0),
	localFontSupport: "queryLocalFonts" in window,
	store: store,
	get previewStyle() {
		if(!store.font) return null;
		const feat = store.font.gsub
			.filter(g => store.features[g] !== false)
			.map(g => `'${g}' ${store.features[g] ? "on" : "off"}`)
			.join(",");
		const variation = !store.font.fvar ? "normal" :
			store.font.fvar.axes
				.map(a => `'${a.tag}' ${store.variations[a.tag]}`)
				.join(",");
		return `white-space: pre-line;` +
			`font-family: preview${store.previewIndex};` +
			`font-feature-settings: ${feat};` +
			`font-variation-settings: ${variation};` +
			`font-size: ${store.previewSize}pt;`;
	},
	get more() {
		const f = store.font;
		if(!f) return false;
		return f.description || f.designer || f.manufacturer || f.copyright || f.trademark;
	},
	// The next two getter are for dealing with a bug in petite-vue 0.4.1
	// that v-for expression is calculated one more time as the upper v-if condition becoming false
	get instances() {
		if(!store.font || !store.font.fvar) return [];
		return store.font.fvar.instances;
	},
	get axes() {
		if(!store.font || !store.font.fvar) return [];
		return store.font.fvar.axes;
	},
	get localFamilies() {
		if(!store.localFonts.length) return [];
		const result = new Set();
		for(const font of store.localFonts) {
			result.add(font.family);
		}
		return [...result];
	},
	getAxisName(axis) {
		return axis.name ? axis.name :
			axis.tag in axisNames ? axisNames[axis.tag] : axis.tag;
	},
	setInstance(instance) {
		store.options.typo_subfamily = instance.name;
		for(let t in instance.coordinates) {
			store.variations[t] = instance.coordinates[t];
		}
	},
	getStep(axis) {
		const range = axis.max - axis.min;
		if(range > 20) return 1;
		if(range > 1) return 0.1;
		return 0.01;
	},
	clear() {
		const selectElement = document.getElementsByTagName("select")[0];
		if(selectElement) selectElement.value = "";
	},
	checkboxChange(f) {
		if(lastValues[f] === true) store.features[f] = undefined;
		if(lastValues[f] === undefined) store.features[f] = false;
		lastValues[f] = store.features[f];
	},
	info() {
		modal("#info").show();
	},
	setUnicodeRange() {
		setPreviewUnicodeRange(store.unicodeRange = getUnicodes());
	},
	optionStyle(f) {
		if(!f) {
			if(store.localFont === "") return "";
			f = store.localFonts[store.localFont];
		}
		return `font-family:'local ${f.fullName}'`;
	},
	familyStyle(f = store.localFamily) {
		const filtered = store.localFonts.filter(font => font.family == f);
		if(!filtered.length) return "";
		let font = filtered.find(f => f.style == "Regular");
		if(!font) {
			filtered.sort((a, b) => a.fullName.length - b.fullName.length);
			font = filtered[0];
		}
		return `font-family:'local ${font.fullName}'`;
	},
	familyChange() {
		store.localFont = store.localFonts.findIndex(f => f.family == store.localFamily);
	},
	setupDiv() {
		// There's nothing reactive here, so this method only run once.
		const div = document.querySelector("div.pre");
		if(supportPlaintext(div)) {
			// Chrome needs this, or the initial empty lines won't be selectable.
			div.innerText = store.sample;
		} else {
			setupPlaintext(div);
			// Firefox needs this, or hitting enter will completely mess up the text.
			div.textContent = store.sample;
		}
	},
	async local() {
		gtag("event", "show_local");
		await navigator.permissions.query({
			name: "local-fonts",
			description: ""
		});
		const fonts = await window.queryLocalFonts();
		if(fonts.length == 0) return; // permission denied
		buildLocalFonts(fonts);
		store.localFonts = fonts;
		modal("#local").show();
	},
	async loadLocal() {
		gtag("event", "open_local");
		const font = store.localFonts[store.localFont];
		let blob;
		try {
			blob = await font.blob();
		} catch(e) {
			alert("An error occur: " + e.message);
			store.unavailableFonts.push(font.postscriptName);
			return;
		} finally {
			store.localFamily = "";
			store.localFont = "";
		}
		modal("#local").hide();
		try {
			await openBlob(blob, font.fullName);
		} catch(e) {
			alert("An error occur: " + e.message);
		}
	}
}).mount();

globalThis.generate = async function() {
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
	const name = store.font.fileName.replace(/\.[a-z0-9]+$/i, "");
	return name + "_freeze." + store.options.format;
}

function clone(obj) {
	return JSON.parse(JSON.stringify(obj));
}

async function getOutputURL() {
	try {
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
		const args = {
			options: options,
			version: store.version,
			unicodes: getUnicodes(),
			variations: store.variations,
			features: store.font.gsub.filter(g => store.features[g] === true),
			disables: store.font.gsub.filter(g => store.features[g] === undefined),
		};
		return await callWorker("save", clone(args));
	} catch(e) {
		alert("An error occur: " + e.message);
		throw e;
	}
}

globalThis.openFile = async function(input) {
	const file = input.files[0];
	if(!file) return;
	input.value = ""; // clear field
	tryOpenFile(file);
}

async function tryOpenFile(file) {
	gtag("event", "open_ttf");
	try {
		await openBlob(file, file.name);
	} catch(e) {
		console.log(e);
		alert(`"${file.name}" is not a valid font file, or is corrupted. ` + note);
	}
}

async function openBlob(blob, name) {
	store.loading = "packages";
	await initialized;
	store.loading = "font";

	let tempURL = URL.createObjectURL(blob);
	let info;
	try {
		info = await callWorker("open", tempURL);
	} catch(e) {
		URL.revokeObjectURL(tempURL);
		store.loading = null;
		throw e;
	}

	console.log(clone(info));
	if(info.preview) {
		URL.revokeObjectURL(tempURL);
		tempURL = info.preview;
	}

	info.fileName = name;
	info.fileSize = getFileSize(blob.size);
	info.gsub = info.gsub.filter(g => !hiddenFeatures.includes(g));
	store.features = {};
	lastValues = {};
	store.variations = {};
	store.glyphs = "";
	store.options = {
		suffix: "Freeze",
		family: info.family,
		subfamily: info.subfamily,
		typo_family: info.typo_family || info.family,
		typo_subfamily: info.typo_subfamily || "",
		fixContour: false,
		singleSub: true,
		customNames: false,
		target: "calt",
		format: "ttf",
	};
	for(let g of info.gsub) store.features[g] = lastValues[g] = false;
	if(info.fvar) {
		for(let a of info.fvar.axes) store.variations[a.tag] = a.default;
	}
	store.font = info;

	// This needs to be done after we have turned on the font UI,
	// so that the browser will actually try to load the font.
	await tryPreview(tempURL);

	store.loading = null;
}

async function tryPreview(url) {
	if(await setPreviewFont(url)) return;

	// If it's not done yet, try to fix legacy font issues.
	if(!info.preview) {
		try {
			const url = await callWorker("legacy");
			if(await setPreviewFont(url)) return;
		} catch(e) {
			console.log(e);
		}
	}

	// If it's already done or the fix fails, show message.
	gtag("event", "preview_failed");
	alert("Font preview won't work for this font. " + note);
}

function getFileSize(size) {
	if(size < 1024) return size + "B"; else size /= 1024;
	if(size < 1024) return size.toFixed(1) + "KiB"; else size /= 1024;
	return size.toFixed(1) + "MiB";
}