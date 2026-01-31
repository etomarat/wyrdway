All TIC-80 games use a palette of 16 colors drawn from 24-bit colorspace (16 million possible colors).  The TIC-80 default palette for all new cartridges is [SWEETIE-16](https://lospec.com/palette-list/sweetie-16).  
The game's starting palette can be modified using the [Sprite Editor](sprite-editor#advanced-mode) in advanced mode.

![Palette_demo](https://github.com/nesbox/TIC-80/assets/26139286/3662f1ce-9192-40a0-ad23-47cfd8b07dd3)

# Alter Palette at Runtime

You can [alter the palette](https://github.com/nesbox/TIC-80/wiki/Sample-RGB-Color-RAM-Address) at runtime using the [poke](poke) command and poking into the `PALETTE` area of [VRAM](ram).  You can replace the whole palette this way, or just a single color.

### Swapping Palette Colors

For more temporary swaps (within a palette) `PALETTE MAP` [VRAM](ram) is what you need.  Let's say we have a sprite that's largely blue but now we'd like a variant that's red (replacing all the blue pixels with red). We don't need a second sprite for this - we can just update the palette map.

```lua
PALETTE_MAP = 0x3FF0
blue = 9
red = 2
poke4(PALETTE_MAP * 2 + blue, red) -- swap the colors
-- draw the sprite
poke4(PALETTE_MAP * 2 + blue, blue) -- swap them back
```

See also [PALETTE MAP](RAM#PALETTE-MAP).

### More than 16 Colors

By combining [poke](poke) and [BDR](BDR) creatively you can potentially display up to 2,176 colors on screen simultaneously (16 colors x 136 scanlines).  As always, each scanline is still restricted to 16 colors.

Example

- [Grey gradient](https://github.com/nesbox/TIC-80/wiki/BDR#example-256-colors)
- [Color gradient](https://github.com/nesbox/TIC-80/wiki/OVR#example)

# 2 or 4-Colors Palette Mode

![BPP_demo](https://github.com/nesbox/TIC-80/assets/26139286/cd5326da-c61d-47a5-980a-e5efc33e8987)

This allows to store more sprites and tiles.
See the [Bits Per Pixel](https://github.com/nesbox/TIC-80/wiki/Bits-Per-Pixel) page.

# Custom Default Palette

If you don't like the default palette and would like to use a custom palette for all your projects, you can modify the default cart template and therefore its palette, using `config default` command.
Do not forget to save.

# TIC-80 Themes

Colors used in the code editor can be configured using the [configuration file](https://github.com/nesbox/TIC-80/wiki/config#themes). One can also change the configuration file palette to customize all editors.

<img src="https://github.com/nesbox/TIC-80/assets/26139286/cfdad03e-a25c-41d8-befc-5c7c34f812a5" width="510">

# Palettes

### SWEETIE-16

![SWEETIE-16](https://i.ibb.co/QJYrBks/SWEETIE16.png)

|Color      |Index|Hex   |
|:---------:|:---:|:----:|
|Black      |0    |1A1C2C|
|Purple     |1    |5D275D|
|Red        |2    |B13E53|
|Orange     |3    |EF7D57|
|Yellow     |4    |FFCD75|
|Light Green|5    |A7F070|
|Green      |6    |38B764|
|Dark Green |7    |257179|
|Dark Blue  |8    |29366F|
|Blue       |9    |3B5DC9|
|Light Blue |10   |41A6F6|
|Cyan       |11   |73EFF7|
|White      |12   |F4F4F4|
|Light Grey |13   |94B0C2|
|Grey       |14   |566C86|
|Dark Grey  |15   |333C57|


Or in a form that can be pasted in the palette editor:
`1a1c2c5d275db13e53ef7d57ffcd75a7f07038b76425717929366f3b5dc941a6f673eff7f4f4f494b0c2566c86333c57`  
The palette editor is accessible in the advanced mode of the sprite editor, with the icon on the right of the palette. The paste icon is on the right of the palette editor.

### DB16

![DB16](https://raw.githubusercontent.com/geoffb/dawnbringer-palettes/master/DB16/db16.png)

Some old cartridges may still use this palette for backwards compatibility.

### Other palettes
Find other palettes on [Lospec website](https://lospec.com/palette-list) where you can set the number of colors to be exactly 16 and download the hex file which content can be copy-pasted to the sprite editor.

### Online palette editor
[TIC-80 palette editor](https://childishgiant.github.io/tic-80-palette-editor/)