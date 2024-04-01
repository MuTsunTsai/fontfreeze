const $ = require('gulp-load-plugins')();
const gulp = require('gulp');
const ordered = require('ordered-read-streams');
const purgeHtml = require('purgecss-from-html');

const dest = 'docs';
const build = 'build';
const srcHtml = 'src/index.html';

gulp.task('html', () =>
	gulp.src(srcHtml)
		.pipe($.newer(dest))
		.pipe($.htmlMinifierTerser({
			collapseWhitespace: true,
			removeComments: true,
			minifyJS: true,
		}))
		// Prevent VS Code Linter error
		.pipe($.replace(/<script>(.+?)<\/script>/g, "<script>$1;</script>"))
		.pipe(gulp.dest(dest))
);

gulp.task('js', () =>
	gulp.src('src/*.js')
		.pipe($.newer(dest))
		.pipe($.terser())
		.pipe(gulp.dest(dest))
);

gulp.task('concatCss', () =>
	ordered([
		gulp.src('node_modules/bootstrap/dist/css/bootstrap.css'),
		gulp.src('src/style.css')
	])
		.pipe($.newer(build + '/style.css'))
		.pipe($.concat('style.css'))
		.pipe($.replace(/(\r|\n)*\/\*.+?\*\/$/, '')) // remove sourcemap
		.pipe(gulp.dest(build))
);

gulp.task('buildCss', () =>
	gulp.src(build + '/style.css')
		.pipe($.newer({
			dest: dest + '/style.css',
			extra: [__filename, srcHtml]
		}))
		.pipe($.purgecss({
			content: [srcHtml],
			defaultExtractor: purgeHtml,
			safelist: {
				standard: [
					/show/, /modal-static/, /modal-backdrop/, // Bootstrap modal
					// extractor can't figure dynamic class
					'disabled',
					'drag',
				],
				variables: [
					/^--bs-btn-disabled/, // Fixes a bug of purgeCss
				],
			},
			variables: true, // for Bootstrap
		}))
		.pipe($.cleanCss())
		.pipe(gulp.dest(dest))
);

gulp.task('css', gulp.series('concatCss', 'buildCss'));

gulp.task('python', () =>
	gulp.src('src/*.py')
		.pipe($.newer(dest))
		.pipe($.exec(file => `pyminify ${file.path} --rename-globals --preserve-globals loadFont,processFont,main,processLegacy`, { pipeStdout: true }))
		.pipe(gulp.dest(dest))
);

gulp.task('default', gulp.parallel('html', 'css', 'js', 'python'));
