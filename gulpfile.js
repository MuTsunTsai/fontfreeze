const exec = require("gulp-exec");
const gulp = require("gulp");
const newer = require("gulp-newer");
const purgecss = require("gulp-purgecss");
const purgeHtml = require("purgecss-from-html");

const build = "build";
const srcHtml = "src/public/index.html";

gulp.task("css", () =>
	gulp.src("node_modules/bootstrap/dist/css/bootstrap.css")
		.pipe(newer({
			dest: build + "/bootstrap.css",
			extra: [__filename, srcHtml]
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
					/^--bs-gray-(8|6)00/,
					/^--bs-(danger|info)$/,
				],
			},
			variables: true, // for Bootstrap
		}))
		.pipe(gulp.dest(build))
);

gulp.task("python", () =>
	gulp.src("src/python/main.py")
		.pipe(newer(build))
		.pipe(exec(file => `pipenv run pyminify ${file.path} --rename-globals --preserve-globals loadFont,processFont,main,processLegacy`, { pipeStdout: true }))
		.pipe(gulp.dest(build))
);

gulp.task("default", gulp.parallel("css", "python"));
