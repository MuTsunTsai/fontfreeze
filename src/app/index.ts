import { createApp } from "vue";
import { createVuetify } from "vuetify";

import App from "./vue/app.vue";

import "./style/main.scss";

const formElements = {
	color: "primary",
	hideDetails: true,
	variant: "outlined",
	density: "comfortable",
};

const preferenceMedia = window.matchMedia("(prefers-color-scheme: dark)");
preferenceMedia.addEventListener("change", e => {
	vuetify.theme.global.name.value = e.matches ? "dark" : "light";
});

const bootstrap = {
	primary: "#0d6efd",
	secondary: "#6c757d",
	success: "#198754",
	error: "#dc3545",
	warning: "#ffc107",
	info: "#0dcaf0",
};

const vuetify = createVuetify({
	display: {
		mobileBreakpoint: "sm",
	},
	theme: {
		defaultTheme: preferenceMedia.matches ? "dark" : "light",
		themes: {
			light: {
				colors: {
					...bootstrap,
					"surface-variant": "#ccc",
					"on-surface-variant": "#000",
				},
			},
			dark: {
				dark: true,
				colors: {
					...bootstrap,
					"surface": "#333",
					"surface-variant": "#444",
					"on-surface-variant": "#fff",
				},
			},
		},
	},
	defaults: {
		VCol: { cols: "auto" },
		VRow: { dense: true },
		VBtn: { class: "text-none" },
		VCheckbox: formElements,
		VSelect: formElements,
		VTextField: formElements,
		VNumberInput: formElements,
		VSlider: formElements,
		VTooltip: { location: "top" },
		VList: { density: "compact" },
		VTable: { density: "compact" },
	},
});

// Initialize Vue
createApp(App).use(vuetify).mount("#app");
