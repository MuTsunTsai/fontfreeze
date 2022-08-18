_M='version'
_L='family'
_K='disables'
_J='features'
_I='Bold Italic'
_H='Italic'
_G='Regular'
_F='input'
_E='options'
_D=None
_C='GSUB'
_B='fvar'
_A='name'
import os
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter,Options as SSOptions,parse_unicodes
from fontTools.varLib.instancer import instantiateVariableFont
PLAT_MAC=1
PLAT_WINDOWS=3
ENC_ROMAN=0
ENC_UNICODE_11=1
LANG_ENGLISH=1033
MACSTYLE={_G:0,'Bold':1,_H:2,_I:3}
OVERLAP_SIMPLE=64
OVERLAP_COMPOUND=1024
def getAxisName(font,tag):
	for A in font[_B].axes:
		if A.axisTag==tag:return font[_A].getDebugName(A.axisNameID)
	return tag
class Instantiate:
	def __init__(A,font,args):
		N='OS/2';K=True;J=', ';C=args;B=font;L=C.get('variations');I=C.get(_E);D=B[_A].getBestFamilyName();O=B[_A].getDebugName(5);F=f"Frozen from {D} {O}."
		if _B in B:P=J.join((f"{getAxisName(B,A)}={C}"for(A,C)in L.items()));F+=f" Sets {P}.";instantiateVariableFont(B,L,inplace=K,overlap=K)
		G=C.get(_J)
		if len(G)>0:G=J.join(G);F+=f" Activates {G}."
		H=C.get(_K)
		if len(H)>0:H=J.join(H);F+=f" Deactivates {H}."
		A.nameTable=B[_A];A.nameTable.names=[];D=I.get(_L);E=I.get('subfamily');M=f"{D} {E}";A.setName(D,1);A.setName(E,2);A.setName(M,3);A.setName(M,4);A.setName('Version 1.000',5);A.setName(Instantiate.getPostscriptName(D,E),6);A.setName('FontFreeze'+C.get(_M),8);A.setName(F,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11)
		try:B['head'].macStyle=MACSTYLE[E];B[N].fsSelection=Instantiate.makeSelection(B[N].fsSelection,E)
		except:pass
		Instantiate.dropVariationTables(B)
		if I.get('fixContour')==K:Instantiate.setOverlapFlags(B)
	def getPostscriptName(A,subfamilyName):B=subfamilyName;A=A.replace(' ','');B=B.replace(' ','');return f"{A}-{B}"
	def setName(A,content,index):C=index;B=content;A.nameTable.setName(B,C,PLAT_MAC,ENC_ROMAN,0);A.nameTable.setName(B,C,PLAT_WINDOWS,ENC_UNICODE_11,LANG_ENGLISH)
	def dropVariationTables(A):
		for B in 'STAT cvar fvar gvar'.split():
			if B in A.keys():del A[B]
	def setOverlapFlags(C):
		B=C['glyf']
		for D in B.keys():
			A=B[D]
			if A.isComposite():A.components[0].flags|=OVERLAP_COMPOUND
			elif A.numberOfContours>0:A.flags[0]|=OVERLAP_SIMPLE
	def makeSelection(A,style):
		B=style;A=A^A
		if B==_G:A|=64
		else:A&=~ 64
		if B=='Bold'or B==_I:A|=32
		else:A&=~ 32
		if B==_H:A|=1
		else:A&=~ 1
		if not A:A=64
		return A
def removeFeature(font,features):
	A=features
	if len(A)==0 or _C not in font:return
	C=font[_C].table.FeatureList.FeatureRecord
	for B in C:
		if B.FeatureTag in A:clearFeatureRecord(B)
