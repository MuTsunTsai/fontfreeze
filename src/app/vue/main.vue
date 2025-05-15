<template>
	<main v-if="store.font">
		<div class="mt-4 text-center">
			<span :style="`vertical-align:-0.25rem; font-family: preview${store.previewIndex};`" class="text-primary h3 me-4">{{
				store.font.family }}</span>
			<div class="d-inline-block">
				<span class="me-3">{{ store.font.version }}</span>
				<Info />
			</div>
		</div>

		<Variable />
		<Features />

		<div class="row mt-3">
			<div class="col-12 col-md-7">
				<label>Subsetting</label>
				<input class="form-control" v-model="store.glyphs" placeholder="Enter characters here.">
			</div>
			<div class="col-12 col-md-5">
				<label>Subsetting mode</label>
				<select class="form-select" v-model="store.subsetMode">
					<option value="exclude">Exclude these glyphs.</option>
					<option value="include">Include only these glyphs.</option>
				</select>
			</div>
		</div>
		<div v-if="store.unicodeRange">unicode-range: {{ store.unicodeRange }};</div>

		<Preview />

		<div class="row">
			<div class="col-12 col-md-6 mt-2">
				<div class="row">
					<label class="col-8 col-form-label text-end">
						Additional line height
						<Tip title="Only works in supported environments. The preview here is the simulated result (for non-zero values)." />
					</label>
					<div class="col">
						<input class="form-control" type="number" v-model.number="store.options.lineHeight" @blur="validateNumber"
							   placeholder="in font units">
					</div>
				</div>
			</div>
			<div class="col-12 col-md-6 mt-2">
				<div class="row">
					<label class="col-8 col-form-label text-end">Additional letter spacing</label>
					<div class="col">
						<input class="form-control" type="number" v-model.number="store.options.spacing" @blur="validateNumber"
							   placeholder="in font units">
					</div>
				</div>
			</div>
		</div>

		<Options />

		<div class="mt-5 row">
			<div class="col">
				<button class="btn btn-lg" type="button" @click="generate" :disabled="store.running"
						:class="store.message ? 'btn-success' : 'btn-primary'">
					{{ store.message || "Generate font!" }}
					<span class="loading ms-2" v-if="store.running"></span>
				</button>
			</div>
			<div class="col text-end" v-if="store.url">
				<a class="btn btn-lg btn-success" :href="store.url" :download="store.download">Download font</a>
			</div>
		</div>
	</main>
</template>

<script setup lang="ts">
	import { store } from "../store";
	import { generate } from "../generate";
	import Info from "./modals/info.vue";
	import Options from "./options.vue";
	import Variable from "./variable.vue";
	import Preview from "./preview.vue";
	import Features from "./features.vue";
	import Tip from "./components/tip.vue";

	function validateNumber(e: Event): void {
		const input = e.target as HTMLInputElement;
		const value = Number(input.value);
		if(!input.value.trim() || Number.isNaN(value)) input.value = "0";
		if(!Number.isInteger(value)) input.value = Math.round(value).toString();
	}
</script>
