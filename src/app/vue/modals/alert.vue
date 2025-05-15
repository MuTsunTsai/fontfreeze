<template>
	<div class="modal fade" ref="el" data-bs-backdrop="static">
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
	const alertModal = shallowRef<Modal>();
	const message = shallowRef<string>();

	export function alert(msg: string): void {
		message.value = msg;
		alertModal.value?.show();
	}
</script>

<script setup lang="ts">
	import { onMounted, shallowRef } from "vue";

	import { modal } from "../../utils";

	import type { Modal } from "bootstrap";

	const el = shallowRef<HTMLElement>();

	onMounted(() => alertModal.value = modal(el.value!));
</script>