def clearFeatureRecord(featureRecord):A=featureRecord;A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0;A.FeatureTag='DELT'
class Activator:
	def __init__(A,font,args):
		B=args;A.font=font;A.features=B.get(_J);A.target=B.get(_E).get('target');A.singleSub=B.get(_E).get('singleSub')
		if len(A.features)==0 or _C not in A.font:return
		A.cmapTables=A.font['cmap'].tables;A.unicodeGlyphs={C for B in A.cmapTables for C in B.cmap.values()};C=A.font[_C].table;A.featureRecords=C.FeatureList.FeatureRecord;A.lookup=C.LookupList.Lookup;D=C.ScriptList.ScriptRecord
		for E in D:A.activateInScript(E.Script)
	def activateInScript(B,script):
		A=script
		if A.DefaultLangSys!=_D:B.activateInLangSys(A.DefaultLangSys)
		for C in A.LangSysRecord:B.activateInLangSys(C.LangSys)
	def activateInLangSys(B,langSys):
		E=langSys;C=_D
		for D in E.FeatureIndex:
			A=B.featureRecords[D]
			if A.FeatureTag==B.target:C=A
		for D in E.FeatureIndex:
			A=B.featureRecords[D]
			if A.FeatureTag in B.features:
				if B.singleSub:B.findSingleSubstitution(A)
				if C==_D:C=A;A.FeatureTag=B.target
				else:Activator.moveFeatureLookups(A.Feature,C.Feature);clearFeatureRecord(A)
		if C!=_D:C.Feature.LookupListIndex.sort()
	def findSingleSubstitution(A,featureRecord):
		for C in featureRecord.Feature.LookupListIndex:
			B=A.lookup[C]
			if B.LookupType==1:
				for D in B.SubTable:
					for (input,E) in D.mapping.items():
						if input in A.unicodeGlyphs:A.singleSubstitution(input,E)
	def singleSubstitution(C,input,output):
		for A in C.cmapTables:
			for B in A.cmap:
				if A.cmap[B]==input:A.cmap[B]=output
	def moveFeatureLookups(A,toFeature):B=toFeature;B.LookupListIndex.extend(A.LookupListIndex);B.LookupCount+=A.LookupCount
def subset(font,unicodes):
	B=unicodes;A='*'
	if B=='':return
	C=Subsetter(SSOptions(layout_scripts=[A],layout_features=[A],name_IDs=[A],name_languages=[A]));C.populate(unicodes=parse_unicodes(B));C.subset(font)
def loadFont():
	D='temp';A=loadTtfFont(D);B=A[_C].table.FeatureList.FeatureRecord if _C in A else[];B=[A.FeatureTag for A in B];C=_D
	if _B in A:C={'axes':[{'tag':B.axisTag,'default':B.defaultValue,'min':B.minValue,'max':B.maxValue,_A:A[_A].getDebugName(B.axisNameID)}for B in A[_B].axes],'instances':[{_A:A[_A].getDebugName(B.subfamilyNameID),'coordinates':B.coordinates}for B in A[_B].instances]}
	if os.path.exists(_F):os.remove(_F)
	os.rename(D,_F);return{_L:A[_A].getBestFamilyName(),'copyright':A[_A].getDebugName(0),'id':A[_A].getDebugName(3),_M:A[_A].getDebugName(5),'trademark':A[_A].getDebugName(7),'manufacturer':A[_A].getDebugName(8),'designer':A[_A].getDebugName(9),'description':A[_A].getDebugName(10),'vendorURL':A[_A].getDebugName(11),'designerURL':A[_A].getDebugName(12),'license':A[_A].getDebugName(13),'licenseURL':A[_A].getDebugName(14),_B:C,'gsub':list(dict.fromkeys(B))}
def loadTtfFont(filename):return TTFont(file=filename,recalcBBoxes=False,fontNumber=0)
def processFont(args):main(args.to_py(),_F,'output')
def main(args,filename,output):
	C='woff2';B=args;A=loadTtfFont(filename);Instantiate(A,B);removeFeature(A,B.get(_K));Activator(A,B);subset(A,B.get('unicodes'))
	if B.get(_E).get('format')==C:A.flavor=C
	A.save(output)