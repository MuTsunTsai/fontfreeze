import { callWorker } from "./bridge";
import { note } from "./constants";
import { store } from "./store";

/**
 * We use a stylesheet to handle preview font.
 * We could also use Font Loading API to add the font directly without using a stylesheet,
 * but it appears that the Unicode range cannot be modified afterwards with that approach.
 */
const style = document.createElement("style");
document.head.appendChild(style);

let fontURL: string;

const BASE_LINE_HEIGHT = 1.5;

export function getPreviewStyle(): string | null {
	if(!store.font) return null;
	const feat = store.font.gsub
		.filter(g => store.features[g] !== false)
		.map(g => `'${g}' ${store.features[g] ? "on" : "off"}`)
		.join(",");
	const variation = !store.font.fvar ? "normal" :
		store.font.fvar.axes
			.map(a => `'${a.tag}' ${store.variations[a.tag]}`)
			.join(",");
	const lineHeight = (store.font.lineHeight + store.options.lineHeight) / store.font.fontHeight;
	const spacing = store.options.spacing / store.font.fontHeight;
	return `white-space: pre-line;` +
		`font-family: preview${store.previewIndex};` +
		`font-feature-settings: ${feat};` +
		`font-variation-settings: ${variation};` +
		`font-size: ${store.previewSize}pt;` +
		`line-height: ${lineHeight * BASE_LINE_HEIGHT};` +
		`letter-spacing: ${spacing}em`;
}

export async function tryPreview(url: string, info: FontInfo) {
	if(await setPreviewFont(url)) return;

	// If it's not done yet, try to fix legacy font issues.
	if(!info.preview) {
		try {
			const url = await callWorker("legacy") as string;
			if(await setPreviewFont(url)) return;
		} catch(e) {
			console.log(e);
		}
	}

	// If it's already done or the fix fails, show message.
	gtag("event", "preview_failed");
	alert("Font preview won't work for this font. " + note);
}

function setPreviewFont(url: string): Promise<boolean> {
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
