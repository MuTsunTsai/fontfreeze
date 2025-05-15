<template>
	<div class="modal fade" ref="el">
		<div class="modal-dialog modal-dialog-centered">
			<div class="modal-content">
				<div class="modal-body" v-html="message"></div>
				<div class="modal-footer">
					<button type="button" class="btn btn-primary" data-bs-dismiss="modal">OK</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
	const modal = shallowRef<Modal>();
	const message = shallowRef<string>();

	export function alert(msg: string): void {
		message.value = msg;
		modal.value?.show();
	}
</script>

<script setup lang="ts">
	import { onMounted, shallowRef } from "vue";
	import Modal from "bootstrap/js/dist/modal";

	const el = shallowRef<HTMLElement>();

	onMounted(() => modal.value = Modal.getOrCreateInstance(el.value!, { backdrop: "static" }));
</script>
