//! Activating and deactivating GSUB features.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::sync::Arc;

use fontoxide_ttlib::ot::table::OtTable;
use fontoxide_ttlib::ot::types::{
	ExtensionSubst, Feature, FeatureParamsAny, FeatureRecord, LangSys, Lookup, LookupSubTable,
};
use fontoxide_ttlib::tables::{Cmap, Gsub};
use fontoxide_ttlib::{Font, TableType, Tag};

use crate::{Args, Error, Result};

/// The tag that a removed feature is renamed to, so that apps won't list it.
const DELETED: Tag = Tag::new(b"DELT");

/// The tags of the GSUB features, in order.
pub(crate) fn feature_tags(font: &mut Font) -> Result<Vec<Tag>> {
	let Some(gsub) = font.get::<Gsub>()? else {
		return Ok(Vec::new());
	};
	Ok(match &gsub.table.feature_list {
		Some(list) => list.feature_record.iter().map(|r| r.feature_tag).collect(),
		None => Vec::new(),
	})
}

fn has_tag(tags: &[String], tag: Tag) -> bool {
	let tag = tag.as_string();
	tags.contains(&tag)
}

/// Renames a feature record.
///
/// The type of the FeatureParams is decided by the feature tag, so the parameters are
/// dropped if they don't fit the new tag. The original Python version instead altered the
/// global type table of fontTools so that a feature renamed to the target keeps its
/// stylistic set or character variant parameters; for features renamed to `DELT` it fell
/// back to keeping the original tags of all removed features.
fn rename_feature(record: &mut FeatureRecord, tag: Tag) {
	record.feature_tag = tag;
	if let Some(feature) = &mut record.feature
		&& feature
			.feature_params
			.as_ref()
			.is_some_and(|p| p.class_name() != FeatureParamsAny::class_for(Some(tag)))
	{
		feature.feature_params = None;
	}
}

fn clear_feature_record(record: &mut FeatureRecord) {
	if let Some(feature) = &mut record.feature {
		feature.lookup_list_index.clear();
	}
	rename_feature(record, DELETED);
}

/// Deactivates features (`removeFeature`).
pub(crate) fn remove_features(font: &mut Font, features: &[String]) -> Result<()> {
	if features.is_empty() {
		return Ok(());
	}
	let Some(gsub) = font.get::<Gsub>()? else {
		return Ok(());
	};
	if let Some(list) = &mut gsub.table.feature_list {
		// We cannot just remove the record, as this would mess up the scripts.
		for record in &mut list.feature_record {
			if has_tag(features, record.feature_tag) {
				clear_feature_record(record);
			}
		}
	}
	Ok(())
}

/// The sub-tables of a lookup, unwrapping Extension Substitution (LookupType 7).
///
/// Many fonts (e.g. Iosevka) wrap their real sub-tables inside Extension lookups to work
/// around the 16-bit offset limit of GSUB.
fn effective_subtables(lookup: &Lookup) -> impl Iterator<Item = &LookupSubTable> {
	lookup
		.sub_table
		.iter()
		.flatten()
		.filter_map(|sub| match &**sub {
			LookupSubTable::ExtensionSubst(ExtensionSubst::Format1(ext)) => {
				ext.ext_sub_table.as_deref()
			}
			LookupSubTable::ExtensionSubst(_) => None,
			other => Some(other),
		})
}

fn effective_subtables_mut(lookup: &mut Lookup) -> impl Iterator<Item = &mut LookupSubTable> {
	lookup
		.sub_table
		.iter_mut()
		.flatten()
		.filter_map(|sub| match &mut **sub {
			LookupSubTable::ExtensionSubst(ExtensionSubst::Format1(ext)) => {
				ext.ext_sub_table.as_deref_mut()
			}
			LookupSubTable::ExtensionSubst(_) => None,
			other => Some(other),
		})
}

fn lang_systems(script_list: &fontoxide_ttlib::ot::types::ScriptList) -> Vec<&LangSys> {
	let mut result = Vec::new();
	for record in &script_list.script_record {
		let Some(script) = &record.script else {
			continue;
		};
		if let Some(default) = &script.default_lang_sys {
			result.push(&**default);
		}
		for record in &script.lang_sys_record {
			if let Some(lang_sys) = &record.lang_sys {
				result.push(&**lang_sys);
			}
		}
	}
	result
}

fn record_at(records: &[FeatureRecord], index: u16) -> Result<&FeatureRecord> {
	records
		.get(index as usize)
		.ok_or_else(|| Error(format!("Feature index {index} out of range")))
}

