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


def getAxisName(font: TTFont, tag: str) -> str:
    for a in font["fvar"].axes:
        if a.axisTag == tag:
            return font["name"].getDebugName(a.axisNameID)
    return tag


class Instantiate:
    def __init__(self, font: TTFont, args):
        variations = args.get("variations")

        options = args.get("options")
        family = font["name"].getBestFamilyName()
        version = font["name"].getDebugName(5)

        description = f"Frozen from {family} {version}."
        if "fvar" in font:
            settings = ", ".join(
                f"{getAxisName(font, k)}={v}" for k, v in variations.items()
            )
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

        self.nameTable = font["name"]
        self.nameTable.names = []
        family = options.get("family")
        subfamily = options.get("subfamily")
        fullName = f"{family} {subfamily}"
        self.setName(family, 1)
        self.setName(subfamily, 2)
        self.setName(fullName, 3)
        self.setName(fullName, 4)
        self.setName("Version 1.000", 5)
        self.setName(Instantiate.getPostscriptName(family, subfamily), 6)
        self.setName("FontFreeze" + args.get("version"), 8)
        self.setName(description, 10)
        self.setName("https://mutsuntsai.github.io/fontfreeze", 11)

        try:
            font["head"].macStyle = MACSTYLE[subfamily]
            font["OS/2"].fsSelection = Instantiate.makeSelection(
                font["OS/2"].fsSelection, subfamily
            )
        except:
            pass
        Instantiate.dropVariationTables(font)
        if options.get("fixContour") == True:
            Instantiate.setOverlapFlags(font)

    def getPostscriptName(familyName, subfamilyName):
        familyName = familyName.replace(" ", "")
        subfamilyName = subfamilyName.replace(" ", "")
        return f"{familyName}-{subfamilyName}"

    def setName(self, content: str, index: int):
        self.nameTable.setName(content, index, PLAT_MAC, ENC_ROMAN, 0)
        self.nameTable.setName(
            content, index, PLAT_WINDOWS, ENC_UNICODE_11, LANG_ENGLISH
        )

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


class Activator:
    def __init__(self, font: TTFont, args: dict) -> None:
        self.font = font
        self.features = args.get("features")
        self.target = args.get("options").get("target")
        self.singleSub = args.get("options").get("singleSub")

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
                    Activator.moveFeatureLookups(
                        featureRecord.Feature, targetRecord.Feature
                    )
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

    def moveFeatureLookups(fromFeature, toFeature):
        toFeature.LookupListIndex.extend(fromFeature.LookupListIndex)
        toFeature.LookupCount += fromFeature.LookupCount


def subset(font: TTFont, unicodes: str):
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


def loadFont():
    font = loadTtfFont("temp")

    features = font["GSUB"].table.FeatureList.FeatureRecord if "GSUB" in font else []
    features = [r.FeatureTag for r in features]

    fvar = (
        {
            "axes": [
                {
                    "tag": a.axisTag,
                    "default": a.defaultValue,
                    "min": a.minValue,
                    "max": a.maxValue,
                    "name": font["name"].getDebugName(a.axisNameID),
                }
                for a in font["fvar"].axes
            ],
            "instances": [
                {
                    "name": font["name"].getDebugName(i.subfamilyNameID),
                    "coordinates": i.coordinates,
                }
                for i in font["fvar"].instances
            ],
        }
        if "fvar" in font
        else None
    )

    # change temp to input, preventing input being overwritten by invalid file
    if os.path.exists("input"):
        os.remove("input")
    os.rename("temp", "input")

    return {
        "family": font["name"].getBestFamilyName(),
        "copyright": font["name"].getDebugName(0),
        "id": font["name"].getDebugName(3),
        "version": font["name"].getDebugName(5),
        "trademark": font["name"].getDebugName(7),
        "manufacturer": font["name"].getDebugName(8),
        "designer": font["name"].getDebugName(9),
        "description": font["name"].getDebugName(10),
        "vendorURL": font["name"].getDebugName(11),
        "designerURL": font["name"].getDebugName(12),
        "license": font["name"].getDebugName(13),
        "licenseURL": font["name"].getDebugName(14),
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
    Instantiate(font, args)
    removeFeature(font, args.get("disables"))
    Activator(font, args)
    subset(font, args.get("unicodes"))

    if args.get("options").get("format") == "woff2":
        font.flavor = "woff2"

    font.save(output)
