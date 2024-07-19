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