fn feature_mut(records: &mut [FeatureRecord], index: usize) -> Result<&mut Feature> {
	records
		.get_mut(index)
		.and_then(|r| r.feature.as_deref_mut())
		.ok_or_else(|| Error(format!("Feature {index} is missing")))
}

fn lookup_at(lookups: &mut [Option<Box<Lookup>>], index: u16) -> Result<Option<&mut Lookup>> {
	lookups
		.get_mut(index as usize)
		.map(|l| l.as_deref_mut())
		.ok_or_else(|| Error(format!("Lookup index {index} out of range")))
}

/// Activates features by merging them into the target feature (`Activator`).
pub(crate) fn activate(font: &mut Font, args: &Args) -> Result<()> {
	let features = &args.features;
	if features.is_empty() || !font.contains(Gsub::TAG) {
		return Ok(());
	}
	let target = Tag::from_str_exact(&args.options.target)
		.ok_or_else(|| Error(format!("Invalid target feature: {}", args.options.target)))?;

	// Guard against an empty GSUB whose sub-tables are None.
	{
		let gsub = &font.require::<Gsub>()?.table;
		if gsub.feature_list.is_none() || gsub.script_list.is_none() || gsub.lookup_list.is_none() {
			return Ok(());
		}
	}

	let cmap_glyphs: BTreeSet<u32> = font
		.require::<Cmap>()?
		.tables
		.iter()
		.flat_map(|t| t.cmap.values().copied())
		.collect();

	let gsub = &mut font.require::<Gsub>()?.table;
	let (Some(script_list), Some(feature_list), Some(lookup_list)) = (
		&gsub.script_list,
		&mut gsub.feature_list,
		&mut gsub.lookup_list,
	) else {
		return Ok(());
	};
	let records = &mut feature_list.feature_record;
	let lookups = &mut lookup_list.lookup;
	let lang_systems = lang_systems(script_list);

	let mut selected = BTreeSet::new();
	for lang_sys in &lang_systems {
		for &index in &lang_sys.feature_index {
			if has_tag(features, record_at(records, index)?.feature_tag) {
				selected.insert(index);
			}
		}
	}

	// For features with a custom value (e.g. cv01=2), shrink each AlternateSet to keep only
	// the chosen entry. After this, the lookup behaves like a Single Substitution regardless
	// of the value passed by the renderer, effectively freezing the variant.
	for &index in &selected {
		let record = record_at(records, index)?;
		if let Some(&value) = args.feature_values.get(&record.feature_tag.as_string())
			&& let Some(feature) = &record.feature
		{
			pick_alternate(lookups, &feature.lookup_list_index, value)?;
		}
	}

	// cmap is shared by all scripts, so the substitution is applied only once.
	let mut substitutions = BTreeMap::new();
	if args.options.single_sub {
		let mut lookup_indices = BTreeSet::new();
		for &index in &selected {
			if let Some(feature) = &record_at(records, index)?.feature {
				lookup_indices.extend(feature.lookup_list_index.iter().copied());
			}
		}
		substitutions = single_substitutions(lookups, &lookup_indices, &cmap_glyphs)?;
		update_ligatures(lookups, &substitutions);
	}

	for lang_sys in &lang_systems {
		activate_in_lang_sys(records, lang_sys, features, target)?;
	}

	if !substitutions.is_empty() {
		apply_to_cmap(font.require::<Cmap>()?, &substitutions);
	}
	Ok(())
}

fn activate_in_lang_sys(
	records: &mut [FeatureRecord],
	lang_sys: &LangSys,
	features: &[String],
	target: Tag,
) -> Result<()> {
	// Try to find an existing target feature.
	let mut target_index = None;
	for &index in &lang_sys.feature_index {
		if record_at(records, index)?.feature_tag == target {
			target_index = Some(index as usize);
		}
	}

	for &index in &lang_sys.feature_index {
		if !has_tag(features, record_at(records, index)?.feature_tag) {
			continue;
		}
		let index = index as usize;
		match target_index {
			None => {
				// If there's no existing one, use the first matching feature as the target.
				target_index = Some(index);
				rename_feature(&mut records[index], target);
			}
			Some(t) => {
				let moved = feature_mut(records, index)?.lookup_list_index.clone();
				feature_mut(records, t)?.lookup_list_index.extend(moved);
				clear_feature_record(&mut records[index]);
			}
		}
	}

	if let Some(t) = target_index {
		feature_mut(records, t)?.lookup_list_index.sort();
	}
	Ok(())
}

