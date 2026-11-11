import { describe, expect, test } from "@rstest/core";

import {
	applyCustomValues, bucketFeatures, formatCustomValues, getFeatureSettings, nextFeatureState, parseCustomValues
} from "../../src/app/features";

import type { FeatureState } from "../../src/app/features";

const GSUB = ["calt", "cv01", "liga", "ss01", "ss02", "zero"];

describe("nextFeatureState", () => {
	test("cycles through unchanged, on and off", () => {
		expect(nextFeatureState(false)).toBe(true);
		expect(nextFeatureState(true)).toBe(undefined);
		expect(nextFeatureState(undefined)).toBe(false);
	});
});

describe("bucketFeatures", () => {
	test("sorts the states", () => {
		const states: Record<string, FeatureState> = {
			calt: false, cv01: 2, liga: undefined, ss01: true, ss02: 0, zero: 1,
		};
		expect(bucketFeatures(GSUB, states)).toEqual({
			features: ["cv01", "ss01", "zero"],
			featureValues: { cv01: 2, zero: 1 },
			// A value of 0 means off.
			disables: ["liga", "ss02"],
		});
	});

	test("only considers the features of the font", () => {
		expect(bucketFeatures(["ss01"], { ss01: true, ss02: true })).toEqual({
			features: ["ss01"], featureValues: {}, disables: [],
		});
	});
});

describe("getFeatureSettings", () => {
	test("previews the states", () => {
		const states: Record<string, FeatureState> = {
			calt: false, cv01: 2, liga: undefined, ss01: true, ss02: 0, zero: false,
		};
		expect(getFeatureSettings(GSUB, states)).toBe("'cv01' 2,'liga' off,'ss01' on,'ss02' 0");
	});
});

describe("custom values", () => {
	const valid = new Set(GSUB);

	test("parses values", () => {
		expect(parseCustomValues(" cv01 = 2 , ss02=3,, ", valid)).toEqual({
			parsed: { cv01: 2, ss02: 3 }, malformed: [], unknownTags: [], badValues: [],
		});
		expect(parseCustomValues("", valid).parsed).toEqual({});
	});

	test("reports errors", () => {
		expect(parseCustomValues("cv01", valid).malformed).toEqual(["cv01"]);
		expect(parseCustomValues("cv01=2=3", valid).malformed).toEqual(["cv01=2=3"]);
		// Not in the font, or not a tag at all.
		expect(parseCustomValues("ss20=1,toolong=1", valid).unknownTags).toEqual(["ss20", "toolong"]);
		expect(parseCustomValues("cv01=-1,ss01=x", valid).badValues).toEqual(["-1", "x"]);
	});

	test("formats values", () => {
		expect(formatCustomValues({ calt: true, cv01: 2, ss01: undefined, zero: 0 })).toBe("cv01=2,zero=0");
	});

	test("applies values", () => {
		const states: Record<string, FeatureState> = { cv01: 2, ss01: 3, ss02: false };
		applyCustomValues(states, { ss01: 1, ss02: 4 });
		// cv01 is removed from the dialog, so it falls back to on.
		expect(states).toEqual({ cv01: true, ss01: 1, ss02: 4 });
	});
});
