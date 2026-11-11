//! A native command line interface, for comparing the output with other implementations.
//!
//! ```text
//! fontfreeze-cli load <input> [<converted output>]   Prints the font info as JSON.
//! fontfreeze-cli legacy <input> <output>
//! fontfreeze-cli process <args.json> <input> <output>
//! ```

use std::process::ExitCode;

fn read(path: &str) -> std::io::Result<std::sync::Arc<[u8]>> {
	Ok(std::fs::read(path)?.into())
}

fn run(args: &[String]) -> Result<(), Box<dyn std::error::Error>> {
	match args {
		[cmd, input, rest @ ..] if cmd == "load" && rest.len() <= 1 => {
			let result = fontfreeze::load_font(read(input)?)?;
			println!("{}", serde_json::to_string_pretty(&result.info)?);
			if let (Some(output), Some(data)) = (rest.first(), result.data) {
				std::fs::write(output, data)?;
			}
		}
		[cmd, input, output] if cmd == "legacy" => {
			std::fs::write(output, fontfreeze::process_legacy(read(input)?)?)?;
		}
		[cmd, args, input, output] if cmd == "process" => {
			let args: fontfreeze::Args = serde_json::from_str(&std::fs::read_to_string(args)?)?;
			let start = std::time::Instant::now();
			let progress = fontfreeze::percent_progress(move |p| {
				eprintln!("{:>7.2}s {p:>3}%", start.elapsed().as_secs_f64());
			});
			let data = fontfreeze::process_font(read(input)?, &args, Some(progress))?;
			std::fs::write(output, data)?;
		}
		_ => return Err("usage: fontfreeze-cli (load <input> [<output>] | legacy <input> <output> | process <args.json> <input> <output>)".into()),
	}
	Ok(())
}

fn main() -> ExitCode {
	let args: Vec<String> = std::env::args().skip(1).collect();
	match run(&args) {
		Ok(()) => ExitCode::SUCCESS,
		Err(e) => {
			eprintln!("error: {e}");
			ExitCode::FAILURE
		}
	}
}
