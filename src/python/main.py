import os, math
from typing import cast

# FontTools is very difficult to get the typings right by nature,
# especially that many classes are dynamically constructed at runtime.
# I have tried the best I can to get as much type hints here as possible.
from fontTools import version
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options as SSOptions, parse_unicodes
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable, cmap_format_4
from fontTools.ttLib.tables._f_v_a_r import Axis, NamedInstance, table__f_v_a_r
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent, table__g_l_y_f
from fontTools.ttLib.tables._h_h_e_a import table__h_h_e_a
from fontTools.ttLib.tables._n_a_m_e import NameRecord, table__n_a_m_e
from fontTools.ttLib.tables._m_o_r_t import table__m_o_r_t
from fontTools.ttLib.tables.otTables import (
    featureParamTypes,
    FeatureParamsStylisticSet,
    FeatureParamsCharacterVariants,
)

hideRemovedFeature = True

MAC_STYLE = {"Regular": 0, "Bold": 1, "Italic": 2, "Bold Italic": 3}


def getAxisName(font: TTFont, tag: str, /) -> str:
    names: table__n_a_m_e = font["name"]
    axes: list[Axis] = font["fvar"].axes
    for a in axes:
        if a.axisTag == tag:
            return names.getDebugName(a.axisNameID)
    return tag


class Instantiate:
    def __init__(self, font: TTFont, args: dict, /):
        variations = args.get("variations")

        options: dict = args.get("options")
        names: table__n_a_m_e = font["name"]
        family = names.getBestFamilyName()
        version = names.getDebugName(5)

        description = f"Frozen from {family} {version}."
        keep_var = cast(bool, options.get("keepVar"))
        if "fvar" in font and not keep_var:
            settings = ", ".join(f"{getAxisName(font, k)}={v}" for k, v in variations.items())
            description += f" Sets {settings}."
            instantiateVariableFont(font, variations, inplace=True, overlap=True)
        features = args.get("features")
        if len(features) > 0:
            features = ", ".join(features)
            description += f" Activates {features}."
        disables = args.get("disables")
        if len(disables) > 0:
            disables = ", ".join(disables)
            description += f" Deactivates {disables}."
        if not hideRemovedFeature:
            description += " Use fallback mode."

        self.nameTable = names
        old_names: list[NameRecord] = self.nameTable.names
        self.nameTable.names = []

        family = options.get("family")
        subfamily = options.get("subfamily")
        typo_family = options.get("typo_family")
        typo_subfamily = options.get("typo_subfamily")

        if not typo_family:
            typo_family = family

        if not typo_subfamily or typo_subfamily == subfamily:
            typo_subfamily = subfamily
            fullName = f"{family} {subfamily}"
        else:
            fullName = f"{family} {typo_subfamily} {subfamily}"

        # refer to https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-ids for a list of name codes
        self.setName(family, 1)
        self.setName(subfamily, 2)
        self.setName(fullName, 3)
        self.setName(fullName, 4)
        self.setName("Version 1.000", 5)
        self.setName(Instantiate.getPostscriptName(family, subfamily), 6)
        self.setName("FontFreeze" + args.get("version"), 8)
        self.setName(description, 10)
        self.setName("https://mutsuntsai.github.io/fontfreeze", 11)
        self.setName(typo_family, 16)
        self.setName(typo_subfamily, 17)
        self.setName(fullName, 18)

        for n in old_names:
            # Keep all names that have IDs > 25, as those are custom names
            # This is necessary for "keep font variable" to work properly
            if n.nameID > 25:
                self.nameTable.setName(n.string, n.nameID, n.platformID, n.platEncID, n.langID)

        try:
            font["head"].macStyle = MAC_STYLE[subfamily]
            font["OS/2"].fsSelection = Instantiate.makeSelection(font["OS/2"].fsSelection, subfamily)
        except Exception:
            pass

        if not keep_var:
            Instantiate.dropVariationTables(font)
        if options.get("fixContour"):
            Instantiate.setOverlapFlags(font)

    def getPostscriptName(familyName: str, subfamilyName: str, /):
        familyName = familyName.replace(" ", "")
        subfamilyName = subfamilyName.replace(" ", "")
        result = f"{familyName}-{subfamilyName}"
        return result[:63]  # The limit is 63 characters

    def setName(self, content: str, index: int, /):
        # Setting MAC platform seems to cause trouble in some fonts,
        # so we don't do that anymore.
        self.nameTable.setName(
            content,
            index,
            3,  # PLAT_WINDOWS,
            1,  # ENC_UNICODE_11
            1033,  # LANG_ENGLISH
        )

    def dropVariationTables(font: TTFont, /):
        for tag in "STAT cvar fvar gvar".split():
            if tag in font.keys():
                del font[tag]

    def setOverlapFlags(font: TTFont, /):
        glyf: table__g_l_y_f = font["glyf"]
        for glyph_name in glyf.keys():
            glyph: Glyph = glyf[glyph_name]

            if glyph.isComposite():
                components: list[GlyphComponent] = glyph.components
                components[0].flags |= 0x0400  # OVERLAP_COMPOUND
            elif glyph.numberOfContours > 0:
                glyph.flags[0] |= 0x40  # OVERLAP_SIMPLE

    def makeSelection(bits, style: str, /):
        bits = bits ^ bits
        if style == "Regular":
            bits |= 0b1000000
        else:
            bits &= ~0b1000000
        if style == "Bold" or style == "Bold Italic":
            bits |= 0b100000
        else:
            bits &= ~0b100000
        if style == "Italic":
            bits |= 0b1
        else:
            bits &= ~0b1
        if not bits:
            bits = 0b1000000
        return bits


