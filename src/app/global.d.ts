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
	gsub: string[];
	fileName: string;
	fileSize: string;
	readonly family: string;
	readonly subfamily: string;
	readonly typo_family: string;
	readonly typo_subfamily: string;
	preview: boolean;
	previewUrl: string;
	fvar: null | {
		axes: Axis[];
	}
}

interface Axis {
	tag: string;
	default: number;
}
