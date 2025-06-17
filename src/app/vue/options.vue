<template>
	<h5 class="text-h5 mt-4">Output options</h5>
	<v-row align="baseline">
		<v-col cols="12" sm="6" class="mt-2">
			<v-text-field label="Font family suffix" v-model="store.options.suffix">
				<template v-slot:prepend-inner>
					<Tip
						 title="Will be added after all family names. Default value is 'Freeze', suggesting that the font is generated with FontFreeze." />
				</template>
			</v-text-field>
		</v-col>
		<v-col cols="12" sm="6" class="mt-md-2 pt-md-3">
			<v-checkbox label="Custom font names" v-model="store.options.customNames" />
		</v-col>
		<template v-if="store.options.customNames">
			<v-col cols="12" sm="6" class="mt-2">
				<v-text-field label="Font family" placeholder="Better be different from the original family name"
							  v-model="store.options.family" />
			</v-col>
			<v-col cols="12" sm="6" class="mt-2">
				<v-select label="Font subfamily" v-model="store.options.subfamily" :items="subfamilies">
					<template v-slot:prepend-inner>
						<Tip title="This can only be one of the four values." />
					</template>
				</v-select>
			</v-col>
			<v-col cols="12" sm="6" class="mt-2">
				<v-text-field label="Typographic family" v-model="store.options.typo_family" />
			</v-col>
			<v-col cols="12" sm="6" class="mt-2">
				<v-text-field label="Typographic subfamily" v-model="store.options.typo_subfamily"
							  :placeholder="store.options.subfamily">
					<template v-slot:prepend-inner>
						<Tip title="'Light', 'SemiBold' etc. Leave it blank to use the same setting as subfamily." />
					</template>
				</v-text-field>
			</v-col>
		</template>
		<v-col cols="12" sm="6" class="mt-2">
			<v-select label="Output format" :items="formats" v-model="store.options.format" />
		</v-col>
		<v-col cols="12" sm="6" class="mt-2">
			<v-text-field label="Target feature for activation" v-model="store.options.target" placeholder="Try 'calt' or 'rvrn'">
				<template v-slot:prepend-inner>
					<Tip title="Set this to 'calt' will usually do. Try 'rvrn' if the former doesn't work." />
				</template>
			</v-text-field>
		</v-col>
		<v-col cols="12" md="6" class="mt-2">
			<v-checkbox class="my-n3 my-md-0" label="Apply substitution by single-glyph features." v-model="store.options.singleSub" />
		</v-col>
		<v-col cols="12" md="6" class="mt-2">
			<v-checkbox class="my-n3 my-md-0" label="Fix contour overlap issues on macOS." v-model="store.options.fixContour" />
		</v-col>
	</v-row>
</template>

<script setup lang="ts">
	import { store } from "../store";
	import Tip from "./components/tip.vue";

	const formats = [
		{
			title: "TTF (TrueType Font)",
			value: "ttf",
		},
		{
			title: "WOFF2 (Web Open Font Format v2)",
			value: "woff2",
		},
	];

	const subfamilies = [
		{
			title: "Regular",
			value: "Regular",
		},
		{
			title: "Bold",
			value: "Bold",
		},
		{
			title: "Italic",
			value: "Italic",
		},
		{
			title: "Bold Italic",
			value: "Bold Italic",
		},
	];
</script>
