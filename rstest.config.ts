import { defineConfig } from "@rstest/core";

// Unit tests of the front end.
// The font processing is tested in src/rust (cargo test).
export default defineConfig({
	include: ["test/unit/**/*.test.ts"],
});
