//! Activating and deactivating GSUB features.
//!
//! Most tests check the core property of freezing: the frozen font, with its default
//! features, shapes text as the original font does with the chosen features on (or off).

mod common;

use common::*;
use serde_json::json;

const VAR: &str = "FFTest-Var.ttf";

/// The features that the UI lets users activate in FFTest-Var.ttf.
const ACTIVATABLE: &[&str] = &["case", "cv01", "ss01", "ss02", "ss03", "ss04", "zero"];

#[test]
fn activate_each_feature() {
	let input = font(VAR);
	for single_sub in [true, false] {
		for &feature in ACTIVATABLE {
			let output = process(
				VAR,
				json!({ "features": [feature], "options": { "singleSub": single_sub } }),
			);
			println!("{feature}, singleSub: {single_sub}");
			assert_frozen(&input, &output, &[(feature, 1)], &[]);
		}
	}
}

#[test]
fn activate_all_features() {
	let input = font(VAR);
	let on: Vec<_> = ACTIVATABLE.iter().map(|&f| (f, 1)).collect();
	for single_sub in [true, false] {
		let output = process(
			VAR,
			json!({ "features": ACTIVATABLE, "options": { "singleSub": single_sub } }),
		);
		println!("singleSub: {single_sub}");
		assert_frozen(&input, &output, &on, &[]);
	}
}

#[test]
fn chained_single_substitutions() {
	// "case" maps one -> one.case, then "ss02" maps one.case -> one.ss02 (issue #27).
	let input = font(VAR);
	let output = process(VAR, json!({ "features": ["case", "ss02"] }));
	assert_frozen(&input, &output, &[("case", 1), ("ss02", 1)], &[]);

	let one = glyph(&input, '1');
	let one_ss02 = 268;
	assert_eq!(subtable(&output, 3, 1).map[&('1' as u32)], one_ss02);
	// Format 0 cannot address glyph IDs above 255, so it is left alone.
	assert_eq!(subtable(&output, 1, 0).map[&('1' as u32)], one);
}

#[test]
fn single_substitution_updates_cmap() {
	let input = font(VAR);
	let output = process(VAR, json!({ "features": ["ss01"] }));
	let a = glyph(&input, 'a');
	let a_ss01 = 15;
	assert_ne!(a, a_ss01);
	for table in cmap(&output) {
		if table.map.contains_key(&('a' as u32)) {
			assert_eq!(
				table.map[&('a' as u32)],
				a_ss01,
				"subtable ({}, {})",
				table.platform,
				table.encoding
			);
		}
	}
	// (0, 3) and (3, 1) share the same subtable, as in the original.
	assert_eq!(subtable(&input, 0, 3).offset, subtable(&input, 3, 1).offset);
	assert_eq!(
		subtable(&output, 0, 3).offset,
		subtable(&output, 3, 1).offset
	);

	// Without singleSub, cmap is untouched.
	let output = process(
		VAR,
		json!({ "features": ["ss01"], "options": { "singleSub": false } }),
	);
	assert_eq!(glyph(&output, 'a'), a);
}

#[test]
fn ligatures_follow_substituted_glyphs() {
	// "ss04" maps f -> f.ss04 in cmap, so "liga" must ligate f.ss04 f.ss04 as it did f f.
	let input = font(VAR);
	let output = process(VAR, json!({ "features": ["ss04"] }));
	assert_ne!(glyph(&output, 'f'), glyph(&input, 'f'));
	assert_eq!(width(&output, "ff"), width(&input, "ff"));
	assert_frozen(&input, &output, &[("ss04", 1)], &[]);
}

#[test]
fn custom_feature_value() {
	let input = font(VAR);
	for value in 1..=3 {
		let output = process(
			VAR,
			json!({ "features": ["cv01"], "featureValues": { "cv01": value } }),
		);
		assert_frozen(&input, &output, &[("cv01", value)], &[]);
		// The chosen alternate is put in cmap.
		assert_eq!(
			width(&output, "g"),
			width(&input, "g") + 20 * (17 - 4 + value as i32)
		);
	}
}

