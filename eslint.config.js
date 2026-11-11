import { createConfig } from "@mutsuntsai/eslint";

export default [
	...createConfig({
		ignores: ["docs/**", "build/**", "src/rust/target/**"],
		import: {
			files: ["src/**/*.vue", "**/*.ts", "eslint.config.js", "gulpfile.js"],
			project: ["src/app", "test/unit"],
		},
		globals: {
			esm: ["gulpfile.js", "eslint.config.js"],
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
		files: ["test/unit/**/*.ts"],
		rules: {
			"@typescript-eslint/no-magic-numbers": "off",
		},
	},

];
