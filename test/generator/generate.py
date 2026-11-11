"""Generates the fonts in test/fonts for the tests of FontFreeze.

The fonts are made with fontTools rather than fontoxide, which FontFreeze itself is built
on, so that a bug in fontoxide cannot cancel itself out in the tests.

Every glyph of a font has a distinct advance width, so the glyphs that a text is shaped
into can be told by the widths alone, even after subsetting has renumbered the glyphs.

Run `uv run generate.py` in this folder. The output is reproducible: rerunning it should
leave test/fonts unchanged.
"""

import sys
from array import array
from pathlib import Path

import ots
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.timeTools import timestampFromString
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTCollection, TTFont, newTable
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.ttLib.tables.DefaultTable import DefaultTable
from fontTools.varLib import build as build_variable

OUTPUT = Path(__file__).resolve().parent.parent / "fonts"

# A fixed time for head.created and head.modified, for reproducible output.
TIMESTAMP = timestampFromString("Mon Jan  1 00:00:00 2024")

UPM = 1000
HEIGHT = 700


def finish(font: TTFont) -> TTFont:
	"""Fixes the timestamps, so that the output is reproducible."""
	font["head"].created = font["head"].modified = TIMESTAMP
	font.recalcTimestamp = False
	return font


def save(font: TTFont, name: str) -> Path:
	path = OUTPUT / name
	font.save(path)
	print(f"{name}: {path.stat().st_size:,} bytes")
	return path


def width_of(index: int) -> int:
	"""The advance width of the index-th glyph, distinct for each glyph."""
	return 400 + 20 * index


def rect(pen, x0: float, y0: float, x1: float, y1: float, clockwise: bool) -> None:
	points = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
	if not clockwise:
		points.reverse()
	pen.moveTo(points[0])
	for p in points[1:]:
		pen.lineTo(p)
	pen.closePath()


def height_of(index: int) -> int:
	return HEIGHT - 50 * (index % 5)


#########################################################################################
# A: FFTest-Var.ttf, a variable TrueType font covering most of the features
#########################################################################################

# The order decides the glyph IDs. "one.ss02" comes after the padding, so that its ID is
# at least 256 and cannot be put in the format 0 cmap.
VAR_GLYPHS = [
	".notdef", "space", "a", "f", "g", "i", "l", "o", "one", "zero", "period",
	"O", "Q", "bar", "smile",
	"a.ss01", "o.calt", "one.case", "g.cv01.1", "g.cv01.2", "g.cv01.3", "zero.zero",
	"f.ss04", "f_f", "f_i", "l_l", "l.ss03", "i.TRK",
]
PADDING = 240
VAR_ORDER = VAR_GLYPHS + [f"pad{i:03}" for i in range(PADDING)] + ["one.ss02"]

VAR_CMAP = {
	0x20: "space",
	0xA0: "space",  # Two code points for one glyph: the spacing is added twice.
	0x61: "a",
	0x66: "f",
	0x67: "g",
	0x69: "i",
	0x6C: "l",
	0x6F: "o",
	0x31: "one",
	0x30: "zero",
	0x2E: "period",
	0x4F: "O",
	0x51: "Q",
	0x1F600: "smile",  # Outside the BMP, for the format 12 subtable.
}

VAR_FEATURES = """
languagesystem DFLT dflt;
languagesystem latn dflt;
languagesystem latn TRK;

# The lookups are defined first, so that their order in the LookupList is as listed here.
# In particular, LIGA comes before SS04, and CASE before SS02.
lookup CCMP { sub pad000 by pad001; } CCMP;
lookup LIGA { sub f f by f_f; sub f i by f_i; } LIGA;
lookup LIGA_TRK { sub l l by l_l; } LIGA_TRK;
lookup CALT { sub o' period by o.calt; } CALT;
lookup CASE { sub one by one.case; } CASE;
lookup SS01 { sub a by a.ss01; } SS01;
lookup SS02 { sub one.case by one.ss02; } SS02;
lookup SS03_SINGLE { sub l by l.ss03; } SS03_SINGLE;
lookup SS03 { sub i l' lookup SS03_SINGLE; } SS03;
lookup SS04 { sub f by f.ss04; } SS04;
lookup CV01 { sub g from [g.cv01.1 g.cv01.2 g.cv01.3]; } CV01;
lookup ZERO useExtension { sub zero by zero.zero; } ZERO;
lookup LOCL_TRK { sub i by i.TRK; } LOCL_TRK;

# Hidden in the UI.
feature ccmp { lookup CCMP; } ccmp;
feature locl { script latn; language TRK exclude_dflt; lookup LOCL_TRK; } locl;

# latn/TRK has an extra lookup, so there are two "liga" FeatureRecords.
feature liga {
	lookup LIGA;
	script latn;
	language TRK;
	lookup LIGA_TRK;
} liga;

# Only in latn/dflt, so that activating features elsewhere has no existing target.
feature calt { script latn; language dflt exclude_dflt; lookup CALT; } calt;

feature case { lookup CASE; } case;
feature ss01 { featureNames { name "Single-storey a"; }; lookup SS01; } ss01;
feature ss02 { featureNames { name "Flagless one"; }; lookup SS02; } ss02;
feature ss03 { lookup SS03; } ss03;
feature ss04 { lookup SS04; } ss04;
feature cv01 {
	cvParameters {
		FeatUILabelNameID { name "Alternate g"; };
		Character 0x67;
	};
	lookup CV01;
} cv01;
feature zero { lookup ZERO; } zero;

feature kern { pos a o -30; } kern;
"""

