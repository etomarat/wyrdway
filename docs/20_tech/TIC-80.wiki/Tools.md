The following is a list of tools that can be used outside of TIC-80 to assist with the creation of carts.

The [PRO version](PRO-Version) allows to use an [external editor](external-editor) to write your code, if that is your preference.

## Converters

These can be very handy if you're migrating to TIC-80 from other virtual fantasy consoles and you already have some cartridges.
- [Tic80tracker](https://www.pouet.net/prod.php?which=95957) - This little tool helps to convert the Amiga Protracker classic module to
TIC-80 format.
- [p8totic](https://bztsrc.gitlab.io/p8totic/) - an all-in-one, web based PICO-8 to TIC-80 cartridge converter. Supports `.p8` and `.p8.png` formats and saves in `.tic` format. This tries to convert everything properly, so not just the assets, but the Lua code (syntax and API calls) too.
- [TicMcTile](https://github.com/PhilSwiss/ticmctile) Convert images to tiles/sprites or charsets in 2, 4 or 16 colors, incl. ready-to-run code for TIC-80
- [Pic-2-Tic](https://github.com/archaicvirus/Pic-2-Tic) A GUI web app, used to convert images to TIC-80 format, with optional dithering, and over 100+ color palettes from lospec.
- [Pixel It](https://giventofly.github.io/pixelit/#tryit) To pixelize an image to any size and palette.
- [TIC-MIDI](https://github.com/wojciech-graj/TIC-MIDI) A CLI tool to convert MIDI files to TIC-80 music tracks.
- [Image Converter for TIC-80](https://github.com/src3453/Image-Converter-for-TIC-80) An image converter that can convert images with 16 or more colors.
- [mulTIColor](https://github.com/RiftTeam/multicolor) Convert images to multicolor-modes (16 colors per line or 31 colors per line), incl. ready-to-run code for TIC-80

## Bundling

TIC-80 does not support loading external code files, so having multiple files and bundling them together into the cart can ease code writing.

* [ScriptPacker](https://github.com/RobLoach/scriptpacker): Package multiple Lua, Wren, Squirrel, or Javascript scripts together, keeping the dependency chain intact.
* [tic-bundle](https://github.com/chronoDave/tic-bundle#readme): Simple CLI tool for bundling TIC-80 cartridge code. Supports any language.
* [TQ-Bundler](https://github.com/scambier/TQ-Bundler): A zero-config single-file executable bundler/watcher/launcher. Supports any language.
* [Amalg](https://github.com/siffiejoe/lua-amalg): A tool that can package a Lua script and its modules into a single file.
* [tic80-stitcher](https://github.com/jahodfra/tic80-stitcher): A tool for building the cartridge from multiple files. Useful when you generate part of the cartridge during the build.
* [tic80-typescript](https://github.com/scambier/tic80-typescript): write your games in TypeScript. Handles transpilation, bundling, and minification.
* [tic80cc](https://github.com/MineRobber9000/tic80cc): Simple bundler/preprocessor for Lua projects.
* [SyllogisTIC](https://bitbucket.org/AMcBain/syllogistic): A CLI build system for packaging files into a cart; currently only supports Lua.

## Maps

While the TIC-80 map editor is very functional, it can be nice to use external tools to enhance the map creation experience.

* [TiledMapEditor-TIC-80](https://github.com/AlRado/TiledMapEditor-TIC-80): Converts between `.tmx` files to TIC-80 `.map` files
* [Tic-Tiled Map Converter](https://github.com/Skaruts/tic-tiled-map-converter): A python script for converting maps between Tiled and TIC-80. 
* [tic2tiled](https://github.com/pixelbath/tic2tiled): An extension for Tiled to export `.ticmap` files, and a(nother) Python script for converting from TIC-80 to Tiled.