import { createConfig } from "@mutsuntsai/eslint";

export default [
	...createConfig({
		ignores: ["docs/**", "build/**", "src/rust/target/**"],
		import: {
			files: ["src/**/*.vue", "**/*.ts", "eslint.config.js", "gulpfile.js"],
			project: ["src/app", "test/unit", "test/e2e"],
		},
		globals: {
			esm: ["gulpfile.js", "eslint.config.js", "playwright.config.ts"],
			browser: ["src/**"],
		},
	}),

	/////////////////////////////////////////////////////////////////////////////////////////////////////
	// Specific scopes
	/////////////////////////////////////////////////////////////////////////////////////////////////////

	{
		files: ["src/**/*.{ts,vue}"],
		rules: {
			"@typescript-eslint/explicit-function-return-type": ["warn", {
				allowExpressions: true,
			}],
		},
	},
	{
		files: ["test/**/*.ts"],
		rules: {
			"@typescript-eslint/no-magic-numbers": "off",
			// The steps of a test are sequential by nature.
			"no-await-in-loop": "off",
		},
	},

];
