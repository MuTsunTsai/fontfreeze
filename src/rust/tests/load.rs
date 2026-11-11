//! Loading fonts (`loadFont`) and fixing legacy fonts (`processLegacy`).

mod common;

use common::*;
use serde_json::json;

#[test]
fn variable_font_info() {
	let result = fontfreeze::load_font(font("FFTest-Var.ttf")).unwrap();
	assert!(result.data.is_none());
	let info = result.info;
	assert_eq!(info.family.as_deref(), Some("FFTest"));
	assert_eq!(info.subfamily.as_deref(), Some("Regular"));
	assert_eq!(
		info.copyright.as_deref(),
		Some("Copyright (c) FontFreeze test")
	);
	assert_eq!(info.id.as_deref(), Some("FFTest Var Regular 1.000"));
	assert_eq!(info.version.as_deref(), Some("Version 1.000"));
	assert_eq!(info.trademark.as_deref(), Some("FFTest is not a trademark"));
	assert_eq!(info.manufacturer.as_deref(), Some("FontFreeze"));
	assert_eq!(info.designer.as_deref(), Some("FontFreeze test generator"));
	assert_eq!(
		info.description.as_deref(),
		Some("A font for the tests of FontFreeze.")
	);
	assert_eq!(
		info.vendor_url.as_deref(),
		Some("https://example.com/vendor")
	);
	assert_eq!(
		info.designer_url.as_deref(),
		Some("https://example.com/designer")
	);
	assert_eq!(info.license.as_deref(), Some("MIT License"));
	assert_eq!(
		info.license_url.as_deref(),
		Some("https://opensource.org/licenses/MIT")
	);
	assert_eq!(info.typo_family.as_deref(), Some("FFTest"));
	assert_eq!(info.typo_subfamily.as_deref(), Some("Var Regular"));
	assert_eq!(info.font_height, 1000);
	assert_eq!(info.line_height, 1300);
	assert!(!info.preview);

	// The two "liga" records are listed once, in the order of the FeatureList.
	assert_eq!(
		info.gsub,
		[
			"calt", "case", "ccmp", "cv01", "liga", "locl", "ss01", "ss02", "ss03", "ss04", "zero"
		]
	);

	let fvar = info.fvar.unwrap();
	let axes: Vec<_> = fvar
		.axes
		.iter()
		.map(|a| (a.tag.as_str(), a.min, a.default, a.max, a.name.as_deref()))
		.collect();
	assert_eq!(
		axes,
		[
			("wght", 100.0, 400.0, 900.0, Some("Weight")),
			("TEST", 0.0, 0.0, 100.0, Some("Test Axis")),
		]
	);
	let instances: Vec<_> = fvar
		.instances
		.iter()
		.map(|i| {
			let coordinates: Vec<_> = i
				.coordinates
				.iter()
				.map(|(k, &v)| (k.as_str(), v))
				.collect();
			(i.name.as_deref(), coordinates)
		})
		.collect();
	assert_eq!(
		instances,
		[
			(Some("Thin"), vec![("wght", 100.0), ("TEST", 0.0)]),
			(Some("Regular"), vec![("wght", 400.0), ("TEST", 0.0)]),
			(Some("Black"), vec![("wght", 900.0), ("TEST", 0.0)]),
			(Some("Tested"), vec![("wght", 400.0), ("TEST", 100.0)]),
		]
	);
}

#[test]
fn static_font_info() {
	let info = fontfreeze::load_font(font("FFTest-Static.otf"))
		.unwrap()
		.info;
	assert_eq!(info.family.as_deref(), Some("FFTest Static"));
	assert_eq!(info.subfamily.as_deref(), Some("Bold Italic"));
	assert_eq!(info.version.as_deref(), Some("Version 2.000"));
	assert_eq!(info.copyright, None);
	assert_eq!(info.typo_family, None);
	assert_eq!(info.typo_subfamily, None);
	assert!(info.fvar.is_none());
	// GSUB without a FeatureList.
	assert!(info.gsub.is_empty());
	assert_eq!(info.font_height, 1000);
	assert_eq!(info.line_height, 1150);
}

#[test]
fn collection_reads_first_font() {
	let info = fontfreeze::load_font(font("FFTest.ttc")).unwrap().info;
	assert_eq!(info.family.as_deref(), Some("FFTest Static"));
	assert!(info.fvar.is_none());

	let output = fontfreeze::process_font(font("FFTest.ttc"), &args(json!({})), None).unwrap();
	assert!(has_table(&output, b"CFF "));
	assert!(!has_table(&output, b"glyf"));
}

#[test]
fn invalid_fonts() {
	assert!(fontfreeze::load_font(font("FFTest-NoOS2.otf")).is_err_and(|e| e.0.contains("OS/2")));
	assert!(fontfreeze::load_font(b"not a font at all".as_slice().into()).is_err());
	assert!(fontfreeze::load_font([].as_slice().into()).is_err());
}

#[test]
fn legacy_big5_font() {
	let result = fontfreeze::load_font(font("FFTest-Big5.ttf")).unwrap();
	let info = result.info;
	assert!(info.preview);
	// Names in the mixed encoding are fixed; those in proper Big5 are kept.
	assert_eq!(info.family.as_deref(), Some("測試明體"));
	assert_eq!(info.subfamily.as_deref(), Some("標準"));
	assert_eq!(info.copyright.as_deref(), Some("版權所有"));
	assert_eq!(info.version.as_deref(), Some("Version 1.000"));

	// The Big5 cmap is replaced with a Unicode one.
	let converted = result.data.expect("the converted font");
	let tables = cmap(&converted);
	assert_eq!(tables.len(), 1);
	let table = &tables[0];
	assert_eq!((table.platform, table.encoding, table.format), (3, 1, 4));
	let chars: Vec<char> = table
		.map
		.keys()
		.map(|&c| char::from_u32(c).unwrap())
		.collect();
	// "AB" (two ASCII bytes) and an invalid code are skipped.
	assert_eq!(chars, [' ', 'A', '中', '和', '永']);
	// The glyphs are kept in order.
	assert_eq!(glyph(&converted, '永'), 3);
	assert_eq!(glyph(&converted, '和'), 4);
	assert_eq!(glyph(&converted, '中'), 5);

	// The broken mort table is removed.
	assert!(has_table(&font("FFTest-Big5.ttf"), b"mort"));
	assert!(!has_table(&converted, b"mort"));

	// The converted font is what the app works on from now on (see `wasm.rs`).
	let output = fontfreeze::process_font(
		converted.as_slice().into(),
		&args(json!({ "variations": {}, "options": { "spacing": 10 } })),
		None,
	)
	.unwrap();
	assert_eq!(width(&output, "永"), width(&converted, "永") + 10);
}

#[test]
fn process_legacy_removes_broken_tables() {
	let fixed = fontfreeze::process_legacy(font("FFTest-Big5.ttf")).unwrap();
	assert!(!has_table(&fixed, b"mort"));
	// Unlike `load_font`, the cmap is not converted.
	assert!(
		cmap(&fixed)
			.iter()
			.any(|t| (t.platform, t.encoding) == (3, 4))
	);

	// A font without problems is just saved again.
	let fixed = fontfreeze::process_legacy(font("FFTest-Var.ttf")).unwrap();
	assert_eq!(width(&fixed, "a"), width(&font("FFTest-Var.ttf"), "a"));
}
