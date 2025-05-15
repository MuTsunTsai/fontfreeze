<template>
	<header class="text-center my-3">
		<picture>
			<source srcset="logo.webp" type="image/webp">
			<img src="logo.png" width="800" height="130" style="max-width:100%; height:auto;">
		</picture>
		<div style="margin-top: -1.5rem;">
			Freeze variations and features in font.
		</div>

		<!-- shields.io -->
		<div class="mb-3 mt-1">
			<img class="me-1 me-sm-2 me-md-3 mt-2" alt="GitHub package.json version"
				 :src="`https://img.shields.io/badge/version-v${version}-green`"><a class="me-1 me-sm-2 me-md-3"
			   href="https://github.com/mutsuntsai/fontfreeze"><img alt="GitHub Repo stars" class="mt-2"
					 src="https://img.shields.io/github/stars/mutsuntsai/fontfreeze?logo=GitHub&color=yellow"></a><a
			   href="https://github.com/mutsuntsai"><img class="mt-2"
					 src="https://img.shields.io/badge/%C2%A92022--2025-Mu--Tsun%20Tsai-blue"></a>
		</div>

		<input type="file" id="upload" @change="openFile($event)" title="Open font file">
		<div class="mt-3 d-flex justify-content-center" style="gap:1rem">
			<label type="button" class="btn btn-success" for="upload" :class="{ disabled: store.loading }">
				<div class="display-4">📂</div>
				<div>Open font file</div>
			</label>
			<span v-if="localFontSupport">
				<button type="button" :disabled="Boolean(store.loading)" class="btn btn-secondary" @click="local">
					<div class="display-4 text-warning">𝕬</div>
					<div>Select local font</div>
				</button>
			</span>
		</div>
		<div class="mt-3">
			<div v-if="store.loading">Loading {{ store.loading }}. Please wait...</div>
			<div v-else-if="store.font">{{ store.font.fileName }} ({{ store.font.fileSize }})</div>
			<div v-else>Open a font or drop a font file anywhere!</div>
		</div>
	</header>
</template>

<script setup lang="ts">
	import { store } from '../store';
	import { tryOpenFile } from '../loader';
	import { local } from "../localFonts";

	const version = VERSION;
	const localFontSupport = "queryLocalFonts" in window;

	function openFile(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if(!file) return;
		input.value = ""; // clear field
		tryOpenFile(file);
	}
</script>
