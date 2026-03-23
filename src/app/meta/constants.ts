
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
export const featureURL: Record<string, string> = {
	aalt: "ae#aalt",
	abvf: "ae#abvf",
	abvm: "ae#abvm",
	abvs: "ae#abvs",
	afrc: "ae#afrc",
	akhn: "ae#akhn",
	apkn: "ae#apkn",
	blwf: "ae#blwf",
	blwm: "ae#blwm",
	blws: "ae#blws",
	calt: "ae#calt",
	case: "ae#case",
	ccmp: "ae#ccmp",
	cfar: "ae#cfar",
	chws: "ae#chws",
	cjct: "ae#cjct",
	clig: "ae#clig",
	cpct: "ae#cpct",
	cpsp: "ae#cpsp",
	cswh: "ae#cswh",
	curs: "ae#curs",
	c2pc: "ae#c2pc",
	c2sc: "ae#c2sc",
	dist: "ae#dist",
	dlig: "ae#dlig",
	dnom: "ae#dnom",
	dtls: "ae#dtls",
	expt: "ae#expt",
	falt: "fj#falt",
	fin2: "fj#fin2",
	fin3: "fj#fin3",
	fina: "fj#fina",
	flac: "fj#flac",
	frac: "fj#frac",
	fwid: "fj#fwid",
	half: "fj#half",
	haln: "fj#haln",
	halt: "fj#halt",
	hist: "fj#hist",
	hkna: "fj#hkna",
	hlig: "fj#hlig",
	hngl: "fj#hngl",
	hojo: "fj#hojo",
	hwid: "fj#hwid",
	init: "fj#init",
	isol: "fj#isol",
	ital: "fj#ital",
	jalt: "fj#jalt",
	jp78: "fj#jp78",
	jp83: "fj#jp83",
	jp90: "fj#jp90",
	jp04: "fj#jp04",
	kern: "ko#kern",
	lfbd: "ko#lfbd",
	liga: "ko#liga",
	ljmo: "ko#ljmo",
	lnum: "ko#lnum",
	locl: "ko#locl",
	ltra: "ko#ltra",
	ltrm: "ko#ltrm",
	mark: "ko#mark",
	med2: "ko#med2",
	medi: "ko#medi",
	mgrk: "ko#mgrk",
	mkmk: "ko#mkmk",
	mset: "ko#mset",
	nalt: "ko#nalt",
	nlck: "ko#nlck",
	nukt: "ko#nukt",
	numr: "ko#numr",
	onum: "ko#onum",
	opbd: "ko#opbd",
	ordn: "ko#ordn",
	ornm: "ko#ornm",
	palt: "pt#palt",
	pcap: "pt#pcap",
	pkna: "pt#pkna",
	pnum: "pt#pnum",
	pref: "pt#pref",
	pres: "pt#pres",
	pstf: "pt#pstf",
	psts: "pt#psts",
	pwid: "pt#pwid",
	qwid: "pt#qwid",
	rand: "pt#rand",
	rclt: "pt#rclt",
	rkrf: "pt#rkrf",
	rlig: "pt#rlig",
	rphf: "pt#rphf",
	rtbd: "pt#rtbd",
	rtla: "pt#rtla",
	rtlm: "pt#rtlm",
	ruby: "pt#ruby",
	rvrn: "pt#rvrn",
	salt: "pt#salt",
	sinf: "pt#sinf",
	size: "pt#size",
	smcp: "pt#smcp",
	smpl: "pt#smpl",
	ssty: "pt#ssty",
	stch: "pt#stch",
	subs: "pt#subs",
	sups: "pt#sups",
	swsh: "pt#swsh",
	titl: "pt#titl",
	tjmo: "pt#tjmo",
	tnam: "pt#tnam",
	tnum: "pt#tnum",
	trad: "pt#trad",
	twid: "pt#twid",
	unic: "uz#unic",
	valt: "uz#valt",
	vapk: "uz#vapk",
	vatu: "uz#vatu",
	vchw: "uz#vchw",
	vert: "uz#vert",
	vhal: "uz#vhal",
	vjmo: "uz#vjmo",
	vkna: "uz#vkna",
	vkrn: "uz#vkrn",
	vpal: "uz#vpal",
	vrt2: "uz#vrt2",
	vrtr: "uz#vrtr",
	zero: "uz#zero",
};

function pad(i: number): string {
	return (i < DECIMAL ? "0" : "") + i;
}

const DECIMAL = 10;
const SS_RANGE = 20;
const CV_RANGE = 99;

for(let i = 1; i <= SS_RANGE; i++) {
	featureURL["ss" + pad(i)] = "pt#ssxx";
}
for(let i = 1; i <= CV_RANGE; i++) {
	featureURL["cv" + pad(i)] = "ae#cv01-cv99";
}

import i18n from "../i18n";

export type SupportedFormats = "ttf" | "woff2";

export function getFormats(format: SupportedFormats): FilePickerAcceptType {
	const { t } = i18n.global;
	const map: Record<SupportedFormats, FilePickerAcceptType> = {
		ttf: {
			description: t("format.ttfDescription"),
			accept: { "font/ttf": ".ttf" as const },
		},
		woff2: {
			description: t("format.woff2Description"),
			accept: { "font/woff2": ".woff2" as const },
		},
	};
	return map[format];
}