def removeFeature(font: TTFont, features: list, /):
    if len(features) == 0 or "GSUB" not in font:
        return
    records = font["GSUB"].table.FeatureList.FeatureRecord
    # We cannot just remove the record, as this will mess up the scripts
    for record in records:
        if record.FeatureTag in features:
            clearFeatureRecord(record)


def clearFeatureRecord(featureRecord, /):
    featureRecord.Feature.LookupListIndex.clear()
    featureRecord.Feature.LookupCount = 0
    if hideRemovedFeature:
        featureRecord.FeatureTag = "DELT"  # Special value


class Activator:
    def __init__(self, font: TTFont, args: dict, /) -> None:
        self.font = font
        self.features = args.get("features")
        options: dict = args.get("options")
        self.target = options.get("target")
        self.singleSub = options.get("singleSub")

        if len(self.features) == 0 or "GSUB" not in self.font:
            return

        self.cmapTables = self.font["cmap"].tables
        self.unicodeGlyphs = {name for table in self.cmapTables for name in table.cmap.values()}

        gsub_table = self.font["GSUB"].table
        self.featureRecords = gsub_table.FeatureList.FeatureRecord
        self.lookup = gsub_table.LookupList.Lookup

        scriptRecords = gsub_table.ScriptList.ScriptRecord
        for scriptRecord in scriptRecords:
            self.activateInScript(scriptRecord.Script)

    def activateInScript(self, script, /):
        if script.DefaultLangSys is not None:
            self.activateInLangSys(script.DefaultLangSys)
        for langSysRecord in script.LangSysRecord:
            self.activateInLangSys(langSysRecord.LangSys)

    def activateInLangSys(self, langSys, /):
        targetRecord = None

        # try to find existing target feature
        for index in langSys.FeatureIndex:
            featureRecord = self.featureRecords[index]
            if featureRecord.FeatureTag == self.target:
                targetRecord = featureRecord

        for index in langSys.FeatureIndex:
            featureRecord = self.featureRecords[index]
            if featureRecord.FeatureTag in self.features:
                if self.singleSub:
                    self.findSingleSubstitution(featureRecord)

                if targetRecord is None:
                    # if there's no existing one, use the first matching feature as target
                    targetRecord = featureRecord
                    # This is required to make work with e.g. SourceCodePro
                    featureParamTypes[self.target] = (
                        FeatureParamsStylisticSet
                        if featureRecord.FeatureTag.startswith("ss")
                        else FeatureParamsCharacterVariants
                    )
                    featureRecord.FeatureTag = self.target
                else:
                    Activator.moveFeatureLookups(featureRecord.Feature, targetRecord.Feature)
                    clearFeatureRecord(featureRecord)

        if targetRecord is not None:
            targetRecord.Feature.LookupListIndex.sort()

    def findSingleSubstitution(self, featureRecord, /):
        for lookupIndex in featureRecord.Feature.LookupListIndex:
            lookup = self.lookup[lookupIndex]
            if lookup.LookupType == 1:  # Single substitution
                for sub in lookup.SubTable:
                    for key, value in sub.mapping.items():
                        if key in self.unicodeGlyphs:
                            self.singleSubstitution(key, value)

    def singleSubstitution(self, key, value, /):
        for table in self.cmapTables:
            for index in table.cmap:
                if table.cmap[index] == key:
                    table.cmap[index] = value

    def moveFeatureLookups(fromFeature, toFeature, /):
        toFeature.LookupListIndex.extend(fromFeature.LookupListIndex)
        toFeature.LookupCount += fromFeature.LookupCount


