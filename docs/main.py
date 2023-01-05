c='big5'
b='cmap'
a='DELT'
Z='version'
Y='family'
X='disables'
W='features'
V='Bold Italic'
U='Italic'
T='Bold'
S='Regular'
R=print
K=False
N='options'
M=len
F='input'
D='GSUB'
G='fvar'
C=None
E=True
B='name'
import os
from fontTools.ttLib import TTFont as d
from fontTools.subset import Subsetter as e,Options as f,parse_unicodes as g
from fontTools.varLib.instancer import instantiateVariableFont as h
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable as i
H=E
j={S:0,T:1,U:2,V:3}
def k(A,C):
	for D in A[G].axes:
		if D.axisTag==C:return A[B].getDebugName(D.axisNameID)
	return C
class I:
	def __init__(A,C,J):
		U='OS/2';S=', ';T=J.get('variations');O=J.get(N);F=C[B].getBestFamilyName();V=C[B].getDebugName(5);K=f"Frozen from {F} {V}."
		if G in C:a=S.join((f"{k(C,A)}={B}"for(A,B)in T.items()));K+=f" Sets {a}.";h(C,T,inplace=E,overlap=E)
		P=J.get(W)
		if M(P)>0:P=S.join(P);K+=f" Activates {P}."
		Q=J.get(X)
		if M(Q)>0:Q=S.join(Q);K+=f" Deactivates {Q}."
		if not H:K+=' Use fallback mode.'
		A.nameTable=C[B];A.nameTable.names=[];F=O.get(Y);D=O.get('subfamily');L=O.get('typo_subfamily')
		if not L or L==D:L=D;R=f"{F} {D}"
		else:R=f"{F} {L} {D}"
		A.setName(F,1);A.setName(D,2);A.setName(R,3);A.setName(R,4);A.setName('Version 1.000',5);A.setName(I.getPostscriptName(F,D),6);A.setName('FontFreeze'+J.get(Z),8);A.setName(K,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11);A.setName(F,16);A.setName(L,17);A.setName(R,18)
		try:C['head'].macStyle=j[D];C[U].fsSelection=I.makeSelection(C[U].fsSelection,D)
		except:pass
		I.dropVariationTables(C)
		if O.get('fixContour')==E:I.setOverlapFlags(C)
	def getPostscriptName(A,B):A=A.replace(' ','');B=B.replace(' ','');C=f"{A}-{B}";return C[:63]
	def setName(A,B,C):A.nameTable.setName(B,C,3,1,1033)
	def dropVariationTables(A):
		for B in 'STAT cvar fvar gvar'.split():
			if B in A.keys():del A[B]
	def setOverlapFlags(C):
		B=C['glyf']
		for D in B.keys():
			A=B[D]
			if A.isComposite():A.components[0].flags|=1024
			elif A.numberOfContours>0:A.flags[0]|=64
	def makeSelection(A,B):
		A=A^A
		if B==S:A|=64
		else:A&=~ 64
		if B==T or B==V:A|=32
		else:A&=~ 32
		if B==U:A|=1
		else:A&=~ 1
		if not A:A=64
		return A
def l(A,B):
	if M(B)==0 or D not in A:return
	E=A[D].table.FeatureList.FeatureRecord
	for C in E:
		if C.FeatureTag in B:L(C)
def L(A):
	A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0
	if H:A.FeatureTag=a
