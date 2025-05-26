<template>
	<span class="tooltip-container" ref="el" data-bs-toggle="tooltip" :data-bs-title="title">
		<slot v-if="$slots['default']"></slot>
		<span v-else class="text-info">ⓘ</span>
	</span>
</template>

<script setup lang="ts">
	import { onMounted, shallowRef, useSlots } from "vue";
	import Tooltip from "bootstrap/js/dist/tooltip";

	const slots = useSlots();

	defineProps<{
		title: string;
	}>();

	const el = shallowRef<HTMLSpanElement>();

	onMounted(() => Tooltip.getOrCreateInstance(el.value!, slots.default ? {
		container: el.value!, // So that the tooltip can be interacted with
		html: true,
		delay: {
			show: 0,
			hide: 50, // Make it less likely to vanish when the mouse is moving towards the tooltip
		},
	} : {}));

</script>

<style lang="css">
	.tooltip-container {
		cursor: pointer;
	}

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
