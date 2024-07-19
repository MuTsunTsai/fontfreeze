// See https://github.com/vuejs/petite-vue/discussions/210 for a hack on typings
// It's not very satisfying but I don't see a better way
import { reactive } from "petite-vue";

export const store = reactive({
	localFonts: [] as FontData[],
	localFont: "",
	localFamily: "",
	unavailableFonts: [] as string[], // postscriptName of the font
	unicodeRange: "",
	loading: null as string | null,
	font: null,
	sample: "",
	glyphs: "",
	subsetMode: "exclude",
	previewSize: 12,
	running: false,
	message: null,
	previewIndex: 0,
	version: "",
});

fetch("sample.txt")
	.then(r => r.text())
	.then(t => store.sample = t);

// Use shields.io as API
fetch("https://img.shields.io/github/package-json/v/mutsuntsai/fontfreeze.json")
	.then(r => r.json())
	.then(j => store.version = " " + j.value);