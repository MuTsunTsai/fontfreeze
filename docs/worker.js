
importScripts("https://cdn.jsdelivr.net/pyodide/v0.21.0/full/pyodide.js");

let pyodide;

async function initPyodide() {
	pyodide = await loadPyodide();
	await pyodide.loadPackage('brotli');
	await pyodide.loadPackage('fonttools');
}

async function init() {
	const [_, script] = await Promise.all([
		initPyodide(),
		fetch("main.py").then(r => r.text())
	]);
	pyodide.runPython(script);
	postMessage("initialized");
}

init();

addEventListener('message', async event => {
	if(!event.ports[0]) return;
	try {
		const [command, data] = event.data;
		let result;
		if(command == "open") result = await open(data);
		if(command == "save") result = save(data);
		event.ports[0].postMessage({
			success: true,
			data: result
		});
	} catch(err) {
		event.ports[0].postMessage({
			success: false,
			data: err.message
		});
	}
});

async function open(url) {
	const response = await fetch(url);
	const buffer = await response.arrayBuffer();
	const array = new Uint8Array(buffer);
	pyodide.FS.writeFile('temp', array);
	const info = pyodide.runPython("loadFont()")
		.toJs({ dict_converter: Object.fromEntries });
	return info;
}

let saveURL;

function save(args) {
	pyodide.globals.get("processFont")(args);
	const content = pyodide.FS.readFile('output');
	const blob = new Blob([content], { type: "font/" + args.options.format });
	if(saveURL) URL.revokeObjectURL(saveURL);
	saveURL = URL.createObjectURL(blob);
	return saveURL;
}