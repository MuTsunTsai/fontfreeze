f='big5'
e='cmap'
d='DELT'
c='version'
b='typo_subfamily'
a='typo_family'
Z='subfamily'
Y='family'
X='disables'
W='features'
V='Bold Italic'
U='Italic'
T='Bold'
S='Regular'
R=print
K=False
O='options'
N=len
F='input'
D='GSUB'
G='fvar'
C=None
E=True
B='name'
import os
from fontTools.ttLib import TTFont as g
from fontTools.subset import Subsetter as h,Options as i,parse_unicodes as j
from fontTools.varLib.instancer import instantiateVariableFont as k
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable as l
from fontTools.ttLib.tables.otTables import featureParamTypes as A,FeatureParamsStylisticSet as m
H=E
n={S:0,T:1,U:2,V:3}
A['calt']=m
def o(A,C):
	for D in A[G].axes:
		if D.axisTag==C:return A[B].getDebugName(D.axisNameID)
	return C
class I:
	def __init__(A,C,J):
		V='OS/2';T=', ';U=J.get('variations');K=J.get(O);F=C[B].getBestFamilyName();d=C[B].getDebugName(5);L=f"Frozen from {F} {d}."
		if G in C:e=T.join((f"{o(C,A)}={B}"for(A,B)in U.items()));L+=f" Sets {e}.";k(C,U,inplace=E,overlap=E)
		P=J.get(W)
		if N(P)>0:P=T.join(P);L+=f" Activates {P}."
		Q=J.get(X)
		if N(Q)>0:Q=T.join(Q);L+=f" Deactivates {Q}."
		if not H:L+=' Use fallback mode.'
		A.nameTable=C[B];A.nameTable.names=[];F=K.get(Y);D=K.get(Z);S=K.get(a);M=K.get(b)
		if not S:S=F
		if not M or M==D:M=D;R=f"{F} {D}"
		else:R=f"{F} {M} {D}"
		A.setName(F,1);A.setName(D,2);A.setName(R,3);A.setName(R,4);A.setName('Version 1.000',5);A.setName(I.getPostscriptName(F,D),6);A.setName('FontFreeze'+J.get(c),8);A.setName(L,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11);A.setName(S,16);A.setName(M,17);A.setName(R,18)
		try:C['head'].macStyle=n[D];C[V].fsSelection=I.makeSelection(C[V].fsSelection,D)
		except:pass
		I.dropVariationTables(C)
		if K.get('fixContour')==E:I.setOverlapFlags(C)
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
def p(A,B):
	if N(B)==0 or D not in A:return
	E=A[D].table.FeatureList.FeatureRecord
	for C in E:
		if C.FeatureTag in B:L(C)
def L(A):
	A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0
	if H:A.FeatureTag=d
class M:
	def __init__(A,E,B):
		A.font=E;A.features=B.get(W);A.target=B.get(O).get('target');A.singleSub=B.get(O).get('singleSub')
		if N(A.features)==0 or D not in A.font:return
		A.cmapTables=A.font[e].tables;A.unicodeGlyphs={C for B in A.cmapTables for C in B.cmap.values()};C=A.font[D].table;A.featureRecords=C.FeatureList.FeatureRecord;A.lookup=C.LookupList.Lookup;F=C.ScriptList.ScriptRecord
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
				else:M.moveFeatureLookups(A.Feature,D.Feature);L(A)
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
def q(D,B):
	A='*'
	if B=='':return
	C=h(i(layout_scripts=[A],layout_features=[A],name_IDs=[A],name_languages=[A]));C.populate(unicodes=j(B));C.subset(D)
def loadFont(I):
	A=J(I);H=A[D].table.FeatureList.FeatureRecord if D in A else[];H=[A.FeatureTag for A in H];L={'axes':[{'tag':C.axisTag,'default':C.defaultValue,'min':C.minValue,'max':C.maxValue,B:A[B].getDebugName(C.axisNameID)}for C in A[G].axes],'instances':[{B:A[B].getDebugName(C.subfamilyNameID),'coordinates':C.coordinates}for C in A[G].instances]}if G in A else C
	if os.path.exists(F):os.remove(F)
	os.rename(I,F);K={Y:A[B].getBestFamilyName(),Z:A[B].getDebugName(2),'copyright':A[B].getDebugName(0),'id':A[B].getDebugName(3),c:A[B].getDebugName(5),'trademark':A[B].getDebugName(7),'manufacturer':A[B].getDebugName(8),'designer':A[B].getDebugName(9),'description':A[B].getDebugName(10),'vendorURL':A[B].getDebugName(11),'designerURL':A[B].getDebugName(12),'license':A[B].getDebugName(13),'licenseURL':A[B].getDebugName(14),a:A[B].getDebugName(16),b:A[B].getDebugName(17),G:L,'gsub':list(dict.fromkeys(H))}
	if A.getBestCmap()==C and r(A):R('Legacy CJK font detected.');P(A);K['preview']=E
	return K
def r(F):
	D=F[e]
	for B in D.tables:
		if B.platformID==3 and B.platEncID==4:
			A=l.newSubtable(4);A.platformID=3;A.platEncID=1;A.language=0;A.cmap={}
			for C in B.cmap:
				try:G=ord(C.to_bytes(2,byteorder='big').decode(f))if C>255 else C;A.cmap[G]=B.cmap[C]
				except:pass
			D.tables=[A];return E
	return K
def s(B):
	A=B.string.decode('utf_16_be');A=bytes(A,encoding='raw_unicode_escape')
	try:A.decode(f);B.string=A
	except:pass
def J(D):
	C=g(file=D,recalcBBoxes=K,fontNumber=0)
	for A in C[B].names:
		if A.platformID==3 and A.platEncID==4:
			try:A.toStr()
			except:s(A)
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
		if d in str(F):H=K;A=Q(B,C);A.save(D)
		else:raise
def Q(args,filename):
	C='woff2';B=args;A=J(filename);I(A,B);p(A,B.get(X));M(A,B);q(A,B.get('unicodes'))
	if B.get(O).get('format')==C:A.flavor=C
	return A