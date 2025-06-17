<template>
	<main v-if="store.font" class="px-8 pb-6">
		<div class="mt-4 text-center">
			<span :style="`vertical-align:-0.25rem; font-family: preview${store.previewIndex};`"
				  class="text-primary text-h5 me-4">{{
					store.font.family }}</span>
			<div class="d-inline-block">
				<span class="me-3">{{ store.font.version }}</span>
				<Info />
			</div>
		</div>

		<Variable />
		<Features />

		<v-row class="mt-3">
			<v-col cols="12" sm="7" md="8" class="mt-2">
				<v-text-field label="Subsetting" v-model="store.glyphs" placeholder="Enter characters here">
					<template v-slot:clear="{ props }">
						<v-icon v-if="store.glyphs" v-bind="props" icon="$delete" class="cursor-pointer" />
					</template>
				</v-text-field>
			</v-col>
			<v-col cols="12" sm="5" md="4" class="mt-2">
				<v-select :items="subsetModes" label="Subsetting mode" v-model="store.subsetMode" />
			</v-col>
		</v-row>
		<div v-if="store.unicodeRange">unicode-range: {{ store.unicodeRange }};</div>

		<Preview />

		<v-row class="mt-3">
			<v-col cols="12" md="6" class="mt-2">
				<v-number-input label="Additional line height" placeholder="in font units" :step="50"
								v-model="store.options.lineHeight" @blur="validateNumber('lineHeight')">
					<template v-slot:prepend-inner>
						<Tip
							 title="Only works in supported environments. The preview here is the simulated result (for non-zero values)." />
					</template>
					<template v-slot:clear="{ props }">
						<v-icon v-if="store.options.lineHeight != 0" v-bind="props" icon="$delete" class="cursor-pointer" />
					</template>
				</v-number-input>
			</v-col>
			<v-col cols="12" md="6" class="mt-2">
				<v-number-input label="Additional letter spacing" placeholder="in font units" :step="50"
								v-model="store.options.spacing" @blur="validateNumber('spacing')" clearable>
					<template v-slot:clear="{ props }">
						<v-icon v-if="store.options.spacing != 0" v-bind="props" icon="$delete" class="cursor-pointer" />
					</template>
				</v-number-input>
			</v-col>
		</v-row>

		<Options />

		<v-row class="mt-5">
			<v-col cols="6">
				<v-btn size="large" :color="store.message ? 'success' : 'primary'" @click="generate" :disabled="store.running">
					{{ store.message || "Generate font!" }}
					<v-progress-circular v-if="store.running" size="20" class="ms-2" indeterminate />
				</v-btn>
			</v-col>
			<v-col cols="6" class="text-end" v-if="store.url">
				<v-btn size="large" color="success" :href="store.url" :download="store.download">Download
					font</v-btn>
			</v-col>
		</v-row>
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

	function validateNumber(key: "lineHeight" | "spacing"): void {
		store.options[key] ??= 0;
	}

	const subsetModes = [
		{
			title: "Exclude these glyphs",
			value: "exclude",
		},
		{
			title: "Include only these glyphs",
			value: "include",
		},
	];

</script>
