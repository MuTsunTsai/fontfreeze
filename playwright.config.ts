import { defineConfig, devices } from "@playwright/test";

const CI = Boolean(process.env.CI);
// Tests the release build in docs/ (built by "pnpm build") instead.
const PREVIEW = Boolean(process.env.E2E_PREVIEW);
const DEV_PORT = 3090;
const PREVIEW_PORT = 3091;
const PORT = PREVIEW ? PREVIEW_PORT : DEV_PORT;
const URL = `http://localhost:${PORT}/fontfreeze/`;

// End-to-end tests of the app in Chromium, with the fonts in test/fonts.
export default defineConfig({
	testDir: "test/e2e",
	fullyParallel: true,
	forbidOnly: CI,
	retries: CI ? 1 : 0,
	reporter: CI ? "github" : "list",
	use: {
		baseURL: URL,
		locale: "en-US",
		trace: "retain-on-failure",
	},
	projects: [
		{
			name: "chromium",
			use: {
				...devices["Desktop Chrome"],
				// Locally, use the installed Chrome
				// instead of downloading Chromium.
				channel: CI ? undefined : "chrome",
			},
		},
	],
	webServer: {
		// "pnpm dev" builds the wasm module first if needed (see "predev").
		command: PREVIEW ? `pnpm exec rsbuild preview --port ${PORT}` : "pnpm dev",
		url: URL,
		reuseExistingServer: !CI,
		timeout: 600_000,
	},
});
