//! Variations, names, metrics, subsetting and the output format.

mod common;

use std::cell::RefCell;
use std::rc::Rc;

use common::*;
use read_fonts::TableProvider;
use serde_json::json;

const VAR: &str = "FFTest-Var.ttf";
const STATIC: &str = "FFTest-Static.otf";

//////////////////////////////////////////////////////////////////////////////////////////
// Variations
//////////////////////////////////////////////////////////////////////////////////////////

#[test]
fn instantiate() {
	let input = font(VAR);
	for (wght, test) in [(400, 0), (100, 0), (900, 0), (650, 50), (900, 100)] {
		let output = process(VAR, json!({ "variations": { "wght": wght, "TEST": test } }));
		assert_frozen(
			&input,
			&output,
			&[],
			&[("wght", wght as f32), ("TEST", test as f32)],
		);
		for tag in [b"fvar", b"gvar", b"cvar", b"STAT", b"HVAR", b"MVAR"] {
			assert!(
				!has_table(&output, tag),
				"{} is kept",
				String::from_utf8_lossy(tag)
			);
		}
	}
}

#[test]
fn instantiate_metrics() {
	// MVAR raises usWinAscent from 1000 to 1100 at wght=900.
	let output = process(VAR, json!({ "variations": { "wght": 900, "TEST": 0 } }));
	assert_eq!(font_ref(&output).os2().unwrap().us_win_ascent(), 1100);
}

#[test]
fn description() {
	let output = process(
		VAR,
		json!({
			"variations": { "wght": 650.5, "TEST": 0 },
			"features": ["ss01", "cv01"],
			"disables": ["liga"],
		}),
	);
	assert_eq!(
		name(&output, 10).as_deref(),
		Some(
			"Frozen from FFTest Version 1.000. Sets Weight=650.5, Test Axis=0. Activates ss01, cv01. Deactivates liga."
		)
	);

	let output = process(STATIC, json!({ "variations": {} }));
	assert_eq!(
		name(&output, 10).as_deref(),
		Some("Frozen from FFTest Static Version 2.000.")
	);
}

#[test]
fn keep_variations() {
	let input = font(VAR);
	let output = process(
		VAR,
		json!({ "options": { "keepVar": true }, "features": ["ss01"] }),
	);
	for tag in [b"fvar", b"gvar", b"cvar", b"STAT", b"HVAR", b"MVAR"] {
		assert!(
			has_table(&output, tag),
			"{} is removed",
			String::from_utf8_lossy(tag)
		);
	}
	assert_eq!(
		name(&output, 10).as_deref(),
		Some("Frozen from FFTest Version 1.000. Activates ss01.")
	);
	// The names of the axes and the instances (IDs > 25) are kept.
	let font = font_ref(&output);
	let fvar = font.fvar().unwrap();
	for axis in fvar.axes().unwrap() {
		assert!(name(&output, axis.axis_name_id().to_u16()).is_some());
	}
	// The variations still work.
	for wght in [100.0, 900.0] {
		for text in TEXTS {
			assert_eq!(
				shape(&output, text, None, &[], &[("wght", wght)]),
				shape(&input, text, None, &[("ss01", 1)], &[("wght", wght)]),
			);
		}
	}
}

//////////////////////////////////////////////////////////////////////////////////////////
// Names
//////////////////////////////////////////////////////////////////////////////////////////

#[test]
fn names_of_frozen_font() {
	let output = process(VAR, json!({}));
	assert_eq!(name(&output, 1).as_deref(), Some("FFTest Freeze"));
	assert_eq!(name(&output, 2).as_deref(), Some("Regular"));
	assert_eq!(name(&output, 3).as_deref(), Some("FFTest Freeze Regular"));
	assert_eq!(name(&output, 4).as_deref(), Some("FFTest Freeze Regular"));
	assert_eq!(name(&output, 5).as_deref(), Some("Version 1.000"));
	assert_eq!(name(&output, 6).as_deref(), Some("FFTestFreeze-Regular"));
	assert_eq!(name(&output, 8).as_deref(), Some("FontFreeze v2.0.0"));
	assert_eq!(
		name(&output, 11).as_deref(),
		Some("https://mutsuntsai.github.io/fontfreeze")
	);
	assert_eq!(name(&output, 16).as_deref(), Some("FFTest Freeze"));
	assert_eq!(name(&output, 17).as_deref(), Some("Regular"));
	assert_eq!(name(&output, 18).as_deref(), Some("FFTest Freeze Regular"));
	// The other names, including the Mac ones, are removed.
	for (id, platform, ..) in names(&output).keys() {
		assert!(
			*id > 25 || *platform == 3,
			"name {id} of platform {platform} is kept"
		);
	}
	assert_eq!(name(&output, 0), None);
	assert_eq!(name(&output, 13), None);
}

