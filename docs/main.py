T='version'
S='family'
R='disables'
Q='features'
P='Bold Italic'
O='Italic'
N='Bold'
M='Regular'
G='input'
J='options'
I=len
F=None
C='GSUB'
D='fvar'
A='name'
import os
from fontTools.ttLib import TTFont as B
from fontTools.subset import Subsetter as U,Options as V,parse_unicodes as W
from fontTools.varLib.instancer import instantiateVariableFont as X
Y=1
Z=3
a=0
b=1
c=1033
d={M:0,N:1,O:2,P:3}
e=64
f=1024
def g(B,C):
	for E in B[D].axes:
		if E.axisTag==C:return B[A].getDebugName(E.axisNameID)
	return C
class E:
	def __init__(B,C,F):
		W='OS/2';P=True;O=', ';U=F.get('variations');N=F.get(J);G=C[A].getBestFamilyName();Y=C[A].getDebugName(5);K=f"Frozen from {G} {Y}."
		if D in C:Z=O.join((f"{g(C,A)}={B}"for(A,B)in U.items()));K+=f" Sets {Z}.";X(C,U,inplace=P,overlap=P)
		L=F.get(Q)
		if I(L)>0:L=O.join(L);K+=f" Activates {L}."
		M=F.get(R)
		if I(M)>0:M=O.join(M);K+=f" Deactivates {M}."
		B.nameTable=C[A];B.nameTable.names=[];G=N.get(S);H=N.get('subfamily');V=f"{G} {H}";B.setName(G,1);B.setName(H,2);B.setName(V,3);B.setName(V,4);B.setName('Version 1.000',5);B.setName(E.getPostscriptName(G,H),6);B.setName('FontFreeze'+F.get(T),8);B.setName(K,10);B.setName('https://mutsuntsai.github.io/fontfreeze',11)
		try:C['head'].macStyle=d[H];C[W].fsSelection=E.makeSelection(C[W].fsSelection,H)
		except:pass
		E.dropVariationTables(C)
		if N.get('fixContour')==P:E.setOverlapFlags(C)
	def getPostscriptName(A,B):A=A.replace(' ','');B=B.replace(' ','');return f"{A}-{B}"
	def setName(A,B,C):A.nameTable.setName(B,C,Y,a,0);A.nameTable.setName(B,C,Z,b,c)
	def dropVariationTables(A):
		for B in 'STAT cvar fvar gvar'.split():
			if B in A.keys():del A[B]
	def setOverlapFlags(C):
		B=C['glyf']
		for D in B.keys():
			A=B[D]
			if A.isComposite():A.components[0].flags|=f
			elif A.numberOfContours>0:A.flags[0]|=e
	def makeSelection(A,B):
		A=A^A
		if B==M:A|=64
		else:A&=~ 64
		if B==N or B==P:A|=32
		else:A&=~ 32
		if B==O:A|=1
		else:A&=~ 1
		if not A:A=64
		return A
def h(A,B):
	if I(B)==0 or C not in A:return
	E=A[C].table.FeatureList.FeatureRecord
	for D in E:
		if D.FeatureTag in B:H(D)
def H(A):A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0;A.FeatureTag='DELT'
class K:
	def __init__(A,E,B):
		A.font=E;A.features=B.get(Q);A.target=B.get(J).get('target');A.singleSub=B.get(J).get('singleSub')
		if I(A.features)==0 or C not in A.font:return
		A.cmapTables=A.font['cmap'].tables;A.unicodeGlyphs={C for B in A.cmapTables for C in B.cmap.values()};D=A.font[C].table;A.featureRecords=D.FeatureList.FeatureRecord;A.lookup=D.LookupList.Lookup;F=D.ScriptList.ScriptRecord
		for G in F:A.activateInScript(G.Script)
	def activateInScript(B,A):
		if A.DefaultLangSys!=F:B.activateInLangSys(A.DefaultLangSys)
		for C in A.LangSysRecord:B.activateInLangSys(C.LangSys)
	def activateInLangSys(B,E):
		C=F
		for D in E.FeatureIndex:
			A=B.featureRecords[D]
			if A.FeatureTag==B.target:C=A
		for D in E.FeatureIndex:
			A=B.featureRecords[D]
			if A.FeatureTag in B.features:
				if B.singleSub:B.findSingleSubstitution(A)
				if C==F:C=A;A.FeatureTag=B.target
				else:K.moveFeatureLookups(A.Feature,C.Feature);H(A)
		if C!=F:C.Feature.LookupListIndex.sort()
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
def i(D,B):
	A='*'
	if B=='':return
	C=U(V(layout_scripts=[A],layout_features=[A],name_IDs=[A],name_languages=[A]));C.populate(unicodes=W(B));C.subset(D)
def loadFont():
	H='temp';B=L(H);E=B[C].table.FeatureList.FeatureRecord if C in B else[];E=[A.FeatureTag for A in E];I={'axes':[{'tag':C.axisTag,'default':C.defaultValue,'min':C.minValue,'max':C.maxValue,A:B[A].getDebugName(C.axisNameID)}for C in B[D].axes],'instances':[{A:B[A].getDebugName(C.subfamilyNameID),'coordinates':C.coordinates}for C in B[D].instances]}if D in B else F
	if os.path.exists(G):os.remove(G)
	os.rename(H,G);return{S:B[A].getBestFamilyName(),'copyright':B[A].getDebugName(0),'id':B[A].getDebugName(3),T:B[A].getDebugName(5),'trademark':B[A].getDebugName(7),'manufacturer':B[A].getDebugName(8),'designer':B[A].getDebugName(9),'description':B[A].getDebugName(10),'vendorURL':B[A].getDebugName(11),'designerURL':B[A].getDebugName(12),'license':B[A].getDebugName(13),'licenseURL':B[A].getDebugName(14),D:I,'gsub':list(dict.fromkeys(E))}
def L(A):return B(file=A,recalcBBoxes=False,fontNumber=0)
def processFont(A):main(A.to_py(),G,'output')
def main(B,D,F):
	C='woff2';A=L(D);E(A,B);h(A,B.get(R));K(A,B);i(A,B.get('unicodes'))
	if B.get(J).get('format')==C:A.flavor=C
	A.save(F)