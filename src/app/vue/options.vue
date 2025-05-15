<template>
	<h5>Output options</h5>
	<div class="row">
		<div class="col-12 col-md-6 mt-2">
			<label>
				Font family suffix
				<Tip title="Will be added after all family names. Default value is 'Freeze', suggesting that the font is generated with FontFreeze." />
			</label>
			<input class="form-control" v-model="store.options.suffix">
		</div>
		<div class="col-12 col-md-6 mt-md-2 pt-md-3">
			<div class="form-check mt-3">
				<input type="checkbox" class="form-check-input" id="chkContour" v-model="store.options.customNames">
				<label class="form-check-label" for="chkContour">Custom font names</label>
			</div>
		</div>
		<template v-if="store.options.customNames">
			<div class="col-12 col-md-6 mt-2">
				<label>Font family</label>
				<input class="form-control" v-model="store.options.family"
					   placeholder="Better be different from the original family name">
			</div>
			<div class="col-12 col-md-6 mt-2">
				<label>
					Font subfamily
					<Tip title="This can only be one of the four values." />
				</label>
				<select class="form-select" v-model="store.options.subfamily">
					<option value="Regular">Regular</option>
					<option value="Bold">Bold</option>
					<option value="Italic">Italic</option>
					<option value="Bold Italic">Bold Italic</option>
				</select>
			</div>
			<div class="col-12 col-md-6 mt-2">
				<label>Typographic family</label>
				<input class="form-control" v-model="store.options.typo_family">
			</div>
			<div class="col-12 col-md-6 mt-2">
				<label>
					Typographic subfamily
					<Tip title="'Light', 'SemiBold' etc. Leave it blank to use the same setting as subfamily." />
				</label>
				<input class="form-control" v-model="store.options.typo_subfamily" :placeholder="store.options.subfamily">
			</div>
		</template>
		<div class="col-12 col-md-6 mt-2">
			<label>Output format</label>
			<select class="form-select" v-model="store.options.format">
				<option value="ttf">TTF</option>
				<option value="woff2">WOFF2</option>
			</select>
		</div>
		<div class="col-12 col-md-6 mt-2">
			<label>Target feature for activation</label>
			<input class="form-control" v-model="store.options.target" placeholder="Try 'calt' or 'rvrn'">
		</div>
		<div class="col-12 col-md-6 mt-2">
			<div class="form-check mt-3">
				<input type="checkbox" class="form-check-input" id="chkSub" v-model="store.options.singleSub">
				<label class="form-check-label" for="chkSub">Apply substitution by single-glyph features.</label>
			</div>
		</div>
		<div class="col-12 col-md-6 mt-md-2">
			<div class="form-check mt-3">
				<input type="checkbox" class="form-check-input" id="chkContour" v-model="store.options.fixContour">
				<label class="form-check-label" for="chkContour">Fix contour overlap issues on macOS.</label>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
	import { store } from "../store";
	import Tip from "./components/tip.vue";
</script>
