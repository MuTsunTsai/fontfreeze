"""Compares FontFreeze with its original Python version (before 2.0) on real fonts.

This is for catching regressions that the generated test fonts don't cover, for example
after updating fontoxide. It is not part of the automated tests, as it is slow and needs
fonts that cannot be committed.

	uv run parity.py [--filter TEXT] [--exclude TEXT] [FONT_OR_FOLDER ...]

The fonts default to test/fonts and samples/. The native CLI must be built first:

	cd src/rust && cargo build --release --features cli

Each font is loaded, fixed as a legacy font, and generated with a set of options by both
versions. A case passes if the output is the same apart from the timestamps, or if the
differences are known (see KNOWN) and the shaping is right: the frozen font shapes text with
its default features as the original font does with the chosen features and variations.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CLI = REPO / "src/rust/target/release" / ("fontfreeze-cli.exe" if os.name == "nt" else "fontfreeze-cli")
OUT = HERE / "out"
CACHE = HERE / ".cache"

# The last commit with the Python version.
LEGACY_COMMIT = "532f75f~1"

FONT_EXTENSIONS = {".ttf", ".otf", ".ttc", ".otc"}

# The tables that differ by design since 2.0 (see CHANGELOG.md).
KNOWN = {
	# Removed features are always renamed to DELT, FeatureParams that don't fit are dropped,
	# and features are merged into the first target of each language system.
	"GSUB",
	# The description no longer mentions the fallback mode.
	"name",
	# advanceWidthMax over all glyphs.
	"hhea",
}

# Features that are on by default, so that features merged into them take effect.
DEFAULT_ON = {"calt", "rvrn", "liga", "ccmp", "locl", "rlig", "clig"}


#########################################################################################
# The Python version, run in a separate process for each call as it has global state
#########################################################################################


def legacy_module() -> Path:
	"""Extracts the original main.py from git."""
	path = CACHE / "main.py"
	if not path.exists():
		CACHE.mkdir(exist_ok=True)
		source = subprocess.run(
			["git", "show", f"{LEGACY_COMMIT}:src/python/main.py"],
			cwd=REPO,
			capture_output=True,
			check=True,
		).stdout
		path.write_bytes(source)
	return path


def run_reference(mode: str, *args: str) -> None:
	sys.path.insert(0, str(CACHE))
	import main as ff  # noqa: PLC0415

	# Use the repacker from the start, as fontoxide does.
	ff.enableRepacker()

	if mode == "load":
		src, out = map(os.path.abspath, args)
		os.chdir(tempfile.mkdtemp())
		shutil.copy(src, "temp")
		info = ff.loadFont("temp")
		info.setdefault("preview", False)
		print(json.dumps(info, ensure_ascii=False))
		if info["preview"]:
			shutil.copy("input", out)
	elif mode == "legacy":
		src, out = map(os.path.abspath, args)
		os.chdir(tempfile.mkdtemp())
		shutil.copy(src, "input")
		ff.processLegacy()
		shutil.copy("input", out)
	elif mode == "process":
		args_file, src, out = args
		with open(args_file, encoding="utf-8") as f:
			ff.main(json.load(f), src, out)


#########################################################################################
# Cases
#########################################################################################


def base_args(info: dict) -> dict:
	"""The arguments with the default options of the UI (see loader.ts)."""
	family = info["family"] or "X"
	return {
		"options": {
			"suffix": "Freeze",
			"family": family + " Freeze",
			"subfamily": "Regular",
			"typo_family": (info.get("typo_family") or family) + " Freeze",
			"typo_subfamily": "",
			"fixContour": False,
			"singleSub": True,
			"keepVar": False,
			"customNames": False,
			"target": "calt",
			"format": "ttf",
			"lineHeight": 0,
			"spacing": 0,
		},
		"version": " v2.0.0",
		"unicodes": "",
		"variations": {a["tag"]: a["default"] for a in (info["fvar"] or {"axes": []})["axes"]},
		"features": [],
		"featureValues": {},
		"disables": [],
	}


def make_cases(info: dict) -> dict[str, dict]:
	gsub = info["gsub"]
	ss = [g for g in gsub if g.startswith("ss")]
	cv = [g for g in gsub if g.startswith("cv")]
	other = [g for g in gsub if g in ("zero", "case", "onum", "dlig", "frac")]
	cases = {}

	def case(name: str, **changes) -> None:
		args = base_args(info)
		for k, v in changes.items():
			if k in args["options"]:
				args["options"][k] = v
			else:
				args[k] = v
		# Pyodide converted integral JavaScript numbers to int.
		args["variations"] = {k: int(v) if float(v).is_integer() else v for k, v in args["variations"].items()}
		cases[name] = args

	case("plain")
	if ss or cv or other:
		some = ss[:2] + cv[:2] + other[:2]
		case("activate", features=some)
		case("activate-nosingle", features=some, singleSub=False)
		case("activate-one", features=(ss[:1] or cv[:1] or other[:1]))
		if cv:
			case("value", features=cv[:2], featureValues={cv[0]: 2})
		case("target-ss20", features=(ss[:2] + cv[:1]), target="ss20")
	if gsub:
		disables = [g for g in gsub if g in ("liga", "calt")] + ss[:1] + cv[:1]
		case("disable", disables=disables)
		case("both", features=(ss[1:3] + cv[1:2]), disables=disables, subfamily="Bold", typo_subfamily="Medium")
	case("metrics", spacing=50, lineHeight=100, fixContour=True, subfamily="Bold Italic")
	case("metrics-odd", spacing=-33, lineHeight=-77)
	case("woff2", format="woff2")
	case("subset", unicodes="U+0020-007E,U+00A0-00FF,U+4E00-4E2F")
	if info["fvar"]:
		axes = info["fvar"]["axes"]
		case("instance", variations={a["tag"]: a["max"] for a in axes})
		case("instance-frac", variations={a["tag"]: (a["min"] + a["max"]) / 2 + 0.5 for a in axes})
		case("keepvar", keepVar=True)
	return cases


#########################################################################################
# Checks
#########################################################################################


def shaping_settings(args: dict) -> tuple[dict, dict] | None:
	"""The features and variations to shape the original font with, so that it should shape
	as the frozen font does with its defaults; None if the output is not comparable."""
	options = args["options"]
	if args["unicodes"] or options["spacing"] or options["format"] != "ttf" or options["keepVar"]:
		return None
	if args["features"] and options["target"] not in DEFAULT_ON:
		return None
	features = {f: args["featureValues"].get(f, 1) for f in args["features"]}
	features.update({f: 0 for f in args["disables"]})
	return features, args["variations"]


def shaping_texts(path: Path) -> list[str]:
	from fontTools.ttLib import TTFont

	with TTFont(path, fontNumber=0, lazy=True) as font:
		codepoints = sorted(font.getBestCmap() or {})
	texts = ["".join(chr(c) for c in codepoints[i : i + 64]) for i in range(0, len(codepoints), 64)]
	return texts + [
		"office fi ffl -> => != <= >= === www 0123456789 0x1F oO 1lI",
		"The quick brown fox jumps over the lazy dog.",
	]


def shape_all(path: Path, texts: list[str], features: dict | None = None, variations: dict | None = None):
	import uharfbuzz as hb

	font = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
	if variations:
		font.set_variations(variations)
	result = []
	for text in texts:
		buffer = hb.Buffer()
		buffer.add_str(text)
		buffer.guess_segment_properties()
		hb.shape(font, buffer, features or {})
		result.append([(p.x_advance, p.x_offset, p.y_offset) for p in buffer.glyph_positions])
	return result


def raw_tables(path: Path) -> dict[str, bytes]:
	from fontTools.ttLib import TTFont

	font = TTFont(path, lazy=True)
	tables = {tag: font.reader[tag] for tag in font.reader.keys()}
	if "head" in tables:
		# Ignore the timestamp and the checksum adjustment.
		head = bytearray(tables["head"])
		head[8:12] = bytes(4)
		head[28:36] = bytes(8)
		tables["head"] = bytes(head)
	return tables


def passes_ots(path: Path) -> bool:
	import ots

	return ots.sanitize(str(path), os.devnull, capture_output=True).returncode == 0


#########################################################################################


def run(command: list) -> subprocess.CompletedProcess:
	return subprocess.run([str(c) for c in command], capture_output=True, text=True, encoding="utf-8")


def reference(*args) -> subprocess.CompletedProcess:
	return run([sys.executable, __file__, "--reference", *args])


def json_from(stdout: str) -> dict:
	# The Python version prints other messages first.
	return json.loads(stdout[stdout.index("{") :])


def compare_case(name: str, src: Path, args: dict | None, texts: list[str]) -> tuple[bool, str]:
	"""Returns whether the case passes, and the report."""
	ext = ".woff2" if args and args["options"]["format"] == "woff2" else ".ttf"
	rs_out, py_out = OUT / f"{name}.rs{ext}", OUT / f"{name}.py{ext}"
	start = time.perf_counter()
	if args is None:
		rs = run([CLI, "legacy", src, rs_out])
		rs_time = time.perf_counter() - start
		py = reference("legacy", src, py_out)
	else:
		args_file = OUT / f"{name}.json"
		args_file.write_text(json.dumps(args, ensure_ascii=False), encoding="utf-8")
		rs = run([CLI, "process", args_file, src, rs_out])
		rs_time = time.perf_counter() - start
		py = reference("process", args_file, src, py_out)
	timing = f"(rs {rs_time:.2f}s, py {time.perf_counter() - start - rs_time:.2f}s)"

	if rs.returncode and py.returncode:
		return True, f"{name}: both fail {timing}\n    rs: {rs.stderr.strip()[-200:]}"
	if rs.returncode:
		return False, f"{name}: RUST FAILS {timing}\n    {rs.stderr.strip()[-300:]}"
	if py.returncode:
		return True, f"{name}: python fails, rust works {timing}"

	if rs_out.read_bytes() == py_out.read_bytes():
		return True, f"{name}: same {timing}"
	rs_tables, py_tables = raw_tables(rs_out), raw_tables(py_out)
	diffs = sorted(t for t in rs_tables.keys() | py_tables.keys() if rs_tables.get(t) != py_tables.get(t))
	if not diffs and list(rs_tables) == list(py_tables):
		return True, f"{name}: same except timestamp {timing}"

	problems = []
	if not diffs:
		problems.append(f"table order: rs={list(rs_tables)} py={list(py_tables)}")
	unknown = [t for t in diffs if t not in KNOWN]
	if unknown:
		problems.append(f"unexpected differences in {', '.join(unknown)}")
	if not passes_ots(rs_out) and passes_ots(py_out):
		problems.append("only the Rust output fails OTS")
	notes = []
	if ext == ".ttf":
		settings = shaping_settings(args) if args else ({}, {})
		rs_shaping, py_shaping = shape_all(rs_out, texts), shape_all(py_out, texts)
		if settings is not None and rs_shaping != shape_all(src, texts, *settings):
			if rs_shaping == py_shaping:
				# Freezing cannot be exact in some cases, for example:
				# - singleSub applies a substitution before all lookups, not in the lookup order;
				# - shapers treat some features specially (e.g. "frac");
				# - shapers hide default ignorables (e.g. soft hyphens) unless substituted by GSUB.
				notes.append("shaping differs from the features, but as in python (a known limit)")
			else:
				problems.append("shaping is wrong, and differs from python")
		elif settings is None and rs_shaping != py_shaping:
			problems.append("shaping differs from python")
	status = "CHECK" if problems else "ok"
	report = f"{name}: {status}, differs in {', '.join(diffs) or 'nothing'} {timing}"
	return not problems, report + "".join(f"\n    {p}" for p in problems + notes)


def collect_fonts(paths: list[str]) -> list[Path]:
	if not paths:
		paths = [str(REPO / "test/fonts"), str(REPO / "samples")]
	fonts = []
	for p in map(Path, paths):
		if p.is_dir():
			fonts += sorted(f for f in p.iterdir() if f.suffix.lower() in FONT_EXTENSIONS)
		elif p.exists():
			fonts.append(p)
	return fonts


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument("paths", nargs="*", help="fonts or folders of fonts")
	parser.add_argument("--filter", default="", help="only run the cases whose names contain this")
	parser.add_argument("--exclude", action="append", default=[], help="skip the cases whose names contain this")
	parser.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
	parser.add_argument("--reference", nargs="+", help=argparse.SUPPRESS)
	options = parser.parse_args()

	if options.reference:
		return run_reference(*options.reference)
	if not CLI.exists():
		sys.exit(f"{CLI} not found; run `cargo build --release --features cli` in src/rust first.")
	legacy_module()
	OUT.mkdir(exist_ok=True)

	def wanted(name: str) -> bool:
		return options.filter in name and not any(e in name for e in options.exclude)

	failures = 0
	jobs = []
	for src in collect_fonts(options.paths):
		stem = src.stem
		rs, py = run([CLI, "load", src, OUT / f"{stem}.load.rs.ttf"]), reference("load", src, OUT / f"{stem}.load.py.ttf")
		if rs.returncode or py.returncode:
			ok = bool(rs.returncode) == bool(py.returncode)
			failures += not ok
			print(f"{src.name} load: {'both fail' if ok else 'CHECK'}\n    rs: {rs.stderr.strip()[-200:]}\n    py: {py.stderr.strip()[-200:]}")
			continue
		rs_info, py_info = json_from(rs.stdout), json_from(py.stdout)
		if rs_info == py_info:
			print(f"{src.name} load: same")
		else:
			failures += 1
			print(f"{src.name} load: CHECK")
			for k in rs_info.keys() | py_info.keys():
				if rs_info.get(k) != py_info.get(k):
					print(f"    {k}: rs={rs_info.get(k)!r} py={py_info.get(k)!r}")
		# A legacy font is generated from the converted font, as the app does.
		work = OUT / f"{stem}.load.rs.ttf" if rs_info["preview"] else src
		texts = shaping_texts(work)
		for case, args in make_cases(py_info).items():
			if wanted(f"{stem}.{case}"):
				jobs.append((f"{stem}.{case}", work, args, texts))
		if wanted(f"{stem}.legacy"):
			jobs.append((f"{stem}.legacy", src, None, texts))

	with ThreadPoolExecutor(options.jobs) as executor:
		for ok, report in executor.map(lambda job: compare_case(*job), jobs):
			failures += not ok
			print(report, flush=True)

	print(f"\n{len(jobs)} cases, {failures} to check.")
	sys.exit(1 if failures else 0)


if __name__ == "__main__":
	main()
