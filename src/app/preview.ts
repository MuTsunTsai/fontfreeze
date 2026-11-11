import { callWorker } from "./bridge";
import i18n from "./i18n";
import { store } from "./store";
import { alert } from "./vue/modals/alert.vue";
import sample from "./meta/sample.txt?raw";

const { t } = i18n.global;

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
	alert(t("error.previewFailed") + t("error.note"));
}

/** Sets the preview font, and returns whether the browser accepts it. */
async function setPreviewFont(url: string): Promise<boolean> {
	if(fontURL) URL.revokeObjectURL(fontURL);
	fontURL = url;
	const sheet = style.sheet!;
	if(sheet.cssRules.length > 0) sheet.deleteRule(0);
	const family = `preview${++store.previewIndex}`;
	sheet.insertRule(`@font-face { font-family: ${family}; src: url('${fontURL}'); }`);
	try {
		// Waits for this font only; the loadingdone event of document.fonts may come
		// from other fonts being loaded at the same time.
		const faces = await document.fonts.load(`1em ${family}`);
		return faces.length > 0 && faces.every(f => f.status == "loaded");
	} catch {
		return false;
	}
}

export function setPreviewUnicodeRange(range: string): void {
	const rule = style.sheet!.cssRules[0] as CSSFontFaceRule;
	rule.style.unicodeRange = range;
}

export { sample };

// TypeScript definition is wrong as of v5.5
interface CSSFontFaceRule extends CSSRule {
	readonly style: CSSFontFaceDeclaration;
}

interface CSSFontFaceDeclaration {
	unicodeRange?: string;
}
