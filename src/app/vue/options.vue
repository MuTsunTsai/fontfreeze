<template>
	<h5 class="text-headline-small mt-4 mb-0">{{ $t("options.title") }}</h5>
	<v-row class="align-baseline">
		<v-col cols="12" sm="6" class="mt-2">
			<v-text-field :label="$t('options.fontFamilySuffix')" v-model="store.options.suffix" :disabled="store.options.customNames">
				<template v-slot:prepend-inner>
					<Tip
						:title="$t('options.suffixTip')" />
				</template>
			</v-text-field>
		</v-col>
		<v-col cols="12" sm="6" class="mt-md-2 pt-md-3">
			<v-checkbox :label="$t('options.customFontNames')" v-model="store.options.customNames" />
		</v-col>
		<template v-if="store.options.customNames">
			<v-col cols="12" sm="6" class="mt-2">
				<v-text-field :label="$t('options.fontFamily')" :placeholder="$t('options.fontFamilyPlaceholder')"
					v-model="store.options.family" />
			</v-col>
			<v-col cols="12" sm="6" class="mt-2">
				<v-select :label="$t('options.fontSubfamily')" v-model="store.options.subfamily" :items="subfamilies">
					<template v-slot:prepend-inner>
						<Tip :title="$t('options.subfamilyTip')" />
					</template>
				</v-select>
			</v-col>
			<v-col cols="12" sm="6" class="mt-2">
				<v-text-field :label="$t('options.typographicFamily')" v-model="store.options.typo_family" />
			</v-col>
			<v-col cols="12" sm="6" class="mt-2">
				<v-text-field :label="$t('options.typographicSubfamily')" v-model="store.options.typo_subfamily"
					:placeholder="store.options.subfamily">
					<template v-slot:prepend-inner>
						<Tip :title="$t('options.typoSubfamilyTip')" />
					</template>
				</v-text-field>
			</v-col>
		</template>
		<v-col cols="12" sm="6" class="mt-2">
			<v-select :label="$t('options.outputFormat')" :items="formats" v-model="store.options.format" />
		</v-col>
		<v-col cols="12" sm="6" class="mt-2">
			<v-text-field :label="$t('options.targetFeature')" v-model="store.options.target" :placeholder="$t('options.targetPlaceholder')">
				<template v-slot:prepend-inner>
					<Tip :title="$t('options.targetTip')" />
				</template>
			</v-text-field>
		</v-col>
		<v-col cols="12" md="6" class="mt-2">
			<v-checkbox class="my-n3 my-md-0" :label="$t('options.singleSub')"
				v-model="store.options.singleSub" />
		</v-col>
		<v-col cols="12" md="6" class="mt-2">
			<v-checkbox class="my-n3 my-md-0" :label="$t('options.fixContour')" v-model="store.options.fixContour" />
		</v-col>
	</v-row>
</template>

<script setup lang="ts">
	import { computed } from "vue";
	import { useI18n } from "vue-i18n";

	import { store } from "../store";
	import Tip from "./components/tip.vue";

	const { t } = useI18n();

	const formats = computed(() => [
		{
			title: t("options.formatTtf"),
			value: "ttf",
		},
		{
			title: t("options.formatWoff2"),
			value: "woff2",
		},
	]);

	const subfamilies = computed(() => [
		{
			title: t("options.subfamilyRegular"),
			value: "Regular",
		},
		{
			title: t("options.subfamilyBold"),
			value: "Bold",
		},
		{
			title: t("options.subfamilyItalic"),
			value: "Italic",
		},
		{
			title: t("options.subfamilyBoldItalic"),
			value: "Bold Italic",
		},
	]);
</script>