# The masters: (wght, TEST) -> the change of the advance widths.
VAR_MASTERS = {
	(400, 0): 0,
	(100, 0): -20,
	(900, 0): 40,
	(400, 100): 10,
}

VAR_INSTANCES = {
	"Thin": (100, 0),
	"Regular": (400, 0),
	"Black": (900, 0),
	"Tested": (400, 100),
}


def var_glyph(name: str, width: int, index: int):
	"""Draws a glyph of A. The point structure must not depend on the master."""
	pen = TTGlyphPen(VAR_ORDER)  # The glyph set is only checked for the component names.
	if name == "Q":
		# A composite glyph with overlapping components.
		pen.addComponent("O", (1, 0, 0, 1, 0, 0))
		pen.addComponent("bar", (1, 0, 0, 1, width // 2, -100))
	elif name == "O":
		# Overlapping contours.
		rect(pen, 50, 0, width // 2 + 50, HEIGHT, True)
		rect(pen, width // 2 - 50, 0, width - 50, HEIGHT, True)
	elif name == "space" or name.startswith("pad"):
		pass
	else:
		rect(pen, 50, 0, width - 50, height_of(index), True)
	return pen.glyph()


def var_master(location: tuple[int, int]) -> TTFont:
	delta = VAR_MASTERS[location]
	is_black = location == (900, 0)

	fb = FontBuilder(UPM, isTTF=True)
	fb.setupGlyphOrder(VAR_ORDER)
	fb.setupCharacterMap(VAR_CMAP)

	widths = {}
	for index, name in enumerate(VAR_ORDER):
		if name.startswith("pad"):
			widths[name] = 0
		elif name == "bar":
			widths[name] = 100
		else:
			widths[name] = width_of(index) + delta
	fb.setupGlyf({name: var_glyph(name, widths[name], i) for i, name in enumerate(VAR_ORDER)})
	glyf = fb.font["glyf"]
	metrics = {}
	for name in VAR_ORDER:
		glyph = glyf[name]
		glyph.recalcBounds(glyf)
		metrics[name] = (widths[name], getattr(glyph, "xMin", 0))
	fb.setupHorizontalMetrics(metrics)

	# The ascent grows with the weight, so that MVAR is needed.
	win_ascent = 1100 if is_black else 1000
	fb.setupHorizontalHeader(ascent=win_ascent, descent=-300)
	fb.setupOS2(
		sTypoAscender=800,
		sTypoDescender=-200,
		sTypoLineGap=0,
		usWinAscent=win_ascent,
		usWinDescent=300,
		achVendID="TEST",
	)
	fb.setupNameTable(
		{
			"copyright": "Copyright (c) FontFreeze test",
			"familyName": "FFTest Var",
			"styleName": "Regular",
			"uniqueFontIdentifier": "FFTest Var Regular 1.000",
			"fullName": "FFTest Var Regular",
			"version": "Version 1.000",
			"psName": "FFTestVar-Regular",
			"trademark": "FFTest is not a trademark",
			"manufacturer": "FontFreeze",
			"designer": "FontFreeze test generator",
			"description": "A font for the tests of FontFreeze.",
			"vendorURL": "https://example.com/vendor",
			"designerURL": "https://example.com/designer",
			"licenseDescription": "MIT License",
			"licenseInfoURL": "https://opensource.org/licenses/MIT",
			"typographicFamily": "FFTest",
			"typographicSubfamily": "Var Regular",
		},
		mac=True,  # The Mac names are dropped by FontFreeze.
	)
	fb.setupPost()

	# Varying control values, so that the font gets a cvar table.
	cvt = newTable("cvt ")
	cvt.values = array("h", [0, 20 + delta])
	fb.font["cvt "] = cvt

	return fb.font


def build_var() -> TTFont:
	ds = DesignSpaceDocument()
	ds.addAxisDescriptor(name="Weight", tag="wght", minimum=100, default=400, maximum=900)
	ds.addAxisDescriptor(name="Test Axis", tag="TEST", minimum=0, default=0, maximum=100)
	for wght, test in VAR_MASTERS:
		ds.addSourceDescriptor(
			font=var_master((wght, test)),
			location={"Weight": wght, "Test Axis": test},
			familyName="FFTest Var",
		)
	for style, (wght, test) in VAR_INSTANCES.items():
		ds.addInstanceDescriptor(
			familyName="FFTest Var",
			styleName=style,
			location={"Weight": wght, "Test Axis": test},
		)
	font, _, _ = build_variable(ds)
	addOpenTypeFeaturesFromString(font, VAR_FEATURES)

	# A legacy Mac subtable. Format 0 can only address glyph IDs below 256.
	mac = CmapSubtable.newSubtable(0)
	mac.platformID, mac.platEncID, mac.language = 1, 0, 0
	mac.cmap = {code: name for code, name in VAR_CMAP.items() if code < 0x80}
	font["cmap"].tables.append(mac)

	return finish(font)


#########################################################################################
# B: FFTest-Static.otf, a static CFF font with an empty GSUB
#########################################################################################

STATIC_ORDER = [".notdef", "space", "a", "b", "c", "one"]
STATIC_CMAP = {0x20: "space", 0x61: "a", 0x62: "b", 0x63: "c", 0x31: "one"}


def build_static() -> TTFont:
	fb = FontBuilder(UPM, isTTF=False)
	fb.setupGlyphOrder(STATIC_ORDER)
	fb.setupCharacterMap(STATIC_CMAP)

	char_strings = {}
	metrics = {}
	for index, name in enumerate(STATIC_ORDER):
		width = width_of(index)
		pen = T2CharStringPen(width, None)
		if name != "space":
			rect(pen, 50, 0, width - 50, height_of(index), False)
		char_strings[name] = pen.getCharString()
		metrics[name] = (width, 0 if name == "space" else 50)
	fb.setupCFF("FFTestStatic-BoldItalic", {"FullName": "FFTest Static Bold Italic"}, char_strings, {})
	fb.setupHorizontalMetrics(metrics)
	fb.setupHorizontalHeader(ascent=900, descent=-250)
	fb.font["head"].macStyle = 0b11  # Bold Italic
	fb.setupOS2(
		sTypoAscender=750,
		sTypoDescender=-250,
		usWinAscent=900,
		usWinDescent=250,
		fsSelection=0b10_0001,
		achVendID="TEST",
	)
	# No typographic names.
	fb.setupNameTable(
		{
			"familyName": "FFTest Static",
			"styleName": "Bold Italic",
			"version": "Version 2.000",
			"psName": "FFTestStatic-BoldItalic",
		}
	)
	fb.setupPost()

	# A GSUB table without any of its lists.
	gsub = newTable("GSUB")
	gsub.table = otTables.GSUB()
	gsub.table.Version = 0x00010000
	gsub.table.ScriptList = None
	gsub.table.FeatureList = None
	gsub.table.LookupList = None
	fb.font["GSUB"] = gsub

	return finish(fb.font)


#########################################################################################
# C: FFTest-Big5.ttf, a legacy CJK font like the 金梅 fonts
#########################################################################################

BIG5_CHARS = ["A", "永", "和", "中"]
BIG5_ORDER = [".notdef", "space", "A", "uni6C38", "uni548C", "uni4E2D", "AB", "invalid"]


def big5(text: str) -> bytes:
	return text.encode("big5")


def big5_code(char: str) -> int:
	return int.from_bytes(big5(char), "big")


def mixed_encoding(text: str) -> bytes:
	"""The broken encoding seen in legacy fonts: each byte of Big5 as a UTF-16 code unit."""
	return "".join(chr(b) for b in big5(text)).encode("utf_16_be")


def build_big5() -> TTFont:
	fb = FontBuilder(UPM, isTTF=True)
	fb.setupGlyphOrder(BIG5_ORDER)

	glyphs = {}
	metrics = {}
	for index, name in enumerate(BIG5_ORDER):
		width = width_of(index)
		pen = TTGlyphPen(None)
		if name != "space":
			rect(pen, 50, 0, width - 50, height_of(index), True)
		glyphs[name] = pen.glyph()
		metrics[name] = (width, 0 if name == "space" else 50)
	fb.setupGlyf(glyphs)
	fb.setupHorizontalMetrics(metrics)
	fb.setupHorizontalHeader(ascent=1000, descent=-200)
	fb.setupPost()

	# Only a Big5 subtable and a Mac one, as in the 金梅 fonts.
	windows = CmapSubtable.newSubtable(4)
	windows.platformID, windows.platEncID, windows.language = 3, 4, 0
	windows.cmap = {
		0x20: "space",
		0x41: "A",
		big5_code("永"): "uni6C38",
		big5_code("和"): "uni548C",
		big5_code("中"): "uni4E2D",
		0x4142: "AB",  # Two ASCII bytes, not a single character: skipped.
		0xFEFE: "invalid",  # Not valid Big5: skipped.
	}
	mac = CmapSubtable.newSubtable(0)
	mac.platformID, mac.platEncID, mac.language = 1, 0, 0
	mac.cmap = {0x20: "space", 0x41: "A"}
	cmap = newTable("cmap")
	cmap.tableVersion = 0
	cmap.tables = [mac, windows]
	fb.font["cmap"] = cmap

	fb.setupOS2(
		sTypoAscender=880,
		sTypoDescender=-120,
		usWinAscent=1000,
		usWinDescent=200,
		ulCodePageRange1=1 << 20,  # Chinese: Traditional
		achVendID="TEST",
	)

	name = newTable("name")
	name.names = []

	def add(string: bytes | str, name_id: int, platform: int, encoding: int, language: int) -> None:
		record = NameRecord()
		record.nameID, record.platformID, record.platEncID, record.langID = name_id, platform, encoding, language
		record.string = string
		name.names.append(record)

	# No English names, so that the fixed names are shown in the UI.
	# Correct Big5: left alone.
	add(big5("版權所有"), 0, 3, 4, 0x404)
	# Mixed encoding: fixed when the font is read.
	add(mixed_encoding("測試明體"), 1, 3, 4, 0x404)
	add(mixed_encoding("標準"), 2, 3, 4, 0x404)
	add(mixed_encoding("測試明體 標準"), 4, 3, 4, 0x404)
	add("Version 1.000".encode("utf_16_be"), 5, 3, 4, 0x404)
	fb.font["name"] = name

	# A broken mort table (5 chains but no data), which should be removed.
	mort = DefaultTable("mort")
	mort.data = bytes.fromhex("00010000 00000005")
	fb.font["mort"] = mort

	return finish(fb.font)


#########################################################################################
# Fonts derived from the above for error cases
#########################################################################################


def without_os2(font: TTFont) -> TTFont:
	del font["OS/2"]
	return font


def zero_win_metrics(font: TTFont) -> TTFont:
	font["OS/2"].usWinAscent = font["OS/2"].usWinDescent = 0
	return font


#########################################################################################


def sanitize(path: Path) -> None:
	"""Checks the font with the OpenType Sanitizer, as browsers do."""
	result = ots.sanitize(str(path), capture_output=True, text=True)
	if result.returncode != 0:
		sys.exit(f"{path.name} failed OTS:\n{result.stdout}{result.stderr}")


def main() -> None:
	OUTPUT.mkdir(exist_ok=True)

	var_path = save(build_var(), "FFTest-Var.ttf")
	static_path = save(build_static(), "FFTest-Static.otf")
	save(build_big5(), "FFTest-Big5.ttf")

	collection = TTCollection()
	# The static font comes first: FontFreeze reads the first font of a collection.
	collection.fonts = [finish(TTFont(static_path)), finish(TTFont(var_path))]
	collection.save(OUTPUT / "FFTest.ttc")
	print(f"FFTest.ttc: {(OUTPUT / 'FFTest.ttc').stat().st_size:,} bytes")

	save(without_os2(finish(TTFont(static_path))), "FFTest-NoOS2.otf")
	save(zero_win_metrics(finish(TTFont(static_path))), "FFTest-ZeroWin.otf")

	# The legacy font is expected to fail, as browsers reject a cmap without Unicode.
	# The collection is left out, as OTS mixes up the glyph counts of its fonts.
	for name in ["FFTest-Var.ttf", "FFTest-Static.otf"]:
		sanitize(OUTPUT / name)


if __name__ == "__main__":
	main()
