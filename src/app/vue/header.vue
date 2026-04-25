<template>
	<header class="text-center my-3">
		<picture>
			<source srcset="logo.webp" type="image/webp">
			<img
				src="logo.png"
				width="800"
				height="130"
				style="max-width:100%; height:auto;"
			>
		</picture>
		<div class="mt-n8">
			{{ $t("header.tagline") }}
		</div>

		<!-- shields.io -->
		<div class="mb-3 mt-1">
			<img
				class="me-1 me-sm-2 me-md-3 mt-2"
				alt="GitHub package.json version"
				:src="`https://img.shields.io/badge/version-v${version}-green`"
			>
			<a class="me-1 me-sm-2 me-md-3" href="https://github.com/mutsuntsai/fontfreeze"><img
				alt="GitHub Repo stars"
				class="mt-2"
				src="https://img.shields.io/github/stars/mutsuntsai/fontfreeze?logo=GitHub&color=yellow"
			></a>
			<a href="https://github.com/mutsuntsai"><img
				class="mt-2"
				:src="`https://img.shields.io/badge/%C2%A92022--${currentYear}-Mu--Tsun%20Tsai-blue`"
			></a>
		</div>

		<input
			id="upload"
			type="file"
			class="d-none"
			:title="$t('header.openFontFile')"
			@change="openFile($event)"
		>
		<v-row class="justify-center mt-3">
			<v-col>
				<v-btn
					for="upload"
					color="success"
					height="auto"
					class="py-2"
					:disabled="Boolean(store.loading)"
				>
					<label for="upload">
						<span class="text-display-large d-inline-block pb-2">📂</span><br>
						<span>{{ $t("header.openFontFile") }}</span>
					</label>
				</v-btn>
			</v-col>
			<v-col v-if="localFontSupport">
				<v-btn
					color="secondary"
					height="auto"
					class="py-2"
					:disabled="Boolean(store.loading)"
					@click="local"
				>
					<div>
						<span class="text-display-large d-inline-block pb-2"><v-icon class="my-n4 text-yellow" icon="mdi-format-font"/></span><br>
						<span>{{ $t("header.selectLocalFont") }}</span>
					</div>
				</v-btn>
			</v-col>
		</v-row>
		<div class="mt-3">
			<div v-if="store.loading">{{ $t("header.loading", { target: store.loading }) }}</div>
			<div v-else-if="store.font">{{ store.font.fileName }} ({{ store.font.fileSize }})</div>
			<div v-else>{{ $t("header.dropHint") }}</div>
		</div>
	</header>
</template>

<script setup lang="ts">
	import { store } from "../store";
	import { tryOpenFile } from "../loader";
	import { local } from "../localFonts";

	const version = VERSION;
	const currentYear = new Date().getFullYear();
	const localFontSupport = "queryLocalFonts" in window;

	function openFile(event: Event): void {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if(!file) return;
		input.value = ""; // clear field
		tryOpenFile(file);
	}
</script>