class O:
	def __init__(A,E,B):
		A.font=E;A.features=B.get(W);A.target=B.get(N).get('target');A.singleSub=B.get(N).get('singleSub')
		if M(A.features)==0 or D not in A.font:return
		A.cmapTables=A.font[b].tables;A.unicodeGlyphs={C for B in A.cmapTables for C in B.cmap.values()};C=A.font[D].table;A.featureRecords=C.FeatureList.FeatureRecord;A.lookup=C.LookupList.Lookup;F=C.ScriptList.ScriptRecord
		for G in F:A.activateInScript(G.Script)
	def activateInScript(B,A):
		if A.DefaultLangSys!=C:B.activateInLangSys(A.DefaultLangSys)
		for D in A.LangSysRecord:B.activateInLangSys(D.LangSys)
	def activateInLangSys(B,F):
		D=C
		for E in F.FeatureIndex:
			A=B.featureRecords[E]
			if A.FeatureTag==B.target:D=A
		for E in F.FeatureIndex:
			A=B.featureRecords[E]
			if A.FeatureTag in B.features:
				if B.singleSub:B.findSingleSubstitution(A)
				if D==C:D=A;A.FeatureTag=B.target
				else:O.moveFeatureLookups(A.Feature,D.Feature);L(A)
		if D!=C:D.Feature.LookupListIndex.sort()
	def findSingleSubstitution(A,D):
		for E in D.Feature.LookupListIndex:
			B=A.lookup[E]
			if B.LookupType==1:
				for F in B.SubTable:
					for (C,G) in F.mapping.items():
						if C in A.unicodeGlyphs:A.singleSubstitution(C,G)
	def singleSubstitution(C,D,E):
		for A in C.cmapTables:
			for B in A.cmap:
				if A.cmap[B]==D:A.cmap[B]=E
	def moveFeatureLookups(A,B):B.LookupListIndex.extend(A.LookupListIndex);B.LookupCount+=A.LookupCount
def m(D,B):
	A='*'
	if B=='':return
	C=e(f(layout_scripts=[A],layout_features=[A],name_IDs=[A],name_languages=[A]));C.populate(unicodes=g(B));C.subset(D)
def loadFont(I):
	A=J(I);H=A[D].table.FeatureList.FeatureRecord if D in A else[];H=[A.FeatureTag for A in H];L={'axes':[{'tag':C.axisTag,'default':C.defaultValue,'min':C.minValue,'max':C.maxValue,B:A[B].getDebugName(C.axisNameID)}for C in A[G].axes],'instances':[{B:A[B].getDebugName(C.subfamilyNameID),'coordinates':C.coordinates}for C in A[G].instances]}if G in A else C
	if os.path.exists(F):os.remove(F)
	os.rename(I,F);K={Y:A[B].getBestFamilyName(),'copyright':A[B].getDebugName(0),'id':A[B].getDebugName(3),Z:A[B].getDebugName(5),'trademark':A[B].getDebugName(7),'manufacturer':A[B].getDebugName(8),'designer':A[B].getDebugName(9),'description':A[B].getDebugName(10),'vendorURL':A[B].getDebugName(11),'designerURL':A[B].getDebugName(12),'license':A[B].getDebugName(13),'licenseURL':A[B].getDebugName(14),G:L,'gsub':list(dict.fromkeys(H))}
	if A.getBestCmap()==C and n(A):R('Legacy CJK font detected.');P(A);K['preview']=E
	return K
def n(F):
	D=F[b]
	for B in D.tables:
		if B.platformID==3 and B.platEncID==4:
			A=i.newSubtable(4);A.platformID=3;A.platEncID=1;A.language=0;A.cmap={}
			for C in B.cmap:
				try:G=ord(C.to_bytes(2,byteorder='big').decode(c))if C>255 else C;A.cmap[G]=B.cmap[C]
				except:pass
			D.tables=[A];return E
	return K
def o(B):
	A=B.string.decode('utf_16_be');A=bytes(A,encoding='raw_unicode_escape')
	try:A.decode(c);B.string=A
	except:pass
def J(D):
	C=d(file=D,recalcBBoxes=K,fontNumber=0)
	for A in C[B].names:
		if A.platformID==3 and A.platEncID==4:
			try:A.toStr()
			except:o(A)
	return C
def P(A):
	B='mort'
	if B in A:
		try:A[B].ensureDecompiled()
		except:R('Drop corrupted mort table.');del A[B]
	A.save(F,reorderTables=C)
def processLegacy():A=J(F);P(A)
def processFont(A):main(A.to_py(),F,'output')
def main(B,C,D):
	global H;H=E;A=Q(B,C)
	try:A.save(D)
	except AssertionError as F:
		if a in str(F):H=K;A=Q(B,C);A.save(D)
		else:raise
def Q(args,filename):
	C='woff2';B=args;A=J(filename);I(A,B);l(A,B.get(X));O(A,B);m(A,B.get('unicodes'))
	if B.get(N).get('format')==C:A.flavor=C
	return A