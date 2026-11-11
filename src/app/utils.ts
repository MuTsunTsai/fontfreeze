
export function clone<T>(obj: T): T {
	return JSON.parse(JSON.stringify(obj));
}

const KB = 1024;

/** Formats a file size, e.g. "1.5MiB". */
export function getFileSize(size: number): string {
	if(size < KB) return size + "B"; else size /= KB;
	if(size < KB) return size.toFixed(1) + "KiB"; else size /= KB;
	return size.toFixed(1) + "MiB";
}
