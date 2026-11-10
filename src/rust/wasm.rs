//! The entry points for the Web Worker (see `worker.ts`).

use serde::Serialize;
use wasm_bindgen::prelude::*;

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
#[wasm_bindgen(js_name = loadFont)]
pub fn load_font(data: &[u8]) -> Result<JsValue, JsError> {
	let result = crate::load_font(data).map_err(to_js_error)?;
	let serializer = serde_wasm_bindgen::Serializer::new().serialize_maps_as_objects(true);
	Ok(result.serialize(&serializer)?)
}

/// Tries to fix a font that the browser refuses to load.
#[wasm_bindgen(js_name = processLegacy)]
pub fn process_legacy(data: &[u8]) -> Result<Vec<u8>, JsError> {
	crate::process_legacy(data).map_err(to_js_error)
}

/// Generates the frozen font.
///
/// `on_progress` is called with the integral percentage of the compression done,
/// for WOFF 2.0 output only.
#[wasm_bindgen(js_name = processFont)]
pub fn process_font(
	data: &[u8],
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
	crate::process_font(data, &args, progress).map_err(to_js_error)
}
