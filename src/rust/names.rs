//! The naming of the frozen font.

use fontoxide_ttlib::Font;
use fontoxide_ttlib::tables::{Head, Name, Os2};

use crate::{Args, Result};

const URL: &str = "https://mutsuntsai.github.io/fontfreeze";

/// The limit of a PostScript name.
const POSTSCRIPT_NAME_LIMIT: usize = 63;

fn postscript_name(family: &str, subfamily: &str) -> String {
	let result = format!("{}-{}", family.replace(' ', ""), subfamily.replace(' ', ""));
	result.chars().take(POSTSCRIPT_NAME_LIMIT).collect()
}

/// Replaces the name table with the names of the frozen font.
pub(crate) fn set_names(font: &mut Font, args: &Args, description: &str) -> Result<()> {
	let options = &args.options;
	let family = options.family.as_str();
	let subfamily = options.subfamily.as_str();
	let typo_family = if options.typo_family.is_empty() {
		family
	} else {
		options.typo_family.as_str()
	};

	let (typo_subfamily, full_name) =
		if options.typo_subfamily.is_empty() || options.typo_subfamily == subfamily {
			(subfamily, format!("{family} {subfamily}"))
		} else {
			let typo_subfamily = options.typo_subfamily.as_str();
			(
				typo_subfamily,
				format!("{family} {typo_subfamily} {subfamily}"),
			)
		};

	let table = font.require::<Name>()?;
	let old_names = std::mem::take(&mut table.names);

	// Setting the Mac platform seems to cause trouble in some fonts,
	// so we only set names for Windows (platform 3, Unicode BMP encoding, English).
	let mut set = |content: &str, id: u16| table.set_name(content, id, 3, 1, 1033);

	// See https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-ids
	set(family, 1);
	set(subfamily, 2);
	set(&full_name, 3);
	set(&full_name, 4);
	set("Version 1.000", 5);
	set(&postscript_name(family, subfamily), 6);
	set(&format!("FontFreeze{}", args.version), 8);
	set(description, 10);
	set(URL, 11);
	set(typo_family, 16);
	set(typo_subfamily, 17);
	set(&full_name, 18);

	for n in old_names {
		// Keep all names that have IDs > 25, as those are custom names.
		// This is necessary for "keep font variable" to work properly.
		if n.name_id > 25 {
			table.set_name(n.string, n.name_id, n.platform_id, n.plat_enc_id, n.lang_id);
		}
	}
	Ok(())
}

/// Sets the style bits of `head` and `OS/2` for the standard subfamilies.
pub(crate) fn set_style(font: &mut Font, subfamily: &str) -> Result<()> {
	let (mac_style, fs_selection) = match subfamily {
		"Regular" => (0, 0b100_0000),
		"Bold" => (1, 0b10_0000),
		"Italic" => (2, 0b1),
		"Bold Italic" => (3, 0b10_0001),
		_ => return Ok(()),
	};
	// As in the original Python version, a missing table is silently skipped,
	// but the bits that come before it are still set.
	let Some(head) = font.get::<Head>()? else {
		return Ok(());
	};
	head.mac_style = mac_style;
	if let Some(os2) = font.get::<Os2>()? {
		os2.fs_selection = fs_selection;
	}
	Ok(())
}
