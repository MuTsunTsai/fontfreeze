import os
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options as SSOptions, parse_unicodes
from fontTools.varLib.instancer import instantiateVariableFont

PLAT_MAC = 1
PLAT_WINDOWS = 3

ENC_ROMAN = 0
ENC_UNICODE_11 = 1

LANG_ENGLISH = 1033

MACSTYLE = {"Regular": 0, "Bold": 1, "Italic": 2, "Bold Italic": 3}

OVERLAP_SIMPLE = 0x40
OVERLAP_COMPOUND = 0x0400


def dropVariationTables(font):
    for tag in "STAT cvar fvar gvar".split():
        if tag in font.keys():
            del font[tag]


def setOverlapFlags(font):
    glyf = font["glyf"]
    for glyph_name in glyf.keys():
        glyph = glyf[glyph_name]

        if glyph.isComposite():
            glyph.components[0].flags |= OVERLAP_COMPOUND
        elif glyph.numberOfContours > 0:
            glyph.flags[0] |= OVERLAP_SIMPLE


def makeSelection(bits, style):
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


def getPostscriptName(familyName, subfamilyName):
    familyName = familyName.replace(" ", "")
    subfamilyName = subfamilyName.replace(" ", "")
    return f"{familyName}-{subfamilyName}"


def updateNames(font: TTFont, options):
    nameTable = font["name"]
    nameTable.names = []
    family = options.get("family")
    subfamily = options.get("subfamily")
    fullName = f"{family} {subfamily}"
    postscriptName = getPostscriptName(family, subfamily)
    nameTable.setName(family, 1, PLAT_MAC, ENC_ROMAN, 0)
    nameTable.setName(family, 1, PLAT_WINDOWS, ENC_UNICODE_11, LANG_ENGLISH)
    nameTable.setName(subfamily, 2, PLAT_MAC, ENC_ROMAN, 0)
    nameTable.setName(subfamily, 2, PLAT_WINDOWS, ENC_UNICODE_11, LANG_ENGLISH)
    nameTable.setName(fullName, 3, PLAT_MAC, ENC_ROMAN, 0)
    nameTable.setName(fullName, 3, PLAT_WINDOWS, ENC_UNICODE_11, LANG_ENGLISH)
    nameTable.setName(fullName, 4, PLAT_MAC, ENC_ROMAN, 0)
    nameTable.setName(fullName, 4, PLAT_WINDOWS, ENC_UNICODE_11, LANG_ENGLISH)
    nameTable.setName("Version 1.000", 5, PLAT_MAC, ENC_ROMAN, 0)
    nameTable.setName("Version 1.000", 5, PLAT_WINDOWS, ENC_UNICODE_11, LANG_ENGLISH)
    nameTable.setName(postscriptName, 6, PLAT_MAC, ENC_ROMAN, 0)
    nameTable.setName(postscriptName, 6, PLAT_WINDOWS, ENC_UNICODE_11, LANG_ENGLISH)


def instantiateFont(font: TTFont, options, variations):
    if "fvar" in font:
        instantiateVariableFont(font, variations, inplace=True, overlap=True)

    updateNames(font, options)
    subfamily = options.get("subfamily")
    try:
        font["head"].macStyle = MACSTYLE[subfamily]
        font["OS/2"].fsSelection = makeSelection(font["OS/2"].fsSelection, subfamily)
    except:
        pass
    dropVariationTables(font)
    if options.get("fixContour") == True:
        setOverlapFlags(font)


def removeFeature(font: TTFont, features: list):
    if len(features) == 0 or "GSUB" not in font:
        return
    records = font["GSUB"].table.FeatureList.FeatureRecord
    # We cannot just remove the record, as this will mess up the scripts
    for record in records:
        if record.FeatureTag in features:
            clearFeatureRecord(record)


def clearFeatureRecord(featureRecord):
    featureRecord.Feature.LookupListIndex.clear()
    featureRecord.Feature.LookupCount = 0
    featureRecord.FeatureTag = "DELT"  # Special value


def moveFeatureLookups(fromFeature, toFeature):
    toFeature.LookupListIndex.extend(fromFeature.LookupListIndex)
    toFeature.LookupCount += fromFeature.LookupCount


