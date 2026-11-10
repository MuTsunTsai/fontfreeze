//! The entry points for the Web Worker (see `worker.ts`).

use serde::Serialize;
use wasm_bindgen::prelude::*;

fn to_js_error(e: crate::Error) -> JsError {
	JsError::new(&e.0)
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
#[wasm_bindgen(js_name = processFont)]
pub fn process_font(data: &[u8], args: JsValue) -> Result<Vec<u8>, JsError> {
	let args: crate::Args = serde_wasm_bindgen::from_value(args)?;
	crate::process_font(data, &args).map_err(to_js_error)
}
