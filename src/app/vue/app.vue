<template>
	<v-app>
		<Dropzone/>
		<Alert/>
		<v-container style="max-width: 1200px;">
			<v-row class="justify-end mb-3 align-center">
				<v-col>
					<v-btn color="secondary" size="small" :href="$t('app.userManualUrl')">📜 {{ $t("app.userManual") }}</v-btn>
				</v-col>
				<v-col>
					<v-btn color="secondary" size="small" href="https://github.com/MuTsunTsai/fontfreeze/issues">🐛 {{ $t("app.reportIssue") }}</v-btn>
				</v-col>
				<v-col>
					<v-menu>
						<template #activator="{ props }">
							<v-btn
								color="secondary"
								size="small"
								v-bind="props"
								append-icon="mdi-menu-down"
								style="font-family: Flag;"
							>
								{{ $t("emoji") }}&ensp;{{ currentLocaleName }}
							</v-btn>
						</template>
						<v-list density="compact">
							<v-list-item
								v-for="item in localeOptions"
								:key="item.value"
								:active="locale === item.value"
								@click="locale = item.value"
							>
								<v-list-item-title>{{ item.title }}</v-list-item-title>
							</v-list-item>
						</v-list>
					</v-menu>
				</v-col>
			</v-row>
			<v-card elevation="3">
				<Header/>
				<Main/>
				<Local/>
			</v-card>
			<v-row class="justify-center mt-3">
				<v-col>
					<a href="https://www.buymeacoffee.com/mutsuntsai" target="_blank"><img
						width="235"
						height="50"
						src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=☕&slug=mutsuntsai&button_colour=6f431f&font_colour=ffffff&font_family=Lato&outline_colour=ffffff&coffee_colour=FFDD00"
					></a>
				</v-col>
				<v-col>
					<!-- Product Hunt -->
					<a
						href="https://www.producthunt.com/posts/fontfreeze?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-fontfreeze"
						target="_blank"
					><img
						class="product-hunt"
						style="width: 235px; height: 50px;"
						width="235"
						height="50"
					></a>
				</v-col>
			</v-row>
		</v-container>
	</v-app>
</template>

<script setup lang="ts">
	import { computed, watch } from "vue";
	import { useI18n } from "vue-i18n";

	import Header from "./header.vue";
	import Dropzone from "./dropzone.vue";
	import Main from "./main.vue";
	import Alert from "./modals/alert.vue";
	import Local from "./modals/local.vue";
	import i18n from "../i18n";

	const { locale } = useI18n();

	const localeOptions = [
		{ name: "English", value: "en" as const },
		{ name: "한국어", value: "ko" as const },
		{ name: "简体中文", value: "zh-CN" as const },
		{ name: "正體中文", value: "zh-TW" as const },
	].map(o => ({
		...o,
		title: i18n.global.messages.value[o.value].emoji + " " + o.name,
	}));

	const currentLocaleName = computed(() =>
		localeOptions.find(o => o.value === locale.value)?.name ?? "English"
	);

	watch(locale, v => localStorage.setItem("fontfreeze-locale", v));
</script>
