<template>
	<div class="dropzone">
		<div class="text-h2">
			<span>Drop font file</span>
		</div>
	</div>
</template>

<script setup lang="ts">
	import { onMounted } from "vue";

	import { tryOpenFile } from "../loader";

	onMounted(() => {
		const dropzone = document.querySelector(".dropzone") as HTMLDivElement;
		const toggle = (event: Event, drag: boolean): void => {
			event.stopPropagation();
			event.preventDefault();
			dropzone.classList.toggle("drag", drag);
		};
		document.body.addEventListener("dragover", event => toggle(event, true));
		dropzone.addEventListener("dragleave", event => toggle(event, false));
		dropzone.addEventListener("drop", event => {
			if(!event.dataTransfer) return;
			toggle(event, false);
			for(let i = 0; i < event.dataTransfer.items.length; i++) {
				const item = event.dataTransfer.items[i];
				if(item.kind == "file") {
					const file = item.getAsFile();
					if(file) tryOpenFile(file);
					return;
				}
			}
		});
	});

</script>

<style lang="scss">
	.dropzone {
		display: none;
		position: fixed;
		background: #8883;
		height: 100%;
		width: 100%;
		padding: 1rem;
		z-index: 2000;

		* {
			/* This is needed to prevent firing dragleave event on child elements. */
			pointer-events: none;
		}

		& > * {
			display: flex;
			border: 5px dashed rgb(var(--v-theme-on-background));
			height: 100%;
			width: 100%;
			justify-content: center;
			align-items: center;
			font-weight: 900;
		}

		&.drag {
			display: block;
			backdrop-filter: blur(5px);
		}

		input {
			cursor: pointer;
			opacity: 0;
			position: absolute;
			top: 0;
			right: 0;
			bottom: 0;
			left: 0;
		}
	}
</style>
