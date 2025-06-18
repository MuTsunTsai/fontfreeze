import gulp from "gulp";
import exec from "gulp-exec";
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

export const python = () =>
	gulp.src("src/python/main.py")
		.pipe(newer(build))
		.pipe(exec(file => `pipenv run pyminify ${file.path} --rename-globals --preserve-globals loadFont,processFont,main,processLegacy`, { pipeStdout: true }))
		.pipe(gulp.dest(build));

export default gulp.parallel(css, python);
