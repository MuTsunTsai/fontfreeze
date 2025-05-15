
/** Features that should not be exposed to the users. */
export const hiddenFeatures = [
	"abvm", "abvs", "akhn", "blwf", "blwm", "blws", "ccmp", "cfar", "cjct", "curs",
	"dist", "dtls", "fin2", "fin3", "fina", "flac", "half", "haln", "init", "isol",
	"ljmo", "locl", "ltra", "ltrm", "mark", "med2", "medi", "mkmk", "nukt", "pref",
	"pres", "pstf", "psts", "rclt", "rkrf", "rlig", "rphf", "rtla", "rtlm", "rvrn",
	"ssty", "stch", "tjmo", "vjmo", "DELT" // last one is special value
];

export const formats = {
	"ttf": {
		description: "TTF font",
		accept: { "font/ttf": ".ttf" as const },
	},
	"woff2": {
		description: "WOFF2 font",
		accept: { "font/woff2": ".woff2" as const },
	}
};

export type SupportedFormats = keyof typeof formats;

export const note =
	"Please try re-exporting the font with editors such as FontForge and see if it fixes the issue. " +
	"If it still doesn't, please submit an issue.";
