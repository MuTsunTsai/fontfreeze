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

> 凍結字型中的可變項與特性。

## 簡介

現代 OpenType 字型支援可變項（variations）和特性（features），允許自訂字型的呈現方式。
問題是，並非所有環境都支援這些機制。
像 Visual Studio 這類的 IDE 只支援選擇字型家族和字型大小，
沒有選擇變體或切換特性的選項。
FontFreeze 是一個工具，可讓您建立指定字型的自訂實例，
以便在這些環境中使用您想要的字型。

- 純前端運作，大型字型檔案無需上傳等待。
- 在瀏覽器中即時預覽結果。
- 匯出為 TTF 或 WOFF2 格式。
- 支援凍結連字特性。
- 支援大多數舊版字型。

## 使用方法

只需造訪 https://mutsuntsai.github.io/fontfreeze 即可啟動應用程式，無需安裝！

開啟 .ttf 檔案後，它會顯示字型資訊和可用的選項。
您可以選擇一個預定義實例來選取特定的變體（用於可變字型），
或自訂每個可變軸。
您也可以從特性列表中選擇要啟用（或停用）的特性：

- 關於每個特性的含義，請查閱您的字型使用手冊。
  大多數情況下，您要找的特性會在 `cv01`-`cv99`、`ss01`-`ss20`、`zero`、`onum` 等之中。\
  （將滑鼠懸停在標籤名稱上會顯示指向 Microsoft Typography 網站相應文件的連結。）
- 大多數程式碼字型的連字定義在 `calt` 特性中。
  如果您想完全停用連字，
  停用 `calt` 通常就能達到效果。
- 留空表示保持其預設行為
  （根據環境不同，可能已啟用或未啟用）。
- 子集化有兩種模式：從字型中移除某些字符
  （當您希望這些字元回退到其他字型時很有用），
  或僅保留某些字符（例如當您只需要少數字元用於網站時很有用）。

最後，點擊 `Generate font!` 來產生您的字型。
就是這麼簡單！

提示：

- 盡可能使用字型的非可變版本作為起點，
  因為它可能比可變版本有更好的微調效果。
- 預覽文字是可編輯的。
  您可以在其中放入任何範例原始碼來預覽結果。
- 如果您有多個不同 DPI 的螢幕，
  在每個螢幕上預覽以確保結果完美。
- 若要搭配 [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) 使用，
  請確保先凍結字型，然後再進行補丁。
  反過來做可能會導致錯誤（參見 [#8](https://github.com/MuTsunTsai/fontfreeze/issues/8#event-9248246359)）。

## 運作原理

FontFreeze 使用 [fonttools](https://github.com/fonttools/fonttools)，
一個用於操作字型的 Python 函式庫。
然後利用 [Pyodide](https://pyodide.org/)
透過 WebAssembly 直接在瀏覽器中執行 Python 程式碼，
因此它是純前端的，後端不會儲存任何資料。
UI 部分使用 [Vue](https://github.com/vuejs/vue) 和 [Vuetify](https://vuetifyjs.com/) 建構。

FontFreeze 停用特性的方式是移除其中的所有查詢表（lookups），
而啟用特性則是將其中的所有查詢表移動到 `calt` 中，
`calt` 在大多數環境中預設是啟用的。
如果這對特定環境不起作用，
您也可以嘗試將「啟用目標特性」設定改為 `rvrn`
（根據 OpenType 規範，這比 `calt` 更具強制性；
請注意，在這種情況下，
您可能還需要同時啟用 `calt` 以使某些其他特性正常運作）。

自 1.3 版起，除了上述方法外，
還有一個選項可以對單一字符特性套用實際的字符替換
（預設為開啟），以在不同環境之間實現最大的相容性。

## 致謝

FontFreeze 特別受到 [vfit](https://github.com/jonpalmisc/vfit) 專案的啟發，
並使用了其中許多部分的原始碼。
其他啟發 FontFreeze 的專案包括：

- [OpenType Feature Freezer](https://github.com/twardoch/fonttools-opentype-feature-freezer)，
  啟發了名稱（不過我使用了額外的方法來凍結特性）。
- [FontDrop!](https://fontdrop.info/)，啟發了使用者介面。
- [Coding Fonts](https://github.com/CSS-Tricks/coding-fonts)
  （原始網站已不再運作，
  但 [這裡](https://coding-fonts.netlify.app/) 有一個複製版），
  啟發了預設的預覽文字。
- [Microsoft Typography](https://docs.microsoft.com/en-us/typography)，
  維護了關於 OpenType 規範的詳細文件。
- [Font Squirrel Webfont Generator](https://www.fontsquirrel.com/tools/webfont-generator)，
  因為它**無法**處理我想要傳入的任何字型，
  迫使我建立了自己的工具。
