
/**
 * We similarly use a stylesheet to handle local fonts.
 * This is the recommended approach.
 */
const localStyle = document.createElement("style");
document.head.appendChild(localStyle);

export function buildLocalFonts(fonts: FontData[]) {
	const sheet = localStyle.sheet!;
	while(sheet.cssRules.length) sheet.deleteRule(0);
	for(const font of fonts) {
		sheet.insertRule(`@font-face { font-family: 'local ${font.fullName}'; src: local('${font.fullName}'), local('${font.postscriptName}');}`);
	}
}
