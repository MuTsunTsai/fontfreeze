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
O=False
H='hhea'
U='options'
N=print
Q='OS/2'
P=len
L='fvar'
K=Exception
G='input'
E=None
C='GSUB'
F=True
D='name'
import os,math as R
from typing import cast
from fontTools import version as A
from fontTools.ttLib import TTFont as m
from fontTools.subset import Subsetter as n,Options as o,parse_unicodes as p
from fontTools.varLib.instancer import instantiateVariableFont as q
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable as r,cmap_format_4
from fontTools.ttLib.tables._f_v_a_r import Axis,NamedInstance,table__f_v_a_r
from fontTools.ttLib.tables._g_l_y_f import Glyph,GlyphComponent,table__g_l_y_f
from fontTools.ttLib.tables._h_h_e_a import table__h_h_e_a
from fontTools.ttLib.tables._n_a_m_e import NameRecord,table__n_a_m_e
from fontTools.ttLib.tables._m_o_r_t import table__m_o_r_t
from fontTools.ttLib.tables.otTables import featureParamTypes as s,FeatureParamsStylisticSet as t,FeatureParamsCharacterVariants as u
I=F
v={W:0,X:1,Y:2,Z:3}
def w(A,B):
	E=A[D];F=A[L].axes
	for C in F:
		if C.axisTag==B:return E.getDebugName(C.axisNameID)
	return B
class J:
	def __init__(A,B,M):
		X=', ';Y=M.get('variations');G=M.get(U);V=B[D];E=V.getBestFamilyName();h=V.getDebugName(5);N=f"Frozen from {E} {h}.";Z=cast(bool,G.get('keepVar'))
		if L in B and not Z:i=X.join(f"{w(B,A)}={C}"for(A,C)in Y.items());N+=f" Sets {i}.";q(B,Y,inplace=F,overlap=F)
		R=M.get(a)
		if P(R)>0:R=X.join(R);N+=f" Activates {R}."
		S=M.get(b)
		if P(S)>0:S=X.join(S);N+=f" Deactivates {S}."
		if not I:N+=' Use fallback mode.'
		A.nameTable=V;j=A.nameTable.names;A.nameTable.names=[];E=G.get(c);C=G.get(d);W=G.get(e);O=G.get(f)
		if not W:W=E
		if not O or O==C:O=C;T=f"{E} {C}"
		else:T=f"{E} {O} {C}"
		A.setName(E,1);A.setName(C,2);A.setName(T,3);A.setName(T,4);A.setName('Version 1.000',5);A.setName(J.getPostscriptName(E,C),6);A.setName('FontFreeze'+M.get(g),8);A.setName(N,10);A.setName('https://mutsuntsai.github.io/fontfreeze',11);A.setName(W,16);A.setName(O,17);A.setName(T,18)
		for H in j:
			if H.nameID>25:A.nameTable.setName(H.string,H.nameID,H.platformID,H.platEncID,H.langID)
		try:B['head'].macStyle=v[C];B[Q].fsSelection=J.makeSelection(B[Q].fsSelection,C)
		except K:pass
		if not Z:J.dropVariationTables(B)
		if G.get('fixContour'):J.setOverlapFlags(B)
	def getPostscriptName(A,B):A=A.replace(' ','');B=B.replace(' ','');C=f"{A}-{B}";return C[:63]
	def setName(A,B,C):A.nameTable.setName(B,C,3,1,1033)
	def dropVariationTables(A):
		for B in'STAT cvar fvar gvar'.split():
			if B in A.keys():del A[B]
	def setOverlapFlags(C):
		B=C['glyf']
		for D in B.keys():
			A=B[D]
			if A.isComposite():E=A.components;E[0].flags|=1024
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
	if P(B)==0 or C not in A:return
	E=A[C].table.FeatureList.FeatureRecord
	for D in E:
		if D.FeatureTag in B:S(D)
def S(A):
	A.Feature.LookupListIndex.clear();A.Feature.LookupCount=0
	if I:A.FeatureTag=h
