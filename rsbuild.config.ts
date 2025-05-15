import { defineConfig } from "@rsbuild/core";
import { pluginSass } from "@rsbuild/plugin-sass";
import { pluginVue } from "@rsbuild/plugin-vue";
import { pluginHtmlMinifierTerser } from "rsbuild-plugin-html-minifier-terser";

import pkg from "./package.json";

const isProduction = process.env.NODE_ENV === "production";

export default defineConfig({
	dev: {
		progressBar: true,
	},
	source: {
		entry: {
			index: "./src/app/index.ts",
		},
		define: {
			VERSION: `"${pkg.version}"`,
		},
		tsconfigPath: "./src/app/tsconfig.json",
	},
	html: {
		template: "./src/public/index.html",
	},
	server: {
		base: "/fontfreeze",
		port: 3090,
		publicDir: {
			name: "src/public",
			copyOnBuild: true,
		},
	},
	output: {
		cleanDistPath: isProduction,
		dataUriLimit: 100,
		legalComments: "none",
		polyfill: "off",
		distPath: {
			root: "docs",
		},
	},
	plugins: [
		pluginSass(),
		pluginVue(),
		pluginHtmlMinifierTerser({
			removeComments: true,
		}),
	],
});
