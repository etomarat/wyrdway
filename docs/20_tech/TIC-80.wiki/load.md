`load <cart>` Load cartridge from the local filesystem.  
`load <cart> [ code | tiles | sprites | map | sfx | music | palette | flags | screen ]` Load data (sprites, map, etc) from an external cart to the already loaded cart.


## Parameters
Required:
* `<cart>` input cart name. `.tic` extension will be added if no extension is used. You can also load `.png` [carts](https://github.com/nesbox/TIC-80/wiki/save#save-as-png-cart).

Optional (1 max):
* `code | tiles | sprites | map | sfx | music | palette | flags` load [code](https://github.com/nesbox/TIC-80/wiki/Code-Editor), [tiles](https://github.com/nesbox/TIC-80/wiki/Sprite-editor), [sprites](https://github.com/nesbox/TIC-80/wiki/Sprite-editor), [map](https://github.com/nesbox/TIC-80/wiki/Map-Editor), [sfx](https://github.com/nesbox/TIC-80/wiki/SFX-editor), [music](https://github.com/nesbox/TIC-80/wiki/Music-editor), [palette](https://github.com/nesbox/TIC-80/wiki/Sprite-editor), [flags](https://github.com/nesbox/TIC-80/wiki/Sprite-editor) from input cart.
* `screen` load [cover image](https://github.com/nesbox/TIC-80/wiki/Cover-image) from input cart.

## Description
Load a cartridge from the local filesystem or load the data of an external cartridge to the currently loaded cart.

To load a code or image from an external file, use [import](https://github.com/nesbox/TIC-80/wiki/import).