#[test]
fn custom_feature_value_out_of_range() {
	// The AlternateSet is left untouched, so it is not a single substitution.
	let input = font(VAR);
	let output = process(
		VAR,
		json!({ "features": ["cv01"], "featureValues": { "cv01": 9 } }),
	);
	assert_eq!(glyph(&output, 'g'), glyph(&input, 'g'));
}

#[test]
fn deactivate_features() {
	let input = font(VAR);
	let disables = ["calt", "liga", "ss01", "cv01"];
	let output = process(VAR, json!({ "disables": disables }));
	let off: Vec<_> = disables.iter().map(|&f| (f, 0)).collect();
	assert_frozen(&input, &output, &off, &[]);

	// The records are kept (the scripts refer to them by index), but renamed and emptied.
	let before = gsub_features(&input);
	let after = gsub_features(&output);
	assert_eq!(before.len(), after.len());
	for ((tag, _, _), (new_tag, lookups, params)) in before.iter().zip(&after) {
		if disables.contains(&tag.as_str()) {
			assert_eq!(new_tag, "DELT");
			assert!(lookups.is_empty());
			assert!(!params);
		} else {
			assert_eq!(new_tag, tag);
		}
	}
}

#[test]
fn activate_with_deactivated_target() {
	// The original Python version kept the tag of a deactivated "calt" in fallback mode,
	// and shapers then used that empty "calt" instead of the one with the activated features.
	let input = font(VAR);
	let output = process(
		VAR,
		json!({ "features": ["ss02", "ss03"], "disables": ["calt", "liga", "ss01", "cv01"] }),
	);
	assert_frozen(
		&input,
		&output,
		&[
			("ss02", 1),
			("ss03", 1),
			("calt", 0),
			("liga", 0),
			("ss01", 0),
			("cv01", 0),
		],
		&[],
	);
}

#[test]
fn feature_params_are_dropped() {
	// ss01 has StylisticSet params and cv01 CharacterVariant params, which don't fit
	// "calt" or "DELT".
	let output = process(VAR, json!({ "features": ["ss01", "cv01"] }));
	for (tag, _, params) in gsub_features(&output) {
		if tag == "calt" || tag == "DELT" {
			assert!(!params, "{tag} has FeatureParams");
		}
	}
	// The untouched ones keep theirs.
	assert!(
		gsub_features(&output)
			.iter()
			.any(|(tag, _, params)| tag == "ss02" && *params)
	);
}

#[test]
fn other_targets() {
	let input = font(VAR);
	// "rvrn" is on by default too.
	let output = process(
		VAR,
		json!({ "features": ["ss01", "zero"], "options": { "target": "rvrn", "singleSub": false } }),
	);
	assert_frozen(&input, &output, &[("ss01", 1), ("zero", 1)], &[]);

	// A target that is off by default only renames the features.
	let output = process(
		VAR,
		json!({ "features": ["ss01", "zero"], "options": { "target": "ss20", "singleSub": false } }),
	);
	let tags: Vec<_> = gsub_features(&output)
		.into_iter()
		.map(|(tag, ..)| tag)
		.collect();
	assert!(tags.contains(&"ss20".to_owned()));
	assert!(!tags.contains(&"ss01".to_owned()));
	assert!(!tags.contains(&"zero".to_owned()));
}

#[test]
fn invalid_target() {
	let error = process_error(
		VAR,
		json!({ "features": ["ss01"], "options": { "target": "toolong" } }),
	);
	assert!(error.contains("Invalid target feature"), "{error}");
}

#[test]
fn font_without_feature_list() {
	// FFTest-Static.otf has a GSUB table without any lists.
	let output = process(
		"FFTest-Static.otf",
		json!({ "variations": {}, "features": ["ss01"], "disables": ["liga"] }),
	);
	assert_eq!(
		width(&output, "abc"),
		width(&font("FFTest-Static.otf"), "abc")
	);
}
