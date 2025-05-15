<template>
	<div class="row align-items-baseline">
		<div class="col-4">
			<h5>Preview</h5>
		</div>
		<div class="col-8 text-end">
			<span class="me-3">{{ store.previewSize }}pt</span>
			<input type="range" class="form-range" style="width:10rem;" min="8" max="48" v-model="store.previewSize">
		</div>
	</div>
	<div class="pre form-control p-3" :style="getPreviewStyle()"></div>
</template>

<script setup lang="ts">
	import { onMounted, watchEffect } from "vue";

	import { setupPlaintext, supportPlaintext } from "../plainText";
	import { sample, setPreviewUnicodeRange } from "../preview";
	import { store } from "../store";
	import { getUnicodes } from "../unicode";

	const BASE_LINE_HEIGHT = 1.5;

	onMounted(() => {
		setupDiv();
		watchEffect(() => setPreviewUnicodeRange(store.unicodeRange = getUnicodes()));
	});

	async function setupDiv(): Promise<void> {
		const div = document.querySelector("div.pre") as HTMLDivElement;
		if(supportPlaintext(div)) {
			// Chrome needs this, or the initial empty lines won't be selectable.
			div.innerText = await sample;
		} else {
			setupPlaintext(div);
			// Firefox needs this, or hitting enter will completely mess up the text.
			div.textContent = await sample;
		}
	}

	function getPreviewStyle(): string | null {
		if(!store.font) return null;
		const feat = store.font.gsub
			.filter(g => store.features[g] !== false)
			.map(g => `'${g}' ${store.features[g] ? "on" : "off"}`)
			.join(",");
		const variation = !store.font.fvar ? "normal" :
			store.font.fvar.axes
				.map(a => `'${a.tag}' ${store.variations[a.tag]}`)
				.join(",");
		const lineHeight = store.options.lineHeight == 0 ? BASE_LINE_HEIGHT :
			(store.font.lineHeight + store.options.lineHeight) / store.font.fontHeight;
		const spacing = store.options.spacing / store.font.fontHeight;
		return `white-space: pre-line;` +
			`font-family: preview${store.previewIndex};` +
			`font-feature-settings: ${feat};` +
			`font-variation-settings: ${variation};` +
			`font-size: ${store.previewSize}pt;` +
			`line-height: ${lineHeight};` +
			`letter-spacing: ${spacing}em`;
	}
</script>
