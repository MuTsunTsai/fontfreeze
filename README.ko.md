# FontFreeze

<p align="center">
<a href="http://mutsuntsai.github.io/fontfreeze"><img width="800" src="https://github.com/MuTsunTsai/fontfreeze/raw/main/docs/logo.png"></a>
</p>

<p align="center">
<img alt="GitHub package.json version" src="https://img.shields.io/github/package-json/v/mutsuntsai/fontfreeze?color=green">
<img alt="GitHub Repo stars"
src="https://img.shields.io/github/stars/mutsuntsai/fontfreeze?logo=GitHub&color=yellow">
<a href="https://github.com/mutsuntsai"><img
src="https://img.shields.io/badge/%C2%A92022--2025-Mu--Tsun%20Tsai-blue"></a>
<a href="https://github.com/Jolg42/awesome-typography"><img alt="Featured in Awesome Typography" src="https://awesome.re/badge.svg"></a>
</p>

<p align="center">
<a href="https://www.buymeacoffee.com/mutsuntsai" target="_blank"><img width="235" height="50" src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=☕&slug=mutsuntsai&button_colour=6f431f&font_colour=ffffff&font_family=Lato&outline_colour=ffffff&coffee_colour=FFDD00" /></a>
</p>

<p align="center">
<a href="https://www.producthunt.com/posts/fontfreeze?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-fontfreeze" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=356516&theme=neutral" alt="FontFreeze - Freeze&#0032;variations&#0032;and&#0032;features&#0032;in&#0032;font | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>
</p>

> 글꼴의 가변 항목과 기능을 고정합니다.

## 소개

최신 OpenType 글꼴은 사용자 정의 가능한 글꼴을 위해 가변 항목(variations)과 기능(features)을 지원합니다.
문제는 모든 환경이 이러한 메커니즘을 지원하지는 않는다는 것입니다.
Visual Studio와 같은 IDE는 글꼴 패밀리와 글꼴 크기 선택만 지원하며,
변형을 선택하거나 기능을 토글하는 옵션이 없습니다.
FontFreeze는 주어진 글꼴의 사용자 정의 인스턴스를 만들 수 있는 도구로,
이러한 환경에서 원하는 글꼴을 정확히 사용할 수 있게 해줍니다.

- 순수 프론트엔드, 대용량 글꼴 파일의 업로드 지연 없음.
- 브라우저에서 즉시 결과 미리보기.
- TTF 또는 WOFF2 형식으로 내보내기.
- 합자 기능 고정 지원.
- 대부분의 레거시 글꼴 지원.

## 사용 방법

https://mutsuntsai.github.io/fontfreeze 에 방문하면 앱이 시작됩니다. 설치가 필요 없습니다!

.ttf 파일을 열면 글꼴 정보와 사용 가능한 옵션이 표시됩니다.
사전 정의된 인스턴스 중 하나를 선택하여 특정 변형을 선택하거나(가변 글꼴의 경우),
각 가변 축을 사용자 정의할 수 있습니다.
기능 목록에서 활성화(또는 비활성화)하려는 기능을 선택할 수도 있습니다:

- 각 기능의 의미에 대해서는 글꼴의 사용 설명서를 참조하세요.
  대부분의 경우 찾고 있는 기능은 `cv01`-`cv99`, `ss01`-`ss20`, `zero`, `onum` 등에 있습니다.\
  (태그 이름 위에 마우스를 올리면 Microsoft Typography 웹사이트의 해당 문서 링크가 표시됩니다.)
- 대부분의 코딩 글꼴은 `calt` 기능에 코딩 합자가 정의되어 있습니다.
  합자를 완전히 비활성화하려면
  `calt`를 비활성화하면 대부분 해결됩니다.
- 기능을 비워두면 기본 동작이 유지됩니다
  (환경에 따라 활성화되거나 비활성화될 수 있습니다).
