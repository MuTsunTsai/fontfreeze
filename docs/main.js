const { reactive, createApp, nextTick } = PetiteVue;

let pyodide;

async function init() {
	const [py, script] = await Promise.all([
		loadPyodide().then(async p => {
			await p.loadPackage('fonttools');
			return p;
		}),
		fetchText("main.py"),
	]);
	pyodide = py;
	pyodide.runPython(script);
}

const initialized = init();

const style = document.createElement("style");
document.head.appendChild(style);

let lastValues;
const store = reactive({
	font: null,
	sample: "",
	previewSize: 12,
	running: false,
	message: null,
	previewIndex: 0,
});
fetchText("sample.md").then(t => store.sample = t)

addEventListener('DOMContentLoaded', () => createApp({
	store,
	get previewStyle() {
		if(!store.font) return null;
		const feat = store.font.gsub
			.filter(g => store.features[g] !== false)
			.map(g => `'${g}' ${store.features[g] ? "on" : "off"}`)
			.join(',');
		const vari = !store.font.fvar ? "normal" :
			store.font.fvar.axes
				.map(a => `'${a.tag}' ${store.variations[a.tag]}`)
				.join(',');
		return `
			white-space: pre-line;
			font-family: preview${store.previewIndex};
			font-feature-settings: ${feat};
			font-variation-settings: ${vari};
			font-size: ${store.previewSize}pt;`;
	},
	// The next two getter are for dealing with a bug in petite-vue 0.4.1
	// that v-for expression is calculated one more time as the upper v-if condition becoming false
	get instances() {
		if(!store.font || !store.font.fvar) return [];
		return store.font.fvar.instances;
	},
	get axes() {
		if(!store.font || !store.font.fvar) return [];
		return store.font.fvar.axes;
	},
	getAxisName(axis) {
		return axis.name ? axis.name :
			axis.tag in axisNames ? axisNames[axis.tag] : axis.tag;
	},
	setInstance(instance) {
		for(let t in instance.coordinates) {
			store.variations[t] = instance.coordinates[t];
		}
	},
	getStep(axis) {
		const range = axis.max - axis.min;
		if(range > 20) return 1;
		if(range > 1) return 0.1;
		return 0.01;
	},
	clear() {
		const selectElement = document.getElementsByTagName('select')[0];
		if(selectElement) selectElement.value = "";
	},
	checkboxChange(f) {
		if(lastValues[f] === true) store.features[f] = undefined;
		if(lastValues[f] === undefined) store.features[f] = false;
		lastValues[f] = store.features[f];
	},
}).mount());

// Features that should not be exposed to the users
const hiddenFeatures = [
	'abvm', 'abvs', 'akhn', 'blwf', 'blwm', 'blws', 'ccmp', 'cfar', 'cjct', 'curs',
	'dist', 'dtls', 'fin2', 'fin3', 'fina', 'flac', 'half', 'haln', 'init', 'isol',
	'ljmo', 'locl', 'ltra', 'ltrm', 'mark', 'med2', 'medi', 'mkmk', 'nukt', 'pref',
	'pres', 'pstf', 'psts', 'rclt', 'rkrf', 'rlig', 'rphf', 'rtla', 'rtlm', 'rvrn',
	'ssty', 'stch', 'tjmo', 'vjmo', 'DELT' // last one is special value
];

const axisNames = {
	"ital": "Italic",
	"opsz": "Optical size",
	"slnt": "Slant",
	"wdth": "Width",
	"wght": "Weight",
};

async function generate() {
	if(store.message) return; // button not ready
	gtag('event', 'save_ttf');
	try {
		if('showSaveFilePicker' in window) {
			store.message = null;
			const handle = await showSaveFilePicker({
				suggestedName: suggestedFileName(),
				types: [{
					description: "TTF font",
					accept: { "font/ttf": ".ttf" },
				}],
			});
			await startAnime();
			const writable = await handle.createWritable();
			await writable.write(getBlob());
			await writable.close();
			store.message = "Generating complete!";
			setTimeout(() => store.message = null, 3000);
		} else {
			await startAnime();
			store.download = suggestedFileName();
			const blob = getBlob();
			if(store.url) URL.revokeObjectURL(store.url);
			store.url = URL.createObjectURL(blob);
		}
	} catch(e) {
		console.log(e);
	}
	store.running = false;
}

function startAnime() {
	const anime = new Promise(resolve => {
		window.addEventListener('animationstart', resolve, { once: true });
	});
	store.running = true;
	return anime;
}

function suggestedFileName() {
	return store.font.fileName.replace(/\.[ot]tf$/i, "_freeze.ttf");
}

function getBlob() {
	try {
		const args = {
			options: store.options,
			variations: store.variations,
			features: store.font.gsub.filter(g => store.features[g] === true),
			disables: store.font.gsub.filter(g => store.features[g] === undefined),
		};
		pyodide.globals.get("processFont")(args);
	} catch(e) {
		alert("An error occur: " + e.message);
		throw e;
	}
	const content = pyodide.FS.readFile('output.ttf');
	return new Blob([content], { type: "font/ttf" });
}

async function openFile(input) {
	gtag('event', 'open_ttf');
	await initialized;
	const file = input.files[0];
	if(!file) return;
	input.value = ""; // clear field
	const buffer = await readFile(file);
	const array = new Uint8Array(buffer);
	pyodide.FS.writeFile('input.ttf', array);
	try {
		const info = pyodide.runPython("loadFont()")
			.toJs({ dict_converter: Object.fromEntries });
		setPreviewFont(file);
		console.log(JSON.parse(JSON.stringify(info)));
		info.fileName = file.name;
		info.fileSize = getFileSize(file);
		info.gsub = info.gsub.filter(g => !hiddenFeatures.includes(g));
		store.features = {};
		lastValues = {};
		store.variations = {};
		store.options = {
			family: info.family + " Freeze",
			subfamily: "Regular",
			fixContour: false,
			target: "calt",
		};
		for(let g of info.gsub) store.features[g] = lastValues[g] = false;
		if(info.fvar) {
			for(let a of info.fvar.axes) store.variations[a.tag] = a.default;
		}
		store.font = info;
	} catch(e) {
		alert(`"${file.name}" is not a valid font file.`);
	}
}

let fontURL;

function setPreviewFont(file) {
	if(fontURL) URL.revokeObjectURL(fontURL);
	fontURL = URL.createObjectURL(file);
	style.sheet.insertRule(`@font-face {
		font-family: preview${++store.previewIndex};
		src: url('${fontURL}')
	}`);
}

function getFileSize(file) {
	let size = file.size;
	if(size < 1024) return size + "B"; else size /= 1024;
	if(size < 1024) return size.toFixed(1) + "KB"; else size /= 1024;
	return size.toFixed(1) + "MB";
}

function fetchText(url) {
	return fetch(url).then(r => r.text());
}

function readFile(file) {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.onload = e => resolve(e.target.result);
		reader.onerror = e => {
			alert('Fail to open file: ' + e.message);
			reject(e);
		};
		reader.readAsArrayBuffer(file);
	});
}
