//! Legacy CJK fonts, in particular those in Big5 encoding.

use fontoxide_encodings::codecs;
use fontoxide_ttlib::tables::name::NameString;
use fontoxide_ttlib::tables::otl::Mort;
use fontoxide_ttlib::tables::{Cmap, CmapSubtable, Name};
use fontoxide_ttlib::{Font, TableType, WriteOptions};

use crate::Result;

/// Python's `raw_unicode_escape` codec.
fn raw_unicode_escape(s: &str) -> Vec<u8> {
	let mut result = Vec::new();
	for c in s.chars() {
		let c = c as u32;
		if c < 0x100 {
			result.push(c as u8);
		} else if c < 0x10000 {
			result.extend(format!("\\u{c:04x}").bytes());
		} else {
			result.extend(format!("\\U{c:08x}").bytes());
		}
	}
	result
}

#[cfg(test)]
#[test]
fn raw_unicode_escape_as_python() {
	assert_eq!(raw_unicode_escape("a\u{e9}"), b"a\xe9");
	assert_eq!(raw_unicode_escape("\u{6c38}"), b"\\u6c38");
	assert_eq!(raw_unicode_escape("\u{1f600}"), b"\\U0001f600");
}

/// Legacy CJK fonts in Big5 encoding in particular might use mixed encoding. See
/// https://learn.microsoft.com/en-us/typography/opentype/spec/name#windows-encoding-ids
pub(crate) fn fix_name_encoding(font: &mut Font) -> Result<()> {
	let names = font.require::<Name>()?;
	for name in &mut names.names {
		if name.platform_id != 3 || name.plat_enc_id != 4 || name.to_unicode().is_ok() {
			continue;
		}
		let NameString::Bytes(bytes) = &name.string else {
			continue;
		};
		let temp = raw_unicode_escape(&codecs::decode("utf_16_be", bytes)?);
		if codecs::decode("big5", &temp).is_ok() {
			name.string = NameString::Bytes(temp);
		}
		// Otherwise we've tried our best.
	}
	Ok(())
}

/// Replaces a Big5 cmap with a Unicode one. Returns whether the font has a Big5 cmap.
pub(crate) fn convert_big5_cmap(font: &mut Font) -> Result<bool> {
	let cmap = font.require::<Cmap>()?;
	let Some(table) = cmap
		.tables
		.iter()
		.find(|t| t.platform_id == 3 && t.plat_enc_id == 4)
	else {
		return Ok(false);
	};
	let mut new_table = CmapSubtable::new(4);
	new_table.platform_id = 3; // Windows
	new_table.plat_enc_id = 1; // Unicode
	new_table.language = Some(0);
	let map = new_table.cmap_mut();
	for (&key, &gid) in table.cmap.iter() {
		if key <= 255 {
			map.insert(key, gid);
			continue;
		}
		let Ok(bytes) = u16::try_from(key).map(u16::to_be_bytes) else {
			continue;
		};
		let Ok(decoded) = codecs::decode("big5", &bytes) else {
			continue;
		};
		// Skip codes that are not a single character (e.g. two ASCII bytes).
		let mut chars = decoded.chars();
		if let (Some(c), None) = (chars.next(), chars.next()) {
			map.insert(c as u32, gid);
		}
	}
	cmap.tables = vec![new_table];
	Ok(true)
}

/// Legacy fonts will likely fail the OpenType Sanitizer (see https://github.com/khaledhosny/ots).
/// For such a font we try to fix it as much as possible, and return the fixed font.
pub(crate) fn fix_legacy(font: &mut Font) -> Result<Vec<u8>> {
	// It is known that the 金梅 series fonts, for example, have problems in their mort tables.
	// Here we check if the mort table makes sense; if not, just delete the table.
	if font.contains(Mort::TAG) && font.get::<Mort>().is_err() {
		font.remove(Mort::TAG);
	}

	// Simply re-saving the font should fix most table alignment issues.
	Ok(font.write(&WriteOptions {
		reorder_tables: None,
		..Default::default()
	})?)
}
