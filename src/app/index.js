import { createApp } from "petite-vue";

import { store, changeFeature } from "./store";
import { getPreviewStyle, setPreviewUnicodeRange } from "./preview";
import { loadLocal, local } from "./localFonts";
import { getUnicodes } from "./unicode";
import { supportPlaintext, setupPlaintext } from "./plainText";
import { generate } from "./generate";
import { tryOpenFile } from "./loader";
import { modal } from "./utils";
import { axisNames } from "./constants";

import "./style.scss";

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
		return getPreviewStyle();
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
	checkboxChange: changeFeature,
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
	local,
	loadLocal,
	validateNumber(e) {
		const input = e.target;
		const value = Number(input.value);
		if(!input.value.trim() || Number.isNaN(value)) input.value = "0";
		if(!Number.isInteger(value)) input.value = Math.round(value).toString();
	}
}).mount();

globalThis.generate = generate;

globalThis.openFile = async function(input) {
	const file = input.files[0];
	if(!file) return;
	input.value = ""; // clear field
	tryOpenFile(file);
}
