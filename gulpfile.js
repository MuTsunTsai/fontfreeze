const cleanCss = require('gulp-clean-css');
const exec = require('gulp-exec');
const gulp = require('gulp');
const html = require('gulp-html-minifier-terser');
const newer = require('gulp-newer');
const replace = require('gulp-replace');
const terser = require('gulp-terser');

const dest = 'docs';

gulp.task('html', () =>
	gulp.src('src/index.html')
		.pipe(newer(dest))
		.pipe(html({
			collapseWhitespace: true,
			removeComments: true,
			minifyJS: true,
		}))
		// Prevent VS Code Linter error
		.pipe(replace(/<script>(.+?)<\/script>/g, "<script>$1;</script>"))
		.pipe(gulp.dest(dest))
);

gulp.task('js', () =>
	gulp.src('src/*.js')
		.pipe(newer(dest))
		.pipe(terser())
		.pipe(gulp.dest(dest))
);

gulp.task('css', () =>
	gulp.src('src/*.css')
		.pipe(newer(dest))
		.pipe(cleanCss())
		.pipe(gulp.dest(dest))
);

gulp.task('python', () =>
	gulp.src('src/*.py')
		.pipe(newer(dest))
		.pipe(exec(file => `pyminify ${file.path} --rename-globals --preserve-globals loadFont,processFont,main`, { pipeStdout: true }))
		.pipe(gulp.dest(dest))
);

gulp.task('default', gulp.parallel('html', 'css', 'js', 'python'));
