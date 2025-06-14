
declare const VERSION: string;

interface FontData {
	readonly family: string;
	readonly fullName: string;
	readonly postscriptName: string;
	readonly style: string;
	blob(): Promise<Blob>;
}

interface Window {
	queryLocalFonts(): Promise<FontData[]>;
}

interface ClipboardEvent {
	originalEvent?: ClipboardEvent;
}

interface FontInfo {
	gsub: readonly string[];
	fileName: string;
	fileSize: string;
	readonly version: string;
	readonly description?: string;
	readonly designer?: string;
	readonly designerURL?: string;
	readonly manufacturer?: string;
	readonly vendorURL?: string;
	readonly copyright?: string;
	readonly trademark?: string;
	readonly license?: string;
	readonly family: string;
	readonly subfamily: string;
	readonly typo_family: string;
	readonly typo_subfamily: string;
	preview: boolean;
	previewUrl: string;
	readonly fvar: null | {
		axes: Axis[];
		instances: FontInstance[];
	};
	readonly fontHeight: number;
	readonly lineHeight: number;
}

interface Axis {
	name?: string;
	tag: string;
	default: number;
	max: number;
	min: number;
}

interface FontInstance {
	name: string;
	coordinates: Record<string, number>;
}

/** Allowing bundling raw contents as strings. */
declare module "*?raw" {
	declare const content: string;
	export default content;
}
