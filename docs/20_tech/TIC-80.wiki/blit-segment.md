# Blit Segment / Low BPP graphics

## Usage
```
poke4(2*0x03FFC, blit_segment)
```
## Description

The blit segment controls how sprite drawing functions will read sprites in memory. It can specify the amount of bits to read per pixel and the position of the spritesheet.

### Total indexing VS local indexing
In TIC-80, sprite drawing functions use two different types of indexing:
- total indexing: `spr` indexes sprites counting 8x8 sprite positions from left to right and from top to bottom on the whole spritesheet
- local indexing: `map`, `ttri` with `texsrc=1` and `font` use 8 bit unsigned integer as indexes. This difference is the reason why those functions are limited to a portion of the spritesheet.

The blit segment modifies how indexes are interpreted.

### Simplified spec for total indexing
```
val | bin  | target memory segment
--------------------------
2  | 0010 | 4bpp  // default value
4  | 0100 | 2bpp
8  | 1000 | 1bpp
```

#### Index Stretching
```
4 bpp                      2 bpp                        1 bpp
 <-------16 cols------->    <--------32 cols-------->    <---------64 cols--------->
+------+---------+------+  +------+-----------+------+  +------+------+------+------+
| 0000 |         | 0015 |  | 0000 |           | 0031 |  | 0000 |             | 0063 |
+------+--     --+------+  +------+--       --+------+  +------+--         --+------+
|                       |  |                         |  |                           |
:       TILES (BG)      :  :        TILES (BG)       :  :         TILES (BG)        :
|                       |  |                         |  |                           |
+    --+--     --+------+  +    --+--       --+------+  +    --+--         --+------+
|                | 0255 |  |                  | 0511 |  |                    | 1023 |
+------+---------+------+  +------+-----------+------+  +------+-------------+------+
| 0256 |         | 0271 |  | 0512 |           | 0527 |  | 1024 |             | 1087 |
+------+--     --+------+  +------+--       --+------+  +------+--         --+------+
|                       |  |                         |  |                           |
:      SPRITES (FG)     :  :       SPRITES (FG)      :  :        SPRITES (FG)       :
|                       |  |                         |  |                           |
+    --+--     --+------+  +    --+--       --+------+  +    --+--         --+------+
|                | 0511 |  |                  | 1023 |  |                    | 2047 |
+------+---------+------+  +------+-----------+------+  +------+------+------+------+
```

### Origin translation and local indexing window
The `blit_segment` can be used to give functions using **local indexing** access to the full spritesheet using **origin translation**. `blit_segment` values define actually define both the way to read pixels and a virtual window in memory.

Because local indexing considers a 16 columns grid, low bpp spritesheets are organized in **pages** of 16 columns, laid out horizontally. The blit segment defines which page will be read.

Also, because both indexing schemes should be usable for any value of `blit_segment`, origin translation is also applicable to **total indexing**. The spritesheet wraps around on both vertical and horizontal axis, and the blit segment defines where the indexing starts.

### Full blit_segment specification
```
val | bin  | target memory segment
--------------------------
0   | 0000 | (reserved)
1   | 0001 | (reserved)
2   | 0010 | 4bpp BG page 0  // default value
3   | 0011 |    " FG page 0
4   | 0100 | 2bpp BG page 0
5   | 0101 |    "  " page 1
6   | 0110 |    " FG page 0
7   | 0111 |    "  " page 1
8   | 1000 | 1bpp BG page 0
9   | 1001 |    "  " page 1
10  | 1010 |    "  " page 2
11  | 1011 |    "  " page 3
12  | 1100 |    " FG page 0
13  | 1101 |    "  " page 1
14  | 1110 |    "  " page 2
15  | 1111 |    "  " page 3
```
If `blit_segment` value is set to either 0 or 1, it will result in the system font graphics showing in the tiles area and no graphics at all in the sprite area.