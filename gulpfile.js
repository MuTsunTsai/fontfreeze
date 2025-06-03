import gulp from "gulp";
import exec from "gulp-exec";
import newer from "gulp-newer";
import purgecss from "gulp-purgecss";
import purgeHtml from "purgecss-from-html";
import { fileURLToPath } from "url";

const build = "build";
const srcHtml = "src/app/**/*.vue";

const __filename = fileURLToPath(import.meta.url);

export const css = () =>
	gulp.src("node_modules/bootstrap/dist/css/bootstrap.css")
		.pipe(newer({
			dest: build + "/bootstrap.css",
			extra: [__filename, srcHtml],
		}))
		.pipe(purgecss({
			content: [srcHtml],
			defaultExtractor: purgeHtml,
			safelist: {
				standard: [
					/show/, /modal-static/, /modal-backdrop/, // Bootstrap modal
					// extractor can't figure dynamic class
					"disabled",
					"drag",
				],
				variables: [
					/^--bs-btn-disabled/, // Fixes a bug of purgeCss
					/^--bs-gray-(\d)00/,
					/^--bs-(danger|info)$/,
				],
				greedy: [
					/tooltip/,
				],
			},
			variables: true, // for Bootstrap
		}))
		.pipe(gulp.dest(build));

export const python = () =>
	gulp.src("src/python/main.py")
		.pipe(newer(build))
		.pipe(exec(file => `pipenv run pyminify ${file.path} --rename-globals --preserve-globals loadFont,processFont,main,processLegacy`, { pipeStdout: true }))
		.pipe(gulp.dest(build));

export default gulp.parallel(css, python);
