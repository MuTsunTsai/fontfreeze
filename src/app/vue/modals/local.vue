<template>
	<v-dialog
		v-model="showLocal"
		max-width="500"
		@after-enter="shouldLoadList = true"
		@after-leave="shouldLoadList = false"
	>
		<v-card>
			<v-card-title class="pt-3">
				<span class="text-headline-small">{{ $t("local.title") }}</span>
			</v-card-title>
			<v-card-text class="py-2">
				<template v-if="shouldLoadList">
					<v-list
						v-model:selected="selected"
						class="control mb-3"
						style="padding: 0; max-height: 20rem; overflow-y: scroll;"
						color="primary"
						selectable
						:items="localFamilies.map(f => ({ title: f, value: f }))"
					>
						<template #title="{ item }">
							<div :style="familyStyle(item.title)">{{ item.title }}</div>
						</template>
						<template #subtitle="{ item }">
							<div class="text-body-small">{{ item.title }}</div>
						</template>
					</v-list>

					<v-select
						v-model.number="store.localFont"
						:items="items"
						:disabled="!store.localFamily"
						style="height:64px;"
					>
						<template #item="{ item, props }">
							<v-list-item v-bind="props">
								<template #title>
									<div :style="optionStyle(item.font)">{{ item.title }}</div>
								</template>
								<template #subtitle>
									<div class="text-body-small">{{ item.title }}</div>
								</template>
							</v-list-item>
						</template>
						<template #selection="{ item }">
							<div>
								<div :style="optionStyle()">{{ item.title }}</div>
								<div class="text-body-small">{{ item.title }}</div>
							</div>
						</template>
					</v-select>

					<div v-if="chromiumVersion < 109" class="mt-3">
						{{ $t("local.experimentalNote") }}
					</div>
				</template>
				<v-skeleton-loader v-else type="card"/>
			</v-card-text>
			<v-card-actions>
				<v-btn color="secondary" @click="cancel">{{ $t("local.cancel") }}</v-btn>
				<v-btn color="primary" :disabled="(typeof store.localFont) != 'number'" @click="loadLocal">{{ $t("local.ok") }}</v-btn>
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
