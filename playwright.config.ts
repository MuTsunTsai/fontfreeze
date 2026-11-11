import { defineConfig, devices } from "@playwright/test";

const CI = Boolean(process.env.CI);
const URL = "http://localhost:3090/fontfreeze/";

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
				// Locally, use the installed Chrome instead of downloading Chromium.
				channel: CI ? undefined : "chrome",
			},
		},
	],
	webServer: {
		// Builds the wasm module first if needed (see the "predev" script).
		command: "pnpm dev",
		url: URL,
		reuseExistingServer: !CI,
		timeout: 600_000,
	},
});