#[test]
fn typographic_names() {
	let output = process(
		VAR,
		json!({ "options": { "subfamily": "Bold", "typo_family": "FFTest Typo", "typo_subfamily": "Medium" } }),
	);
	assert_eq!(name(&output, 2).as_deref(), Some("Bold"));
	assert_eq!(
		name(&output, 4).as_deref(),
		Some("FFTest Freeze Medium Bold")
	);
	assert_eq!(name(&output, 16).as_deref(), Some("FFTest Typo"));
	assert_eq!(name(&output, 17).as_deref(), Some("Medium"));

	// The same subfamilies are not repeated.
	let output = process(
		VAR,
		json!({ "options": { "subfamily": "Bold", "typo_subfamily": "Bold" } }),
	);
	assert_eq!(name(&output, 4).as_deref(), Some("FFTest Freeze Bold"));
}

#[test]
fn postscript_name_limit() {
	let family = "A Very Long Family Name That Goes On And On And On And On And On And On";
	let output = process(
		VAR,
		json!({ "options": { "family": family, "subfamily": "Bold Italic" } }),
	);
	let ps = name(&output, 6).unwrap();
	assert_eq!(ps.len(), 63);
	assert!(ps.starts_with("AVeryLongFamilyName"));
	assert!(!ps.contains(' '));
}

#[test]
fn style_bits() {
	let input = font(VAR);
	let original = {
		let font = font_ref(&input);
		(
			font.head().unwrap().mac_style().bits(),
			font.os2().unwrap().fs_selection().bits(),
		)
	};
	for (subfamily, expected) in [
		("Regular", (0, 0b100_0000)),
		("Bold", (1, 0b10_0000)),
		("Italic", (2, 0b1)),
		("Bold Italic", (3, 0b10_0001)),
		// Custom subfamilies leave the bits alone.
		("Medium", original),
	] {
		let output = process(VAR, json!({ "options": { "subfamily": subfamily } }));
		let font = font_ref(&output);
		let bits = (
			font.head().unwrap().mac_style().bits(),
			font.os2().unwrap().fs_selection().bits(),
		);
		assert_eq!(bits, expected, "{subfamily}");
	}
}

//////////////////////////////////////////////////////////////////////////////////////////
// Metrics
//////////////////////////////////////////////////////////////////////////////////////////

#[test]
fn letter_spacing() {
	let input = font(VAR);
	let output = process(VAR, json!({ "options": { "spacing": 50 } }));
	assert_eq!(width(&output, "a"), width(&input, "a") + 50);
	// The space is mapped from both U+0020 and U+00A0, so it is widened twice (as in the
	// original Python version).
	assert_eq!(width(&output, " "), width(&input, " ") + 100);
	// Glyphs not in cmap are not changed.
	assert_eq!(width(&output, "ff"), width(&input, "ff"));

	let font = font_ref(&output);
	let hmtx = font.hmtx().unwrap();
	let gid = glyph(&output, 'a') as usize;
	// Centered: the left side bearing grows by half.
	assert_eq!(hmtx.h_metrics()[gid].side_bearing(), 50 + 25);
	let max = hmtx.h_metrics().iter().map(|m| m.advance()).max().unwrap();
	assert_eq!(font.hhea().unwrap().advance_width_max().to_u16(), max);

	// Negative spacing does not go below zero.
	let output = process(VAR, json!({ "options": { "spacing": -1000 } }));
	assert_eq!(width(&output, "a"), 0);
	// Odd spacing is rounded as fontTools does.
	let output = process(VAR, json!({ "options": { "spacing": -33 } }));
	assert_eq!(width(&output, "a"), width(&input, "a") - 33);
}

#[test]
fn line_height() {
	// usWinAscent 1000 + usWinDescent 300, plus 100 distributed proportionally.
	let output = process(VAR, json!({ "options": { "lineHeight": 100 } }));
	let font = font_ref(&output);
	let os2 = font.os2().unwrap();
	assert_eq!((os2.us_win_ascent(), os2.us_win_descent()), (1077, 323));
	let hhea = font.hhea().unwrap();
	assert_eq!(
		(hhea.ascender().to_i16(), hhea.descender().to_i16()),
		(1077, -323)
	);

	let output = process(VAR, json!({ "options": { "lineHeight": -2000 } }));
	let os2 = font_ref(&output).os2().unwrap();
	assert_eq!((os2.us_win_ascent(), os2.us_win_descent()), (0, 0));

	let error = process_error(
		"FFTest-ZeroWin.otf",
		json!({ "variations": {}, "options": { "lineHeight": 10 } }),
	);
	assert_eq!(error, "division by zero");
}

