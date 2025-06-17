<template>
	<v-dialog v-model="show" width="auto" persistent>
		<v-card>
			<v-card-text>
				<div v-html="message"></div>
			</v-card-text>
			<v-card-actions>
				<v-btn color="primary" @click="show = false">OK</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script lang="ts">
	const message = shallowRef<string>();
	const show = shallowRef(false);

	export function alert(msg: string): void {
		message.value = msg;
		show.value = true;
	}
</script>

<script setup lang="ts">
	import { shallowRef } from "vue";
</script>
