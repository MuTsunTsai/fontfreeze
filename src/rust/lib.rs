//! FontFreeze: freezes the variations and the OpenType features of a font.
//!
//! This is the core of the web app, compiled to WebAssembly and run in a Web Worker
//! (see `wasm.rs`). The logic is independent of the target so that it can also be
//! run natively (see `cli.rs`).

mod activator;
mod legacy;
mod metrics;
mod names;
#[cfg(target_arch = "wasm32")]
mod wasm;

use std::collections::HashMap;
use std::fmt;

use fontoxide_ttlib::tables::cmap::DEFAULT_CMAP_PREFERENCES;
use fontoxide_ttlib::tables::{Fvar, Name, Os2};
use fontoxide_ttlib::{Flavor, Font, Progress, ReadOptions, TableType, Tag, WriteOptions};
use fontoxide_varlib::instancer::{AxisLimits, AxisTriple, InstancerOptions, OverlapMode};
use indexmap::IndexMap;
use serde::{Deserialize, Serialize};

/// An error, carrying the message shown to the user.
#[derive(Debug)]
pub struct Error(pub String);

impl fmt::Display for Error {
	fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
		f.write_str(&self.0)
	}
}

impl std::error::Error for Error {}

macro_rules! impl_from_error {
	($($ty:ty),*) => {
		$(impl From<$ty> for Error {
			fn from(e: $ty) -> Self {
				Error(e.to_string())
			}
		})*
	};
}

impl_from_error!(
	fontoxide_ttlib::Error,
	fontoxide_subset::Error,
	fontoxide_encodings::codecs::CodecError
);

impl From<&str> for Error {
	fn from(s: &str) -> Self {
		Error(s.to_owned())
	}
}

impl From<String> for Error {
	fn from(s: String) -> Self {
		Error(s)
	}
}

pub type Result<T> = std::result::Result<T, Error>;

//////////////////////////////////////////////////////////////////////////////////////////
// Arguments
//////////////////////////////////////////////////////////////////////////////////////////

/// The arguments of [`process_font`], as sent by the UI (see `generate.ts`).
#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Args {
	pub options: Options,
	/// The version of FontFreeze, e.g. `" v2.0.0"`.
	pub version: String,
	/// The characters to keep, in the format of `fontTools.subset.parse_unicodes`;
	/// empty to keep all.
	#[serde(default)]
	pub unicodes: String,
	/// The location to instantiate at, by axis tag. The order is kept for the description.
	#[serde(default)]
	pub variations: IndexMap<String, f64>,
	/// The features to activate.
	#[serde(default)]
	pub features: Vec<String>,
	/// The 1-based index of the alternate to keep, for features with a custom value.
	#[serde(default)]
	pub feature_values: HashMap<String, i64>,
	/// The features to deactivate.
	#[serde(default)]
	pub disables: Vec<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Options {
	pub family: String,
	pub subfamily: String,
	#[serde(default)]
	pub typo_family: String,
	#[serde(default)]
	pub typo_subfamily: String,
	#[serde(rename = "keepVar", default)]
	pub keep_var: bool,
	#[serde(rename = "fixContour", default)]
	pub fix_contour: bool,
	#[serde(rename = "singleSub", default)]
	pub single_sub: bool,
	/// Additional line height, in font units.
	#[serde(rename = "lineHeight", default)]
	pub line_height: Option<f64>,
	/// Additional letter spacing, in font units.
	#[serde(default)]
	pub spacing: Option<f64>,
	/// The feature that the activated features are merged into.
	#[serde(default)]
	pub target: String,
	/// `ttf` or `woff2`.
	#[serde(default)]
	pub format: String,
}

//////////////////////////////////////////////////////////////////////////////////////////
// Font info
//////////////////////////////////////////////////////////////////////////////////////////

