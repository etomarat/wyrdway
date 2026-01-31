# BPP **_(Bits Per Pixel)_**

![BPP_demo](https://github.com/nesbox/TIC-80/assets/26139286/cd5326da-c61d-47a5-980a-e5efc33e8987)

**BPP** is a setting in the **TIC-80** [Sprite Editor advanced mode](https://github.com/nesbox/TIC-80/wiki/Sprite-editor#advanced-mode).
Lowering the number of Bits Per Pixel reduces the number of colors but allows to store more sprites and tiles.

BPP Values:
* 4 Bit - Palette of 16 colors (including transparency), 256 sprites and 256 tiles. Default value.
* 2 Bit - Palette of 4 colors (including transparency), 512 sprites and 512 tiles.
* 1 Bit - Palette of 2 colors (including transparency), 1024 sprites and 1024 tiles.

**Note**: Transparency is not required. Set the `spr()` colorkey to -1 if you don't need transparency to use all available colors.

## Usage Example

If you want to use 1 BPP setting for a sprite, first define functions to set BPP:

```lua
function set1bpp()
    poke4(2 * 0x3ffc, 8) -- 0b1000
end

function set4bpp()
    poke4(2 * 0x3ffc, 2) -- 0b0010
end
```

Call the 1 BPP function, draw your sprites, reset the drawing to 4 BPP when you are done with 1 BPP:

```lua
set1bpp()
spr(1217,x,y,0)
set4bpp()
```

This also works with font(); you can use 1bpp mode to draw your spritesheet, then simply call set1bpp() before calling font().

## Example Cart

Find the example cart with the sprites on [tic80.com](https://tic80.com/play?cart=3515). This is the cart used to make [above GIF](https://github.com/nesbox/TIC-80/wiki/Bits-Per-Pixel/#bpp-bits-per-pixel).  

```lua
-- script:  lua

x1 = 20
x2 = 95
x4 = 170
y = 50

function set1bpp() -- Function to use 1 BPP (bit per pixel) sprite mode
  poke4(2 * 0x3ffc, 8)
end

function set2bpp() -- Function to use 2 BPP sprite mode
  poke4(2 * 0x3ffc, 4)
end

function set4bpp() -- Function to use 4 BPP sprite mode
  poke4(2 * 0x3ffc, 2)
end

function TIC()
  cls(13)

  -- Set to 1 BPP mode and display sprite
  set1bpp()
  spr(44, x1, y, 0, 3, 0, 0, 2, 2)
  print("1 BPP", x1, y - 10) -- Display text label above the sprite

  -- Set to 2 BPP mode and display sprite
  set2bpp()
  spr(13, x2, y, 0, 3, 0, 0, 2, 2)
  print("2 BPP", x2, y - 10)

  -- Set to 4 BPP mode and display sprite
  set4bpp()
  spr(1, x4, y, 14, 3, 0, 0, 2, 2)
  print("4 BPP", x4, y - 10)
end
```

## NOTE

* Changing to lower BPP values will result in **stretched out sprites**.
* Changing to higher BPP values will result in **Corrupted sprites**.
* When pasting a sprite created with a different BPP value, the same corruptions will occur for higher and lower values respectively

## Address List

Use this address VRAM: `0x3FFC` - [Blit Segment](https://github.com/nesbox/TIC-80/wiki/blit-segment)
* Required using `poke()` and `poke4()`

**List:**
```
0000 SYS GFX
0001 FONT

0010 4bpp BG Page 0
0011 4bpp FG Page 0

0100 2bpp BG Page 0
0101 2bpp BG Page 1
0110 2bpp FG Page 0
0111 2bpp FG Page 1

1000 1bpp BG Page 0
1001 1bpp BG Page 1
1010 1bpp BG Page 2
1011 1bpp BG Page 3
1100 1bpp FG Page 0
1101 1bpp FG Page 1
1110 1bpp FG Page 2
1111 1bpp FG Page 3
```

## Links
[More information on Bits Per Pixel.](https://www.tutorialspoint.com/dip/concept_of_bits_per_pixel.htm)

