import { callWorker } from "./bridge";
import { note } from "./meta/constants";
import { store } from "./store";
import { alert } from "./vue/modals/alert.vue";
import sample from "./meta/sample.txt?raw";

/**
 * We use a stylesheet to handle preview font.
 * We could also use Font Loading API to add the font directly without using a stylesheet,
 * but it appears that the Unicode range cannot be modified afterwards with that approach.
 */
const style = document.createElement("style");
document.head.appendChild(style);

let fontURL: string;

export async function tryPreview(url: string, info: FontInfo): Promise<void> {
	if(await setPreviewFont(url)) return;

	// If it's not done yet, try to fix legacy font issues.
	if(!info.preview) {
		try {
			const altUrl = await callWorker("legacy") as string;
			if(await setPreviewFont(altUrl)) return;
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

export function setPreviewUnicodeRange(range: string): void {
	const rule = style.sheet!.cssRules[0] as CSSFontFaceRule;
	rule.style.unicodeRange = range;
}

export { sample };

/**
 * @see https://github.com/microsoft/TypeScript/issues/51885
 */
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
