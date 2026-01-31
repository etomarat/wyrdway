![Sprite Editor Demo](https://raw.githubusercontent.com/wiki/nesbox/tic.computer/images/sprite.gif)

You can define two 128x128 sprite sheets in the game, one for foreground objects and the other for backgrounds. The terms 'sprite' and 'tile' are used interchangeably as they are essentially the same thing although 'tile' is usually used when referring to sprites that make up the game map (if any).

At the top right, you'll see a slider for editing a 8x8, 16x16, 32x32, or 64x64 segment of a sprite sheet. There are also two tabs for selecting the **foreground** (FG) or **background** (BG) sheets. A new cart will initialize 2 frames of Ticsy's animation in the background set of sprites.

On the left is a sprite-drawing area and on the right is a view of the selected sprite sheet (FG or BG).

A number at top left shows the selected sprite index. On the far left is a brush size selector, ranging from 1 pixel to 4 pixels square. On the bottom of the tile editor is a basic drawing tool set.

* **Brush** draws on the selected tile.
* **Color Picker** chooses the color based on the pixel clicked.
* **Select** allows you to select any part of a sprite which can then be moved using the arrows near each edge of the drawing area.
* **Fill** is a basic paint bucket tool. It allows you to fill a mono-colored area of the tile with the current color.
* **Flip Horizontal** and **Flip Vertical** allow the tile to be flipped in either axis.
* **Rotate** allows you to rotate a tile 90 degrees clockwise.
* **Erase** clears the entire tile.

Below the tool set is a color selector with 16 colors. Starting the system or a new cart initializes the palette to the default [palette](Palette).

## Advanced mode

You can access advanced mode by clicking on the top left button in the window. This advanced mode will display new options, such as
* The set **flags** triggers on the right. Each sprite has eight flags which can be used to store information or signal different conditions. For example, flag 0 might be used to indicate that the sprite is invisible, flag 6 might indicate that the sprite should be drawn scaled, etc. To read the value of sprite flags, see [fget](https://github.com/nesbox/TIC-80/wiki/fget).
* A RGB editor button on the right of the palette colors. Note that you can **edit the hex color codes** by clicking on it. You can also **copy-paste palettes** from another cartridge with buttons on the right of the palette.
* A color depth selector [(Bits Per Pixel)](https://github.com/nesbox/TIC-80/wiki/Bits-Per-Pixel) at the bottom. This allows to extend the sprites area by reducing the number of colors available.

![video24](https://github.com/nesbox/TIC-80/assets/26139286/72a9f766-be94-41f1-93be-b514e98ffec6)

## Bankswitching

[PRO version](https://github.com/nesbox/TIC-80/wiki/PRO-Version) allows to use 8 [memory banks](https://github.com/nesbox/TIC-80/wiki/Bankswitching) to draw more sprites and tiles. This is different from the two palettes (bank0 and bank1 in advanced mode) that are accessible without the PRO version.

## Hotkeys
```
TAB                     Switch tiles/sprites.
[]                      Choose previous/next palette color.
-/=                     Change brush size.
SCROLL                  Canvas zoom.
1                       Select brush.
2                       Select color picker.
3                       Select selection tool.
4                       Select filling tool.
5                       Flip horizontally.
6                       Flip vertically.
7                       Rotate.
8/DELETE                Erase.
```
The [general hotkeys](https://github.com/nesbox/TIC-80/wiki/Hotkeys#general) are available in the sprite editor too.