
/**
 * Features that should not be exposed to the users,
 * based on the "UI suggestion" fields listed on Microsoft website.
 */
export const hiddenFeatures = [
	"abvm", "abvs", "akhn", "blwf", "blwm", "blws", "ccmp", "cfar", "cjct", "curs",
	"dist", "dtls", "fin2", "fin3", "fina", "flac", "half", "haln", "init", "isol",
	"ljmo", "locl", "ltra", "ltrm", "mark", "med2", "medi", "mkmk", "nukt", "pref",
	"pres", "pstf", "psts", "rclt", "rkrf", "rlig", "rphf", "rtla", "rtlm", "rvrn",
	"ssty", "stch", "tjmo", "vjmo", "DELT", // last one is special value
];

/**
 * Base on https://learn.microsoft.com/en-us/typography/opentype/spec/featurelist
 */
export const featureTitle: Record<string, [string, string]> = {
	aalt: ["Access All Alternates", "ae#aalt"],
	abvf: ["Above-base Forms", "ae#abvf"],
	abvm: ["Above-base Mark Positioning", "ae#abvm"],
	abvs: ["Above-base Substitutions", "ae#abvs"],
	afrc: ["Alternative Fractions", "ae#afrc"],
	akhn: ["Akhand", "ae#akhn"],
	apkn: ["Kerning for Alternate Proportional Widths", "ae#apkn"],
	blwf: ["Below-base Forms", "ae#blwf"],
	blwm: ["Below-base Mark Positioning", "ae#blwm"],
	blws: ["Below-base Substitutions", "ae#blws"],
	calt: ["Contextual Alternates", "ae#calt"],
	case: ["Case-sensitive Forms", "ae#case"],
	ccmp: ["Glyph Composition / Decomposition", "ae#ccmp"],
	cfar: ["Conjunct Form After Ro", "ae#cfar"],
	chws: ["Contextual Half-width Spacing", "ae#chws"],
	cjct: ["Conjunct Forms", "ae#cjct"],
	clig: ["Contextual Ligatures", "ae#clig"],
	cpct: ["Centered CJK Punctuation", "ae#cpct"],
	cpsp: ["Capital Spacing", "ae#cpsp"],
	cswh: ["Contextual Swash", "ae#cswh"],
	curs: ["Cursive Positioning", "ae#curs"],
	c2pc: ["Petite Capitals From Capitals", "ae#c2pc"],
	c2sc: ["Small Capitals From Capitals", "ae#c2sc"],
	dist: ["Distances", "ae#dist"],
	dlig: ["Discretionary Ligatures", "ae#dlig"],
	dnom: ["Denominators", "ae#dnom"],
	dtls: ["Dotless Forms", "ae#dtls"],
	expt: ["Expert Forms", "ae#expt"],
	falt: ["Final Glyph on Line Alternates", "fj#falt"],
	fin2: ["Terminal Forms #2", "fj#fin2"],
	fin3: ["Terminal Forms #3", "fj#fin3"],
	fina: ["Terminal Forms", "fj#fina"],
	flac: ["Flattened Accent Forms", "fj#flac"],
	frac: ["Fractions", "fj#frac"],
	fwid: ["Full Widths", "fj#fwid"],
	half: ["Half Forms", "fj#half"],
	haln: ["Halant Forms", "fj#haln"],
	halt: ["Alternate Half Widths", "fj#halt"],
	hist: ["Historical Forms", "fj#hist"],
	hkna: ["Horizontal Kana Alternates", "fj#hkna"],
	hlig: ["Historical Ligatures", "fj#hlig"],
	hngl: ["Hangul", "fj#hngl"],
	hojo: ["Hojo Kanji Forms (JIS X 0212-1990 Kanji Forms)", "fj#hojo"],
	hwid: ["Half Widths", "fj#hwid"],
	init: ["Initial Forms", "fj#init"],
	isol: ["Isolated Forms", "fj#isol"],
	ital: ["Italics", "fj#ital"],
	jalt: ["Justification Alternates", "fj#jalt"],
	jp78: ["JIS78 Forms", "fj#jp78"],
	jp83: ["JIS83 Forms", "fj#jp83"],
	jp90: ["JIS90 Forms", "fj#jp90"],
	jp04: ["JIS2004 Forms", "fj#jp04"],
	kern: ["Kerning", "ko#kern"],
	lfbd: ["Left Bounds", "ko#lfbd"],
	liga: ["Standard Ligatures", "ko#liga"],
	ljmo: ["Leading Jamo Forms", "ko#ljmo"],
	lnum: ["Lining Figures", "ko#lnum"],
	locl: ["Localized Forms", "ko#locl"],
	ltra: ["Left-to-right Alternates", "ko#ltra"],
	ltrm: ["Left-to-right Mirrored Forms", "ko#ltrm"],
	mark: ["Mark Positioning", "ko#mark"],
	med2: ["Medial Forms #2", "ko#med2"],
	medi: ["Medial Forms", "ko#medi"],
	mgrk: ["Mathematical Greek", "ko#mgrk"],
	mkmk: ["Mark to Mark Positioning", "ko#mkmk"],
	mset: ["Mark Positioning via Substitution", "ko#mset"],
	nalt: ["Alternate Annotation Forms", "ko#nalt"],
	nlck: ["NLC Kanji Forms", "ko#nlck"],
	nukt: ["Nukta Forms", "ko#nukt"],
	numr: ["Numerators", "ko#numr"],
	onum: ["Oldstyle Figures", "ko#onum"],
	opbd: ["Optical Bounds", "ko#opbd"],
	ordn: ["Ordinals", "ko#ordn"],
	ornm: ["Ornaments", "ko#ornm"],
	palt: ["Proportional Alternate Widths", "pt#palt"],
	pcap: ["Petite Capitals", "pt#pcap"],
	pkna: ["Proportional Kana", "pt#pkna"],
	pnum: ["Proportional Figures", "pt#pnum"],
	pref: ["Pre-base Forms", "pt#pref"],
	pres: ["Pre-base Substitutions", "pt#pres"],
	pstf: ["Post-base Forms", "pt#pstf"],
	psts: ["Post-base Substitutions", "pt#psts"],
	pwid: ["Proportional Widths", "pt#pwid"],
	qwid: ["Quarter Widths", "pt#qwid"],
	rand: ["Randomize", "pt#rand"],
	rclt: ["Required Contextual Alternates", "pt#rclt"],
	rkrf: ["Rakar Forms", "pt#rkrf"],
	rlig: ["Required Ligatures", "pt#rlig"],
	rphf: ["Reph Form", "pt#rphf"],
	rtbd: ["Right Bounds", "pt#rtbd"],
	rtla: ["Right-to-left Alternates", "pt#rtla"],
	rtlm: ["Right-to-left Mirrored Forms", "pt#rtlm"],
	ruby: ["Ruby Notation Forms", "pt#ruby"],
	rvrn: ["Required Variation Alternates", "pt#rvrn"],
	salt: ["Stylistic Alternates", "pt#salt"],
	sinf: ["Scientific Inferiors", "pt#sinf"],
	size: ["Optical size", "pt#size"],
	smcp: ["Small Capitals", "pt#smcp"],
	smpl: ["Simplified Forms", "pt#smpl"],
	ssty: ["Math Script-style Alternates", "pt#ssty"],
	stch: ["Stretching Glyph Decomposition", "pt#stch"],
	subs: ["Subscript", "pt#subs"],
	sups: ["Superscript", "pt#sups"],
	swsh: ["Swash", "pt#swsh"],
	titl: ["Titling", "pt#titl"],
	tjmo: ["Trailing Jamo Forms", "pt#tjmo"],
	tnam: ["Traditional Name Forms", "pt#tnam"],
	tnum: ["Tabular Figures", "pt#tnum"],
	trad: ["Traditional Forms", "pt#trad"],
	twid: ["Third Widths", "pt#twid"],
	unic: ["Unicase", "uz#unic"],
	valt: ["Alternate Vertical Metrics", "uz#valt"],
	vapk: ["Kerning for Alternate Proportional Vertical Metrics", "uz#vapk"],
	vatu: ["Vattu Variants", "uz#vatu"],
	vchw: ["Vertical Contextual Half-width Spacing", "uz#vchw"],
	vert: ["Vertical Alternates", "uz#vert"],
	vhal: ["Alternate Vertical Half Metrics", "uz#vhal"],
	vjmo: ["Vowel Jamo Forms", "uz#vjmo"],
	vkna: ["Vertical Kana Alternates", "uz#vkna"],
	vkrn: ["Vertical Kerning", "uz#vkrn"],
	vpal: ["Proportional Alternate Vertical Metrics", "uz#vpal"],
	vrt2: ["Vertical Alternates and Rotation", "uz#vrt2"],
	vrtr: ["Vertical Alternates for Rotation", "uz#vrtr"],
	zero: ["Slashed Zero", "uz#zero"],
};

function pad(i: number): string {
	return (i < DECIMAL ? "0" : "") + i;
}

const DECIMAL = 10;
const SS_RANGE = 20;
const CV_RANGE = 99;

for(let i = 1; i <= SS_RANGE; i++) {
	featureTitle["ss" + pad(i)] = ["Stylistic Set " + i, "pt#ssxx"];
}
for(let i = 1; i <= CV_RANGE; i++) {
	featureTitle["cv" + pad(i)] = ["Character Variant " + i, "ae#cv01-cv99"];
}

export const formats = {
	ttf: {
		description: "TTF font",
		accept: { "font/ttf": ".ttf" as const },
	},
	woff2: {
		description: "WOFF2 font",
		accept: { "font/woff2": ".woff2" as const },
	},
};

export type SupportedFormats = keyof typeof formats;

export const note =
	`Please try re-exporting the font with editors such as <a href="https://fontforge.org/">FontForge</a> and see if it fixes the issue. ` +
	`If it still doesn't, please submit an <a href="https://github.com/MuTsunTsai/fontfreeze/issues">issue</a>.`;
