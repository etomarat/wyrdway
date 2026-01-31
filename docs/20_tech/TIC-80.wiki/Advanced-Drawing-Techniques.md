## `0x03FF0` Palette Map / Swapping colors

### Usage
```
poke4(2*0x03FF0 + color_index, mapped_color_index)
```
### Description

```
+-------+-------------------+-------+
| ADDR  | INFO              | SIZE  |
|-------+-------------------+-------|
| 00000 | SCREEN            | 16320 | 240x136 = 32640 4bit pixels
| 03FC0 | PALETTE           | 48    | 16 x 24bit RGB color values
| 03FF0 | PALETTE MAP       | 8     | 16 x 4bit color indexes (for palette swapping of individual sprites)
+-------+-------------------+-------+
```

**TIC-80** uses `PALETTE MAP` to swap 4 bits colors indices to be drawn to any combination of 4 bits colors in the palette. The mapped 4 bits color is written on `SCREEN`.

With sprite-drawing functions (`spr`, `map`, `ttri`), this color swap is done when reading the color from sprite memory.

`colorkey` parameters are applied on source colors, swapping out color indices before remapping.

---

## `0x03FFC` Blit Segment / Low BPP graphics ([BETA FEATURE, spec might change before release]0.80)

Please see [Blit Segment](blit-segment).