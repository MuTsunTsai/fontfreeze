//! Letter spacing and line height.

use std::collections::BTreeMap;

use fontoxide_ttlib::Font;
use fontoxide_ttlib::tables::cmap::DEFAULT_CMAP_PREFERENCES;
use fontoxide_ttlib::tables::{Hhea, Hmtx, Os2};

use crate::{Error, Result};

/// fontTools' `otRound`, which rounds half up.
fn ot_round(v: f64) -> f64 {
	(v + 0.5).floor()
}

#[cfg(test)]
#[test]
fn ot_round_rounds_half_up() {
	assert_eq!(ot_round(0.5), 1.0);
	assert_eq!(ot_round(-0.5), 0.0);
	assert_eq!(ot_round(-1.5), -1.0);
	assert_eq!(ot_round(2.4), 2.0);
	assert_eq!(
		to_int::<u16>(-1.0, "x").unwrap_err().0,
		"x out of range: -1"
	);
}

fn to_int<T: TryFrom<i64>>(v: f64, name: &str) -> Result<T> {
	T::try_from(ot_round(v) as i64).map_err(|_| Error(format!("{name} out of range: {v}")))
}

/// Adds `delta` to the advance width of each glyph in the cmap, keeping the glyph centered.
pub(crate) fn change_font_spacing(font: &mut Font, delta: f64) -> Result<()> {
	let cmap = font
		.get_best_cmap(&DEFAULT_CMAP_PREFERENCES)?
		.ok_or("The font has no Unicode cmap")?;
	let hmtx = font.require::<Hmtx>()?;

	// Metrics are kept unrounded until the end, as fontTools rounds them only when compiling.
	let mut metrics: BTreeMap<u32, (f64, f64)> = BTreeMap::new();
	// Note that a glyph mapped from several code points is adjusted once for each of them,
	// as the original Python version does.
	for &gid in cmap.values() {
		let (width, lsb) = match metrics.get(&gid) {
			Some(&m) => m,
			None => {
				let (w, l) = hmtx
					.get(gid)
					.ok_or_else(|| Error(format!("Glyph {gid} has no horizontal metrics")))?;
				(w as f64, l as f64)
			}
		};
		let width = (width + delta).max(0.0);
		let lsb = (lsb + delta / 2.0).clamp(-32768.0, 32767.0);
		metrics.insert(gid, (width, lsb));
	}
	for (gid, (width, lsb)) in metrics {
		hmtx.set(
			gid,
			(
				to_int(width, "advance width")?,
				to_int(lsb, "left side bearing")?,
			),
		);
	}

	// Over all glyphs, including those not in cmap (the original Python version missed them).
	let max_width = hmtx
		.metrics
		.values()
		.map(|&(width, _)| width)
		.max()
		.unwrap_or(0);
	font.require::<Hhea>()?.advance_width_max = max_width;
	Ok(())
}

/// Adds `delta` to the line height, distributed proportionally to the ascent and descent.
pub(crate) fn change_line_height(font: &mut Font, delta: f64) -> Result<()> {
	let os2 = font.require::<Os2>()?;
	let ascent = os2.us_win_ascent as f64;
	let descent = os2.us_win_descent as f64;
	let total = ascent + descent;
	if total == 0.0 {
		return Err("division by zero".into());
	}
	let new_total = total + delta;
	let ascent = (ascent * new_total / total).ceil().max(0.0);
	let descent = (descent * new_total / total).floor().max(0.0);

	os2.us_win_ascent = to_int(ascent, "usWinAscent")?;
	os2.us_win_descent = to_int(descent, "usWinDescent")?;
	let hhea = font.require::<Hhea>()?;
	hhea.ascent = to_int(ascent, "ascent")?;
	hhea.descent = to_int(-descent, "descent")?;
	Ok(())
}
