import { describe, expect, test } from "@rstest/core";

import { applySuffix, suggestedFileName } from "../../src/app/naming";
import { getFileSize } from "../../src/app/utils";

describe("applySuffix", () => {
	const options = { family: "Font", typo_family: "Font Typo", suffix: "Freeze", customNames: false };

	test("appends the suffix", () => {
		expect(applySuffix(options)).toEqual({ ...options, family: "Font Freeze", typo_family: "Font Typo Freeze" });
		// The input is not changed.
		expect(options.family).toBe("Font");
	});

	test("respects the 32-character limit of MS Word on the family name", () => {
		const family = "x".repeat(25);
		expect(applySuffix({ ...options, family }).family).toBe(family + " Freeze");
		expect(applySuffix({ ...options, family: family + "x" }).family).toBe(family + "x");
		// The typographic family name has no limit.
		expect(applySuffix({ ...options, typo_family: family + "x" }).typo_family).toBe(family + "x Freeze");
	});

	test("does nothing for custom names or without a suffix", () => {
		expect(applySuffix({ ...options, customNames: true })).toEqual({ ...options, customNames: true });
		expect(applySuffix({ ...options, suffix: "" })).toEqual({ ...options, suffix: "" });
		expect(applySuffix({ ...options, family: "", typo_family: "" }).family).toBe("");
	});
});

describe("suggestedFileName", () => {
	test("replaces the extension", () => {
		expect(suggestedFileName("Font-Regular.ttf", "ttf")).toBe("Font-Regular_freeze.ttf");
		expect(suggestedFileName("Font.Regular.OTF", "woff2")).toBe("Font.Regular_freeze.woff2");
		expect(suggestedFileName("msjh.ttc", "ttf")).toBe("msjh_freeze.ttf");
		expect(suggestedFileName("noext", "ttf")).toBe("noext_freeze.ttf");
	});
});

describe("getFileSize", () => {
	test("formats sizes", () => {
		expect(getFileSize(0)).toBe("0B");
		expect(getFileSize(1023)).toBe("1023B");
		expect(getFileSize(1024)).toBe("1.0KiB");
		expect(getFileSize(1536)).toBe("1.5KiB");
		expect(getFileSize(5 * 1024 * 1024)).toBe("5.0MiB");
	});
});
