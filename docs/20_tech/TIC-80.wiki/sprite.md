# Sprite

A "sprite" in TIC-80 is an 8 pixel wide and 8 pixel tall image. Each pixel is drawn using one of the 16 available colors from the [palette](palette). Lower [BPP](Bits-Per-Pixel) blitting modes are also available - allowing 2 or 4 color sprites.

Sprites can be divided into foreground sprites and background sprites (which are called tiles). The `TILES` section of [RAM](ram) stores background sprites while the `SPRITES` section stores foreground sprites.

- `TILES` - 256 background tiles (0..255)
- `SPRITES` - 256 foreground sprites (256..511)


A sprite can be directly draw in the screen using the [spr](spr) function or used in the [Map Editor](map-editor) as tiles (and then drawn with [map](map).

**See also:**

- [BPP](bpp)
- [BLIT Segment](blit-segment)