<template>
	<div v-if="store.font?.gsub?.length">
		<h5>Features</h5>
		<div class="d-flex flex-wrap">
			<div v-for="f in store.font.gsub" style="flex-basis: 5.5rem;" :key="f">
				<div class="form-check">
					<input type="checkbox" class="form-check-input" :id="'chk' + f"
						   :indeterminate.prop="store.features[f] === undefined" v-model="store.features[f]"
						   @change="changeFeature(f)">
					<label class="form-check-label" :for="'chk' + f">{{ f }}</label>
				</div>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
	import { store } from "../store";

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
</script>

<script setup lang="ts">
	function changeFeature(f: string): void {
		if(lastValues[f] === true) store.features[f] = undefined;
		if(lastValues[f] === undefined) store.features[f] = false;
		lastValues[f] = store.features[f];
	}
</script>