/// The information of a font shown in the UI (`FontInfo` in `global.d.ts`).
#[derive(Debug, Clone, Serialize)]
pub struct FontInfo {
	pub family: Option<String>,
	pub subfamily: Option<String>,
	pub copyright: Option<String>,
	pub id: Option<String>,
	pub version: Option<String>,
	pub trademark: Option<String>,
	pub manufacturer: Option<String>,
	pub designer: Option<String>,
	pub description: Option<String>,
	#[serde(rename = "vendorURL")]
	pub vendor_url: Option<String>,
	#[serde(rename = "designerURL")]
	pub designer_url: Option<String>,
	pub license: Option<String>,
	#[serde(rename = "licenseURL")]
	pub license_url: Option<String>,
	pub typo_family: Option<String>,
	pub typo_subfamily: Option<String>,
	pub fvar: Option<FvarInfo>,
	/// The GSUB feature tags, without duplicates.
	pub gsub: Vec<String>,
	#[serde(rename = "fontHeight")]
	pub font_height: i32,
	#[serde(rename = "lineHeight")]
	pub line_height: i32,
	/// Whether this is a legacy CJK font that has been converted for previewing.
	pub preview: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct FvarInfo {
	pub axes: Vec<AxisInfo>,
	pub instances: Vec<InstanceInfo>,
}

#[derive(Debug, Clone, Serialize)]
pub struct AxisInfo {
	pub tag: String,
	pub default: f64,
	pub min: f64,
	pub max: f64,
	pub name: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct InstanceInfo {
	pub name: Option<String>,
	pub coordinates: IndexMap<String, f64>,
}

/// The result of [`load_font`].
#[derive(Debug, Clone, Serialize)]
pub struct LoadResult {
	pub info: FontInfo,
	/// The font to use from now on, if it has been converted (legacy CJK fonts);
	/// otherwise the original data should be used.
	#[serde(with = "serde_bytes")]
	pub data: Option<Vec<u8>>,
}

fn tag_string(tag: &[u8; 4]) -> String {
	Tag(*tag).as_string()
}

fn get_fvar(font: &mut Font) -> Result<Option<FvarInfo>> {
	if !font.contains(Fvar::TAG) {
		return Ok(None);
	}
	let fvar = font.require::<Fvar>()?.clone();
	let names = font.require::<Name>()?;
	Ok(Some(FvarInfo {
		axes: fvar
			.axes
			.iter()
			.map(|a| AxisInfo {
				tag: tag_string(&a.axis_tag),
				default: a.default_value,
				min: a.min_value,
				max: a.max_value,
				name: names.get_debug_name(a.axis_name_id),
			})
			.collect(),
		instances: fvar
			.instances
			.iter()
			.map(|i| {
				// Keep the order of the axes, as in fontTools.
				let coordinates = fvar
					.axes
					.iter()
					.filter_map(|a| {
						let tag = Tag(a.axis_tag);
						i.coordinates.get(&tag).map(|&v| (tag.as_string(), v))
					})
					.collect();
				InstanceInfo {
					name: names.get_debug_name(i.subfamily_name_id),
					coordinates,
				}
			})
			.collect(),
	}))
}

/// Reads a font as the rest of FontFreeze expects (`loadTtfFont`).
pub(crate) fn read_font(data: &[u8]) -> Result<Font> {
	let mut font = Font::read(
		data.to_vec(),
		ReadOptions {
			recalc_bboxes: false,
			font_number: Some(0), // in case it's a font collection
			..Default::default()
		},
	)?;
	legacy::fix_name_encoding(&mut font)?;
	Ok(font)
}

/// Reads a font and returns its information (`loadFont`).
pub fn load_font(data: &[u8]) -> Result<LoadResult> {
	let mut font = read_font(data)?;

	let os2 = font.require::<Os2>()?;
	let font_height = os2.s_typo_ascender as i32 - os2.s_typo_descender as i32;
	let line_height = os2.us_win_ascent as i32 + os2.us_win_descent as i32;

	// A font may contain a GSUB table whose FeatureList is None (an empty GSUB with no
	// features), so checking for GSUB alone is not enough.
	let mut gsub: Vec<String> = Vec::new();
	for tag in activator::feature_tags(&mut font)? {
		let tag = tag.as_string();
		if !gsub.contains(&tag) {
			gsub.push(tag);
		}
	}

	let fvar = get_fvar(&mut font)?;
	let names = font.require::<Name>()?;
	let name = |id| names.get_debug_name(id);
	let mut info = FontInfo {
		family: names.best_family_name(),
		subfamily: name(2),
		copyright: name(0),
		id: name(3),
		version: name(5),
		trademark: name(7),
		manufacturer: name(8),
		designer: name(9),
		description: name(10),
		vendor_url: name(11),
		designer_url: name(12),
		license: name(13),
		license_url: name(14),
		typo_family: name(16),
		typo_subfamily: name(17),
		fvar,
		gsub,
		font_height,
		line_height,
		preview: false,
	};

	let mut converted = None;
	if font.get_best_cmap(&DEFAULT_CMAP_PREFERENCES)?.is_none()
		&& legacy::convert_big5_cmap(&mut font)?
	{
		// Legacy CJK font detected.
		converted = Some(legacy::fix_legacy(&mut font)?);
		info.preview = true;
	}

	Ok(LoadResult {
		info,
		data: converted,
	})
}

/// Tries to fix a font that the browser refuses to load (`processLegacy`).
pub fn process_legacy(data: &[u8]) -> Result<Vec<u8>> {
	let mut font = read_font(data)?;
	legacy::fix_legacy(&mut font)
}

//////////////////////////////////////////////////////////////////////////////////////////
// Processing
//////////////////////////////////////////////////////////////////////////////////////////

/// Generates the frozen font (`processFont`).
///
/// `progress` is called with the fraction of the Brotli compression done, for WOFF 2.0
/// output only, as that takes most of the time for large fonts.
pub fn process_font(data: &[u8], args: &Args, progress: Option<Progress>) -> Result<Vec<u8>> {
	let mut font = read_font(data)?;
	instantiate(&mut font, args)?;
	activator::remove_features(&mut font, &args.disables)?;
	activator::activate(&mut font, args)?;
	subset(&mut font, &args.unicodes)?;

	let options = &args.options;
	let spacing = options.spacing.unwrap_or(0.0);
	if spacing != 0.0 {
		metrics::change_font_spacing(&mut font, spacing)?;
	}
	let line_height = options.line_height.unwrap_or(0.0);
	if line_height != 0.0 {
		metrics::change_line_height(&mut font, line_height)?;
	}

	if options.format == "woff2" {
		font.flavor = Some(Flavor::Woff2);
	}

	Ok(font.write(&WriteOptions {
		woff2_progress: progress,
		..Default::default()
	})?)
}

/// Wraps `report` as a [`Progress`] that is called only when the integral percentage
/// changes, as fontoxide reports the progress thousands of times for a large font.
///
/// The percentage stops at 99: fontoxide reports the fraction of the data read by Brotli,
/// which reaches 1.0 while the encoder is still working on the last block (seconds on
/// wasm for a large font), so the completion is signaled by the result instead.
pub fn percent_progress(report: impl Fn(u32) + 'static) -> Progress {
	let last = std::cell::Cell::new(None);
	std::rc::Rc::new(move |fraction: f64| {
		let percent = ((fraction.clamp(0.0, 1.0) * 100.0).floor() as u32).min(99);
		if last.replace(Some(percent)) != Some(percent) {
			report(percent);
		}
	})
}

/// Formats a number as Python does for an int or a float converted from JavaScript.
fn format_number(v: f64) -> String {
	if v.fract() == 0.0 && v.abs() < 1e16 {
		format!("{}", v as i64)
	} else {
		format!("{v}")
	}
}

fn axis_name(font: &mut Font, tag: &str) -> Result<String> {
	let axes = font.require::<Fvar>()?.axes.clone();
	let names = font.require::<Name>()?;
	for a in axes {
		if tag_string(&a.axis_tag) == tag {
			return Ok(names
				.get_debug_name(a.axis_name_id)
				.unwrap_or_else(|| "None".into()));
		}
	}
	Ok(tag.to_owned())
}

/// Instantiates the font and sets up its names (`Instantiate`).
fn instantiate(font: &mut Font, args: &Args) -> Result<()> {
	let options = &args.options;
	let name_table = font.require::<Name>()?;
	let family = name_table
		.best_family_name()
		.unwrap_or_else(|| "None".into());
	let version = name_table
		.get_debug_name(5)
		.unwrap_or_else(|| "None".into());

	let mut description = format!("Frozen from {family} {version}.");
	let keep_var = options.keep_var;
	if font.contains(Fvar::TAG) && !keep_var {
		let mut settings = Vec::new();
		for (k, &v) in &args.variations {
			settings.push(format!("{}={}", axis_name(font, k)?, format_number(v)));
		}
		description += &format!(" Sets {}.", settings.join(", "));
		let limits: AxisLimits = args
			.variations
			.iter()
			.map(|(k, &v)| (k.clone(), Some(AxisTriple::pin(v))))
			.collect();
		fontoxide_varlib::instancer::instantiate_variable_font(
			font,
			&limits,
			&InstancerOptions {
				overlap: OverlapMode::KeepAndSetFlags,
				..Default::default()
			},
		)?;
	}
	if !args.features.is_empty() {
		description += &format!(" Activates {}.", args.features.join(", "));
	}
	if !args.disables.is_empty() {
		description += &format!(" Deactivates {}.", args.disables.join(", "));
	}

	names::set_names(font, args, &description)?;
	names::set_style(font, &options.subfamily)?;

	if !keep_var {
		for tag in [b"STAT", b"cvar", b"fvar", b"gvar"] {
			font.remove(Tag::new(tag));
		}
	}
	if options.fix_contour {
		fontoxide_varlib::instancer::set_mac_overlap_flags(font)?;
	}
	Ok(())
}

fn subset(font: &mut Font, unicodes: &str) -> Result<()> {
	if unicodes.is_empty() {
		return Ok(());
	}
	let mut options = fontoxide_subset::Options::default();
	options.parse_opts(
		&[
			"--layout-scripts=*",
			"--layout-features=*",
			"--name-IDs=*",
			"--name-languages=*",
		],
		&[],
	)?;
	let mut subsetter = fontoxide_subset::Subsetter::new(options);
	subsetter.populate(&[], &[], &fontoxide_subset::parse_unicodes(unicodes)?, "");
	subsetter.subset(font)?;
	Ok(())
}
