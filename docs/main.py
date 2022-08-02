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

inputFont = None


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


def moveFeatureInLangSys(langSys, featureRecords, features: list, target: str):
    targetRecord = None
    # try to find existing target feature
    for index in langSys.FeatureIndex:
        featureRecord = featureRecords[index]
        if featureRecord.FeatureTag == target:
            targetRecord = featureRecord
    for index in langSys.FeatureIndex:
        featureRecord = featureRecords[index]
        if featureRecord.FeatureTag in features:
            if targetRecord == None:
                # if there's no existing one, use the first matching feature as target
                targetRecord = featureRecord
                featureRecord.FeatureTag = target
            else:
                moveFeatureLookups(featureRecord.Feature, targetRecord.Feature)
                clearFeatureRecord(featureRecord)
    if targetRecord != None:
        targetRecord.Feature.LookupListIndex.sort()


def moveFeatureInScript(script, featureRecords, features: list, target: str):
    if script.DefaultLangSys != None:
        moveFeatureInLangSys(script.DefaultLangSys, featureRecords, features, target)
    for langSysRecord in script.LangSysRecord:
        moveFeatureInLangSys(langSysRecord.LangSys, featureRecords, features, target)


def moveFeature(font: TTFont, features: list, target: str):
    if len(features) == 0 or "GSUB" not in font:
        return

    table = font["GSUB"].table
    featureRecords = table.FeatureList.FeatureRecord
    scriptRecords = table.ScriptList.ScriptRecord
    for scriptRecord in scriptRecords:
        moveFeatureInScript(scriptRecord.Script, featureRecords, features, target)


def subset(font: TTFont, unicodes: str):
    if unicodes == "":
        return
    sub = Subsetter(SSOptions(layout_features=["*"])) # keep all features
    sub.populate(unicodes=parse_unicodes(unicodes))
    sub.subset(font)


def loadFont():
    global inputFont
    inputFont = TTFont(file="input.ttf", recalcBBoxes=False)

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


def processFont(args):
    main(args.to_py(), "input.ttf")


def main(args, filename):
    font = TTFont(file=filename, recalcBBoxes=False)
    instantiateFont(font, args.get("options"), args.get("variations"))
    removeFeature(font, args.get("disables"))
    moveFeature(font, args.get("features"), args.get("options").get("target"))
    subset(font, args.get("unicodes"))
    font.save("output.ttf")
