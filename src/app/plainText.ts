
// plaintext-only support detection
// https://stackoverflow.com/questions/10672081
export function supportPlaintext(div: HTMLDivElement) {
	try {
		const p = "plaintext-only";
		div.contentEditable = p;
		return div.contentEditable == p;
	} catch(e) {
		return false;
	}
}

// Fallback for browsers not supporting plaintext-only (i.e. Firefox)
// https://stackoverflow.com/questions/21205785
export function setupPlaintext(div: HTMLDivElement) {
	div.contentEditable = "true";
	div.addEventListener("keydown", e => {
		//override pressing enter in contenteditable
		if(e.keyCode == 13) {
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
		let text = (e.originalEvent || e).clipboardData!.getData("text/plain");
		//insert text manually
		insertTextAtSelection(div, text);
	});
}

function insertTextAtSelection(div: HTMLDivElement, txt: string) {
	//get selection area so we can position insert
	let sel = window.getSelection()!;
	let text = div.textContent!;
	let before = Math.min(sel.focusOffset, sel.anchorOffset);
	let after = Math.max(sel.focusOffset, sel.anchorOffset);
	//ensure string ends with \n so it displays properly
	let afterStr = text.substring(after);
	if(afterStr == "") afterStr = "\n";
	//insert content
	div.textContent = text.substring(0, before) + txt + afterStr;
	//restore cursor at correct position
	sel.removeAllRanges();
	let range = document.createRange();
	//childNodes[0] should be all the text
	range.setStart(div.childNodes[0], before + txt.length);
	range.setEnd(div.childNodes[0], before + txt.length);
	sel.addRange(range);
}
