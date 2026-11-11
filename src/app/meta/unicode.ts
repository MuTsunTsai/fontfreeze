type Range = [number, number];

export type SubsetMode = "exclude" | "include";

const UNICODE_RANGE = 0x10FFFF; // Full unicode range
const HEX = 16;

/**
 * The characters to keep in the format of `fontTools.subset.parse_unicodes`,
 * given the characters to exclude or include; empty to keep all.
 */
export function getUnicodes(glyphs: string, mode: SubsetMode): string {
	const codes = getCharCodes(glyphs);
	if(mode == "exclude") {
		const ranges: Range[] = [[0, UNICODE_RANGE]];
		if(codes.length == 0) return "";
		for(const code of codes) {
			const range = ranges.find(r => r[0] <= code && code <= r[1]);
			if(!range) continue;
			const end = range[1];
			range[1] = code - 1;
			ranges.push([code + 1, end]);
		}
		return ranges.filter(r => r[0] <= r[1]).map(formatRange).join(", ").toUpperCase();
	} else {
		if(codes.length == 0) return "U+0";
		const ranges: Range[] = [];
		let start = codes[0], end = start;
		for(let i = 1; i <= codes.length; i++) {
			const code = codes[i];
			if(end == code - 1) { end = code; } else {
				ranges.push([start, end]);
				start = code;
				end = code;
			}
		}
		return ranges.map(formatRange).join(", ").toUpperCase();
	}
}

/** The sorted distinct code points of the characters. */
function getCharCodes(glyphs: string): number[] {
	const set = new Set<number>();
	for(const char of glyphs) set.add(char.codePointAt(0)!);
	return [...set].sort((a, b) => a - b);
}

function formatRange(r: Range): string {
	let result = "U+" + r[0].toString(HEX);
	if(r[1] > r[0]) result += "-" + r[1].toString(HEX);
	return result;
}
