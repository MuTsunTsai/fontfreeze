g='big5'
f='cmap'
e='DELT'
d='version'
c='typo_subfamily'
b='typo_family'
a='subfamily'
Z='family'
Y='disables'
X='features'
W='Bold Italic'
V='Italic'
U='Bold'
T='Regular'
N=False
M=print
Q='options'
P=len
L=Exception
H='input'
E='GSUB'
G='fvar'
F=True
D=None
C='name'
import os
from typing import cast
from fontTools import version as A
from fontTools.ttLib import TTFont as h
from fontTools.subset import Subsetter as i,Options as j,parse_unicodes as k
from fontTools.varLib.instancer import instantiateVariableFont as l
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable as m
from fontTools.ttLib.tables.otTables import featureParamTypes as n,FeatureParamsStylisticSet as o,FeatureParamsCharacterVariants as p
J=F
q={T:0,U:1,V:2,W:3}
def r(A,B):
	for D in A[G].axes:
		if D.axisTag==B:return A[C].getDebugName(D.axisNameID)
	return B
class K:
	def __init__(A,B,M):
		f='OS/2';V=', ';W=M.get('variations');H=M.get(Q);E=B[C].getBestFamilyName();g=B[C].getDebugName(5);N=f"Frozen from {E} {g}.";e=cast(bool,H.get('keepVar'))
		if G in B and not e:h=V.join(f"{r(B,A)}={C}"for(A,C)in W.items());N+=f" Sets {h}.";l(B,W,inplace=F,overlap=F)
		R=M.get(X)
		if P(R)>0:R=V.join(R);N+=f" Activates {R}."
		S=M.get(Y)
		if P(S)>0:S=V.join(S);N+=f" Deactivates {S}."
		if not J:N+=' Use fallback mode.'
		A.nameTable=B[C];i=A.nameTable.names;A.nameTable.names=[];E=H.get(Z);D=H.get(a);U=H.get(b);O=H.get(c)
		if not U:U=E
		if not O or O==D:O=D;T=f"{E} {D}"
		else:T=f"{E} {O} {D}"
		A.setName(E,1);A.setName(D,2);A.setName(T,3);A.setName(T,4);A.setName('Version 1.000',5);A.setName(K.getPostscriptName(E,D),6);A.setName('FontFreeze'+M.get(d),8);A.setName(N,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11);A.setName(U,16);A.setName(O,17);A.setName(T,18)
		for I in i:
			if I.nameID>25:A.nameTable.setName(I.string,I.nameID,I.platformID,I.platEncID,I.langID)
		try:B['head'].macStyle=q[D];B[f].fsSelection=K.makeSelection(B[f].fsSelection,D)
		except L:pass
		if not e:K.dropVariationTables(B)
		if H.get('fixContour'):K.setOverlapFlags(B)
	def getPostscriptName(A,B):A=A.replace(' ','');B=B.replace(' ','');C=f"{A}-{B}";return C[:63]
	def setName(A,B,C):A.nameTable.setName(B,C,3,1,1033)
	def dropVariationTables(A):
		for B in'STAT cvar fvar gvar'.split():
			if B in A.keys():del A[B]
	def setOverlapFlags(C):
		B=C['glyf']
		for D in B.keys():
			A=B[D]
			if A.isComposite():A.components[0].flags|=1024
			elif A.numberOfContours>0:A.flags[0]|=64
	def makeSelection(A,B):
		A=A^A
		if B==T:A|=64
		else:A&=~64
		if B==U or B==W:A|=32
		else:A&=~32
		if B==V:A|=1
		else:A&=~1
		if not A:A=64
		return A
def s(A,B):
	if P(B)==0 or E not in A:return
	D=A[E].table.FeatureList.FeatureRecord
	for C in D:
		if C.FeatureTag in B:O(C)
def O(A):
	A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0
	if J:A.FeatureTag=e
