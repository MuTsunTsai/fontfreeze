<template>
	<v-dialog v-model="show" max-width="500">
		<v-card>
			<v-card-title class="pt-3">
				<span class="text-headline-small">{{ $t("features.customDialog.title") }}</span>
			</v-card-title>
			<v-card-text class="py-2">
				<div class="text-body-medium mb-2">{{ $t("features.customDialog.hint") }}</div>
				<v-text-field
					v-model="input"
					placeholder="cv01=2,ss02=3"
					autofocus
					:error-messages="errorMsg"
					hide-details="auto"
					@keydown.enter="confirm"
				/>
			</v-card-text>
			<v-card-actions>
				<v-btn color="secondary" @click="show = false">{{ $t("features.customDialog.cancel") }}</v-btn>
				<v-btn color="primary" @click="confirm">{{ $t("features.customDialog.ok") }}</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script lang="ts">
	const show = shallowRef(false);
	const input = shallowRef("");
	const errorMsg = shallowRef("");

	export function showCustomFeatures(): void {
		// Build the initial string from existing custom values in the store.
		input.value = formatCustomValues(store.features);
		errorMsg.value = "";
		show.value = true;
	}
</script>

<script setup lang="ts">
	import { shallowRef } from "vue";
	import { useI18n } from "vue-i18n";

	import { store } from "../../store";
	import { applyCustomValues, formatCustomValues, parseCustomValues } from "../../features";

	import type { ParseResult } from "../../features";

	const { t } = useI18n();

	function buildErrorMessage(r: ParseResult): string {
		const errors: string[] = [];
		if(r.malformed.length > 0) {
			errors.push(t("features.customDialog.errMalformed", { items: r.malformed.join(", ") }));
		}
		if(r.unknownTags.length > 0) {
			errors.push(t("features.customDialog.errUnknownTag", { items: r.unknownTags.join(", ") }));
		}
		if(r.badValues.length > 0) {
			errors.push(t("features.customDialog.errBadValue", { items: r.badValues.join(", ") }));
		}
		return errors.join(" ");
	}

	function confirm(): void {
		if(!store.font) return;
		const validTags = new Set(store.font.gsub);
		const result = parseCustomValues(input.value, validTags);
		const errMsg = buildErrorMessage(result);
		if(errMsg) {
			errorMsg.value = errMsg;
			return;
		}
		applyCustomValues(store.features, result.parsed);
		errorMsg.value = "";
		show.value = false;
	}
</script>
