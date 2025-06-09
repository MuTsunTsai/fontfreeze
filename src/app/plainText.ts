
/**
 * `plaintext-only` support detection.
 * @see https://stackoverflow.com/questions/10672081
 *
 * Note that this feature is now Baseline 2025.
 * @see https://webstatus.dev/features/contenteditable-plaintextonly?q=baseline_date%3A2025-01-01..2025-12-31
 */
export function supportPlaintext(div: HTMLDivElement): boolean {
	try {
		const p = "plaintext-only";
		div.contentEditable = p;
		return div.contentEditable == p;
	} catch(e) {
		return false;
	}
}

const ENTER_CODE = 13;

/**
 * Fallback for browsers not supporting plaintext-only (i.e. Firefox < 136)
 * @see https://stackoverflow.com/questions/21205785
 */
export function setupPlaintext(div: HTMLDivElement): void {
	div.contentEditable = "true";
	div.addEventListener("keydown", e => {
		//override pressing enter in contenteditable
		if(e.keyCode == ENTER_CODE) {
			//don"t automatically put in divs
			e.preventDefault();
			e.stopPropagation();
			//insert newline
			insertTextAtSelection(div, "\n");
		}
	});
	div.addEventListener("paste", e => {
		//cancel paste
		e.preventDefault();
		//get plaintext from clipboard
		const text = (e.originalEvent || e).clipboardData!.getData("text/plain");
		//insert text manually
		insertTextAtSelection(div, text);
	});
}

function insertTextAtSelection(div: HTMLDivElement, txt: string): void {
	//get selection area so we can position insert
	const sel = window.getSelection()!;
	const text = div.textContent!;
	const before = Math.min(sel.focusOffset, sel.anchorOffset);
	const after = Math.max(sel.focusOffset, sel.anchorOffset);
	//ensure string ends with \n so it displays properly
	let afterStr = text.substring(after);
	if(afterStr == "") afterStr = "\n";
	//insert content
	div.textContent = text.substring(0, before) + txt + afterStr;
	//restore cursor at correct position
	sel.removeAllRanges();
	const range = document.createRange();
	//childNodes[0] should be all the text
	range.setStart(div.childNodes[0], before + txt.length);
	range.setEnd(div.childNodes[0], before + txt.length);
	sel.addRange(range);
}