/// Reduces the AlternateSets (GSUB Type 3) to the chosen alternate.
///
/// For cv01-cv99 and ss01-ss20, the feature value is a 1-based index into the
/// AlternateSet. After the reduction the lookup always picks the same glyph.
fn pick_alternate(lookups: &mut [Option<Box<Lookup>>], indices: &[u16], value: i64) -> Result<()> {
	for &index in indices {
		let Some(lookup) = lookup_at(lookups, index)? else {
			continue;
		};
		for sub in effective_subtables_mut(lookup) {
			let LookupSubTable::AlternateSubst(sub) = sub else {
				continue;
			};
			for alternates in sub.alternates.values_mut() {
				// If the value is out of range, leave the AlternateSet untouched.
				if value >= 1 && value as usize <= alternates.len() {
					*alternates = vec![alternates[value as usize - 1]];
				}
			}
		}
	}
	Ok(())
}

/// Computes the substitution of each glyph in cmap by the given lookups, applied one by
/// one as a shaper does, so that chained substitutions compose (e.g. "case" one -> one.cap,
/// then "ss07" one.cap -> one.c).
fn single_substitutions(
	lookups: &mut [Option<Box<Lookup>>],
	indices: &BTreeSet<u16>,
	glyphs: &BTreeSet<u32>,
) -> Result<BTreeMap<u32, u32>> {
	let mut current: BTreeMap<u32, u32> = glyphs.iter().map(|&g| (g, g)).collect();
	for &index in indices {
		let Some(lookup) = lookup_at(lookups, index)? else {
			continue;
		};
		let mut mapping: HashMap<u32, u32> = HashMap::new();
		for sub in effective_subtables(lookup) {
			// The first sub-table covering a glyph wins.
			match sub {
				LookupSubTable::SingleSubst(sub) => {
					for (&k, &v) in &sub.mapping {
						mapping.entry(k).or_insert(v);
					}
				}
				// Alternate substitution reduced to a single choice.
				LookupSubTable::AlternateSubst(sub) => {
					for (&k, alternates) in &sub.alternates {
						if let [v] = alternates[..] {
							mapping.entry(k).or_insert(v);
						}
					}
				}
				_ => {}
			}
		}
		for value in current.values_mut() {
			if let Some(&v) = mapping.get(value) {
				*value = v;
			}
		}
	}
	Ok(current.into_iter().filter(|(g, v)| g != v).collect())
}

/// Applies the substitutions to cmap.
fn apply_to_cmap(cmap: &mut Cmap, substitutions: &BTreeMap<u32, u32>) {
	// Sub-tables may share the same mapping (e.g. (0, 3) and (3, 1)), so process each
	// mapping once and keep it shared. As in the original Python version, the format of the
	// last sub-table sharing a mapping decides.
	let mut groups: Vec<(Arc<_>, u16, Vec<usize>)> = Vec::new();
	for (i, table) in cmap.tables.iter().enumerate() {
		match groups
			.iter_mut()
			.find(|(m, ..)| Arc::ptr_eq(m, &table.cmap))
		{
			Some((_, format, members)) => {
				*format = table.format;
				members.push(i);
			}
			None => groups.push((table.cmap.clone(), table.format, vec![i])),
		}
	}
	for (map, format, members) in groups {
		let mut new_map = (*map).clone();
		let mut changed = false;
		for glyph in new_map.values_mut() {
			// Format 0 (legacy Mac) can only address glyph IDs below 256.
			if let Some(&value) = substitutions.get(glyph)
				&& (format != 0 || value < 256)
			{
				*glyph = value;
				changed = true;
			}
		}
		if changed {
			let new_map = Arc::new(new_map);
			for i in members {
				cmap.tables[i].cmap = new_map.clone();
			}
		}
	}
}

/// Updates the substituted glyphs in all ligature substitutions.
fn update_ligatures(lookups: &mut [Option<Box<Lookup>>], substitutions: &BTreeMap<u32, u32>) {
	let sub = |g: u32| substitutions.get(&g).copied().unwrap_or(g);
	for lookup in lookups.iter_mut().flatten() {
		for table in effective_subtables_mut(lookup) {
			let LookupSubTable::LigatureSubst(table) = table else {
				continue;
			};
			let mut ligatures: BTreeMap<u32, Vec<_>> = BTreeMap::new();
			for (first, mut set) in std::mem::take(&mut table.ligatures) {
				for lig in &mut set {
					for c in &mut lig.component {
						*c = sub(*c);
					}
				}
				ligatures.entry(sub(first)).or_default().extend(set);
			}
			table.ligatures = ligatures;
		}
	}
}
