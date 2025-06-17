<template>
	<v-app>
		<Dropzone />
		<Alert />
		<v-container>
			<v-row justify="end" class="mb-3">
				<v-col>
					<v-btn color="secondary" size="small" href="https://github.com/MuTsunTsai/fontfreeze">📜 User manual</v-btn>
				</v-col>
				<v-col>
					<v-btn color="secondary" size="small" href="https://github.com/MuTsunTsai/fontfreeze/issues">🐛 Report issue</v-btn>
				</v-col>
			</v-row>
			<v-card elevation="3">
				<Header />
				<Main />
				<Local />
			</v-card>
			<v-row justify="center" class="mt-3">
				<v-col>
					<a href="https://www.buymeacoffee.com/mutsuntsai" target="_blank"><img width="235" height="50"
							 src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=☕&slug=mutsuntsai&button_colour=6f431f&font_colour=ffffff&font_family=Lato&outline_colour=ffffff&coffee_colour=FFDD00" /></a>
				</v-col>
				<v-col>
					<!-- Product Hunt -->
					<a href="https://www.producthunt.com/posts/fontfreeze?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-fontfreeze"
					   target="_blank"><img class="product-hunt" style="width: 235px; height: 50px;" width="235"
							 height="50" /></a>
				</v-col>
			</v-row>
		</v-container>
	</v-app>
</template>

<script setup lang="ts">
	import Header from "./header.vue";
	import Dropzone from "./dropzone.vue";
	import Main from "./main.vue";
	import Alert from "./modals/alert.vue";
	import Local from "./modals/local.vue";
</script>
