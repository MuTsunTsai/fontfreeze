<template>
	<div v-if="store.font!.fvar" class="mb-3">
		<v-row align="center" justify="space-between">
			<v-col>
				<h5 class="text-h5">
					Variations
					<Tip
						 title="Whenever possible, use a non-variable version of the font as starting point, as it will likely give better hinting than the variable one." />
				</h5>
			</v-col>
			<v-col>
				<v-checkbox v-model="store.options.keepVar" label="Keep the font variable" />
			</v-col>
		</v-row>

		<div v-if="!store.options.keepVar">
			<div class="d-flex mb-3 mt-2">
				<v-select label="Predefined instances" :items="instanceItems" v-model="selectedInstance" />
			</div>
			<div v-for="(a, i) in axes" class="mb-1" :key="i">
				<v-row align="center">
					<v-col style="width: 5rem;">
						{{ getAxisName(a) }}
					</v-col>
					<v-col class="d-none d-sm-block">
						<v-slider v-model.number="store.variations[a.tag]" :min="a.min" :max="a.max" :step="getStep(a)"
								  width="15rem" @update:model-value="clear">
						</v-slider>
					</v-col>
					<v-col>
						<v-number-input density="compact" v-model="store.variations[a.tag]" :min="a.min" :max="a.max"
										:step="getStep(a)" />
					</v-col>
				</v-row>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
	import { computed, shallowRef, watch } from "vue";

	import Tip from "./components/tip.vue";
	import { store } from "../store";

	const axisNames: Record<string, string> = {
		ital: "Italic",
		opsz: "Optical size",
		slnt: "Slant",
		wdth: "Width",
		wght: "Weight",
	};

	const instances = computed(() => {
		if(!store.font || !store.font.fvar) return [];
		return store.font.fvar.instances;
	});

	const axes = computed(() => {
		if(!store.font || !store.font.fvar) return [];
		return store.font.fvar.axes;
	});

	const LARGE_THRESHOLD = 20;
	const MINI_STEP = 0.1;
	const TINY_STEP = 0.01;

	function getStep(axis: Axis): number {
		const range = axis.max - axis.min;
		if(range > LARGE_THRESHOLD) return 1;
		if(range > 1) return MINI_STEP;
		return TINY_STEP;
	}

	function getAxisName(axis: Axis): string {
		if(axis.name) return axis.name;
		return axis.tag in axisNames ? axisNames[axis.tag] : axis.tag;
	}

	function clear(): void {
		selectedInstance.value = undefined;
	}

	const selectedInstance = shallowRef<number>();
	const instanceItems = computed(() => instances.value.map((i, j) => ({
		title: i.name,
		value: j,
	})));
	watch(selectedInstance, () => {
		if(selectedInstance.value === undefined) return;
		const instance = instances.value[selectedInstance.value];
		store.options.typo_subfamily = instance.name;
		for(const t in instance.coordinates) {
			store.variations[t] = instance.coordinates[t];
		}
	});
</script>
