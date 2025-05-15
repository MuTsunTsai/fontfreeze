<template>
	<span class="text-info" ref="el" data-bs-toggle="tooltip" :data-bs-title="title">ⓘ</span>
</template>

<script setup lang="ts">
	import { onMounted, shallowRef } from "vue";
	import Tooltip from "bootstrap/js/dist/tooltip";

	defineProps<{
		title: string;
	}>();

	const el = shallowRef<HTMLSpanElement>();

	onMounted(() => Tooltip.getOrCreateInstance(el.value!));

</script>

<style lang="css">
	.tooltip {
		--bs-tooltip-opacity: 1 !important;
		--bs-tooltip-bg: var(--bs-gray-200) !important;
		--bs-tooltip-color: var(--bs-black) !important;
	}

	.tooltip-inner {
		text-align: left !important;
	}

	@media (prefers-color-scheme: dark) {
		.tooltip {
			--bs-tooltip-bg: var(--bs-gray-700) !important;
			--bs-tooltip-color: var(--bs-white) !important;
		}
	}
</style>
