l='big5'
k='lineHeight'
j='hmtx'
i='cmap'
h='DELT'
g='version'
f='typo_subfamily'
e='typo_family'
d='subfamily'
c='family'
b='disables'
a='features'
Z='Bold Italic'
Y='Italic'
X='Bold'
W='Regular'
I=False
N=print
B='hhea'
R='OS/2'
Q='options'
P=len
L=Exception
H='input'
E='GSUB'
G='fvar'
F=True
D=None
C='name'
import os,math as O
from typing import cast
from fontTools import version as A
from fontTools.ttLib import TTFont as m
from fontTools.subset import Subsetter as n,Options as o,parse_unicodes as p
from fontTools.varLib.instancer import instantiateVariableFont as q
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable as r
from fontTools.ttLib.tables.otTables import featureParamTypes as s,FeatureParamsStylisticSet as t,FeatureParamsCharacterVariants as u
J=F
v={W:0,X:1,Y:2,Z:3}
def w(A,B):
	for D in A[G].axes:
		if D.axisTag==B:return A[C].getDebugName(D.axisNameID)
	return B
class K:
	def __init__(A,B,M):
		W=', ';X=M.get('variations');H=M.get(Q);E=B[C].getBestFamilyName();Z=B[C].getDebugName(5);N=f"Frozen from {E} {Z}.";Y=cast(bool,H.get('keepVar'))
		if G in B and not Y:h=W.join(f"{w(B,A)}={C}"for(A,C)in X.items());N+=f" Sets {h}.";q(B,X,inplace=F,overlap=F)
		S=M.get(a)
		if P(S)>0:S=W.join(S);N+=f" Activates {S}."
		T=M.get(b)
		if P(T)>0:T=W.join(T);N+=f" Deactivates {T}."
		if not J:N+=' Use fallback mode.'
		A.nameTable=B[C];i=A.nameTable.names;A.nameTable.names=[];E=H.get(c);D=H.get(d);V=H.get(e);O=H.get(f)
		if not V:V=E
		if not O or O==D:O=D;U=f"{E} {D}"
		else:U=f"{E} {O} {D}"
		A.setName(E,1);A.setName(D,2);A.setName(U,3);A.setName(U,4);A.setName('Version 1.000',5);A.setName(K.getPostscriptName(E,D),6);A.setName('FontFreeze'+M.get(g),8);A.setName(N,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11);A.setName(V,16);A.setName(O,17);A.setName(U,18)
		for I in i:
			if I.nameID>25:A.nameTable.setName(I.string,I.nameID,I.platformID,I.platEncID,I.langID)
		try:B['head'].macStyle=v[D];B[R].fsSelection=K.makeSelection(B[R].fsSelection,D)
		except L:pass
		if not Y:K.dropVariationTables(B)
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
		if B==W:A|=64
		else:A&=~64
		if B==X or B==Z:A|=32
		else:A&=~32
		if B==Y:A|=1
		else:A&=~1
		if not A:A=64
		return A
def x(A,B):
	if P(B)==0 or E not in A:return
	D=A[E].table.FeatureList.FeatureRecord
	for C in D:
		if C.FeatureTag in B:S(C)
def S(A):
	A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0
	if J:A.FeatureTag=h
class T:
	def __init__(A,D,B):
		A.font=D;A.features=B.get(a);A.target=B.get(Q).get('target');A.singleSub=B.get(Q).get('singleSub')
		if P(A.features)==0 or E not in A.font:return
		A.cmapTables=A.font[i].tables;A.unicodeGlyphs={B for A in A.cmapTables for B in A.cmap.values()};C=A.font[E].table;A.featureRecords=C.FeatureList.FeatureRecord;A.lookup=C.LookupList.Lookup;F=C.ScriptList.ScriptRecord
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
				if C is D:C=A;s[B.target]=t if A.FeatureTag.startswith('ss')else u;A.FeatureTag=B.target
				else:T.moveFeatureLookups(A.Feature,C.Feature);S(A)
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
def y(D,B):
	A='*'
	if B=='':return
	C=n(o(layout_scripts=[A],layout_features=[A],name_IDs=[A],name_languages=[A]));C.populate(unicodes=p(B));C.subset(D)
