<template>
	<Teleport to="body">
		<div class="modal fade" id="local" data-bs-backdrop="static">
			<div class="modal-dialog modal-dialog-centered">
				<div class="modal-content">
					<div class="modal-header">
						<h4 class="m-0">Select local font</h4>
					</div>
					<div class="modal-body">
						<select v-if="shouldLoadList" class="form-select mb-3" v-model="store.localFamily" required
								@change="familyChange" :style="familyStyle()" size="5">
							<option value="" hidden>Select local font family</option>
							<option v-for="(f, i) in localFamilies" :key="i" :value="f" v-text="f" :style="familyStyle(f)">
							</option>
						</select>
						<div v-else class="form-control loading w-100 mb-3" style="font-size: 3rem !important; height: 10rem;">
						</div>

						<select class="form-select" v-model.number="store.localFont" required :style="optionStyle()">
							<option value="" hidden>Select font style</option>
							<option v-for="(f, i) in store.localFonts" :key="i" :value="i" :style="optionStyle(f)"
									:hidden="f.family != store.localFamily"
									:disabled="store.unavailableFonts.includes(f.postscriptName)">
								{{ f.fullName }}</option>
						</select>
						<div class="mt-3" v-if="chromiumVersion < 109">
							Note: This is an experimental feature and it may not work for manually installed fonts.
							If it doesn't work for a particular font, you can still upload the font file manually.
							This is a bug in Chromium and will be fixed in version 109.
						</div>
					</div>
					<div class="modal-footer">
						<button class="btn btn-secondary" type="button" @click="store.localFont = ''"
								data-bs-dismiss="modal">Cancel</button>
						<button class="btn btn-primary" type="button" @click="loadLocal"
								:disabled="(typeof store.localFont) != 'number'">OK</button>
					</div>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<script setup lang="ts">
	import { computed, onMounted, shallowRef } from "vue";

	import { loadLocal } from "../../localFonts";
	import { store } from "../../store";

	const chromiumVersion = parseInt(navigator.userAgentData?.brands.find(b => b.brand == "Chromium")?.version ?? "0");

	const shouldLoadList = shallowRef(false);
	onMounted(() => {
		// const el = document.getElementById("local")!;
		// el.addEventListener("shown.bs.modal", () => shouldLoadList.value = true);
		// el.addEventListener("hidden.bs.modal", () => shouldLoadList.value = false);
	});

	function familyStyle(family = store.localFamily): string {
		const filtered = store.localFonts.filter(font => font.family == family);
		if(!filtered.length) return "";
		let font = filtered.find((f: FontData): boolean => f.style == "Regular");
		if(!font) {
			filtered.sort((a, b) => a.fullName.length - b.fullName.length);
			font = filtered[0];
		}
		return `font-family:'local ${font.fullName}'`;
	}

	function optionStyle(f?: FontData): string {
		if(!f) {
			if(store.localFont === "") return "";
			f = store.localFonts[store.localFont];
		}
		return `font-family:'local ${f.fullName}'`;
	}

	const localFamilies = computed(() => {
		if(!store.localFonts.length) return [];
		const result = new Set<string>();
		for(const font of store.localFonts) {
			result.add(font.family);
		}
		return [...result];
	});

	function familyChange(): void {
		store.localFont = store.localFonts.findIndex(f => f.family == store.localFamily);
	}
</script>
