import { openBlob } from "./loader";
import { store } from "./store";
import { modal } from "./utils";

/**
 * We similarly use a stylesheet to handle local fonts.
 * This is the recommended approach.
 */
const localStyle = document.createElement("style");
document.head.appendChild(localStyle);

export async function local() {
	gtag("event", "show_local");
	await navigator.permissions.query({
		name: "local-fonts" as PermissionName
	});
	const fonts = await window.queryLocalFonts();
	if(fonts.length == 0) return; // permission denied
	buildLocalFonts(fonts);
	store.localFonts = fonts;
	modal("#local").show();
}

export async function loadLocal() {
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
		store.localFamily = "";
		store.localFont = "";
	}
	modal("#local").hide();
	try {
		await openBlob(blob, font.fullName);
	} catch(e) {
		if(e instanceof Error) alert("An error occur: " + e.message);
	}
}

function buildLocalFonts(fonts: FontData[]) {
	const sheet = localStyle.sheet!;
	while(sheet.cssRules.length) sheet.deleteRule(0);
	for(const font of fonts) {
		sheet.insertRule(`@font-face { font-family: 'local ${font.fullName}'; src: local('${font.fullName}'), local('${font.postscriptName}');}`);
	}
}
