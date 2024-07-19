import { store } from "./store";

type Range = [number, number];

export function getUnicodes() {
	const glyphs = getGlyphCharCodes();
	if(store.subsetMode == 'exclude') {
		const ranges: Range[] = [[0, 0x10FFFF]]; // Full unicode range
		if(glyphs.length == 0) return "";
		for(const code of glyphs) {
			const range = ranges.find(r => r[0] <= code && code <= r[1]);
			if(!range) continue;
			const end = range[1];
			range[1] = code - 1;
			ranges.push([code + 1, end]);
		}
		return ranges.filter(r => r[0] <= r[1]).map(formatRange).join(', ').toUpperCase();
	} else {
		if(glyphs.length == 0) return "U+0";
		const ranges: Range[] = [];
		let start = glyphs[0], end = start;
		for(let i = 1; i <= glyphs.length; i++) {
			const code = glyphs[i];
			if(end == code - 1) end = code;
			else {
				ranges.push([start, end]);
				start = code;
				end = code;
			}
		}
		return ranges.map(formatRange).join(', ').toUpperCase();
	}
}

function getGlyphCharCodes(): number[] {
	const set = new Set<number>();
	for(let i = 0; i < store.glyphs.length; i++) {
		// Handle UTF-32 code
		const codePoint = store.glyphs.codePointAt(i)!;
		const charCode = store.glyphs.charCodeAt(i);
		if(charCode != codePoint) i++;
		set.add(codePoint);
	}
	const result = [...set];
	result.sort((a, b) => a - b);
	return result;
}

function formatRange(r: Range) {
	let result = "U+" + r[0].toString(16);
	if(r[1] > r[0]) result += "-" + r[1].toString(16);
	return result;
}
