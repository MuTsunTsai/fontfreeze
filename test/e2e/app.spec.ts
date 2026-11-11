import { readFile } from "fs/promises";
import { join } from "path";
import { expect, test } from "@playwright/test";

import type { Locator, Page } from "@playwright/test";

const FONTS = join(import.meta.dirname, "../fonts");

/**
 * The advance widths of the glyphs in FFTest-Var.ttf at the default location
 * (see test/generator/generate.py); each glyph has a distinct width.
 */
const WIDTH = {
	"a": 440,
	"g": 480,
	"one": 560,
	"a.ss01": 700,
	"g.cv01.2": 780,
};
/** The change of the widths at wght=900. */
const BLACK = 40;

test.beforeEach(async ({ page }) => {
	// Keep the tests offline (and out of the analytics).
	await page.route(url => url.hostname != "localhost", route => route.abort());
	// Use the download link instead of the file picker, which cannot be automated.
	await page.addInitScript("delete Window.prototype.showSaveFilePicker; delete window.showSaveFilePicker;");
	await page.goto("");
});

//////////////////////////////////////////////////////////////////////////////////////////
// Helpers
//////////////////////////////////////////////////////////////////////////////////////////

async function open(page: Page, name: string): Promise<void> {
	await page.setInputFiles("#upload", join(FONTS, name));
	await expect(page.getByText(`${name} (`)).toBeVisible();
}

/** Generates the font, and returns the file name and the content of the download. */
async function generate(page: Page): Promise<[string, Buffer]> {
	const link = page.getByRole("link", { name: "Download font" });
	const before = await link.isVisible() ? await link.getAttribute("href") : null;
	await page.getByRole("button", { name: "Generate font!" }).click();
	await expect.poll(async () => await link.isVisible() && await link.getAttribute("href")).not.toBe(before);
	const [download] = await Promise.all([page.waitForEvent("download"), link.click()]);
	return [download.suggestedFilename(), await readFile(await download.path())];
}

/** Measures the texts with a font at 1000px, i.e. in the units of the test fonts. */
function measure(page: Page, font: Buffer, texts: string[]): Promise<number[]> {
	return page.evaluate(async ({ bytes, strings }) => {
		const face = new FontFace("measure" + Math.random().toString().slice(2), new Uint8Array(bytes));
		await face.load();
		document.fonts.add(face);
		const context = document.createElement("canvas").getContext("2d")!;
		context.font = `1000px "${face.family}"`;
		return strings.map(t => context.measureText(t).width);
	}, { bytes: [...font], strings: texts });
}

function feature(page: Page, tag: string): Locator {
	return page.locator(".v-selection-control").filter({ hasText: new RegExp(`^${tag}$`) });
}

/**
 * The state of a feature checkbox as shown: unchanged (false), on (true) or off (undefined).
 *
 * The icon is checked rather than the input, as the latter can be out of sync: Vuetify
 * keeps its own state while the model value is undefined (off).
 */
async function featureState(page: Page, tag: string): Promise<boolean | undefined> {
	const icon = await feature(page, tag).locator(".v-icon").getAttribute("class");
	if(icon?.includes("mdi-close-box")) return undefined;
	return Boolean(icon?.includes("mdi-checkbox-marked"));
}

async function choose(page: Page, label: string, option: string): Promise<void> {
	await page.getByLabel(label).click({ force: true });
	await page.getByRole("option", { name: option }).click();
}

function alertDialog(page: Page): Locator {
	return page.locator(".v-dialog .v-card").filter({ has: page.getByRole("button", { name: "OK" }) });
}

//////////////////////////////////////////////////////////////////////////////////////////
// Tests
//////////////////////////////////////////////////////////////////////////////////////////

test("shows the information of a font", async ({ page }) => {
	await open(page, "FFTest-Var.ttf");
	await expect(page.getByText("Version 1.000")).toBeVisible();

	// The features, without the hidden ones and the duplicates.
	const tags = await page.locator(".v-selection-control label").allInnerTexts();
	const features = tags.filter(t => /^[a-z0-9]{4}$/.test(t));
	expect(features).toEqual(["calt", "case", "cv01", "liga", "ss01", "ss02", "ss03", "ss04", "zero"]);

	// The variations.
	await expect(page.getByText("Weight", { exact: true })).toBeVisible();
	await expect(page.getByText("Test Axis", { exact: true })).toBeVisible();

	await page.getByRole("button", { name: "More info" }).click();
	await expect(page.getByText("A font for the tests of FontFreeze.")).toBeVisible();
});

test("cycles the state of a feature", async ({ page }) => {
	await open(page, "FFTest-Var.ttf");
	expect(await featureState(page, "ss01")).toBe(false);
	for(const state of [true, undefined, false, true, undefined, false]) {
		await feature(page, "ss01").locator("input").click();
		expect(await featureState(page, "ss01")).toBe(state);
		// The input is in sync, for accessibility.
		expect(await feature(page, "ss01").locator("input").isChecked()).toBe(state === true);
	}
});

test("sets custom feature values", async ({ page }) => {
	await open(page, "FFTest-Var.ttf");
	const dialog = page.locator(".v-dialog").filter({ hasText: "Custom feature values" });

	await page.getByRole("button", { name: "Custom" }).click();
	await dialog.getByRole("textbox").fill("cv01=2, ss05=1");
	await dialog.getByRole("button", { name: "OK" }).click();
	await expect(dialog.getByText("Unknown feature tag: ss05.")).toBeVisible();
	await dialog.getByRole("textbox").fill("cv01=2");
	await dialog.getByRole("button", { name: "OK" }).click();
	await expect(dialog).toBeHidden();
	await expect(page.locator(".feature-custom-box[data-value='2']")).toBeVisible();

	// Removing the value turns the feature on, and the checkbox works as usual.
	await page.getByRole("button", { name: "Custom" }).click();
	await expect(dialog.getByRole("textbox")).toHaveValue("cv01=2");
	await dialog.getByRole("textbox").fill("");
	await dialog.getByRole("button", { name: "OK" }).click();
	expect(await featureState(page, "cv01")).toBe(true);
	await feature(page, "cv01").locator("input").click();
	expect(await featureState(page, "cv01")).toBe(undefined);
});

