import { createI18n } from "vue-i18n";
import { probablyChina } from "probably-china";

import en from "../locale/en.json";
import zhTW from "../locale/zh-TW.json";
import zhCN from "../locale/zh-CN.json";
import ko from "../locale/ko.json";

// Replace the flag to avoid unnecessary trouble.
if(probablyChina) zhTW.emoji = "🇭🇰";

const LOCALE_KEY = "fontfreeze-locale";
const supportedLocales = ["en", "zh-TW", "zh-CN", "ko"];

function detectLocale(): string {
	const saved = localStorage.getItem(LOCALE_KEY);
	if(saved && supportedLocales.includes(saved)) return saved;
	const lang = navigator.language;
	if(lang.startsWith("zh")) {
		return lang.includes("TW") || lang.includes("HK") ? "zh-TW" : "zh-CN";
	}
	if(lang.startsWith("ko")) return "ko";
	return "en";
}

const i18n = createI18n({
	legacy: false,
	locale: detectLocale(),
	fallbackLocale: "en",
	messages: {
		en,
		"zh-TW": zhTW,
		"zh-CN": zhCN,
		ko,
	},
});

export default i18n;