class T:
	def __init__(A,F,D):
		A.font=F;A.features=D.get(a);E=D.get(U);A.target=E.get('target');A.singleSub=E.get('singleSub')
		if P(A.features)==0 or C not in A.font:return
		A.cmapTables=A.font[i].tables;A.unicodeGlyphs={B for A in A.cmapTables for B in A.cmap.values()};B=A.font[C].table;A.featureRecords=B.FeatureList.FeatureRecord;A.lookup=B.LookupList.Lookup;G=B.ScriptList.ScriptRecord
		for H in G:A.activateInScript(H.Script)
	def activateInScript(B,A):
		if A.DefaultLangSys is not E:B.activateInLangSys(A.DefaultLangSys)
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
				if C is E:C=A;s[B.target]=t if A.FeatureTag.startswith('ss')else u;A.FeatureTag=B.target
				else:T.moveFeatureLookups(A.Feature,C.Feature);S(A)
		if C is not E:C.Feature.LookupListIndex.sort()
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
def A4(font,from_width,to_width):
	C=from_width;B=to_width;A=font;D=A[j];G=A.getBestCmap();I=(B-C)/2
	for(L,E)in G.items():
		J,K=D[E]
		if J==C:D[E]=B,K+I
	F=A[H];F.advanceWidthMax=max(B,F.advanceWidthMax)
def z(font,delta):
	D=delta;B=font;E=B[j];G=B.getBestCmap();C=0
	for(K,F)in G.items():
		A,I=E[F];A+=D;E[F]=A,I+D/2
		if A>C:C=A
	J=B[H];J.advanceWidthMax=C
def A0(font,delta):B=font[Q];C=B.usWinAscent;A=B.usWinDescent;E=C+A;F=E+delta;C=R.ceil(C*F/E);A=R.floor(A*F/E);D=font[H];D.ascent=D.ascender=B.usWinAscent=C;B.usWinDescent=A;D.descent=D.descender=-A
def A1(font):
	A=font
	if not L in A:return
	B=A[D];C=A[L];E=C.axes;F=C.instances;return{'axes':[{'tag':A.axisTag,'default':A.defaultValue,'min':A.minValue,'max':A.maxValue,D:B.getDebugName(A.axisNameID)}for A in E],'instances':[{D:B.getDebugName(A.subfamilyNameID),'coordinates':A.coordinates}for A in F]}
def loadFont(J):
	B=M(J);H=B[Q];A=B[D];I=B[C].table.FeatureList.FeatureRecord if C in B else[];I=[A.FeatureTag for A in I]
	if os.path.exists(G):os.remove(G)
	os.rename(J,G);K={c:A.getBestFamilyName(),d:A.getDebugName(2),'copyright':A.getDebugName(0),'id':A.getDebugName(3),g:A.getDebugName(5),'trademark':A.getDebugName(7),'manufacturer':A.getDebugName(8),'designer':A.getDebugName(9),'description':A.getDebugName(10),'vendorURL':A.getDebugName(11),'designerURL':A.getDebugName(12),'license':A.getDebugName(13),'licenseURL':A.getDebugName(14),e:A.getDebugName(16),f:A.getDebugName(17),L:A1(B),'gsub':list(dict.fromkeys(I)),'fontHeight':H.sTypoAscender-H.sTypoDescender,k:H.usWinAscent+H.usWinDescent}
	if B.getBestCmap()is E and A2(B):N('Legacy CJK font detected.');V(B);K['preview']=F
	return K
def A2(E):
	D=E[i]
	for B in D.tables:
		if B.platformID==3 and B.platEncID==4:
			A=r.newSubtable(4);A.platformID=3;A.platEncID=1;A.language=0;A.cmap={}
			for C in B.cmap:
				try:G=ord(C.to_bytes(2,byteorder='big').decode(l))if C>255 else C;A.cmap[G]=B.cmap[C]
				except K:pass
			D.tables=[A];return F
	return O
def A3(B):
	A=B.string.decode('utf_16_be');A=bytes(A,encoding='raw_unicode_escape')
	try:A.decode(l);B.string=A
	except K:pass
def M(C):
	B=m(file=C,recalcBBoxes=O,fontNumber=0);E=B[D].names
	for A in E:
		if A.platformID==3 and A.platEncID==4:
			try:A.toStr()
			except K:A3(A)
	return B
def V(A):
	B='mort'
	if B in A:
		try:C=A[B];C.ensureDecompiled()
		except K:N('Drop corrupted mort table.');del A[B]
	A.save(G,reorderTables=E)
def processLegacy():A=M(G);V(A)
def processFont(A):main(A.to_py(),G,'output')
def main(C,D,E):
	global I;I=F;A=B(C,D)
	try:A.save(E)
	except AssertionError as G:
		if h in str(G):I=O;A=B(C,D);A.save(E)
		else:raise
def B(args,filename):
	F='woff2';B=args;A=M(filename);J(A,B);x(A,B.get(b));T(A,B);y(A,B.get('unicodes'));C=B.get(U);D=C.get('spacing')
	if D!=0:z(A,D)
	E=C.get(k)
	if E!=0:A0(A,E)
	if C.get('format')==F:A.flavor=F
	return A
N(f"FontTools version: {A}")