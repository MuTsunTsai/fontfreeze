# FontFreeze

<p align="center">
  <a href="http://mutsuntsai.github.io/fontfreeze"><img width="800" src="https://github.com/MuTsunTsai/fontfreeze/raw/main/docs/logo.png"></a>
</p>

![GitHub package.json version](https://img.shields.io/github/package-json/v/mutsuntsai/fontfreeze?color=green)
![GitHub Repo stars](https://img.shields.io/github/stars/mutsuntsai/fontfreeze?logo=GitHub&color=yellow)
![Copyright](https://img.shields.io/badge/%C2%A92022-Mu--Tsun%20Tsai-blue)

> Freeze variations and features in font.

## Introduction

Modern OpenType fonts support variations and features that allow customizable fonts.
The problem is that not all environments support these mechanisms.
IDEs such as Visual Studio only support choosing font family and font size,
without any options to select variants or toggle features.
FontFreeze is a tool that allows you to create a customized instance of a given font,
so that you may use exactly the font you want in those environments.

## How to use it

Simply visit https://mutsuntsai.github.io/fontfreeze to launch the app, no installation required!

As you open a .ttf file, it will show you the font info and the available options.
You can then select a particular variant (for variable fonts) by selecting one of the predefined instances,
or customize each variable axis.
You can also select features you want to activate (or deactivate) from the feature list:

- For the meaning of each feature, look up the user manual of your font.
  In most cases, the feature you are looking for will be among `cv01`-`cv99`, `ss01`-`ss20`, `zero`, `onum`, etc.
- Most coding fonts have their coding ligatures defined in the `calt` feature.
  If you want to completely disable ligatures,
  deactivating `calt` will usually do the trick.
- Leaving a feature blank means keeping its default behavior
  (which may or may not be activated depending on the environment).

Finally, click `Generate font!` to generate your font.
It's that simple!

Tips:

- Whenever possible, use a non-variable version of the font as starting point,
  as it will likely give better hinting than the variable one.
- The preview text is editable.
  You can put any sample source code in it to preview the result.
- If you have multiple screens with different DPIs,
  preview on each of them to make sure the result is perfect.

## How it works

FontFreeze uses [fonttools](https://github.com/fonttools/fonttools),
a Python library for manipulating fonts.
In then utilizes [Pyodide](https://pyodide.org/)
to run Python code directly in your browser through WebAssembly,
so it's purely front-end and nothing is stored in the back-end.
The UI part is built with [petite-vue](https://github.com/vuejs/petite-vue) and [Bootstrap](https://getbootstrap.com/).

The way FontFreeze deactivates a feature is by removing all lookups inside it,
and it activates a feature by moving all lookups in it into `calt`,
which is usually activated by default in most environments.
If this doesn't work for a particular environment,
you may also try changing the "Target feature for activation" setting to `rvrn`
(which is more forced than `calt` by the OpenType specification;
note that in this case,
you might also need to activate `calt` as well for some other features to function).

## Acknowledgment

FontFreeze is especially inspired by the project
[vfit](https://github.com/jonpalmisc/vfit),
and I used many parts of the source code from it.
Other projects that inspired FontFreeze include:

- [OpenType Feature Freezer](https://github.com/twardoch/fonttools-opentype-feature-freezer),
  for inspiring the name (I used a very different approach to freeze the features though).
- [FontDrop!](https://fontdrop.info/), for inspiring the user interface.
- [Coding Fonts](https://github.com/CSS-Tricks/coding-fonts)
  (the original site no longer works,
  but [here](https://coding-fonts.netlify.app/) is a clone of it),
  for inspiring the default preview text.
- [Microsoft Typography](https://docs.microsoft.com/en-us/typography),
  for maintaining a detailed documentation on the OpenType specs.

The "FontFreeze" banner is generated using [Text Generator](https://www.textfx.co/).