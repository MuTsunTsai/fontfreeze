declare module "*.vue" {
	import type { DefineComponent } from "vue";

	const component: DefineComponent<object, object, unknown>;
	export default component;
}

declare module "*.scss" {
	const styles: object;
	export default styles;
}

declare module "*.css" {
	const styles: object;
	export default styles;
}
