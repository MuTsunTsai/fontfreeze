
# Change Log
All notable changes to this project will be documented in this file.

## [1.11.0] - 2025-05-14

- Change line height and letter spacing ([#13](https://github.com/MuTsunTsai/fontfreeze/issues/13)).

### Patches

- 1.11.1: Migrate from petite-vue to vue and improve UI.

## [1.10.0] - 2024-10-21

### Added

- Allowing keeping the font variable ([#17](https://github.com/MuTsunTsai/fontfreeze/issues/17)).

### Patches

- 1.10.1: Minor refactoring.
- 1.10.2: Keeps feature settings during font loading if the feature set is the same.
- 1.10.3: Adds error message for invalid activation targets.
- 1.10.4: Fix instance names when keeping the font variable.

## [1.9.0] - 2024-04-11

### Added

- Display unicode-range for subsetting.

### Patches

- 1.9.1: Improve range display logic.
- 1.9.2: Improve local font UI.
- 1.9.3: Migrate project to Rsbuild.

## [1.8.0] - 2023-02-26

### Changed

- Will now automatically fill-in typographic family and subfamily names.
- Name settings are now initially hidden, with only the suffix option visible.

### Fixed

- 1.8.3: Fix issue [#11].

## [1.7.0] - 2022-11-09

### Fixed

- 1.7.3: Fix the bug that hiding deactivated features doesn't work for some fonts ([#4](https://github.com/MuTsunTsai/fontfreeze/issues/4)). In that case FontFreeze will fallback to not hiding those features.

### Added

- Supporting typographic subfamily name setting. ([#3](https://github.com/MuTsunTsai/fontfreeze/issues/3))

## [1.6.0] - 2022-10-06

### Added

- One may choose to exclude or to include the subsetting glyphs.
- Update to Pyodide 0.21.3.

### Fixed

- Incorrectly handles glyphs within the higher Unicode range.
- Emoji icons not showing in some environments.
- 1.6.1: Preview box may only use plaintext from now.

## [1.5.0] - 2022-08-23

### Added

- New UI design, allowing file dropping anywhere on the page.
- Capable of handling more legacy font files.
- Improved error handling.

## [1.4.0] - 2022-08-18

### Added

- Progress indicator for loading Python packages.
- Add description in generated font.

### Fixed

- 1.4.5: Update to Pyodide 0.21.1, which fixed issue in Safari v14.

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
