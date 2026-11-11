/**
 * The state of a GSUB feature chosen by the user.
 *
 * - `false`: unchanged, keeping the default behavior of the font.
 * - `true`: activated.
 * - `undefined`: deactivated.
 * - A number N: activated with a custom value set via the dialog (e.g. 'cv01' 2);
 *   any positive N selects the N-th alternate of a GSUB Type 3 AlternateSet,
 *   and 0 means off (per the OpenType spec).
 */
export type FeatureState = boolean | number | undefined;

/** The state after clicking the checkbox of a feature: unchanged -> on -> off -> unchanged. */
export function nextFeatureState(state: FeatureState): FeatureState {
	if(state === false) return true;
	if(state === undefined) return false;
	return undefined;
}

/** The CSS `font-feature-settings` previewing the states. */
export function getFeatureSettings(gsub: readonly string[], features: Record<string, FeatureState>): string {
	return gsub
		.filter(g => features[g] !== false)
		.map(g => {
			const v = features[g];
			if(typeof v === "number") return `'${g}' ${v}`;
			return `'${g}' ${v ? "on" : "off"}`;
		})
		.join(",");
}

export interface FeatureBuckets {
	/** The tags to activate. */
	features: string[];
	/** The subset of `features` that carry a custom alternate index. */
	featureValues: Record<string, number>;
	/** The tags to deactivate. */
	disables: string[];
}

/** Sorts the states into the arguments that the Rust side expects. */
export function bucketFeatures(gsub: readonly string[], states: Record<string, FeatureState>): FeatureBuckets {
	const features: string[] = [];
	const featureValues: Record<string, number> = {};
	const disables: string[] = [];
	for(const g of gsub) {
		const v = states[g];
		if(v === true) {
			features.push(g);
		} else if(typeof v === "number") {
			if(v >= 1) {
				features.push(g);
				featureValues[g] = v;
			} else {
				disables.push(g);
			}
		} else if(v === undefined) {
			disables.push(g);
		}
	}
	return { features, featureValues, disables };
}

//////////////////////////////////////////////////////////////////////////////////////////
// Custom values
//////////////////////////////////////////////////////////////////////////////////////////

// Matches "tag = digits" with arbitrary surrounding whitespace.
// Tag must be exactly 4 chars (the OpenType layout-tag length).
const ITEM_RE = /^\s*([A-Za-z0-9]{4})\s*=\s*(-?\d+)\s*$/;
// Catches the shape "something = something" without enforcing tag/digit rules,
// so we can tell "wrong overall format" apart from "wrong tag/value".
const SHAPE_RE = /^\s*[^=,\s]+\s*=\s*[^=,]*\s*$/;
const TAG_RE = /^[A-Za-z0-9]{4}$/;

export interface ParseResult {
	parsed: Record<string, number>;
	malformed: string[];
	unknownTags: string[];
	badValues: string[];
}

/** Parses the custom values entered in the dialog, e.g. "cv01=2,ss02=3". */
export function parseCustomValues(text: string, validTags: ReadonlySet<string>): ParseResult {
	const result: ParseResult = { parsed: {}, malformed: [], unknownTags: [], badValues: [] };
	for(const piece of text.split(",")) {
		const raw = piece.trim();
		if(!raw) continue;
		if(!SHAPE_RE.test(raw)) {
			result.malformed.push(raw);
			continue;
		}
		const m = raw.match(ITEM_RE);
		if(!m) {
			// Shape is "x=y" but the tag isn't 4 chars or value isn't pure digits.
			const eq = raw.indexOf("=");
			const tagPart = raw.slice(0, eq).trim();
			const valPart = raw.slice(eq + 1).trim();
			if(!TAG_RE.test(tagPart)) result.unknownTags.push(tagPart);
			else result.badValues.push(valPart);
			continue;
		}
		const tag = m[1];
		const value = parseInt(m[2], 10);
		if(!validTags.has(tag)) result.unknownTags.push(tag);
		else if(value < 0) result.badValues.push(m[2]);
		else result.parsed[tag] = value;
	}
	return result;
}

/** The custom values in the format of the dialog. */
export function formatCustomValues(states: Record<string, FeatureState>): string {
	const parts: string[] = [];
	for(const tag in states) {
		const v = states[tag];
		if(typeof v === "number") parts.push(`${tag}=${v}`);
	}
	return parts.join(",");
}

/** Applies the custom values from the dialog to the states. */
export function applyCustomValues(states: Record<string, FeatureState>, values: Record<string, number>): void {
	// Tags removed from the dialog fall back to plain "enabled",
	// so that the regular checkbox tri-state resumes for them.
	for(const tag in states) {
		if(typeof states[tag] === "number" && !(tag in values)) states[tag] = true;
	}
	Object.assign(states, values);
}
