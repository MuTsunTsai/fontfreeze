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
L=False
P='options'
O=len
K=Exception
E='input'
D='GSUB'
G='fvar'
F=True
C=None
B='name'
import os
from typing import cast
from fontTools.ttLib import TTFont as h
from fontTools.subset import Subsetter as i,Options as j,parse_unicodes as k
from fontTools.varLib.instancer import instantiateVariableFont as l
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable as m
from fontTools.ttLib.tables.otTables import featureParamTypes as n,FeatureParamsStylisticSet as o,FeatureParamsCharacterVariants as p
I=F
q={T:0,U:1,V:2,W:3}
def r(A,C):
	for D in A[G].axes:
		if D.axisTag==C:return A[B].getDebugName(D.axisNameID)
	return C
class J:
	def __init__(A,C,L):
		e='OS/2';U=', ';V=L.get('variations');H=L.get(P);E=C[B].getBestFamilyName();f=C[B].getDebugName(5);M=f"Frozen from {E} {f}.";W=cast(bool,H.get('keepVar'))
		if G in C and not W:g=U.join(f"{r(C,A)}={B}"for(A,B)in V.items());M+=f" Sets {g}.";l(C,V,inplace=F,overlap=F)
		Q=L.get(X)
		if O(Q)>0:Q=U.join(Q);M+=f" Activates {Q}."
		R=L.get(Y)
		if O(R)>0:R=U.join(R);M+=f" Deactivates {R}."
		if not I:M+=' Use fallback mode.'
		A.nameTable=C[B];A.nameTable.names=[];E=H.get(Z);D=H.get(a);T=H.get(b);N=H.get(c)
		if not T:T=E
		if not N or N==D:N=D;S=f"{E} {D}"
		else:S=f"{E} {N} {D}"
		A.setName(E,1);A.setName(D,2);A.setName(S,3);A.setName(S,4);A.setName('Version 1.000',5);A.setName(J.getPostscriptName(E,D),6);A.setName('FontFreeze'+L.get(d),8);A.setName(M,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11);A.setName(T,16);A.setName(N,17);A.setName(S,18)
		try:C['head'].macStyle=q[D];C[e].fsSelection=J.makeSelection(C[e].fsSelection,D)
		except K:pass
		if not W:J.dropVariationTables(C)
		if H.get('fixContour'):J.setOverlapFlags(C)
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
	if O(B)==0 or D not in A:return
	E=A[D].table.FeatureList.FeatureRecord
	for C in E:
		if C.FeatureTag in B:M(C)
def M(A):
	A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0
	if I:A.FeatureTag=e
class N:
	def __init__(A,E,B):
		A.font=E;A.features=B.get(X);A.target=B.get(P).get('target');A.singleSub=B.get(P).get('singleSub')
		if O(A.features)==0 or D not in A.font:return
		A.cmapTables=A.font[f].tables;A.unicodeGlyphs={B for A in A.cmapTables for B in A.cmap.values()};C=A.font[D].table;A.featureRecords=C.FeatureList.FeatureRecord;A.lookup=C.LookupList.Lookup;F=C.ScriptList.ScriptRecord
		for G in F:A.activateInScript(G.Script)
	def activateInScript(B,A):
		if A.DefaultLangSys is not C:B.activateInLangSys(A.DefaultLangSys)
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
				if D is C:D=A;n[B.target]=o if A.FeatureTag.startswith('ss')else p;A.FeatureTag=B.target
				else:N.moveFeatureLookups(A.Feature,D.Feature);M(A)
		if D is not C:D.Feature.LookupListIndex.sort()
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
def loadFont(J):
	A=H(J);I=A[D].table.FeatureList.FeatureRecord if D in A else[];I=[A.FeatureTag for A in I];L={'axes':[{'tag':C.axisTag,'default':C.defaultValue,'min':C.minValue,'max':C.maxValue,B:A[B].getDebugName(C.axisNameID)}for C in A[G].axes],'instances':[{B:A[B].getDebugName(C.subfamilyNameID),'coordinates':C.coordinates}for C in A[G].instances]}if G in A else C
	if os.path.exists(E):os.remove(E)
	os.rename(J,E);K={Z:A[B].getBestFamilyName(),a:A[B].getDebugName(2),'copyright':A[B].getDebugName(0),'id':A[B].getDebugName(3),d:A[B].getDebugName(5),'trademark':A[B].getDebugName(7),'manufacturer':A[B].getDebugName(8),'designer':A[B].getDebugName(9),'description':A[B].getDebugName(10),'vendorURL':A[B].getDebugName(11),'designerURL':A[B].getDebugName(12),'license':A[B].getDebugName(13),'licenseURL':A[B].getDebugName(14),b:A[B].getDebugName(16),c:A[B].getDebugName(17),G:L,'gsub':list(dict.fromkeys(I))}
	if A.getBestCmap()is C and u(A):S('Legacy CJK font detected.');Q(A);K['preview']=F
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
	return L
def v(B):
	A=B.string.decode('utf_16_be');A=bytes(A,encoding='raw_unicode_escape')
	try:A.decode(g);B.string=A
	except K:pass
def H(D):
	C=h(file=D,recalcBBoxes=L,fontNumber=0)
	for A in C[B].names:
		if A.platformID==3 and A.platEncID==4:
			try:A.toStr()
			except K:v(A)
	return C
def Q(A):
	B='mort'
	if B in A:
		try:A[B].ensureDecompiled()
		except K:S('Drop corrupted mort table.');del A[B]
	A.save(E,reorderTables=C)
def processLegacy():A=H(E);Q(A)
def processFont(A):main(A.to_py(),E,'output')
def main(B,C,D):
	global I;I=F;A=R(B,C)
	try:A.save(D)
	except AssertionError as E:
		if e in str(E):I=L;A=R(B,C);A.save(D)
		else:raise
def R(args,filename):
	C='woff2';B=args;A=H(filename);J(A,B);s(A,B.get(Y));N(A,B);t(A,B.get('unicodes'))
	if B.get(P).get('format')==C:A.flavor=C
	return A