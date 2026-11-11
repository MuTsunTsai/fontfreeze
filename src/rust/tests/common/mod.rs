//! Helpers shared by the integration tests.
//!
//! The test fonts are made by `test/generator/generate.py`; see the comments there for the
//! design of each font. The output is checked with fontations (read-fonts and harfrust)
//! rather than fontoxide, so that a bug in fontoxide cannot cancel itself out.
#![allow(dead_code)]

use std::collections::BTreeMap;
use std::path::Path;
use std::sync::Arc;

use fontfreeze::Args;
use harfrust::{Buffer, Feature, Language, ShapeOptions, ShaperFont, Tag};
use read_fonts::tables::cmap::CmapSubtable;
use read_fonts::tables::glyf::{CompositeGlyphFlags, Glyph};
use read_fonts::types::GlyphId;
use read_fonts::{FontRef, TableProvider};
use serde_json::{Value, json};

/// Reads a test font.
pub fn font(name: &str) -> Arc<[u8]> {
	let path = Path::new(env!("CARGO_MANIFEST_DIR"))
		.join("../../test/fonts")
		.join(name);
	std::fs::read(&path)
		.unwrap_or_else(|e| panic!("cannot read {}: {e}", path.display()))
		.into()
}

/// The arguments as sent by the UI for FFTest-Var.ttf with the default options (see
/// `createDefaultOption` in `loader.ts`), with `patch` merged in.
pub fn args(patch: Value) -> Args {
	let mut base = json!({
		"options": {
			"suffix": "Freeze",
			"family": "FFTest Freeze",
			"subfamily": "Regular",
			"typo_family": "FFTest Freeze",
			"typo_subfamily": "",
			"keepVar": false,
			"fixContour": false,
			"singleSub": true,
			"customNames": false,
			"lineHeight": 0,
			"spacing": 0,
			"target": "calt",
			"format": "ttf",
		},
		"version": " v2.0.0",
		"unicodes": "",
		"variations": { "wght": 400, "TEST": 0 },
		"features": [],
		"featureValues": {},
		"disables": [],
	});
	merge(&mut base, patch);
	serde_json::from_value(base).expect("invalid arguments")
}

fn merge(base: &mut Value, patch: Value) {
	match (base, patch) {
		(Value::Object(base), Value::Object(patch)) => {
			for (k, v) in patch {
				merge(base.entry(k).or_insert(Value::Null), v);
			}
		}
		(base, patch) => *base = patch,
	}
}

/// Generates a font from a test font.
pub fn process(name: &str, patch: Value) -> Vec<u8> {
	fontfreeze::process_font(font(name), &args(patch), None).expect("process_font failed")
}

/// Generates a font from a test font, expecting an error.
pub fn process_error(name: &str, patch: Value) -> String {
	match fontfreeze::process_font(font(name), &args(patch), None) {
		Ok(_) => panic!("process_font should fail"),
		Err(e) => e.0,
	}
}

//////////////////////////////////////////////////////////////////////////////////////////
// Shaping
//////////////////////////////////////////////////////////////////////////////////////////

/// The texts for checking the shaping. Each glyph of the test fonts has a distinct
/// advance width, so the advances tell which glyphs are used.
pub const TEXTS: &[&str] = &[
	"a g o. ff fi il ll ao 1 0",
	// Common script only, which is shaped with the DFLT script.
	"1 0 .",
	"\u{1F600}",
];

/// The languages to shape the texts in: the default language system, and TRK (Turkish).
pub const LANGUAGES: &[Option<&str>] = &[None, Some("tr")];

/// Shapes a text, returning the advance and the offset of each glyph.
pub fn shape(
	data: &[u8],
	text: &str,
	language: Option<&str>,
	features: &[(&str, u32)],
	variations: &[(&str, f32)],
) -> Vec<(i32, i32)> {
	let font = harfrust::Font::new(data.to_vec(), 0).expect("harfrust cannot read the font");
	let font = font
		.instance_builder()
		.variations(variations.iter().copied())
		.build();
	let shaper = ShaperFont::new(&font);
	let mut buffer = Buffer::new();
	buffer.push_str(text);
	buffer.guess_segment_properties();
	buffer.set_language(language.map(|l| Language::new(l).unwrap()));
	let features: Vec<Feature> = features
		.iter()
		.map(|(tag, value)| Feature::new(Tag::new_checked(tag.as_bytes()).unwrap(), *value, ..))
		.collect();
	harfrust::shape(
		&shaper,
		&mut buffer,
		ShapeOptions::new().features(&features),
	)
	.unwrap();
	buffer
		.glyph_positions()
		.iter()
		.map(|p| (p.x_advance, p.x_offset))
		.collect()
}

/// Checks that the frozen font, with its default features, shapes the texts as the
/// original font does with the given features and variations.
pub fn assert_frozen(
	input: &[u8],
	output: &[u8],
	features: &[(&str, u32)],
	variations: &[(&str, f32)],
) {
	for text in TEXTS {
		for &language in LANGUAGES {
			assert_eq!(
				shape(output, text, language, &[], &[]),
				shape(input, text, language, features, variations),
				"text {text:?}, language {language:?}"
			);
		}
	}
}

