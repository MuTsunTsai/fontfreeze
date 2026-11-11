import type { SupportedFormats } from "./meta/constants";

const MS_CHAR_LIMIT = 32; // There's a 32-char limit in MS Word

interface Names {
	family: string;
	typo_family: string;
	suffix: string;
	customNames: boolean;
}

/** Appends the suffix to the family names, unless the names are customized. */
export function applySuffix<T extends Names>(options: T): T {
	const result = { ...options };
	if(result.customNames || !result.suffix) return result;
	// The family name is left alone if it would be too long.
	if(result.family && result.family.length + result.suffix.length < MS_CHAR_LIMIT) {
		result.family += " " + result.suffix;
	}
	if(result.typo_family) result.typo_family += " " + result.suffix;
	return result;
}

/** The suggested name of the generated file, e.g. "Font-Regular_freeze.woff2". */
export function suggestedFileName(fileName: string, format: SupportedFormats): string {
	const name = fileName.replace(/\.[a-z0-9]+$/i, "");
	return name + "_freeze." + format;
}
