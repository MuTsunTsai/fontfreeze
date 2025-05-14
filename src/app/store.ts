// See https://github.com/vuejs/petite-vue/discussions/210 for a hack on typings
// We've made a PNPM patch for it in this repo
import { reactive } from "petite-vue";

import type { SupportedFormats } from "./constants";

declare const VERSION: string;

export const store = reactive({
	localFonts: [] as FontData[],
	localFont: "" as string | number,
	localFamily: "",
	unavailableFonts: [] as string[], // postscriptName of the font
	unicodeRange: "",
	loading: null as string | null,
	font: null as FontInfo | null,
	sample: "",
	glyphs: "",
	subsetMode: "exclude",
	previewSize: 12,
	running: false,
	message: null as string | null,
	url: null as string | null,
	download: null as string | null,
	previewIndex: 0,
	version: " v" + VERSION,
	features: {} as Record<string, boolean | undefined>,
	variations: {} as Record<string, number>,
	options: {
		suffix: "",
		keepVar: false,
		family: "",
		subfamily: "",
		typo_family: "",
		typo_subfamily: "",
		fixContour: false,
		singleSub: true,
		customNames: false,
		lineHeight: 0,
		spacing: 0,
		target: "",
		format: "ttf" as SupportedFormats,
	},
});

/** The last value before the current value for each features. */
let lastValues: Record<string, boolean | undefined>;

const lastFeatures = new Set<string>();

export function changeFeature(f: string) {
	if(lastValues[f] === true) store.features[f] = undefined;
	if(lastValues[f] === undefined) store.features[f] = false;
	lastValues[f] = store.features[f];
}

export function setupFeatures(gsub: string[]) {
	if(sameFeatures(gsub)) return;

	lastFeatures.clear();
	store.features = {};
	lastValues = {};
	for(const g of gsub) {
		lastFeatures.add(g);
		store.features[g] = lastValues[g] = false;
	}
}

function sameFeatures(gsub: string[]) {
	if(gsub.length != lastFeatures.size) return false;
	for(const g of gsub) {
		if(!lastFeatures.has(g)) return false;
	}
	return true;
}

export type StoreType = typeof store;

fetch("sample.txt")
	.then(r => r.text())
	.then(t => store.sample = t);
