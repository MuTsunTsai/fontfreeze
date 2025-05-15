<template>
	<div v-if="store.font!.fvar">
		<div class="float-end">
			<div class="form-check">
				<input type="checkbox" class="form-check-input" id="chk_var" v-model="store.options.keepVar">
				<label class="form-check-label" for="chk_var">Keep the font variable</label>
			</div>
		</div>
		<h5>Variations</h5>
		<div v-if="!store.options.keepVar">
			<div class="d-flex mb-3">
				<label class="col-form-label pe-3">Predefined instances:</label>
				<div class="flex-grow-1">
					<select @change="setInstance(instances[Number(($event.target as HTMLSelectElement).value)])"
							class="form-select" required>
						<option value="" hidden>Select a predefined instance</option>
						<option v-for="(i, j) in instances" :key="i.name + j" :value="j">{{ i.name }}</option>
					</select>
				</div>
			</div>
			<div v-for="(a, i) in axes" class="mb-1" :key="i">
				<input type="range" class="form-range me-4" style="width:10rem;" @input="clear"
					   v-model.number="store.variations[a.tag]" :min="a.min" :max="a.max" :step="getStep(a)">
				<input type="number" class="form-control form-control-sm d-inline-block me-4" style="width:5rem;"
					   v-model.number="store.variations[a.tag]" :min="a.min" :max="a.max" :step="getStep(a)" @input="clear">
				<label>{{ getAxisName(a) }}</label>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
	import { computed } from "vue";

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

	function setInstance(instance: FontInstance): void {
		store.options.typo_subfamily = instance.name;
		for(const t in instance.coordinates) {
			store.variations[t] = instance.coordinates[t];
		}
	}

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
		const selectElement = document.getElementsByTagName("select")[0];
		if(selectElement) selectElement.value = "";
	}
</script>
