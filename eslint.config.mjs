// import globals from "globals";
// import pluginJs from "@eslint/js";
// import pluginTs from "typescript-esnlint";
// import pluginVue from "eslint-plugin-vue";
// import pluginImport from "eslint-plugi-import";
import { createConfig } from "@mutsuntsai/eslint";

export default [
	...createConfig({
		ignores: ["docs/**"],
		import: ["src/**/*.vue", "**/*.ts", "eslint.config.mjs"],
		project: ["src/app"],
		globals: {
			cjs: ["gulpfile.js"],
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
