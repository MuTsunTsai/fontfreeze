import { describe, expect, test } from "@rstest/core";

import { getUnicodes } from "../../src/app/meta/unicode";

describe("getUnicodes", () => {
	test("keeps everything without glyphs to exclude", () => {
		expect(getUnicodes("", "exclude")).toBe("");
	});

	test("excludes glyphs", () => {
		expect(getUnicodes("b", "exclude")).toBe("U+0-61, U+63-10FFFF");
		// Adjacent and repeated characters, in any order.
		expect(getUnicodes("cba a", "exclude")).toBe("U+0-1F, U+21-60, U+64-10FFFF");
		// The ends of the range.
		expect(getUnicodes("\0\u{10FFFF}", "exclude")).toBe("U+1-10FFFE");
	});

	test("includes glyphs", () => {
		expect(getUnicodes("", "include")).toBe("U+0");
		expect(getUnicodes("a", "include")).toBe("U+61");
		expect(getUnicodes("cab x", "include")).toBe("U+20, U+61-63, U+78");
	});

	test("handles characters outside the BMP", () => {
		// A surrogate pair is one character, not two.
		expect(getUnicodes("😀a", "include")).toBe("U+61, U+1F600");
		expect(getUnicodes("😀", "exclude")).toBe("U+0-1F5FF, U+1F601-10FFFF");
	});
});
