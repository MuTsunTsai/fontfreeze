
# Change Log
All notable changes to this project will be documented in this file.

## [1.3.0] - 2022-08-16

### Added

- Make substitution by single-glyph features for maximal compatibility ([#2](https://github.com/MuTsunTsai/fontfreeze/issues/2)).

## [1.2.0] - 2022-08-11

### Added

- Loading locally installed fonts using [local fonts API](https://web.dev/local-fonts/).
- Option to export to WOFF2 format.

### Changed

- Upgrade Pyodide to version 0.21.0, which now includes `brotli` package (contributed by [myself](https://github.com/pyodide/pyodide/pull/2925) for this project).
- Use web worker for Pyodide.

## [1.1.0] - 2022-08-02
  
### Added
 
- "Remove glyphs" functionality.

## [1.0.0] - 2022-07-26
 
Initial release.