- 서브세팅에는 두 가지 모드가 있습니다: 글꼴에서 특정 글리프를 제거하거나
  (해당 문자를 다른 글꼴로 폴백하고 싶을 때 유용),
  특정 글리프만 유지하는 것입니다(예: 웹사이트에 몇 개의 문자만 필요한 경우).

마지막으로 `Generate font!`을 클릭하여 글꼴을 생성합니다.
정말 간단합니다!

팁:

- 가능하면 글꼴의 비가변 버전을 시작점으로 사용하세요.
  비가변 버전이 가변 버전보다 더 나은 힌팅을 제공할 수 있습니다.
- 미리보기 텍스트는 편집 가능합니다.
  결과를 미리보기 위해 원하는 샘플 소스 코드를 넣을 수 있습니다.
- 서로 다른 DPI의 모니터가 여러 대 있다면,
  각 모니터에서 미리보기하여 결과가 완벽한지 확인하세요.
- [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts)와 함께 사용하려면,
  먼저 글꼴을 고정한 다음 패치하세요.
  반대로 하면 오류가 발생할 수 있습니다([#8](https://github.com/MuTsunTsai/fontfreeze/issues/8#event-9248246359) 참조).

## 작동 원리

FontFreeze는 글꼴 조작을 위한 Python 라이브러리인
[fonttools](https://github.com/fonttools/fonttools)를 사용합니다.
그런 다음 [Pyodide](https://pyodide.org/)를 활용하여
WebAssembly를 통해 브라우저에서 직접 Python 코드를 실행하므로,
순수 프론트엔드이며 백엔드에 아무것도 저장되지 않습니다.
UI 부분은 [Vue](https://github.com/vuejs/vue)와 [Vuetify](https://vuetifyjs.com/)로 구축되었습니다.

FontFreeze가 기능을 비활성화하는 방식은 그 안의 모든 룩업(lookups)을 제거하는 것이고,
기능을 활성화하는 것은 그 안의 모든 룩업을 `calt`로 이동시키는 것입니다.
`calt`는 대부분의 환경에서 기본적으로 활성화되어 있습니다.
특정 환경에서 이것이 작동하지 않으면,
"활성화 대상 기능" 설정을 `rvrn`으로 변경해 볼 수도 있습니다
(OpenType 사양에 따르면 `calt`보다 더 강제적입니다.
이 경우 일부 다른 기능이 작동하려면
`calt`도 함께 활성화해야 할 수 있습니다).

버전 1.3부터, 위의 접근 방식 외에도
단일 글리프 기능에 대해 실제 글리프 대체를 적용하는 옵션이 추가되었습니다
(기본적으로 켜져 있음). 이는 다양한 환경에서 최대한의 호환성을 제공합니다.

## 감사의 말

FontFreeze는 특히 [vfit](https://github.com/jonpalmisc/vfit) 프로젝트에서 영감을 받았으며,
그 소스 코드의 많은 부분을 사용했습니다.
FontFreeze에 영감을 준 다른 프로젝트들:

- [OpenType Feature Freezer](https://github.com/twardoch/fonttools-opentype-feature-freezer),
  이름에 영감을 주었습니다(다만 기능을 고정하기 위해 추가적인 접근 방식을 사용했습니다).
- [FontDrop!](https://fontdrop.info/), 사용자 인터페이스에 영감을 주었습니다.
- [Coding Fonts](https://github.com/CSS-Tricks/coding-fonts)
  (원래 사이트는 더 이상 작동하지 않지만,
  [여기](https://coding-fonts.netlify.app/)에 복제본이 있습니다),
  기본 미리보기 텍스트에 영감을 주었습니다.
- [Microsoft Typography](https://docs.microsoft.com/en-us/typography),
  OpenType 사양에 대한 상세한 문서를 유지 관리합니다.
- [Font Squirrel Webfont Generator](https://www.fontsquirrel.com/tools/webfont-generator),
  제가 전달하려는 글꼴 중 **어떤 것도** 처리하지 못해서
  직접 도구를 만들게 했습니다.
