<template>
	<div v-if="store.font?.gsub?.length">
		<h5>
			Features
			<Tip
				 title="In most cases, the feature you are looking for will be among cv01-cv99, ss01-ss20, zero, onum, etc. (look up the user manual of your font). Hover over the a tag name to link to its general documentation." />
		</h5>
		<div class="d-flex flex-wrap">
			<div v-for="f in store.font.gsub" style="flex-basis: 5.5rem;" :key="f">
				<div class="form-check">
					<input type="checkbox" class="form-check-input" :id="'chk' + f"
						   :indeterminate.prop="store.features[f] === undefined" v-model="store.features[f]"
						   @change="changeFeature(f)">
					<label class="form-check-label" :class="{ 'text-secondary': !(f in featureTitle) }" :for="'chk' + f">
						<Tip :title="featureTip(f)">{{ f }}</Tip>
					</label>
				</div>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
	import { store } from "../store";
	import { featureTitle } from "../meta/constants";
	import Tip from "./components/tip.vue";

	/** The last value before the current value for each features. */
	let lastValues: Record<string, boolean | undefined>;

	const lastFeatures = new Set<string>();

	export function setupFeatures(gsub: readonly string[]): void {
		if(sameFeatures(gsub)) return;

		lastFeatures.clear();
		store.features = {};
		lastValues = {};
		for(const g of gsub) {
			lastFeatures.add(g);
			store.features[g] = lastValues[g] = false;
		}
	}

	function sameFeatures(gsub: readonly string[]): boolean {
		if(gsub.length != lastFeatures.size) return false;
		for(const g of gsub) {
			if(!lastFeatures.has(g)) return false;
		}
		return true;
	}

	function featureTip(f: string): string {
		if(f in featureTitle) {
			const d = featureTitle[f];
			return `<a href="https://learn.microsoft.com/en-us/typography/opentype/spec/features_${d[1]}">${d[0]}</a> ↗️`;
		}
		return "Unknown feature";
	}
</script>

<script setup lang="ts">
	function changeFeature(f: string): void {
		if(lastValues[f] === true) store.features[f] = undefined;
		if(lastValues[f] === undefined) store.features[f] = false;
		lastValues[f] = store.features[f];
	}
</script>