/// The total advance of a text shaped with the default features.
pub fn width(data: &[u8], text: &str) -> i32 {
	shape(data, text, None, &[], &[])
		.iter()
		.map(|(a, _)| a)
		.sum()
}

//////////////////////////////////////////////////////////////////////////////////////////
// Tables
//////////////////////////////////////////////////////////////////////////////////////////

pub fn font_ref(data: &[u8]) -> FontRef<'_> {
	FontRef::new(data).expect("read-fonts cannot read the font")
}

pub fn has_table(data: &[u8], tag: &[u8; 4]) -> bool {
	font_ref(data)
		.table_data(read_fonts::types::Tag::new(tag))
		.is_some()
}

/// The offsets of the tables in the table directory.
pub fn table_offsets(data: &[u8]) -> Vec<u32> {
	font_ref(data)
		.table_directory()
		.table_records()
		.iter()
		.map(|r| r.offset())
		.collect()
}

/// A name record: (name ID, platform ID, encoding ID, language ID) -> string.
pub fn names(data: &[u8]) -> BTreeMap<(u16, u16, u16, u16), String> {
	let font = font_ref(data);
	let table = font.name().unwrap();
	table
		.name_record()
		.iter()
		.map(|r| {
			let string = r
				.string(table.string_data())
				.map(|s| s.chars().collect())
				.unwrap_or_default();
			(
				(
					r.name_id().to_u16(),
					r.platform_id(),
					r.encoding_id(),
					r.language_id(),
				),
				string,
			)
		})
		.collect()
}

/// A Windows English name.
pub fn name(data: &[u8], id: u16) -> Option<String> {
	names(data).get(&(id, 3, 1, 0x409)).cloned()
}

pub struct Subtable {
	pub platform: u16,
	pub encoding: u16,
	pub format: u16,
	pub offset: u32,
	pub map: BTreeMap<u32, u32>,
}

pub fn cmap(data: &[u8]) -> Vec<Subtable> {
	let font = font_ref(data);
	let cmap = font.cmap().unwrap();
	cmap.encoding_records()
		.iter()
		.map(|r| {
			let subtable = r.subtable(cmap.offset_data()).unwrap();
			let format = match subtable {
				CmapSubtable::Format0(_) => 0,
				CmapSubtable::Format4(_) => 4,
				CmapSubtable::Format12(_) => 12,
				_ => panic!("unexpected cmap format"),
			};
			Subtable {
				platform: r.platform_id() as u16,
				encoding: r.encoding_id(),
				format,
				offset: r.subtable_offset().to_u32(),
				map: subtable
					.iter()
					.map(|(c, g)| (c, g.to_u32()))
					.filter(|&(_, g)| g != 0)
					.collect(),
			}
		})
		.collect()
}

pub fn subtable(data: &[u8], platform: u16, encoding: u16) -> Subtable {
	cmap(data)
		.into_iter()
		.find(|t| t.platform == platform && t.encoding == encoding)
		.unwrap_or_else(|| panic!("no ({platform}, {encoding}) subtable"))
}

/// A GSUB feature record: (tag, lookup indices, whether it has FeatureParams).
pub type FeatureInfo = (String, Vec<u16>, bool);

pub fn gsub_features(data: &[u8]) -> Vec<FeatureInfo> {
	let font = font_ref(data);
	let gsub = font.gsub().unwrap();
	let list = gsub.feature_list().unwrap();
	list.feature_records()
		.iter()
		.map(|r| {
			let feature = r.feature(list.offset_data()).unwrap();
			(
				r.feature_tag().to_string(),
				feature
					.lookup_list_indices()
					.iter()
					.map(|i| i.get())
					.collect(),
				!feature.feature_params_offset().is_null(),
			)
		})
		.collect()
}

/// The glyph ID that a character is mapped to by the best cmap.
pub fn glyph(data: &[u8], c: char) -> u32 {
	font_ref(data)
		.cmap()
		.unwrap()
		.map_codepoint(c)
		.unwrap_or_else(|| panic!("{c:?} is not mapped"))
		.to_u32()
}

/// Whether the OVERLAP_SIMPLE or OVERLAP_COMPOUND flag of a glyph is set.
pub fn has_overlap_flag(data: &[u8], gid: u32) -> bool {
	let font = font_ref(data);
	let loca = font.loca(None).unwrap();
	let glyf = font.glyf().unwrap();
	match loca.get_glyf(GlyphId::new(gid), &glyf).unwrap() {
		Some(Glyph::Simple(g)) => g.has_overlapping_contours(),
		Some(Glyph::Composite(g)) => g
			.components()
			.next()
			.is_some_and(|c| c.flags.contains(CompositeGlyphFlags::OVERLAP_COMPOUND)),
		None => false,
	}
}