def subset(font: TTFont, unicodes: str, /):
    if unicodes == "":
        return
    sub = Subsetter(
        SSOptions(
            layout_scripts=["*"],
            layout_features=["*"],
            name_IDs=["*"],
            name_languages=["*"],
        )
    )
    sub.populate(unicodes=parse_unicodes(unicodes))
    sub.subset(font)


#####################################################################################################
#####################################################################################################


def change_font_width(font: TTFont, from_width: int, to_width: int):
    hmtx = font["hmtx"]
    cmap = font.getBestCmap()
    lsb_delta = (to_width - from_width) / 2

    for codepoint, glyph_name in cmap.items():
        width, lsb = hmtx[glyph_name]
        if width == from_width:
            hmtx[glyph_name] = (to_width, lsb + lsb_delta)
            # Uncomment the next line for debugging
            # print(f"Change width {chr(codepoint)} ({glyph_name}): {width} → {to_width}")

    hhea: table__h_h_e_a = font["hhea"]
    hhea.advanceWidthMax = max(to_width, hhea.advanceWidthMax)


def change_font_spacing(font: TTFont, delta: int):
    hmtx = font["hmtx"]
    cmap = font.getBestCmap()

    max_width = 0
    for codepoint, glyph_name in cmap.items():
        width, lsb = hmtx[glyph_name]
        width += delta
        hmtx[glyph_name] = (width, lsb + delta / 2)
        if width > max_width:
            max_width = width

    hhea: table__h_h_e_a = font["hhea"]
    hhea.advanceWidthMax = max_width


def change_line_height(font: TTFont, delta: int):
    OS2 = font["OS/2"]
    ascent = OS2.usWinAscent
    descent = OS2.usWinDescent
    total = ascent + descent
    new_total = total + delta
    ascent = math.ceil(ascent * new_total / total)
    descent = math.floor(descent * new_total / total)

    hhea: table__h_h_e_a = font["hhea"]
    hhea.ascent = hhea.ascender = OS2.usWinAscent = ascent
    OS2.usWinDescent = descent
    hhea.descent = hhea.descender = -descent


#####################################################################################################
#####################################################################################################


def getFvar(font: TTFont) -> dict:
    if not "fvar" in font:
        return None

    names: table__n_a_m_e = font["name"]
    fvar: table__f_v_a_r = font["fvar"]
    axes: list[Axis] = fvar.axes
    instances: list[NamedInstance] = fvar.instances
    return {
        "axes": [
            {
                "tag": a.axisTag,
                "default": a.defaultValue,
                "min": a.minValue,
                "max": a.maxValue,
                "name": names.getDebugName(a.axisNameID),
            }
            for a in axes
        ],
        "instances": [
            {
                "name": names.getDebugName(i.subfamilyNameID),
                "coordinates": i.coordinates,
            }
            for i in instances
        ],
    }


def loadFont(filename: str, /):
    font = loadTtfFont(filename)

    OS2 = font["OS/2"]
    names: table__n_a_m_e = font["name"]
    features = font["GSUB"].table.FeatureList.FeatureRecord if "GSUB" in font else []
    features = [r.FeatureTag for r in features]

    # change temp to input, preventing input being overwritten by invalid file
    if os.path.exists("input"):
        os.remove("input")
    os.rename(filename, "input")

    info = {
        "family": names.getBestFamilyName(),
        "subfamily": names.getDebugName(2),
        "copyright": names.getDebugName(0),
        "id": names.getDebugName(3),
        "version": names.getDebugName(5),
        "trademark": names.getDebugName(7),
        "manufacturer": names.getDebugName(8),
        "designer": names.getDebugName(9),
        "description": names.getDebugName(10),
        "vendorURL": names.getDebugName(11),
        "designerURL": names.getDebugName(12),
        "license": names.getDebugName(13),
        "licenseURL": names.getDebugName(14),
        "typo_family": names.getDebugName(16),
        "typo_subfamily": names.getDebugName(17),
        "fvar": getFvar(font),
        "gsub": list(dict.fromkeys(features)),
        "fontHeight": OS2.sTypoAscender - OS2.sTypoDescender,
        "lineHeight": OS2.usWinAscent + OS2.usWinDescent,
    }

    if font.getBestCmap() is None and convertBig5Cmap(font):
        print("Legacy CJK font detected.")
        fixLegacy(font)
        info["preview"] = True

    return info