#[test]
fn fix_contour() {
	let o = 11;
	let q = 12; // A composite glyph.
	let output = process(VAR, json!({ "options": { "keepVar": true } }));
	assert!(!has_overlap_flag(&output, o));
	assert!(!has_overlap_flag(&output, q));
	let output = process(
		VAR,
		json!({ "options": { "keepVar": true, "fixContour": true } }),
	);
	assert!(has_overlap_flag(&output, o));
	assert!(has_overlap_flag(&output, q));

	// Instantiating sets the flags anyway.
	let output = process(VAR, json!({}));
	assert!(has_overlap_flag(&output, o));

	// Nothing to fix for CFF fonts, which used to fail.
	let output = process(
		STATIC,
		json!({ "variations": {}, "options": { "fixContour": true } }),
	);
	assert!(has_table(&output, b"CFF "));
}

//////////////////////////////////////////////////////////////////////////////////////////
// Subsetting
//////////////////////////////////////////////////////////////////////////////////////////

#[test]
fn subset() {
	let input = font(VAR);
	let output = process(VAR, json!({ "unicodes": "U+61, U+6F, U+1F600" }));
	let chars: Vec<u32> = subtable(&output, 3, 10).map.keys().copied().collect();
	assert_eq!(chars, [0x61, 0x6F, 0x1F600]);
	assert!(font_ref(&output).maxp().unwrap().num_glyphs() < 10);
	// The kerning between a and o is kept.
	assert_eq!(
		shape(&output, "ao\u{1F600}", None, &[], &[]),
		shape(&input, "ao\u{1F600}", None, &[], &[])
	);
	assert_eq!(
		width(&output, "ao"),
		width(&input, "a") + width(&input, "o") - 30
	);

	// Glyphs reachable through the features are kept.
	let output = process(VAR, json!({ "unicodes": "U+61", "features": ["ss01"] }));
	assert_eq!(width(&output, "a"), 700);
	let output = process(
		VAR,
		json!({ "unicodes": "U+67", "features": ["cv01"], "options": { "singleSub": false } }),
	);
	assert_eq!(width(&output, "g"), 760);
}

#[test]
fn subset_static() {
	let input = font(STATIC);
	let output = process(STATIC, json!({ "variations": {}, "unicodes": "U+20-61" }));
	assert_eq!(width(&output, "a"), width(&input, "a"));
	assert!(
		font_ref(&output)
			.cmap()
			.unwrap()
			.map_codepoint('b')
			.is_none()
	);
}

//////////////////////////////////////////////////////////////////////////////////////////
// Output format
//////////////////////////////////////////////////////////////////////////////////////////

#[test]
fn woff2() {
	for name in [VAR, STATIC] {
		let reports = Rc::new(RefCell::new(Vec::new()));
		let progress = {
			let reports = reports.clone();
			fontfreeze::percent_progress(move |p| reports.borrow_mut().push(p))
		};
		let output = fontfreeze::process_font(
			font(name),
			&args(json!({ "variations": {}, "options": { "format": "woff2", "spacing": 10 } })),
			Some(progress),
		)
		.unwrap();
		assert_eq!(&output[..4], b"wOF2");

		let reports = reports.borrow();
		assert!(!reports.is_empty(), "{name}: no progress");
		assert!(reports.is_sorted(), "{name}: {reports:?}");
		assert!(reports.iter().all(|&p| p <= 99), "{name}: {reports:?}");

		// Decoded with fontoxide, as fontations cannot read WOFF2.
		let ttf = fontoxide_ttlib::Font::read(output, Default::default())
			.and_then(|mut f| {
				f.flavor = None;
				f.write(&Default::default())
			})
			.unwrap();
		let plain = process(
			name,
			json!({ "variations": {}, "options": { "spacing": 10 } }),
		);
		for text in TEXTS {
			assert_eq!(
				shape(&ttf, text, None, &[], &[]),
				shape(&plain, text, None, &[], &[])
			);
		}
	}
}

#[test]
fn ttf_output_of_cff_font() {
	// The format only decides the flavor; CFF outlines are kept.
	let output = process(STATIC, json!({ "variations": {} }));
	assert_eq!(&output[..4], b"OTTO");
	assert_eq!(width(&output, "abc"), width(&font(STATIC), "abc"));
}
