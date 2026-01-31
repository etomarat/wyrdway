<!-- to resize -->
![logo](https://user-images.githubusercontent.com/13716824/93653165-a3560b00-fa0f-11ea-880b-550c7184ecbc.png)
# TIC-80 tiny computer

**TIC-80** is a **FREE** and **OPEN SOURCE** fantasy computer for making, playing and sharing tiny games:
**[https://tic80.com](https://tic80.com)**

Built-in development tools include code, sprite, map, sound and music editors. Along with the command line tools this provides everything you need to create a mini retro game. Once your game is finished you can export it to a cartridge file, which can be stored and uploaded to the [TIC-80 website](https://tic80.com/). Alternatively, it can be packed into a stand-alone player that works on all popular platforms and can be distributed as you wish.

To make a retro styled game, the whole process of creation takes place under some technical limitations:

|| Specifications |
| --- | --- |
| Resolution | 240x136 pixel [display](display#coordinate-system) |
| Color | 16 color [palette](palette) (chosen from 24-bit colorspace) |
| Input | 4 gamepads with 8 buttons / mouse / keyboard |
| Sprites | 256 foreground sprites and 256 background tiles (8x8 pixel) |
| Map | 240x136 tiles (ie, 1920x1088 pixels) |
| Sound | 4 channels (with editable waveform envelopes) |
| Code | 512KB of source or 256KB [compiled](wasm) `BINARY` size |
| Memory | Up to 272kb of [RAM](ram) (including 32KB of [VRAM](ram)) |
| Bankswitching |  Up to 8 [banks](Bankswitching) in cart ([PRO version](pro-version) only) |


### Table of Contents

- [Console](#console)
- [Code Editor](#code-editor)
- [Sprite Editor](#sprite-editor)
- [Map Editor](#map-editor)
- [SFX Editor](#sfx-editor)
- [Music Editor](#music-editor)
- [Supported Platforms](#supported-platforms)
- [Binary Downloads](#binary-downloads)
- [Nightly Builds](#nightly-builds)
- [Pro Version](#pro-version)
- [Forks](#forks)
- [Translators](#translators)


## Console

![demo_console_v1 1](https://github.com/nesbox/TIC-80/assets/26139286/765a7d2d-1e38-4451-af3e-266608c7bfca)

The Console provides a command line interface to many common commands such as changing folders, creating and saving cartridges, etc. It's similar to the terminal found on desktop operating systems but specifically tailored to TIC-80 development.    Type `help` to get started or review the [full list of commands](Console#available-commands).

- For those operating systems that support it, tab completion and command history is available.

[Learn more about the Console](Console).



## Code Editor

![demo_code_editor_v1 1](https://github.com/nesbox/TIC-80/assets/26139286/a6663f6a-3ba6-41e9-932e-a62896906f75)

TIC-80 includes a powerful built-in code editor to assist with game development. It's entirely possible to design, code, and maintain a game without ever leaving the TIC-80 environment.

TIC-80 Supports [multiple scripting languages](https://github.com/nesbox/TIC-80/wiki/supported-languages), including:
  * [Lua](https://www.lua.org)
  * [MoonScript](https://moonscript.org)
  * [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
  * [Wren](http://wren.io/)
  * [Fennel](https://fennel-lang.org)
  * [Squirrel](http://www.squirrel-lang.org)
  * [Ruby](https://www.ruby-lang.org/en/)
  * [Janet](https://janet-lang.org/)
  * [Scheme](https://www.scheme.org/)
  * [Python](https://www.python.org/)

It's also easy to use an [external editor](external-editor) such as VS Code, Atom, etc. if that is your preference.

Before getting started you may want to [learn more about the code editor](Code-Editor) or review our detailed [API Reference](API).


## Sprite Editor

![demo_sprite_editor_v1 1](https://github.com/nesbox/TIC-80/assets/26139286/e18336a1-0574-4b34-9846-11f6e34e34ef)

The Sprite Editor allows editing of two 128x128 pixel sprite sheets, one for the foreground and one for the background.  The terms 'sprite' and 'tile' are sometimes used interchangeably, although 'tile' usually refers to background sprites that make up a game's map.

- 256 foreground sprites and 256 background tiles (each 8x8 pixels)
- Includes brush, select, move, fill, flip, rotate and other tools
- Edit a 8x8, 16x16, 32x32, or 64x64 segment at once
- Edit your game's starting [palette](palette) colors

Sprite and tiles are usually rendered to the screen using the [spr](spr) and [map](map) API functions.

[Learn more about the Sprite Editor](sprite-editor).

## Map Editor

![Map Editor Demo](https://user-images.githubusercontent.com/1101448/105969223-11cf6780-6099-11eb-9dbb-48609c43c568.gif)

[Learn more about the Map Editor](Map-Editor).

## SFX Editor

![SFX Editor Screen Capture](https://user-images.githubusercontent.com/13716824/125197918-9254df80-e257-11eb-8a20-645b4278d00f.png)


TIC-80 allows up to 64 sound effects which can also be used as instruments in the [Music Editor](Music-Editor). The [sfx](sfx) API allows for playing individual sound effects.

[Learn more about the SFX Editor](SFX-Editor).

## Music Editor

![Music Editor Screen Capture](https://user-images.githubusercontent.com/13716824/125197909-8a953b00-e257-11eb-9f61-455d8f927285.png)

The built-in editor makes it easy to compose and edit a soundtrack for your game, with the ability to store up to 8 separate pieces of music.

[Learn more about the Music Editor](Music-Editor).



## Supported Platforms

TIC is developed in pure C, with SDL and Lua libraries. It works on all popular platforms, including:

- HTML5
- Windows
- Windows 10 UWP
- Linux 32/64bit
- Android
- Mac OS
- Raspberry Pi
- Pocket CHIP
- iOS (courtesy of CliffsDover and Bruno Philipe)
- libretro (see more details on the [[Handheld Support]] page)

Native versions of TIC support [command line arguments](command-line-arguments) when called from the command line or other programs (such as an [external editor](external-editor)).

You can find the iOS/tvOS versions here:

- 0.60.3: https://github.com/brunophilipe/TIC-80
- 0.45.0: https://github.com/CliffsDover/TIC-80


## Binary Downloads
You can download compiled versions for the major operating systems directly from our [releases page](https://github.com/nesbox/TIC-80/releases).

## Nightly Builds
These can be downloaded from our [nightly builds](https://nightly.link/nesbox/TIC-80/workflows/build/main) page or the [Github Actions](https://github.com/nesbox/TIC-80/actions?query=branch%3Amaster) page.


## Pro Version
To help support TIC-80 development, we have a [PRO Version](PRO-Version).
This version has a few additional features and can be purchased from [our Itch.io page](https://nesbox.itch.io/tic80).

Users who can't afford to buy the PRO version can easily [build](https://github.com/nesbox/TIC-80#build-instructions) it from the source code. (`cmake .. -DBUILD_PRO=On`)


## Forks

There is a fork of TIC-80 that supports game scripting with the Brainfuck language. See https://github.com/lolbot-iichan/TIC-80/wiki for details and samples.

There is a fork of TIC-80 that supports exercises within Lua (with multiple unit tests, progress save, and other features) to help with teaching programming and game development. This university project was renamed 'FEUP-8' and can be found here [afonsojramos/feup-8](https://github.com/afonsojramos/feup-8/).

There is a fork of TIC-80 made for byte jams and byte battle sessions where you have an `fft()` function available returning you fast fourier transformation values responding to the audio playing on your desktop. It can be found here [aliceisjustplaying/TIC-80](https://github.com/aliceisjustplaying/TIC-80).


## Translators

* French translation (WIP)         : [GitHub @Red-Rapious](https://github.com/Red-Rapious/TIC-80/blob/master/README.md)
* Chinese translation              : [GitHub @Ark2000](https://github.com/Ark2000/TIC-80/blob/master/README.md)
* Brazilian Portuguese translation : [GitHub @h3nr1ke](https://github.com/h3nr1ke/TIC-80/blob/master/README.md)