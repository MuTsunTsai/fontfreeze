import { shallowRef } from "vue";

import { openBlob } from "./loader";
import { store } from "./store";
import { alert } from "./vue/modals/alert.vue";

/**
 * We similarly use a stylesheet to handle local fonts.
 * This is the recommended approach.
 */
const localStyle = document.createElement("style");
document.head.appendChild(localStyle);

export const showLocal = shallowRef(false);

export async function local(): Promise<void> {
	gtag("event", "show_local");
	await navigator.permissions.query({
		name: "local-fonts" as PermissionName,
	});
	const fonts = await window.queryLocalFonts();
	if(fonts.length == 0) return; // permission denied
	buildLocalFonts(fonts);
	store.localFonts = fonts;
	showLocal.value = true;
}

export async function loadLocal(): Promise<void> {
	gtag("event", "open_local");
	const font = store.localFonts[store.localFont as number];
	let blob;
	try {
		blob = await font.blob();
	} catch(e) {
		if(e instanceof Error) alert("An error occur: " + e.message);
		store.unavailableFonts.push(font.postscriptName);
		return;
	} finally {
		if(store.localFamily) store.localFamily = "";
		if(store.localFont) store.localFont = "";
	}
	showLocal.value = false;
	try {
		await openBlob(blob, font.fullName);
	} catch(e) {
		if(e instanceof Error) alert("An error occur: " + e.message);
	}
}

function buildLocalFonts(fonts: FontData[]): void {
	const sheet = localStyle.sheet!;
	while(sheet.cssRules.length) sheet.deleteRule(0);
	for(const font of fonts) {
		sheet.insertRule(`@font-face { font-family: 'local ${font.fullName}'; src: local('${font.fullName}'), local('${font.postscriptName}');}`);
	}
}
