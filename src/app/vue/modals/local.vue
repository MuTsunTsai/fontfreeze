<template>
	<v-dialog v-model="showLocal" max-width="500" @after-enter="shouldLoadList = true" @after-leave="shouldLoadList = false">
		<v-card>
			<v-card-title>
				<h4 class="text-h5">Select local font</h4>
			</v-card-title>
			<v-card-text>
				<template v-if="shouldLoadList">
					<v-list class="control mb-3 pa-0" style="max-height: 20rem; overflow-y: scroll;" color="primary"
							v-model:selected="selected" selectable :items="localFamilies.map((f, i) => ({ title: f, value: f }))">
						<template v-slot:title="{ item }">
							<div :style="familyStyle(item.title)">{{ item.title }}</div>
						</template>
						<template v-slot:subtitle="{ item }">
							<div class="text-caption">{{ item.title }}</div>
						</template>
					</v-list>

					<v-select v-model.number="store.localFont" :items="items" :disabled="!store.localFamily" style="height:64px;">
						<template v-slot:item="{ item, props }">
							<v-list-item v-bind="props">
								<template v-slot:title>
									<div :style="optionStyle(item.raw.font)">{{ item.title }}aa</div>
								</template>
								<template v-slot:subtitle>
									<div class="text-caption">{{ item.title }}</div>
								</template>
							</v-list-item>
						</template>
						<template v-slot:selection="{ item }">
							<div>
								<div :style="optionStyle()">{{ item.title }}</div>
								<div class="text-caption">{{ item.title }}</div>
							</div>
						</template>
					</v-select>

					<div class="mt-3" v-if="chromiumVersion < 109">
						Note: This is an experimental feature and it may not work for manually installed fonts.
						If it doesn't work for a particular font, you can still upload the font file manually.
						This is a bug in Chromium and will be fixed in version 109.
					</div>
				</template>
				<v-skeleton-loader v-else type="card" />
			</v-card-text>
			<v-card-actions>
				<v-btn color="secondary" @click="cancel">Cancel</v-btn>
				<v-btn color="primary" @click="loadLocal" :disabled="(typeof store.localFont) != 'number'">OK</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script setup lang="ts">
	import { computed, ref, shallowRef, watch } from "vue";

	import { loadLocal, showLocal } from "../../localFonts";
	import { store } from "../../store";

	const chromiumVersion = parseInt(navigator.userAgentData?.brands.find(b => b.brand == "Chromium")?.version ?? "0");

	const shouldLoadList = shallowRef(false);

	const selected = ref([] as string[]);

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
		return `font-family:'local ${f.fullName}' !important`;
	}

	const localFamilies = computed(() => {
		if(!store.localFonts.length) return [];
		const result = new Set<string>();
		for(const font of store.localFonts) {
			result.add(font.family);
		}
		return [...result];
	});

	watch(selected, () => {
		store.localFamily = selected.value[0];
		store.localFont = store.localFonts.findIndex(f => f.family == store.localFamily);
	});

	function cancel(): void {
		store.localFont = "";
		showLocal.value = false;
	}

	const items = computed(() => store.localFonts
		.map((f, i) => ({ f, i }))
		.filter(f => f.f.family == store.localFamily)
		.map(f => ({
			title: f.f.fullName,
			value: f.i,
			font: f.f,
		}))
	);
</script>
