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
		const parts: string[] = [];
		for(const tag in store.features) {
			const v = store.features[tag];
			if(typeof v === "number") parts.push(`${tag}=${v}`);
		}
		input.value = parts.join(",");
		errorMsg.value = "";
		show.value = true;
	}
</script>

<script setup lang="ts">
	import { shallowRef } from "vue";
	import { useI18n } from "vue-i18n";

	import { store } from "../../store";

	const { t } = useI18n();

	// Matches "tag = digits" with arbitrary surrounding whitespace.
	// Tag must be exactly 4 chars (the OpenType layout-tag length).
	const ITEM_RE = /^\s*([A-Za-z0-9]{4})\s*=\s*(-?\d+)\s*$/;
	// Catches the shape "something = something" without enforcing tag/digit rules,
	// so we can tell "wrong overall format" apart from "wrong tag/value".
	const SHAPE_RE = /^\s*[^=,\s]+\s*=\s*[^=,]*\s*$/;

	interface ParseResult {
		parsed: Record<string, number>;
		malformed: string[];
		unknownTags: string[];
		badValues: string[];
	}

	function parseEntries(text: string, validTags: Set<string>): ParseResult {
		const result: ParseResult = { parsed: {}, malformed: [], unknownTags: [], badValues: [] };
		if(text.length === 0) return result;
		for(const piece of text.split(",")) {
			const raw = piece.trim();
			if(!raw) continue;
			if(!SHAPE_RE.test(raw)) {
				result.malformed.push(raw);
				continue;
			}
			const m = raw.match(ITEM_RE);
			if(!m) {
				// Shape is "x=y" but the tag isn't 4 chars or value isn't pure digits.
				const eq = raw.indexOf("=");
				const tagPart = raw.slice(0, eq).trim();
				const valPart = raw.slice(eq + 1).trim();
				if(!/^[A-Za-z0-9]{4}$/.test(tagPart)) result.unknownTags.push(tagPart);
				else result.badValues.push(valPart);
				continue;
			}
			const tag = m[1];
			const value = parseInt(m[2], 10);
			if(!validTags.has(tag)) result.unknownTags.push(tag);
			else if(value < 0) result.badValues.push(m[2]);
			else result.parsed[tag] = value;
		}
		return result;
	}

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
		const result = parseEntries(input.value.trim(), validTags);
		const errMsg = buildErrorMessage(result);
		if(errMsg) {
			errorMsg.value = errMsg;
			return;
		}
		// Tags removed from the dialog fall back to plain "enabled" (boolean true)
		// so the regular checkbox tri-state resumes for them.
		for(const tag in store.features) {
			if(typeof store.features[tag] === "number" && !(tag in result.parsed)) {
				store.features[tag] = true;
			}
		}
		for(const tag in result.parsed) {
			store.features[tag] = result.parsed[tag];
		}
		errorMsg.value = "";
		show.value = false;
	}
</script>
