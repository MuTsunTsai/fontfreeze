<template>
	<v-tooltip :text="title" max-width="200">
		<template #activator="{ props }">
			<slot v-if="$slots['default']" v-bind="props" class="cursor-pointer"/>
			<v-icon
				v-else
				v-bind="props"
				class="text-info cursor-pointer"
				icon="mdi-information-outline"
			/>
		</template>
	</v-tooltip>
</template>

<script setup lang="ts">
	defineProps<{
		title: string;
	}>();
</script>
