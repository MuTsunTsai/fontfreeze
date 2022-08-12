const { reactive, createApp, nextTick } = PetiteVue;

const worker = new Worker("worker.js");
const initialized = new Promise(resolve => {
	worker.addEventListener('message', e => {
		if(e.data == "initialized") resolve();
	}, { once: true });
});

function callWorker(command, data) {
	return new Promise((resolve, reject) => {
		const channel = new MessageChannel();
		worker.postMessage([command, data], [channel.port2]);
		channel.port1.onmessage = e => {
			const { success, data } = e.data;
			if(success) resolve(data);
			else reject(new Error(data));
		};
	});
}

const style = document.createElement("style");
document.head.appendChild(style);

let lastValues;
const store = reactive({
	localFontSupport: 'queryLocalFonts' in window,
	localFonts: [],
	localFont: "",
	unavailableFonts: [],
	loading: null,
	font: null,
	sample: "",
	removeGlyphs: "",
	previewSize: 12,
	running: false,
	message: null,
	previewIndex: 0,
});

fetch("sample.md")
	.then(r => r.text())
	.then(t => store.sample = t);

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
	get more() {
		const f = store.font;
		if(!f) return false;
		return f.description || f.designer || f.manufacturer || f.copyright || f.trademark;
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
	info() {
		bootstrap.Modal.getOrCreateInstance("#info").show();
	},
	setUnicodeRange() {
		style.sheet.cssRules[0].style.unicodeRange = getUnicodes();
	}
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

const formats = {
	"ttf": {
		description: "TTF font",
		accept: { "font/ttf": ".ttf" },
	},
	"woff2": {
		description: "WOFF2 font",
		accept: { "font/woff2": ".woff2" },
	}
}

async function generate() {
	if(store.message) return; // button not ready
	gtag('event', 'save_' + store.options.format);
	try {
		if('showSaveFilePicker' in window) {
			store.message = null;
			const handle = await showSaveFilePicker({
				suggestedName: suggestedFileName(),
				types: [formats[store.options.format]],
			});
			await startAnime();
			const url = await getOutputURL();
			const response = await fetch(url);
			const content = await response.arrayBuffer();
			const blob = new Blob([content], { type: "font/" + store.options.format });
			const writable = await handle.createWritable();
			await writable.write(blob);
			await writable.close();
			store.message = "Generating complete!";
			setTimeout(() => store.message = null, 3000);
		} else {
			await startAnime();
			store.url = await getOutputURL();
			store.download = suggestedFileName();
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
	const name = store.font.fileName.replace(/\.[a-z0-9]+$/i, "");
	return name + "_freeze." + store.options.format;
}

function clone(obj) {
	return JSON.parse(JSON.stringify(obj));
}

async function getOutputURL() {
	try {
		const args = {
			options: store.options,
			unicodes: getUnicodes(),
			variations: store.variations,
			features: store.font.gsub.filter(g => store.features[g] === true),
			disables: store.font.gsub.filter(g => store.features[g] === undefined),
		};
		return await callWorker('save', clone(args));
	} catch(e) {
		alert("An error occur: " + e.message);
		throw e;
	}
}

async function openFile(input) {
	gtag('event', 'open_ttf');
	const file = input.files[0];
	if(!file) return;
	input.value = ""; // clear field
	try {
		await openBlob(file, file.name);
	} catch(e) {
		console.log(e);
		alert(`"${file.name}" is not a valid font file.`);
	}
}

async function openBlob(blob, name) {


	store.loading = "packages";
	await initialized;
	store.loading = "font";

	const tempURL = URL.createObjectURL(blob);
	let info;
	try {
		info = await callWorker('open', tempURL);
	} catch(e) {
		URL.revokeObjectURL(tempURL);
		throw e;
	} finally {
		store.loading = null;
	}

	console.log(clone(info));
	setPreviewFont(tempURL);

	info.fileName = name;
	info.fileSize = getFileSize(blob);
	info.gsub = info.gsub.filter(g => !hiddenFeatures.includes(g));
	store.features = {};
	lastValues = {};
	store.variations = {};
	store.removeGlyphs = "";
	store.options = {
		family: info.family + " Freeze",
		subfamily: "Regular",
		fixContour: false,
		target: "calt",
		format: "ttf",
	};
	for(let g of info.gsub) store.features[g] = lastValues[g] = false;
	if(info.fvar) {
		for(let a of info.fvar.axes) store.variations[a.tag] = a.default;
	}
	store.font = info;
}

function getRemoveCharCodes() {
	const removes = [];
	for(let i = 0; i < store.removeGlyphs.length; i++) {
		removes.push(store.removeGlyphs.charCodeAt(i));
	}
	removes.sort();
	return removes;
}

function getUnicodes() {
	const removes = getRemoveCharCodes(), ranges = [[0, 0x10FFFF]];
	if(removes.length == 0) return "";
	for(let code of removes) {
		const range = ranges.find(r => r[0] <= code && code <= r[1]);
		if(!range) continue;
		const end = range[1];
		range[1] = code - 1;
		ranges.push([code + 1, end]);
	}
	return ranges
		.filter(r => r[0] <= r[1])
		.map(r => `U+${r[0].toString(16)}-${r[1].toString(16)}`)
		.join(',');
}

let fontURL;

function setPreviewFont(url) {
	if(fontURL) URL.revokeObjectURL(fontURL);
	fontURL = url;
	if(style.sheet.cssRules.length > 0) style.sheet.deleteRule(0);
	style.sheet.insertRule(`@font-face {
		font-family: preview${++store.previewIndex};
		src: url('${fontURL}');
	}`);
}

function getFileSize(blob) {
	let size = blob.size;
	if(size < 1024) return size + "B"; else size /= 1024;
	if(size < 1024) return size.toFixed(1) + "KiB"; else size /= 1024;
	return size.toFixed(1) + "MiB";
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

async function local() {
	await navigator.permissions.query({
		name: "local-fonts",
		description: ""
	});
	const fonts = await window.queryLocalFonts();
	if(fonts.length == 0) return; // permission denied
	store.localFonts = fonts;
	bootstrap.Modal.getOrCreateInstance("#local").show();
}

async function loadLocal() {
	const font = store.localFonts[store.localFont];
	let blob;
	try {
		blob = await font.blob();
	} catch(e) {
		alert("An error occur: " + e.message);
		store.unavailableFonts.push(font.postscriptName);
		return;
	} finally {
		store.localFont = "";
	}
	bootstrap.Modal.getOrCreateInstance("#local").hide();
	try {
		await openBlob(blob, font.fullName);
	} catch(e) {
		alert("An error occur: " + e.message);
	}
}
