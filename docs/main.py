Z=False
Y='big5'
X='cmap'
W='version'
V='family'
U='disables'
T='features'
S='Bold Italic'
R='Italic'
Q='Bold'
P='Regular'
O=print
L='options'
K=len
H=True
E='input'
D='GSUB'
F='fvar'
C=None
B='name'
import os
from fontTools.ttLib import TTFont as a
from fontTools.subset import Subsetter as b,Options as c,parse_unicodes as d
from fontTools.varLib.instancer import instantiateVariableFont as e
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable as f
g={P:0,Q:1,R:2,S:3}
def h(A,C):
	for D in A[F].axes:
		if D.axisTag==C:return A[B].getDebugName(D.axisNameID)
	return C
class G:
	def __init__(A,C,I):
		X='OS/2';R=', ';S=I.get('variations');M=I.get(L);E=C[B].getBestFamilyName();Y=C[B].getDebugName(5);N=f"Frozen from {E} {Y}."
		if F in C:Z=R.join((f"{h(C,A)}={B}"for(A,B)in S.items()));N+=f" Sets {Z}.";e(C,S,inplace=H,overlap=H)
		O=I.get(T)
		if K(O)>0:O=R.join(O);N+=f" Activates {O}."
		P=I.get(U)
		if K(P)>0:P=R.join(P);N+=f" Deactivates {P}."
		A.nameTable=C[B];A.nameTable.names=[];E=M.get(V);D=M.get('subfamily');J=M.get('typo_subfamily')
		if not J or J==D:J=D;Q=f"{E} {D}"
		else:Q=f"{E} {J} {D}"
		A.setName(E,1);A.setName(D,2);A.setName(Q,3);A.setName(Q,4);A.setName('Version 1.000',5);A.setName(G.getPostscriptName(E,D),6);A.setName('FontFreeze'+I.get(W),8);A.setName(N,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11);A.setName(E,16);A.setName(J,17);A.setName(Q,18)
		try:C['head'].macStyle=g[D];C[X].fsSelection=G.makeSelection(C[X].fsSelection,D)
		except:pass
		G.dropVariationTables(C)
		if M.get('fixContour')==H:G.setOverlapFlags(C)
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
		if B==P:A|=64
		else:A&=~ 64
		if B==Q or B==S:A|=32
		else:A&=~ 32
		if B==R:A|=1
		else:A&=~ 1
		if not A:A=64
		return A
def i(A,B):
	if K(B)==0 or D not in A:return
	E=A[D].table.FeatureList.FeatureRecord
	for C in E:
		if C.FeatureTag in B:J(C)
def J(A):A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0;A.FeatureTag='DELT'
class M:
	def __init__(A,E,B):
		A.font=E;A.features=B.get(T);A.target=B.get(L).get('target');A.singleSub=B.get(L).get('singleSub')
		if K(A.features)==0 or D not in A.font:return
		A.cmapTables=A.font[X].tables;A.unicodeGlyphs={C for B in A.cmapTables for C in B.cmap.values()};C=A.font[D].table;A.featureRecords=C.FeatureList.FeatureRecord;A.lookup=C.LookupList.Lookup;F=C.ScriptList.ScriptRecord
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
				else:M.moveFeatureLookups(A.Feature,D.Feature);J(A)
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
def j(D,B):
	A='*'
	if B=='':return
	C=b(c(layout_scripts=[A],layout_features=[A],name_IDs=[A],name_languages=[A]));C.populate(unicodes=d(B));C.subset(D)
def loadFont(J):
	A=I(J);G=A[D].table.FeatureList.FeatureRecord if D in A else[];G=[A.FeatureTag for A in G];L={'axes':[{'tag':C.axisTag,'default':C.defaultValue,'min':C.minValue,'max':C.maxValue,B:A[B].getDebugName(C.axisNameID)}for C in A[F].axes],'instances':[{B:A[B].getDebugName(C.subfamilyNameID),'coordinates':C.coordinates}for C in A[F].instances]}if F in A else C
	if os.path.exists(E):os.remove(E)
	os.rename(J,E);K={V:A[B].getBestFamilyName(),'copyright':A[B].getDebugName(0),'id':A[B].getDebugName(3),W:A[B].getDebugName(5),'trademark':A[B].getDebugName(7),'manufacturer':A[B].getDebugName(8),'designer':A[B].getDebugName(9),'description':A[B].getDebugName(10),'vendorURL':A[B].getDebugName(11),'designerURL':A[B].getDebugName(12),'license':A[B].getDebugName(13),'licenseURL':A[B].getDebugName(14),F:L,'gsub':list(dict.fromkeys(G))}
	if A.getBestCmap()==C and k(A):O('Legacy CJK font detected.');N(A);K['preview']=H
	return K
def k(E):
	D=E[X]
	for B in D.tables:
		if B.platformID==3 and B.platEncID==4:
			A=f.newSubtable(4);A.platformID=3;A.platEncID=1;A.language=0;A.cmap={}
			for C in B.cmap:
				try:F=ord(C.to_bytes(2,byteorder='big').decode(Y))if C>255 else C;A.cmap[F]=B.cmap[C]
				except:pass
			D.tables=[A];return H
	return Z
def l(B):
	A=B.string.decode('utf_16_be');A=bytes(A,encoding='raw_unicode_escape')
	try:A.decode(Y);B.string=A
	except:pass
def I(D):
	C=a(file=D,recalcBBoxes=Z,fontNumber=0)
	for A in C[B].names:
		if A.platformID==3 and A.platEncID==4:
			try:A.toStr()
			except:l(A)
	return C
def N(A):
	B='mort'
	if B in A:
		try:A[B].ensureDecompiled()
		except:O('Drop corrupted mort table.');del A[B]
	A.save(E,reorderTables=C)
def processLegacy():A=I(E);N(A)
def processFont(A):main(A.to_py(),E,'output')
def main(B,D,E):
	C='woff2';A=I(D);G(A,B);i(A,B.get(U));M(A,B);j(A,B.get('unicodes'))
	if B.get(L).get('format')==C:A.flavor=C
	A.save(E)