import { store } from "./store";

/**
 * We use a stylesheet to handle preview font.
 * We could also use Font Loading API to add the font directly without using a stylesheet,
 * but it appears that the Unicode range cannot be modified afterwards with that approach.
 */
const style = document.createElement("style");
document.head.appendChild(style);

let fontURL: string;

export function setPreviewFont(url: string): Promise<boolean> {
	if(fontURL) URL.revokeObjectURL(fontURL);
	fontURL = url;
	const sheet = style.sheet!;
	if(sheet.cssRules.length > 0) sheet.deleteRule(0);
	return new Promise(resolve => {
		// LoadingDone event always fires, regardless of font validity.
		document.fonts.onloadingdone = event => {
			// if the font is valid, fontfaces array will contain one element.
			resolve((event as FontFaceSetLoadEvent).fontfaces.length > 0);
		};
		sheet.insertRule(
			`@font-face {` +
			`font-family: preview${++store.previewIndex};` +
			`src: url('${fontURL}');` +
			`}`
		);
	});
}

export function setPreviewUnicodeRange(range: string) {
	const rule = style.sheet!.cssRules[0] as CSSFontFaceRule;
	rule.style.unicodeRange = range;
}

// https://github.com/microsoft/TypeScript/issues/51885
interface FontFaceSetLoadEvent extends Event {
	readonly fontfaces: readonly FontFace[];
}

// TypeScript definition is wrong as of v5.5
interface CSSFontFaceRule extends CSSRule {
	readonly style: CSSFontFaceDeclaration;
}

interface CSSFontFaceDeclaration {
	unicodeRange?: string;
}