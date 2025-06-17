<template>
	<v-tooltip :text="title" max-width="200">
		<template v-slot:activator="{ props }">
			<slot v-bind="props" class="cursor-pointer" v-if="$slots['default']"></slot>
			<v-icon v-else v-bind="props" class="text-info cursor-pointer" icon="mdi-information-outline" />
		</template>
	</v-tooltip>
</template>

<script setup lang="ts">
	defineProps<{
		title: string;
	}>();
</script>
