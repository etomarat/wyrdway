`import [ binary | tiles | sprites | map | code | screen] <file> [bank=0 x=0 y=0 w=0 h=0 vbank=0]`

## Parameters
Required:
* `<file>` input file name.

Options (choose 1):
* `binary` import binary segment into the cartridge, which is what WASM cartridges run.
* `tiles | sprites` to import a png image as [tiles](https://github.com/nesbox/TIC-80/wiki/Sprite-editor) or [sprites](https://github.com/nesbox/TIC-80/wiki/Sprite-editor). Use the `x, y` arguments to choose the position at which it should be imported and `w, h` to choose to import only a rectangle of the input image of width `w` and/or height `h` starting from the top left of the image.
* `map` to import a .map file as [map](https://github.com/nesbox/TIC-80/wiki/Map-Editor) at position `x, y` ([map coordinates](https://github.com/nesbox/TIC-80/wiki/Map-Editor#map-coordinates)). A map file can be created from an other cart with the [export](https://github.com/nesbox/TIC-80/wiki/export) command. The tiles and sprites used by the original cart map need to be present in the new cart.
* `code` to import a text file as [code](https://github.com/nesbox/TIC-80/wiki/Code-Editor).
* `screen` to import a png image as [cover image](https://github.com/nesbox/TIC-80/wiki/Cover-image). The png should be 240×136 pixels.

Fully optional:
* `bank` Choose the [bank](https://github.com/nesbox/TIC-80/wiki/Bankswitching) to witch you want to import.
* `x y` position where to import in tiles, sprites or map.
* `w h` width and height you want to import from the image for tiles, sprites or map.
* `vbank` Choose the [VRAM bank](https://github.com/nesbox/TIC-80/wiki/RAM#vram) to which you want to import.

## Description
Import code/images from an external file (not a cart).

Use `load` to import code/sprites/music/… from another cart.

## Importing Images
Put your file to import in the `TIC-80/` folder and not the folder where your exe file is. Find the `TIC-80` folder by typing `folder` in the console.

While importing images, colors are merged to the closest color of the palette.  
For example, with default palette, this image:  

![easter](https://github.com/nesbox/TIC-80/assets/26139286/a317730e-0f5d-44c0-8ef3-5790314f0d42)  

becomes:  

![import_screenshot](https://github.com/nesbox/TIC-80/assets/26139286/24a08632-2ce5-4ea2-b35a-3e8a1533083e)

Note that if the palette is all black (like default bank1) the imported image will be all black.