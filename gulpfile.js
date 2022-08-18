const cleanCss = require('gulp-clean-css');
const exec = require('gulp-exec');
const gulp = require('gulp');
const html = require('gulp-html-minifier-terser');
const replace = require('gulp-replace');
const terser = require('gulp-terser');

gulp.task('html', () =>
	gulp.src('src/index.html')
		.pipe(html({
			collapseWhitespace: true,
			removeComments: true,
			minifyJS: true,
		}))
		// Prevent VS Code Linter error
		.pipe(replace(/<script>(.+?)<\/script>/g, "<script>$1;</script>"))
		.pipe(gulp.dest('docs'))
);

gulp.task('js', () =>
	gulp.src('src/*.js')
		.pipe(terser())
		.pipe(gulp.dest('docs'))
);

gulp.task('css', () =>
	gulp.src('src/*.css')
		.pipe(cleanCss())
		.pipe(gulp.dest('docs'))
);

gulp.task('python', () =>
	gulp.src('src/*.py')
		.pipe(exec(file => `pyminify ${file.path}`, { pipeStdout: true }))
		.pipe(gulp.dest('docs'))
);

gulp.task('default', gulp.parallel('html', 'css', 'js'));
