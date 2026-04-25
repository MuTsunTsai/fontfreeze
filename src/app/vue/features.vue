<template>
	<div v-if="store.font?.gsub?.length">
		<h5 class="text-title-large my-2 d-flex align-center">
			<span>{{ $t("features.title") }}</span>
			<Tip :title="$t('features.tip')"/>
			<v-btn
				class="ms-2"
				density="comfortable"
				variant="outlined"
				color="primary"
				@click="showCustomFeatures"
			>
				{{ $t("features.custom") }}
			</v-btn>
		</h5>
		<div class="d-flex flex-wrap">
			<div v-for="f in store.font.gsub" :key="f" style="flex-basis: 5rem;">
				<!-- Custom value: render a non-clickable numbered box. -->
				<div v-if="typeof store.features[f] === 'number'" class="feature-custom d-flex align-center my-n1">
					<div class="feature-custom-box" :data-value="store.features[f]"/>
					<v-tooltip interactive open-on-hover>
						<template #activator="{ props }">
							<span v-bind="props" class="feature-custom-label">{{ f }}</span>
						</template>
						<span v-if="featureURL[f]">
							<a :href="`https://learn.microsoft.com/en-us/typography/opentype/spec/features_${featureURL[f]}`">
								{{ getFeatureTitle(f) }}
							</a> ↗️
						</span>
						<span v-else>{{ $t("features.unknown") }}</span>
					</v-tooltip>
				</div>
				<!-- Regular tri-state checkbox. -->
				<v-checkbox
					v-else
					v-model="store.features[f]"
					:indeterminate="store.features[f] === undefined"
					color="primary"
					class="my-n1"
					indeterminate-icon="mdi-close-box text-error"
					@change="changeFeature(f)"
				>
					<template #label>
						<v-tooltip interactive open-on-hover>
							<template #activator="{ props }">
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
		<CustomFeatures/>
	</div>
</template>

<script lang="ts">
	import { useI18n } from "vue-i18n";

	import { store } from "../store";
	import { featureURL } from "../meta/constants";
	import Tip from "./components/tip.vue";
	import CustomFeatures, { showCustomFeatures } from "./modals/customFeatures.vue";

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
		// Only the boolean/undefined v-checkbox path triggers changeFeature
		// (number-valued features render a non-clickable box, see template).
		const current = store.features[f];
		lastValues[f] = typeof current === "number" ? undefined : current;
	}
</script>

<style lang="scss">
	.feature-custom {
		// Aligns with the v-checkbox visible footprint:
		// - height 48px matches v-checkbox total (control 48 + label 12+12 padding)
		// - 6px inline padding mirrors the centered ripple/icon area of v-checkbox
		min-height: 48px;
		padding-inline-start: 6px;
	}

	.feature-custom-box {
		// The mdi checkbox-blank-outline glyph occupies a 24x24 cell but its
		// visible square is 18x18 with a ~1.5px stroke (measured empirically).
		// Reproduce that here: outer 24x24 footprint, inner visible 18x18 box.
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;

		&::before {
			content: attr(data-value);
			width: 1.25rem;
			height: 1.25rem;
			border: 0.15rem solid rgb(var(--v-theme-primary));
			border-radius: 2px;
			display: flex;
			align-items: center;
			justify-content: center;
			font-size: 0.75rem;
			font-weight: 500;
			line-height: 1;
			position: relative;
			color: rgb(var(--v-theme-primary));
		}
	}

	.feature-custom-label {
		margin-inline-start: 6px;
	}
</style>
