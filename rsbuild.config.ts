import { defineConfig } from "@rsbuild/core";
import { pluginSass } from "@rsbuild/plugin-sass";
import { pluginVue } from "@rsbuild/plugin-vue";
import { VuetifyPlugin } from "webpack-plugin-vuetify";
import { pluginHtmlMinifierTerser } from "rsbuild-plugin-html-minifier-terser";
import { existsSync, statSync } from "fs";

import pkg from "./package.json";

const isProduction = process.env.NODE_ENV === "production";

// Used for the loading progress; built by the gulp task "wasm".
const wasmFile = "./build/wasm/fontfreeze_bg.wasm";
const wasmSize = existsSync(wasmFile) ? statSync(wasmFile).size : 0;

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
			WASM_SIZE: String(wasmSize),
		},
		assetsInclude: [/\.txt$/],
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
	performance: {
		buildCache: true,
	},
	plugins: [
		pluginSass(),
		pluginVue(),
		pluginHtmlMinifierTerser({
			removeComments: true,
		}),
	],
	tools: {
		rspack: (_, { appendPlugins }) => {
			appendPlugins(new VuetifyPlugin({}));
		},
	},
});
