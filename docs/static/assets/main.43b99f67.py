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
S=print
M=False
P='options'
O=len
K=Exception
H='input'
E='GSUB'
G='fvar'
F=True
D=None
C='name'
import os
from typing import cast
from fontTools.ttLib import TTFont as h
from fontTools.subset import Subsetter as i,Options as j,parse_unicodes as k
from fontTools.varLib.instancer import instantiateVariableFont as l
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable as m
from fontTools.ttLib.tables.otTables import featureParamTypes as n,FeatureParamsStylisticSet as o,FeatureParamsCharacterVariants as p
I=F
q={T:0,U:1,V:2,W:3}
def r(A,B):
	for D in A[G].axes:
		if D.axisTag==B:return A[C].getDebugName(D.axisNameID)
	return B
class J:
	def __init__(A,B,L):
		e='OS/2';U=', ';V=L.get('variations');H=L.get(P);E=B[C].getBestFamilyName();f=B[C].getDebugName(5);M=f"Frozen from {E} {f}.";W=cast(bool,H.get('keepVar'))
		if G in B and not W:g=U.join(f"{r(B,A)}={C}"for(A,C)in V.items());M+=f" Sets {g}.";l(B,V,inplace=F,overlap=F)
		Q=L.get(X)
		if O(Q)>0:Q=U.join(Q);M+=f" Activates {Q}."
		R=L.get(Y)
		if O(R)>0:R=U.join(R);M+=f" Deactivates {R}."
		if not I:M+=' Use fallback mode.'
		A.nameTable=B[C];A.nameTable.names=[];E=H.get(Z);D=H.get(a);T=H.get(b);N=H.get(c)
		if not T:T=E
		if not N or N==D:N=D;S=f"{E} {D}"
		else:S=f"{E} {N} {D}"
		A.setName(E,1);A.setName(D,2);A.setName(S,3);A.setName(S,4);A.setName('Version 1.000',5);A.setName(J.getPostscriptName(E,D),6);A.setName('FontFreeze'+L.get(d),8);A.setName(M,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11);A.setName(T,16);A.setName(N,17);A.setName(S,18)
		try:B['head'].macStyle=q[D];B[e].fsSelection=J.makeSelection(B[e].fsSelection,D)
		except K:pass
		if not W:J.dropVariationTables(B)
		if H.get('fixContour'):J.setOverlapFlags(B)
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
	if O(B)==0 or E not in A:return
	D=A[E].table.FeatureList.FeatureRecord
	for C in D:
		if C.FeatureTag in B:N(C)
def N(A):
	A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0
	if I:A.FeatureTag=e
class Q:
	def __init__(A,D,B):
		A.font=D;A.features=B.get(X);A.target=B.get(P).get('target');A.singleSub=B.get(P).get('singleSub')
		if O(A.features)==0 or E not in A.font:return
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
				else:Q.moveFeatureLookups(A.Feature,C.Feature);N(A)
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
def A(font,from_width,to_width):
	F='hhea';C=from_width;B=to_width;A=font;D=A['hmtx'];G=A.getBestCmap();H=(B-C)/2
	for(K,E)in G.items():
		I,J=D[E]
		if I==C:D[E]=B,J+H
	A[F].advanceWidthMax=max(B,A[F].advanceWidthMax)
def loadFont(J):
	B=L(J);A=B[C];I=B[E].table.FeatureList.FeatureRecord if E in B else[];I=[A.FeatureTag for A in I];M={'axes':[{'tag':B.axisTag,'default':B.defaultValue,'min':B.minValue,'max':B.maxValue,C:A.getDebugName(B.axisNameID)}for B in B[G].axes],'instances':[{C:A.getDebugName(B.subfamilyNameID),'coordinates':B.coordinates}for B in B[G].instances]}if G in B else D
	if os.path.exists(H):os.remove(H)
	os.rename(J,H);K={Z:A.getBestFamilyName(),a:A.getDebugName(2),'copyright':A.getDebugName(0),'id':A.getDebugName(3),d:A.getDebugName(5),'trademark':A.getDebugName(7),'manufacturer':A.getDebugName(8),'designer':A.getDebugName(9),'description':A.getDebugName(10),'vendorURL':A.getDebugName(11),'designerURL':A.getDebugName(12),'license':A.getDebugName(13),'licenseURL':A.getDebugName(14),b:A.getDebugName(16),c:A.getDebugName(17),G:M,'gsub':list(dict.fromkeys(I))}
	if B.getBestCmap()is D and u(B):S('Legacy CJK font detected.');R(B);K['preview']=F
	return K
def u(E):
	D=E[f]
	for B in D.tables:
		if B.platformID==3 and B.platEncID==4:
			A=m.newSubtable(4);A.platformID=3;A.platEncID=1;A.language=0;A.cmap={}
			for C in B.cmap:
				try:G=ord(C.to_bytes(2,byteorder='big').decode(g))if C>255 else C;A.cmap[G]=B.cmap[C]
				except K:pass
			D.tables=[A];return F
	return M
def v(B):
	A=B.string.decode('utf_16_be');A=bytes(A,encoding='raw_unicode_escape')
	try:A.decode(g);B.string=A
	except K:pass
def L(D):
	B=h(file=D,recalcBBoxes=M,fontNumber=0)
	for A in B[C].names:
		if A.platformID==3 and A.platEncID==4:
			try:A.toStr()
			except K:v(A)
	return B
def R(A):
	B='mort'
	if B in A:
		try:A[B].ensureDecompiled()
		except K:S('Drop corrupted mort table.');del A[B]
	A.save(H,reorderTables=D)
def processLegacy():A=L(H);R(A)
def processFont(A):main(A.to_py(),H,'output')
def main(C,D,E):
	global I;I=F;A=B(C,D)
	try:A.save(E)
	except AssertionError as G:
		if e in str(G):I=M;A=B(C,D);A.save(E)
		else:raise
def B(args,filename):
	C='woff2';B=args;A=L(filename);J(A,B);s(A,B.get(Y));Q(A,B);t(A,B.get('unicodes'))
	if B.get(P).get('format')==C:A.flavor=C
	return A