class Activator:
    def __init__(self, font: TTFont, args: dict) -> None:
        self.font = font
        self.features = args.get("features")
        self.target = args.get("options").get("target")
        self.singleSub = args.get("options").get("singleSub")

    def activate(self):
        if len(self.features) == 0 or "GSUB" not in self.font:
            return

        self.cmapTables = self.font["cmap"].tables
        self.unicodeGlyphs = {
            name for table in self.cmapTables for name in table.cmap.values()
        }

        table = self.font["GSUB"].table
        self.featureRecords = table.FeatureList.FeatureRecord
        self.lookup = table.LookupList.Lookup

        scriptRecords = table.ScriptList.ScriptRecord
        for scriptRecord in scriptRecords:
            self.activateInScript(scriptRecord.Script)

    def activateInScript(self, script):
        if script.DefaultLangSys != None:
            self.activateInLangSys(script.DefaultLangSys)
        for langSysRecord in script.LangSysRecord:
            self.activateInLangSys(langSysRecord.LangSys)

    def activateInLangSys(self, langSys):
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

                if targetRecord == None:
                    # if there's no existing one, use the first matching feature as target
                    targetRecord = featureRecord
                    featureRecord.FeatureTag = self.target
                else:
                    moveFeatureLookups(featureRecord.Feature, targetRecord.Feature)
                    clearFeatureRecord(featureRecord)

        if targetRecord != None:
            targetRecord.Feature.LookupListIndex.sort()

    def findSingleSubstitution(self, featureRecord):
        for lookupIndex in featureRecord.Feature.LookupListIndex:
            lookup = self.lookup[lookupIndex]
            if lookup.LookupType == 1:  # Single substitution
                for sub in lookup.SubTable:
                    for input, output in sub.mapping.items():
                        if input in self.unicodeGlyphs:
                            self.singleSubstitution(input, output)

    def singleSubstitution(self, input, output):
        for table in self.cmapTables:
            for index in table.cmap:
                if table.cmap[index] == input:
                    table.cmap[index] = output


def subset(font: TTFont, unicodes: str):
    if unicodes == "":
        return
    sub = Subsetter(SSOptions(layout_features=["*"]))  # keep all features
    sub.populate(unicodes=parse_unicodes(unicodes))
    sub.subset(font)


def loadFont():
    inputFont = loadTtfFont("temp")

    features = (
        inputFont["GSUB"].table.FeatureList.FeatureRecord if "GSUB" in inputFont else []
    )
    features = list(map(lambda r: r.FeatureTag, features))

    fvar = None
    if "fvar" in inputFont:
        fvar = {
            "axes": list(
                map(
                    lambda a: {
                        "tag": a.axisTag,
                        "default": a.defaultValue,
                        "min": a.minValue,
                        "max": a.maxValue,
                        "name": inputFont["name"].getDebugName(a.axisNameID),
                    },
                    inputFont["fvar"].axes,
                )
            ),
            "instances": list(
                map(
                    lambda i: {
                        "name": inputFont["name"].getDebugName(i.subfamilyNameID),
                        "coordinates": i.coordinates,
                    },
                    inputFont["fvar"].instances,
                )
            ),
        }

    # change temp to input, preventing input being overwritten by invalid file
    if os.path.exists("input"):
        os.remove("input")
    os.rename("temp", "input")

    return {
        "family": inputFont["name"].getBestFamilyName(),
        "copyright": inputFont["name"].getDebugName(0),
        "id": inputFont["name"].getDebugName(3),
        "version": inputFont["name"].getDebugName(5),
        "trademark": inputFont["name"].getDebugName(7),
        "manufacturer": inputFont["name"].getDebugName(8),
        "designer": inputFont["name"].getDebugName(9),
        "description": inputFont["name"].getDebugName(10),
        "vendorURL": inputFont["name"].getDebugName(11),
        "designerURL": inputFont["name"].getDebugName(12),
        "license": inputFont["name"].getDebugName(13),
        "licenseURL": inputFont["name"].getDebugName(14),
        "fvar": fvar,
        "gsub": list(dict.fromkeys(features)),
    }


def loadTtfFont(filename: str):
    return TTFont(
        file=filename,
        recalcBBoxes=False,
        fontNumber=0,  # in case it's a font collection
    )


def processFont(args):
    main(args.to_py(), "input", "output")


def main(args: dict, filename: str, output: str):
    font = loadTtfFont(filename)
    instantiateFont(font, args.get("options"), args.get("variations"))
    removeFeature(font, args.get("disables"))
    Activator(font, args).activate()
    subset(font, args.get("unicodes"))

    if args.get("options").get("format") == "woff2":
        font.flavor = "woff2"

    font.save(output)
