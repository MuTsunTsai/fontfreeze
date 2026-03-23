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
<a href="https://www.buymeacoffee.com/mutsuntsai" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-orange.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 235px !important;" /></a>
</p>

<p align="center">
<a href="https://www.producthunt.com/posts/fontfreeze?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-fontfreeze" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=356516&theme=neutral" alt="FontFreeze - Freeze&#0032;variations&#0032;and&#0032;features&#0032;in&#0032;font | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>
</p>

> 冻结字体中的可变项与特性。

## 简介

现代 OpenType 字体支持可变项（variations）和特性（features），允许自定义字体的呈现方式。
问题是，并非所有环境都支持这些机制。
像 Visual Studio 这类的 IDE 只支持选择字体家族和字体大小，
没有选择变体或切换特性的选项。
FontFreeze 是一个工具，可让您创建指定字体的自定义实例，
以便在这些环境中使用您想要的字体。

- 纯前端运作，大型字体文件无需上传等待。
- 在浏览器中即时预览结果。
- 导出为 TTF 或 WOFF2 格式。
- 支持冻结连字特性。
- 支持大多数旧版字体。

## 使用方法

只需访问 https://mutsuntsai.github.io/fontfreeze 即可启动应用程序，无需安装！

打开 .ttf 文件后，它会显示字体信息和可用的选项。
您可以选择一个预定义实例来选取特定的变体（用于可变字体），
或自定义每个可变轴。
您也可以从特性列表中选择要启用（或停用）的特性：

- 关于每个特性的含义，请查阅您的字体使用手册。
  大多数情况下，您要找的特性会在 `cv01`-`cv99`、`ss01`-`ss20`、`zero`、`onum` 等之中。\
  （将鼠标悬停在标签名称上会显示指向 Microsoft Typography 网站相应文档的链接。）
- 大多数代码字体的连字定义在 `calt` 特性中。
  如果您想完全停用连字，
  停用 `calt` 通常就能达到效果。
- 留空表示保持其默认行为
  （根据环境不同，可能已启用或未启用）。
- 子集化有两种模式：从字体中移除某些字符
  （当您希望这些字符回退到其他字体时很有用），
  或仅保留某些字符（例如当您只需要少数字符用于网站时很有用）。

最后，点击 `Generate font!` 来生成您的字体。
就是这么简单！

提示：

- 尽可能使用字体的非可变版本作为起点，
  因为它可能比可变版本有更好的微调效果。
- 预览文字是可编辑的。
  您可以在其中放入任何示例源代码来预览结果。
- 如果您有多个不同 DPI 的屏幕，
  在每个屏幕上预览以确保结果完美。
- 若要搭配 [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) 使用，
  请确保先冻结字体，然后再进行补丁。
  反过来做可能会导致错误（参见 [#8](https://github.com/MuTsunTsai/fontfreeze/issues/8#event-9248246359)）。

## 运作原理

FontFreeze 使用 [fonttools](https://github.com/fonttools/fonttools)，
一个用于操作字体的 Python 库。
然后利用 [Pyodide](https://pyodide.org/)
通过 WebAssembly 直接在浏览器中运行 Python 代码，
因此它是纯前端的，后端不会存储任何数据。
UI 部分使用 [Vue](https://github.com/vuejs/vue) 和 [Vuetify](https://vuetifyjs.com/) 构建。

FontFreeze 停用特性的方式是移除其中的所有查找表（lookups），
而启用特性则是将其中的所有查找表移动到 `calt` 中，
`calt` 在大多数环境中默认是启用的。
如果这对特定环境不起作用，
您也可以尝试将「启用目标特性」设置改为 `rvrn`
（根据 OpenType 规范，这比 `calt` 更具强制性；
请注意，在这种情况下，
您可能还需要同时启用 `calt` 以使某些其他特性正常运作）。

自 1.3 版起，除了上述方法外，
还有一个选项可以对单一字符特性应用实际的字符替换
（默认为开启），以在不同环境之间实现最大的兼容性。

## 致谢

FontFreeze 特别受到 [vfit](https://github.com/jonpalmisc/vfit) 项目的启发，
并使用了其中许多部分的源代码。
其他启发 FontFreeze 的项目包括：

- [OpenType Feature Freezer](https://github.com/twardoch/fonttools-opentype-feature-freezer)，
  启发了名称（不过我使用了额外的方法来冻结特性）。
- [FontDrop!](https://fontdrop.info/)，启发了用户界面。
- [Coding Fonts](https://github.com/CSS-Tricks/coding-fonts)
  （原始网站已不再运作，
  但 [这里](https://coding-fonts.netlify.app/) 有一个克隆版），
  启发了默认的预览文字。
- [Microsoft Typography](https://docs.microsoft.com/en-us/typography)，
  维护了关于 OpenType 规范的详细文档。
- [Font Squirrel Webfont Generator](https://www.fontsquirrel.com/tools/webfont-generator)，
  因为它**无法**处理我想要传入的任何字体，
  迫使我创建了自己的工具。
