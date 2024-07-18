(()=>{"use strict";var e={178:function(e,t,n){var a,o;let r,i,l=n("623"),s=n("271"),f=new Worker(new URL(n.p+n.u("197"),n.b)),u=new Promise((e,t)=>{let n=a=>{"initialized"==a.data?(f.removeEventListener("message",n),e()):"error"in a.data?t(Error(a.data.error)):"progress"in a.data&&g.loading&&(g.loading=`packages (${a.data.progress}%)`)};f.addEventListener("message",n)}),c=document.createElement("style");document.head.appendChild(c);let d=document.createElement("style");document.head.appendChild(d);let g=(0,l.qj)({localFonts:[],localFont:"",localFamily:"",unavailableFonts:[],unicodeRange:"",loading:null,font:null,sample:"",glyphs:"",subsetMode:"exclude",previewSize:12,running:!1,message:null,previewIndex:0,version:""}),m=["abvm","abvs","akhn","blwf","blwm","blws","ccmp","cfar","cjct","curs","dist","dtls","fin2","fin3","fina","flac","half","haln","init","isol","ljmo","locl","ltra","ltrm","mark","med2","medi","mkmk","nukt","pref","pres","pstf","psts","rclt","rkrf","rlig","rphf","rtla","rtlm","rvrn","ssty","stch","tjmo","vjmo","DELT"],p={ital:"Italic",opsz:"Optical size",slnt:"Slant",wdth:"Width",wght:"Weight"},v={ttf:{description:"TTF font",accept:{"font/ttf":".ttf"}},woff2:{description:"WOFF2 font",accept:{"font/woff2":".woff2"}}},h="Please try re-exporting the font with editors such as FontForge and see if it fixes the issue. If it still doesn't, please submit an issue.",y=e=>s.u_.getOrCreateInstance(e);function w(e,t){return new Promise((n,a)=>{let o=new MessageChannel;f.postMessage([e,t],[o.port2]),o.port1.onmessage=e=>{let{success:t,data:o}=e.data;t?n(o):a(Error(o))}})}fetch("sample.txt").then(e=>e.text()).then(e=>g.sample=e),fetch("https://img.shields.io/github/package-json/v/mutsuntsai/fontfreeze.json").then(e=>e.json()).then(e=>g.version=" "+e.value);let b=document.querySelector(".dropzone"),F=(e,t)=>{e.stopPropagation(),e.preventDefault(),b.classList.toggle("drag",t)};document.body.addEventListener("dragover",e=>F(e,!0)),b.addEventListener("dragleave",e=>F(e,!1)),b.addEventListener("drop",e=>{F(e,!1);let t=[...e.dataTransfer.items].find(e=>"file"==e.kind);t&&j(t.getAsFile())}),(0,l.ri)({chromiumVersion:parseInt((null===(o=navigator.userAgentData)||void 0===o?void 0:null===(a=o.brands.find(e=>"Chromium"==e.brand))||void 0===a?void 0:a.version)??0),localFontSupport:"queryLocalFonts"in window,store:g,get previewStyle(){if(!g.font)return null;let e=g.font.gsub.filter(e=>!1!==g.features[e]).map(e=>`'${e}' ${g.features[e]?"on":"off"}`).join(","),t=g.font.fvar?g.font.fvar.axes.map(e=>`'${e.tag}' ${g.variations[e.tag]}`).join(","):"normal";return`white-space: pre-line;font-family: preview${g.previewIndex};font-feature-settings: ${e};font-variation-settings: ${t};font-size: ${g.previewSize}pt;`},get more(){let e=g.font;if(!e)return!1;return e.description||e.designer||e.manufacturer||e.copyright||e.trademark},get instances(){if(!g.font||!g.font.fvar)return[];return g.font.fvar.instances},get axes(){if(!g.font||!g.font.fvar)return[];return g.font.fvar.axes},get localFamilies(){if(!g.localFonts.length)return[];let e=new Set;for(let t of g.localFonts)e.add(t.family);return[...e]},getAxisName:e=>e.name?e.name:e.tag in p?p[e.tag]:e.tag,setInstance(e){for(let t in g.options.typo_subfamily=e.name,e.coordinates)g.variations[t]=e.coordinates[t]},getStep(e){let t=e.max-e.min;return t>20?1:t>1?.1:.01},clear(){let e=document.getElementsByTagName("select")[0];e&&(e.value="")},checkboxChange(e){!0===r[e]&&(g.features[e]=void 0),void 0===r[e]&&(g.features[e]=!1),r[e]=g.features[e]},info(){y("#info").show()},setUnicodeRange(){c.sheet.cssRules[0].style.unicodeRange=g.unicodeRange=$()},optionStyle(e){if(!e){if(""===g.localFont)return"";e=g.localFonts[g.localFont]}return`font-family:'local ${e.fullName}'`},familyStyle(){let e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:g.localFamily,t=g.localFonts.filter(t=>t.family==e);if(!t.length)return"";let n=t.find(e=>"Regular"==e.style);return!n&&(t.sort((e,t)=>e.fullName.length-t.fullName.length),n=t[0]),`font-family:'local ${n.fullName}'`},familyChange(){g.localFont=g.localFonts.findIndex(e=>e.family==g.localFamily)},setupDiv(){let e=document.querySelector("div.pre");(function(e){try{let t="plaintext-only";return e.contentEditable=t,e.contentEditable==t}catch(e){return!1}})(e)?e.innerText=g.sample:(function(e){e.contentEditable="true",e.addEventListener("keydown",t=>{13==t.keyCode&&(t.preventDefault(),t.stopPropagation(),x(e,"\n"))}),e.addEventListener("paste",t=>{t.preventDefault(),x(e,(t.originalEvent||t).clipboardData.getData("text/plain"))})}(e),e.textContent=g.sample)},async local(){gtag("event","show_local"),await navigator.permissions.query({name:"local-fonts",description:""});let e=await window.queryLocalFonts();0!=e.length&&(function(e){let t=d.sheet;for(;t.cssRules.length;)t.deleteRule(0);for(let n of e)t.insertRule(`@font-face { font-family: 'local ${n.fullName}'; src: local('${n.fullName}'), local('${n.postscriptName}');}`)}(e),g.localFonts=e,y("#local").show())},async loadLocal(){let e;gtag("event","open_local");let t=g.localFonts[g.localFont];try{e=await t.blob()}catch(e){alert("An error occur: "+e.message),g.unavailableFonts.push(t.postscriptName);return}finally{g.localFamily="",g.localFont=""}y("#local").hide();try{await L(e,t.fullName)}catch(e){alert("An error occur: "+e.message)}}}).mount();globalThis.generate=async function(){if(!g.message){gtag("event","save_"+g.options.format);try{if("showSaveFilePicker"in window){g.message=null;let e=await showSaveFilePicker({suggestedName:S(),types:[v[g.options.format]]});await k();let t=await R(),n=await fetch(t),a=await n.arrayBuffer(),o=new Blob([a],{type:"font/"+g.options.format}),r=await e.createWritable();await r.write(o),await r.close(),g.message="Generating complete!",setTimeout(()=>g.message=null,3e3)}else await k(),g.url=await R(),g.download=S()}catch(e){console.log(e)}g.running=!1}};function x(e,t){let n=window.getSelection(),a=e.textContent,o=Math.min(n.focusOffset,n.anchorOffset),r=Math.max(n.focusOffset,n.anchorOffset),i=a.substring(r);""==i&&(i="\n"),e.textContent=a.substring(0,o)+t+i,n.removeAllRanges();let l=document.createRange();l.setStart(e.childNodes[0],o+t.length),l.setEnd(e.childNodes[0],o+t.length),n.addRange(l)}function k(){let e=new Promise(e=>{addEventListener("animationstart",e,{once:!0})});return g.running=!0,e}function S(){return g.font.fileName.replace(/\.[a-z0-9]+$/i,"")+"_freeze."+g.options.format}function O(e){return JSON.parse(JSON.stringify(e))}async function R(){try{for(let e in g.variations)g.variations[e]=Number(g.variations[e]);g.options.family=g.options.family.trim(),g.options.typo_subfamily=g.options.typo_subfamily.trim();let e=O(g.options);e.suffix&&(e.family&&e.family.length+e.suffix.length<32&&(e.family+=" "+e.suffix),e.typo_family&&(e.typo_family+=" "+e.suffix));let t={options:e,version:g.version,unicodes:$(),variations:g.variations,features:g.font.gsub.filter(e=>!0===g.features[e]),disables:g.font.gsub.filter(e=>void 0===g.features[e])};return await w("save",O(t))}catch(e){throw alert("An error occur: "+e.message),e}}async function j(e){gtag("event","open_ttf");try{await L(e,e.name)}catch(t){console.log(t),alert(`"${e.name}" is not a valid font file, or is corrupted. `+h)}}async function L(e,t){let n;g.loading="packages",await u,g.loading="font";let a=URL.createObjectURL(e);try{n=await w("open",a)}catch(e){throw URL.revokeObjectURL(a),g.loading=null,e}for(let o of(console.log(O(n)),n.preview&&(URL.revokeObjectURL(a),a=n.preview),n.fileName=t,n.fileSize=function(e){return e<1024?e+"B":(e/=1024,e<1024)?e.toFixed(1)+"KiB":(e/=1024,e.toFixed(1)+"MiB")}(e.size),n.gsub=n.gsub.filter(e=>!m.includes(e)),g.features={},r={},g.variations={},g.glyphs="",g.options={suffix:"Freeze",family:n.family,subfamily:n.subfamily,typo_family:n.typo_family||n.family,typo_subfamily:n.typo_subfamily||"",fixContour:!1,singleSub:!0,customNames:!1,target:"calt",format:"ttf"},n.gsub))g.features[o]=r[o]=!1;if(n.fvar)for(let e of n.fvar.axes)g.variations[e.tag]=e.default;g.font=n,await E(a),g.loading=null}async function E(e){if(!await _(e)){if(!info.preview)try{let e=await w("legacy");if(await _(e))return}catch(e){console.log(e)}gtag("event","preview_failed"),alert("Font preview won't work for this font. "+h)}}globalThis.openFile=async function(e){let t=e.files[0];t&&(e.value="",j(t))};function N(e){let t="U+"+e[0].toString(16);return e[1]>e[0]&&(t+="-"+e[1].toString(16)),t}function $(){let e=function(){let e=new Set;for(let t=0;t<g.glyphs.length;t++){let n=g.glyphs.codePointAt(t);g.glyphs.charCodeAt(t)!=n&&t++,e.add(n)}let t=[...e];return t.sort((e,t)=>e-t),t}();if("exclude"==g.subsetMode){let t=[[0,1114111]];if(0==e.length)return"";for(let n of e){let e=t.find(e=>e[0]<=n&&n<=e[1]);if(!e)continue;let a=e[1];e[1]=n-1,t.push([n+1,a])}return t.filter(e=>e[0]<=e[1]).map(N).join(", ").toUpperCase()}{if(0==e.length)return"U+0";let t=[],n=e[0],a=n;for(let o=1;o<=e.length;o++){let r=e[o];a==r-1||(t.push([n,a]),n=r),a=r}return t.map(N).join(", ").toUpperCase()}}function _(e){return i&&URL.revokeObjectURL(i),i=e,c.sheet.cssRules.length>0&&c.sheet.deleteRule(0),new Promise(e=>{document.fonts.onloadingdone=t=>{e(t.fontfaces.length>0)},c.sheet.insertRule(`@font-face {font-family: preview${++g.previewIndex};src: url('${i}');}`)})}}},t={};function n(a){var o=t[a];if(void 0!==o)return o.exports;var r=t[a]={exports:{}};return e[a](r,r.exports,n),r.exports}n.m=e,n.d=function(e,t){for(var a in t)n.o(t,a)&&!n.o(e,a)&&Object.defineProperty(e,a,{enumerable:!0,get:t[a]})},n.u=function(e){return"static/js/async/"+e+".ebb2c6f6.js"},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},(()=>{var e=[];n.O=function(t,a,o,r){if(a){r=r||0;for(var i=e.length;i>0&&e[i-1][2]>r;i--)e[i]=e[i-1];e[i]=[a,o,r];return}for(var l=1/0,i=0;i<e.length;i++){for(var a=e[i][0],o=e[i][1],r=e[i][2],s=!0,f=0;f<a.length;f++)(!1&r||l>=r)&&Object.keys(n.O).every(function(e){return n.O[e](a[f])})?a.splice(f--,1):(s=!1,r<l&&(l=r));if(s){e.splice(i--,1);var u=o();void 0!==u&&(t=u)}}return t}})(),n.p="/fontfreeze/",n.rv=function(){return"1.0.0-alpha.5"},(()=>{n.b=document.baseURI||self.location.href;var e={980:0};n.O.j=function(t){return 0===e[t]};var t=function(t,a){var o=a[0],r=a[1],i=a[2],l,s,f=0;if(o.some(function(t){return 0!==e[t]})){for(l in r)n.o(r,l)&&(n.m[l]=r[l]);if(i)var u=i(n)}for(t&&t(a);f<o.length;f++)s=o[f],n.o(e,s)&&e[s]&&e[s][0](),e[s]=0;return n.O(u)},a=self.webpackChunkfontfreeze=self.webpackChunkfontfreeze||[];a.forEach(t.bind(null,0)),a.push=t.bind(null,a.push.bind(a))})(),n.ruid="bundler=rspack@1.0.0-alpha.5";var a=n.O(void 0,["545"],function(){return n("178")});a=n.O(a)})();