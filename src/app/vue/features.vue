<template>
	<div v-if="store.font?.gsub?.length">
		<h5 class="text-title-large my-2">
			{{ $t("features.title") }}
			<Tip :title="$t('features.tip')" />
		</h5>
		<div class="d-flex flex-wrap">
			<div v-for="f in store.font.gsub" style="flex-basis: 5rem;" :key="f">
				<v-checkbox :indeterminate="store.features[f] === undefined" v-model="store.features[f]"
					@change="changeFeature(f)" color="primary" class="my-n1"
					indeterminate-icon="mdi-close-box text-error">
					<template v-slot:label>
						<v-tooltip interactive open-on-hover>
							<template v-slot:activator="{ props }">
								<span v-bind="props">{{ f }}</span>
							</template>
							<span v-if="featureURL[f]">
								<a :href="`https://learn.microsoft.com/en-us/typography/opentype/spec/features_${featureURL[f]}`">
									{{ getFeatureTitle(f) }}
								</a> ↗️
							</span>
							<span v-else>{{ $t("features.unknown") }}</span>
						</v-tooltip>
					</template>
				</v-checkbox>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
	import { store } from "../store";
	import { featureURL } from "../meta/constants";
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

</script>

<script setup lang="ts">
	import { useI18n } from "vue-i18n";

	const { t } = useI18n();

	function getFeatureTitle(tag: string): string {
		const ssMatch = tag.match(/^ss(\d+)$/);
		if(ssMatch) return t("feature.ss", { n: parseInt(ssMatch[1]) });
		const cvMatch = tag.match(/^cv(\d+)$/);
		if(cvMatch) return t("feature.cv", { n: parseInt(cvMatch[1]) });
		return t("feature." + tag);
	}

	function changeFeature(f: string): void {
		if(lastValues[f] === true) store.features[f] = undefined;
		if(lastValues[f] === undefined) store.features[f] = false;
		lastValues[f] = store.features[f];
	}
</script>
