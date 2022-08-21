X=False
W='big5'
V='version'
U='family'
T='disables'
S='features'
R='Bold Italic'
Q='Italic'
P='Bold'
O='Regular'
I='cmap'
K='options'
J=len
H='input'
G=True
E=None
C='GSUB'
D='fvar'
B='name'
import os
from fontTools.ttLib import TTFont as Y
from fontTools.subset import Subsetter as Z,Options as a,parse_unicodes as b
from fontTools.varLib.instancer import instantiateVariableFont as c
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable as d
e={O:0,P:1,Q:2,R:3}
def f(A,C):
	for E in A[D].axes:
		if E.axisTag==C:return A[B].getDebugName(E.axisNameID)
	return C
class F:
	def __init__(A,C,E):
		W='OS/2';P=', ';Q=E.get('variations');O=E.get(K);H=C[B].getBestFamilyName();X=C[B].getDebugName(5);L=f"Frozen from {H} {X}."
		if D in C:Y=P.join((f"{f(C,A)}={B}"for(A,B)in Q.items()));L+=f" Sets {Y}.";c(C,Q,inplace=G,overlap=G)
		M=E.get(S)
		if J(M)>0:M=P.join(M);L+=f" Activates {M}."
		N=E.get(T)
		if J(N)>0:N=P.join(N);L+=f" Deactivates {N}."
		A.nameTable=C[B];A.nameTable.names=[];H=O.get(U);I=O.get('subfamily');R=f"{H} {I}";A.setName(H,1);A.setName(I,2);A.setName(R,3);A.setName(R,4);A.setName('Version 1.000',5);A.setName(F.getPostscriptName(H,I),6);A.setName('FontFreeze'+E.get(V),8);A.setName(L,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11)
		try:C['head'].macStyle=e[I];C[W].fsSelection=F.makeSelection(C[W].fsSelection,I)
		except:pass
		F.dropVariationTables(C)
		if O.get('fixContour')==G:F.setOverlapFlags(C)
	def getPostscriptName(A,B):A=A.replace(' ','');B=B.replace(' ','');return f"{A}-{B}"
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
		if B==O:A|=64
		else:A&=~ 64
		if B==P or B==R:A|=32
		else:A&=~ 32
		if B==Q:A|=1
		else:A&=~ 1
		if not A:A=64
		return A
def g(A,B):
	if J(B)==0 or C not in A:return
	E=A[C].table.FeatureList.FeatureRecord
	for D in E:
		if D.FeatureTag in B:L(D)
def L(A):A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0;A.FeatureTag='DELT'
class M:
	def __init__(A,E,B):
		A.font=E;A.features=B.get(S);A.target=B.get(K).get('target');A.singleSub=B.get(K).get('singleSub')
		if J(A.features)==0 or C not in A.font:return
		A.cmapTables=A.font[I].tables;A.unicodeGlyphs={C for B in A.cmapTables for C in B.cmap.values()};D=A.font[C].table;A.featureRecords=D.FeatureList.FeatureRecord;A.lookup=D.LookupList.Lookup;F=D.ScriptList.ScriptRecord
		for G in F:A.activateInScript(G.Script)
	def activateInScript(B,A):
		if A.DefaultLangSys!=E:B.activateInLangSys(A.DefaultLangSys)
		for C in A.LangSysRecord:B.activateInLangSys(C.LangSys)
	def activateInLangSys(B,F):
		C=E
		for D in F.FeatureIndex:
			A=B.featureRecords[D]
			if A.FeatureTag==B.target:C=A
		for D in F.FeatureIndex:
			A=B.featureRecords[D]
			if A.FeatureTag in B.features:
				if B.singleSub:B.findSingleSubstitution(A)
				if C==E:C=A;A.FeatureTag=B.target
				else:M.moveFeatureLookups(A.Feature,C.Feature);L(A)
		if C!=E:C.Feature.LookupListIndex.sort()
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
def h(D,B):
	A='*'
	if B=='':return
	C=Z(a(layout_scripts=[A],layout_features=[A],name_IDs=[A],name_languages=[A]));C.populate(unicodes=b(B));C.subset(D)
def loadFont(J):
	A=N(J);F=A[C].table.FeatureList.FeatureRecord if C in A else[];F=[A.FeatureTag for A in F];L={'axes':[{'tag':C.axisTag,'default':C.defaultValue,'min':C.minValue,'max':C.maxValue,B:A[B].getDebugName(C.axisNameID)}for C in A[D].axes],'instances':[{B:A[B].getDebugName(C.subfamilyNameID),'coordinates':C.coordinates}for C in A[D].instances]}if D in A else E
	if os.path.exists(H):os.remove(H)
	os.rename(J,H);K={U:A[B].getBestFamilyName(),'copyright':A[B].getDebugName(0),'id':A[B].getDebugName(3),V:A[B].getDebugName(5),'trademark':A[B].getDebugName(7),'manufacturer':A[B].getDebugName(8),'designer':A[B].getDebugName(9),'description':A[B].getDebugName(10),'vendorURL':A[B].getDebugName(11),'designerURL':A[B].getDebugName(12),'license':A[B].getDebugName(13),'licenseURL':A[B].getDebugName(14),D:L,'gsub':list(dict.fromkeys(F))}
	if A[I].getBestCmap()==E and i(A):print('Legacy CJK font detected.');A.save(H);K['preview']=G
	return K
def i(E):
	D=E[I]
	for B in D.tables:
		if B.platformID==3 and B.platEncID==4:
			A=d.newSubtable(4);A.platformID=3;A.platEncID=1;A.language=0;A.cmap={}
			for C in B.cmap:
				try:F=ord(C.to_bytes(2,byteorder='big').decode(W))if C>255 else C;A.cmap[F]=B.cmap[C]
				except:pass
			D.tables=[A];return G
	return X
def j(B):
	A=B.string.decode('utf_16_be');A=bytes(A,encoding='raw_unicode_escape')
	try:A.decode(W);B.string=A
	except:pass
def N(D):
	C=Y(file=D,recalcBBoxes=X,fontNumber=0)
	for A in C[B].names:
		if A.platformID==3 and A.platEncID==4:
			try:A.toStr()
			except:j(A)
	return C
def processFont(A):main(A.to_py(),H,'output')
def main(B,D,E):
	C='woff2';A=N(D);F(A,B);g(A,B.get(T));M(A,B);h(A,B.get('unicodes'))
	if B.get(K).get('format')==C:A.flavor=C
	A.save(E)