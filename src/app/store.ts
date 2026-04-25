import { reactive } from "vue";

import type { SupportedFormats } from "./meta/constants";

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
	// `boolean | undefined` keeps the original tri-state (on/off/default).
	// A `number` means "custom value N" set via the dialog (e.g. 'cv01' 2).
	// 0 is treated as off (per OpenType spec), any positive N selects the
	// N-th alternate from the GSUB Type 3 AlternateSet.
	features: {} as Record<string, boolean | number | undefined>,
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
export type OptionType = StoreType["options"];