def convertBig5Cmap(font: TTFont, /) -> bool:
    cmap = font["cmap"]
    for table in cmap.tables:
        if table.platformID == 3 and table.platEncID == 4:  # Big5
            new_table: cmap_format_4 = CmapSubtable.newSubtable(4)
            new_table.platformID = 3  # Windows
            new_table.platEncID = 1  # Unicode
            new_table.language = 0
            new_table.cmap = {}
            for key in table.cmap:
                try:
                    newKey = ord(key.to_bytes(2, byteorder="big").decode("big5")) if key > 255 else key
                    new_table.cmap[newKey] = table.cmap[key]
                except Exception:
                    pass
            cmap.tables = [new_table]
            return True
    return False


# Legacy CJK fonts in Big5 encoding in particular might use mixed encoding. For more info, see
# https://docs.microsoft.com/en-us/typography/opentype/spec/name#windows-encoding-ids
def fixEncoding(name: NameRecord, /):
    temp = name.string.decode("utf_16_be")
    temp = bytes(temp, encoding="raw_unicode_escape")
    try:
        temp.decode("big5")
        name.string = temp
    except Exception:
        pass  # We've tried our best


def loadTtfFont(filename: str, /):
    font = TTFont(
        file=filename,
        recalcBBoxes=False,
        fontNumber=0,  # in case it's a font collection
    )

    # Fix legacy CJK font name encoding
    names: list[NameRecord] = font["name"].names
    for name in names:
        if name.platformID == 3 and name.platEncID == 4:  # Big5
            try:
                name.toStr()
            except Exception:
                fixEncoding(name)

    return font


# Legacy fonts will likely fail the OpenType Sanitizer (see https://github.com/khaledhosny/ots)
# For such a font we tried to fix the font as much as possible.
def fixLegacy(font: TTFont, /):
    # It is known that 金梅 series fonts, for example, have problems in their mort tables.
    # Here we perform a check to see if mort table data make sense.
    # If not, just delete the table.
    if "mort" in font:
        try:
            mort: table__m_o_r_t = font["mort"]
            mort.ensureDecompiled()
        except Exception:
            print("Drop corrupted mort table.")
            del font["mort"]

    # Simply re-saving the font should fix most table alignment issues.
    font.save("input", reorderTables=None)


#####################################################################################################
#####################################################################################################


def processLegacy():
    font = loadTtfFont("input")
    fixLegacy(font)


def processFont(args, /):
    main(args.to_py(), "input", "output")


def main(args: dict, filename: str, output: str, /):
    global hideRemovedFeature
    hideRemovedFeature = True
    font = generateFont(args, filename)

    try:
        font.save(output)
    except AssertionError as msg:
        if "DELT" in str(msg):
            # For unknown reason, some fonts have problem with the "DELT" idea,
            # for example JetBrains Mono v2.303 (specifically).
            # In that case fallback and do not change the feature name.
            hideRemovedFeature = False
            font = generateFont(args, filename)
            font.save(output)
        else:
            raise


def generateFont(args: dict, filename: str):
    font = loadTtfFont(filename)
    Instantiate(font, args)
    removeFeature(font, args.get("disables"))
    Activator(font, args)
    subset(font, args.get("unicodes"))

    options: dict = args.get("options")
    spacing = options.get("spacing")
    if spacing != 0:
        change_font_spacing(font, spacing)
    line_height = options.get("lineHeight")
    if line_height != 0:
        change_line_height(font, line_height)

    if options.get("format") == "woff2":
        font.flavor = "woff2"

    return font


print(f"FontTools version: {version}")
