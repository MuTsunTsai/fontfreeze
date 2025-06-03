import { createConfig } from "@mutsuntsai/eslint";

export default [
	...createConfig({
		ignores: ["docs/**"],
		import: ["src/**/*.vue", "**/*.ts", "eslint.config.js", "gulpfile.js"],
		project: ["src/app"],
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

];