class R:
	def __init__(A,D,B):
		A.font=D;A.features=B.get(X);A.target=B.get(Q).get('target');A.singleSub=B.get(Q).get('singleSub')
		if P(A.features)==0 or E not in A.font:return
		A.cmapTables=A.font[f].tables;A.unicodeGlyphs={B for A in A.cmapTables for B in A.cmap.values()};C=A.font[E].table;A.featureRecords=C.FeatureList.FeatureRecord;A.lookup=C.LookupList.Lookup;F=C.ScriptList.ScriptRecord
		for G in F:A.activateInScript(G.Script)
	def activateInScript(B,A):
		if A.DefaultLangSys is not D:B.activateInLangSys(A.DefaultLangSys)
		for C in A.LangSysRecord:B.activateInLangSys(C.LangSys)
	def activateInLangSys(B,F):
		C=D
		for E in F.FeatureIndex:
			A=B.featureRecords[E]
			if A.FeatureTag==B.target:C=A
		for E in F.FeatureIndex:
			A=B.featureRecords[E]
			if A.FeatureTag in B.features:
				if B.singleSub:B.findSingleSubstitution(A)
				if C is D:C=A;n[B.target]=o if A.FeatureTag.startswith('ss')else p;A.FeatureTag=B.target
				else:R.moveFeatureLookups(A.Feature,C.Feature);O(A)
		if C is not D:C.Feature.LookupListIndex.sort()
	def findSingleSubstitution(A,D):
		for E in D.Feature.LookupListIndex:
			B=A.lookup[E]
			if B.LookupType==1:
				for F in B.SubTable:
					for(C,G)in F.mapping.items():
						if C in A.unicodeGlyphs:A.singleSubstitution(C,G)
	def singleSubstitution(C,D,E):
		for A in C.cmapTables:
			for B in A.cmap:
				if A.cmap[B]==D:A.cmap[B]=E
	def moveFeatureLookups(A,B):B.LookupListIndex.extend(A.LookupListIndex);B.LookupCount+=A.LookupCount
def t(D,B):
	A='*'
	if B=='':return
	C=i(j(layout_scripts=[A],layout_features=[A],name_IDs=[A],name_languages=[A]));C.populate(unicodes=k(B));C.subset(D)
def w(font,from_width,to_width):
	F='hhea';C=from_width;B=to_width;A=font;D=A['hmtx'];G=A.getBestCmap();H=(B-C)/2
	for(K,E)in G.items():
		I,J=D[E]
		if I==C:D[E]=B,J+H
	A[F].advanceWidthMax=max(B,A[F].advanceWidthMax)
def loadFont(K):
	B=I(K);A=B[C];J=B[E].table.FeatureList.FeatureRecord if E in B else[];J=[A.FeatureTag for A in J];N={'axes':[{'tag':B.axisTag,'default':B.defaultValue,'min':B.minValue,'max':B.maxValue,C:A.getDebugName(B.axisNameID)}for B in B[G].axes],'instances':[{C:A.getDebugName(B.subfamilyNameID),'coordinates':B.coordinates}for B in B[G].instances]}if G in B else D
	if os.path.exists(H):os.remove(H)
	os.rename(K,H);L={Z:A.getBestFamilyName(),a:A.getDebugName(2),'copyright':A.getDebugName(0),'id':A.getDebugName(3),d:A.getDebugName(5),'trademark':A.getDebugName(7),'manufacturer':A.getDebugName(8),'designer':A.getDebugName(9),'description':A.getDebugName(10),'vendorURL':A.getDebugName(11),'designerURL':A.getDebugName(12),'license':A.getDebugName(13),'licenseURL':A.getDebugName(14),b:A.getDebugName(16),c:A.getDebugName(17),G:N,'gsub':list(dict.fromkeys(J))}
	if B.getBestCmap()is D and u(B):M('Legacy CJK font detected.');S(B);L['preview']=F
	return L
def u(E):
	D=E[f]
	for B in D.tables:
		if B.platformID==3 and B.platEncID==4:
			A=m.newSubtable(4);A.platformID=3;A.platEncID=1;A.language=0;A.cmap={}
			for C in B.cmap:
				try:G=ord(C.to_bytes(2,byteorder='big').decode(g))if C>255 else C;A.cmap[G]=B.cmap[C]
				except L:pass
			D.tables=[A];return F
	return N
def v(B):
	A=B.string.decode('utf_16_be');A=bytes(A,encoding='raw_unicode_escape')
	try:A.decode(g);B.string=A
	except L:pass
def I(D):
	B=h(file=D,recalcBBoxes=N,fontNumber=0)
	for A in B[C].names:
		if A.platformID==3 and A.platEncID==4:
			try:A.toStr()
			except L:v(A)
	return B
def S(A):
	B='mort'
	if B in A:
		try:A[B].ensureDecompiled()
		except L:M('Drop corrupted mort table.');del A[B]
	A.save(H,reorderTables=D)
def processLegacy():A=I(H);S(A)
def processFont(A):main(A.to_py(),H,'output')
def main(C,D,E):
	global J;J=F;A=B(C,D)
	try:A.save(E)
	except AssertionError as G:
		if e in str(G):J=N;A=B(C,D);A.save(E)
		else:raise
def B(args,filename):
	C='woff2';B=args;A=I(filename);K(A,B);s(A,B.get(Y));R(A,B);t(A,B.get('unicodes'))
	if B.get(Q).get('format')==C:A.flavor=C
	return A
M(f"FontTools version: {A}")