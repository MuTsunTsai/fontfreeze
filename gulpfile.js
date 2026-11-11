import { spawnSync } from "child_process";
import { existsSync, readFileSync, statSync, writeFileSync } from "fs";
import gulp from "gulp";
import newer from "gulp-newer";
import purgecss from "gulp-purgecss";
import purgeHtml from "purgecss-from-html";
import { fileURLToPath } from "url";

const build = "build";
const srcVue = "src/app/**/*.vue";
const srcHtml = "src/public/index.html";

const __filename = fileURLToPath(import.meta.url);

// This is a very native extractor for Vuetify
function vuetifyExtract(content, attr, prefix = attr) {
	return (content.match(new RegExp(`(?<=${attr}=")[^"]+(?=")`, "g")) ?? []).map(s => prefix + "-" + s);
}

export const css = () =>
	gulp.src("node_modules/vuetify/dist/vuetify.css")
		.pipe(newer({
			dest: build + "/vuetify.css",
			extra: [__filename, srcVue, srcHtml],
		}))
		.pipe(purgecss({
			content: [srcVue, srcHtml],
			defaultExtractor: content => {
				const result = purgeHtml(content);
				result.classes.push(
					...vuetifyExtract(content, "justify"),
					...vuetifyExtract(content, "align"),
					...vuetifyExtract(content, "elevation"),
					...vuetifyExtract(content, "color", "bg")
				);
				return result;
			},
			safelist: {
				standard: [
					/text-none/,
					/d-sm-table-cell/,
				],
			},
			variables: false,
		}))
		.pipe(gulp.dest(build));

function run(command, args, cwd) {
	console.log("> " + [command, ...args].join(" "));
	const result = spawnSync(command, args, { cwd, stdio: "inherit" });
	if(result.status !== 0) throw new Error(`${command} failed with exit code ${result.status ?? result.error}`);
}

/**
 * Builds the Rust crate into build/wasm.
 * Cargo builds incrementally,
 * and the rest is skipped if the module is unchanged.
 * @param {boolean} optimize Whether to run wasm-opt, which takes minutes.
 */
function buildWasm(optimize) {
	const crate = "src/rust";
	const out = build + "/wasm";
	const target = "wasm32-unknown-unknown";
	run("cargo", ["build", "--release", "--target", target], crate);

	const wasmFile = `${crate}/target/${target}/release/fontfreeze.wasm`;
	const stamp = out + "/.source";
	const source = statSync(wasmFile).mtimeMs + (optimize ? " optimized" : "");
	if(existsSync(stamp) && readFileSync(stamp, "utf8") == source) return;

	// The default module path is omitted,
	// as the worker fetches the module itself to report the progress.
	run("wasm-bindgen", [wasmFile, "--out-dir", out, "--target", "web", "--omit-default-module-path"]);
	if(optimize) {
		// The features enabled by default on the target,
		// which wasm-opt must be told about.
		const features = ["bulk-memory", "nontrapping-float-to-int", "sign-ext", "multivalue", "reference-types", "mutable-globals"];
		const bg = out + "/fontfreeze_bg.wasm";
		run(process.execPath, ["node_modules/binaryen/bin/wasm-opt", bg, "-Oz", "-o", bg, ...features.map(f => "--enable-" + f)]);
	}
	writeFileSync(stamp, source);
}

export const wasm = done => {
	buildWasm(false);
	done();
};

export const wasmRelease = done => {
	buildWasm(true);
	done();
};

export const release = gulp.parallel(css, wasmRelease);

export default gulp.parallel(css, wasm);