def A3(font,from_width,to_width):
	D=from_width;C=to_width;A=font;E=A[j];G=A.getBestCmap();H=(C-D)/2
	for(K,F)in G.items():
		I,J=E[F]
		if I==D:E[F]=C,J+H
	A[B].advanceWidthMax=max(C,A[B].advanceWidthMax)
def z(font,delta):
	E=delta;C=font;F=C[j];H=C.getBestCmap();D=0
	for(J,G)in H.items():
		A,I=F[G];A+=E;F[G]=A,I+E/2
		if A>D:D=A
	C[B].advanceWidthMax=D
def A0(font,delta):C=font[R];D=C.usWinAscent;A=C.usWinDescent;F=D+A;G=F+delta;D=O.ceil(D*G/F);A=O.floor(A*G/F);E=font[B];E.ascent=E.ascender=C.usWinAscent=D;C.usWinDescent=A;E.descent=E.descender=-A
def loadFont(K):
	B=M(K);I=B[R];A=B[C];J=B[E].table.FeatureList.FeatureRecord if E in B else[];J=[A.FeatureTag for A in J];O={'axes':[{'tag':B.axisTag,'default':B.defaultValue,'min':B.minValue,'max':B.maxValue,C:A.getDebugName(B.axisNameID)}for B in B[G].axes],'instances':[{C:A.getDebugName(B.subfamilyNameID),'coordinates':B.coordinates}for B in B[G].instances]}if G in B else D
	if os.path.exists(H):os.remove(H)
	os.rename(K,H);L={c:A.getBestFamilyName(),d:A.getDebugName(2),'copyright':A.getDebugName(0),'id':A.getDebugName(3),g:A.getDebugName(5),'trademark':A.getDebugName(7),'manufacturer':A.getDebugName(8),'designer':A.getDebugName(9),'description':A.getDebugName(10),'vendorURL':A.getDebugName(11),'designerURL':A.getDebugName(12),'license':A.getDebugName(13),'licenseURL':A.getDebugName(14),e:A.getDebugName(16),f:A.getDebugName(17),G:O,'gsub':list(dict.fromkeys(J)),'fontHeight':I.sTypoAscender-I.sTypoDescender,k:I.usWinAscent+I.usWinDescent}
	if B.getBestCmap()is D and A1(B):N('Legacy CJK font detected.');U(B);L['preview']=F
	return L
def A1(E):
	D=E[i]
	for B in D.tables:
		if B.platformID==3 and B.platEncID==4:
			A=r.newSubtable(4);A.platformID=3;A.platEncID=1;A.language=0;A.cmap={}
			for C in B.cmap:
				try:G=ord(C.to_bytes(2,byteorder='big').decode(l))if C>255 else C;A.cmap[G]=B.cmap[C]
				except L:pass
			D.tables=[A];return F
	return I
def A2(B):
	A=B.string.decode('utf_16_be');A=bytes(A,encoding='raw_unicode_escape')
	try:A.decode(l);B.string=A
	except L:pass
def M(D):
	B=m(file=D,recalcBBoxes=I,fontNumber=0)
	for A in B[C].names:
		if A.platformID==3 and A.platEncID==4:
			try:A.toStr()
			except L:A2(A)
	return B
def U(A):
	B='mort'
	if B in A:
		try:A[B].ensureDecompiled()
		except L:N('Drop corrupted mort table.');del A[B]
	A.save(H,reorderTables=D)
def processLegacy():A=M(H);U(A)
def processFont(A):main(A.to_py(),H,'output')
def main(B,C,D):
	global J;J=F;A=V(B,C)
	try:A.save(D)
	except AssertionError as E:
		if h in str(E):J=I;A=V(B,C);A.save(D)
		else:raise
def V(args,filename):
	F='woff2';B=args;A=M(filename);K(A,B);x(A,B.get(b));T(A,B);y(A,B.get('unicodes'));C=B.get(Q);D=C.get('spacing')
	if D!=0:z(A,D)
	E=C.get(k)
	if E!=0:A0(A,E)
	if C.get('format')==F:A.flavor=F
	return A
N(f"FontTools version: {A}")