//! The entry points for the Web Worker (see `worker.ts`).
//!
//! The font being worked on is kept here rather than in JavaScript, so that generating
//! the font again and again does not copy it into the wasm memory each time, which grows
//! the memory for good.

use std::cell::RefCell;
use std::sync::Arc;

use serde::Serialize;
use wasm_bindgen::prelude::*;

thread_local! {
	/// The font being worked on, set by [`load_font`] and [`process_legacy`].
	static INPUT: RefCell<Option<Arc<[u8]>>> = const { RefCell::new(None) };
}

fn input() -> Result<Arc<[u8]>, JsError> {
	INPUT
		.with_borrow(Option::clone)
		.ok_or_else(|| JsError::new("No font is loaded"))
}

fn set_input(data: Arc<[u8]>) {
	INPUT.set(Some(data));
}

fn to_js_error(e: crate::Error) -> JsError {
	JsError::new(&e.0)
}

/// Runs when the module is initialized.
#[wasm_bindgen(start)]
fn start() {
	// There is no system clock on wasm32-unknown-unknown; it is needed for head.modified.
	fontoxide_ttlib::set_clock(|| js_sys::Date::now() / 1000.0);
}

/// Reads a font and returns `{ info, data }`; see [`crate::LoadResult`].
///
/// If successful, the font (or the converted one, if any) becomes the font being worked on.
#[wasm_bindgen(js_name = loadFont)]
pub fn load_font(data: &[u8]) -> Result<JsValue, JsError> {
	let data: Arc<[u8]> = data.into();
	let result = crate::load_font(data.clone()).map_err(to_js_error)?;
	// Only replace the input once the font is known to be valid.
	set_input(match &result.data {
		Some(converted) => converted.as_slice().into(),
		None => data,
	});
	let serializer = serde_wasm_bindgen::Serializer::new().serialize_maps_as_objects(true);
	Ok(result.serialize(&serializer)?)
}

/// Tries to fix the font being worked on, which the browser refuses to load,
/// and returns the fixed font.
#[wasm_bindgen(js_name = processLegacy)]
pub fn process_legacy() -> Result<Vec<u8>, JsError> {
	let fixed = crate::process_legacy(input()?).map_err(to_js_error)?;
	set_input(fixed.as_slice().into());
	Ok(fixed)
}

/// Generates the frozen font from the font being worked on.
///
/// `on_progress` is called with the integral percentage of the compression done,
/// for WOFF 2.0 output only.
#[wasm_bindgen(js_name = processFont)]
pub fn process_font(
	args: JsValue,
	on_progress: Option<js_sys::Function>,
) -> Result<Vec<u8>, JsError> {
	let args: crate::Args = serde_wasm_bindgen::from_value(args)?;
	let progress = on_progress.map(|f| {
		crate::percent_progress(move |p| {
			// The progress is only informative, so errors from the callback are ignored.
			let _ = f.call1(&JsValue::NULL, &JsValue::from(p));
		})
	});
	crate::process_font(input()?, &args, progress).map_err(to_js_error)
}
