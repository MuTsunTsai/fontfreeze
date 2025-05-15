import { reactive } from "vue";

import type { SupportedFormats } from "./constants";

export const store = reactive({
	localFonts: [] as FontData[],
	localFont: "" as "" | number,
	localFamily: "",
	unavailableFonts: [] as string[], // postscriptName of the font
	unicodeRange: "",
	loading: null as string | null,
	font: null as FontInfo | null,
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

export type StoreType = typeof store;