test("generates a frozen font", async ({ page }) => {
	await open(page, "FFTest-Var.ttf");
	await feature(page, "ss01").locator("input").click();
	await page.getByRole("button", { name: "Custom" }).click();
	await page.locator(".v-dialog").getByRole("textbox").fill("cv01=2");
	await page.locator(".v-dialog").getByRole("button", { name: "OK" }).click();
	await choose(page, "Predefined instances", "Black");

	const [name, font] = await generate(page);
	expect(name).toBe("FFTest-Var_freeze.ttf");
	expect(await measure(page, font, ["a", "g", "1"])).toEqual([
		WIDTH["a.ss01"] + BLACK,
		WIDTH["g.cv01.2"] + BLACK,
		WIDTH.one + BLACK,
	]);

	// The input is kept in wasm, so it can be generated again with other options.
	await feature(page, "ss01").locator("input").click(); // Now deactivated.
	const [, again] = await generate(page);
	expect(await measure(page, again, ["a"])).toEqual([WIDTH.a + BLACK]);
});

test("generates WOFF2", async ({ page }) => {
	await open(page, "FFTest-Var.ttf");
	await choose(page, "Output format", "WOFF2 (Web Open Font Format v2)");
	const [name, font] = await generate(page);
	expect(name).toBe("FFTest-Var_freeze.woff2");
	expect(font.subarray(0, 4).toString()).toBe("wOF2");
	expect(await measure(page, font, ["a"])).toEqual([WIDTH.a]);
});

test("subsets the font", async ({ page }) => {
	await open(page, "FFTest-Var.ttf");
	await page.getByLabel("Subsetting", { exact: true }).fill("ag");
	await choose(page, "Subsetting mode", "Include only these glyphs");
	await expect(page.getByText("unicode-range: U+61, U+67;")).toBeVisible();
	const [, font] = await generate(page);
	// Characters not kept fall back to another font.
	const [a, one] = await measure(page, font, ["a", "1"]);
	expect(a).toBe(WIDTH.a);
	expect(one).not.toBe(WIDTH.one);
});

test("converts a legacy Big5 font", async ({ page }) => {
	await open(page, "FFTest-Big5.ttf");
	// The fixed name, and no alert for the preview.
	await expect(page.getByText("測試明體")).toBeVisible();
	await expect(alertDialog(page)).toBeHidden();
	const [, font] = await generate(page);
	expect(await measure(page, font, ["永"])).toEqual([460]);
});

test("fixes a font that the browser rejects", async ({ page }) => {
	// The browser rejects misaligned tables, so the font is saved again (`processLegacy`).
	await open(page, "FFTest-Misaligned.otf");
	await expect(alertDialog(page)).toBeHidden();
	const loaded = await page.evaluate(() => [...document.fonts].some(f => f.family.startsWith("preview") && f.status == "loaded"));
	expect(loaded).toBe(true);
	const [, font] = await generate(page);
	expect(await measure(page, font, ["a"])).toEqual([440]);
});

test("keeps the font after opening an invalid file", async ({ page }) => {
	await open(page, "FFTest-Var.ttf");
	await page.setInputFiles("#upload", { name: "bad.ttf", mimeType: "font/ttf", buffer: Buffer.from("not a font") });
	await expect(alertDialog(page)).toContainText("\"bad.ttf\" is not a valid font file");
	await alertDialog(page).getByRole("button", { name: "OK" }).click();
	const [name, font] = await generate(page);
	expect(name).toBe("FFTest-Var_freeze.ttf");
	expect(await measure(page, font, ["a"])).toEqual([WIDTH.a]);
});

test("shows errors from the font processing", async ({ page }) => {
	await open(page, "FFTest-ZeroWin.otf");
	await page.getByLabel("Additional line height").fill("100");
	await page.getByRole("button", { name: "Generate font!" }).click();
	await expect(alertDialog(page)).toContainText("An error occur: division by zero");
});

test("fixes contours of a CFF font", async ({ page }) => {
	await open(page, "FFTest-Static.otf");
	await page.getByLabel("Fix contour overlap issues on macOS.").check();
	const [, font] = await generate(page);
	expect(font.subarray(0, 4).toString()).toBe("OTTO");
});

test("opens a local font", async ({ page }) => {
	const data = (await readFile(join(FONTS, "FFTest-Static.otf"))).toString("base64");
	await page.addInitScript(base64 => {
		const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0));
		const font = {
			family: "FFTest Static",
			fullName: "FFTest Static Bold Italic",
			postscriptName: "FFTestStatic-BoldItalic",
			style: "Bold Italic",
			blob: () => Promise.resolve(new Blob([bytes])),
		};
		Object.assign(window, { queryLocalFonts: () => Promise.resolve([font]) });
	}, data);
	await page.reload();

	await page.getByRole("button", { name: "Select local font" }).click();
	const dialog = page.locator(".v-dialog").filter({ hasText: "Select local font" });
	await dialog.getByRole("option", { name: /FFTest Static/ }).first().click();
	await dialog.getByRole("button", { name: "OK" }).click();
	await expect(page.getByText("FFTest Static Bold Italic (")).toBeVisible();
});
