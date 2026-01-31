`export [ win | winxp | linux | rpi | mac | html | binary | tiles | sprites | map | mapimg | sfx | music | screen | help] <outfile> [bank=0 vbank=0 id=0 alone=0]`

## Parameters
Required:  
* `<outfile>` output file name, with no file extension (especially not .tic).

Options (choose 1):  
* `win | winxp | linux | rpi | mac` export currently loaded cart as native build for the platform of your choice.
* `html` export cart to HTML.
* `binary` export binary segment for WASM cartridges.
* `tiles | sprites | mapimg` export [tiles](https://github.com/nesbox/TIC-80/wiki/Sprite-editor), [sprites](https://github.com/nesbox/TIC-80/wiki/Sprite-editor) or [map](https://github.com/nesbox/TIC-80/wiki/Map-Editor) as png image.
* `map` export [map](https://github.com/nesbox/TIC-80/wiki/Map-Editor) as `.map` file.
* `sfx | music` export [sfx](https://github.com/nesbox/TIC-80/wiki/SFX-editor) or [music](https://github.com/nesbox/TIC-80/wiki/Music-editor) as `.wav` file. Set `id` option to choose the sfx id or music track. See [below](https://github.com/nesbox/TIC-80/wiki/export#export-music) to change the sustain music setting.
* `screen` export [cover image](https://github.com/nesbox/TIC-80/wiki/Cover-image) as png image.
* `help` export help content in a markdown file with console commands, API functions and much more.

Fully optional:  
* `bank` Choose the [bank](https://github.com/nesbox/TIC-80/wiki/Bankswitching) from which you want to export.
* `vbank` Choose the [VRAM bank](https://github.com/nesbox/TIC-80/wiki/RAM#vram) from which you want to export.
* `id` to choose the sfx id or music track you want to export.
* `alone` Use `alone=1` to export the game without the editors [[PRO version](https://github.com/nesbox/TIC-80/wiki/PRO-Version)]. Users won't be able to see/edit your code/sprites/map/sfx/music.

## Description

Export currently loaded cart to HTML or as a native build.  
Export sprites, map or cover as image. Export sfx or music to wav files. Use [import](https://github.com/nesbox/TIC-80/wiki/import) to import these files to another cart or use [load](https://github.com/nesbox/TIC-80/wiki/load) to load data directly from a cart to an other one.  
Export the help content about API functions, console command and more in a markdown file.

NOTE: Do not export over your saved cart you could loose the data. Exported files don't need `.tic` file extension.

Use `save <outfile>.png` to export your cart as a png file that can be loaded by TIC-80.

## Export music
When you export music, there is no command parameter to choose to sustain notes between frames, but the sustain setting is taken from the editor (at the top right). 

![screen3](https://github.com/nesbox/TIC-80/assets/26139286/c29b4c97-d259-4692-9ab6-c4ea2b81233e)

