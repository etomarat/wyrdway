# OVR - Overlay

_This function is **deprecated** as of 1.0. - please use [vbank](https://github.com/nesbox/TIC-80/wiki/vbank) instead. It was added in version 0.6._

The **OVR** callback is the final step in rendering a frame. It draws on a separate layer and can be used together with [BDR](BDR) to create separate background or foreground layers and other visual effects.

## Usage

``` lua
function OVR()
  --Draw foreground
end
```

Since `OVR()` happens after all the scanline callbacks it can be used to draw sprites with a static palette (even if `BDR()` is otherwise changing the palette on each line). The example below shows this in action.

## Example

``` lua
-- title:  Overlap demo
-- author: librorumque
-- desc:   OVR() example
-- script: lua

PALETTE_ADDR=0x03FC0
CHANGE_COL=8
SCANLINES=144

x=96
y=24

function BDR(line)
  --[[
    Gradient background
  ]]
  local color=(0xff*line/SCANLINES)
  poke(PALETTE_ADDR+3*CHANGE_COL, color)
end

function OVR()
  --[[
    This sprite uses the same blue as the
    background, but it's not affected by
    BDR() palette swap
  ]]
  spr(1,x,y,14,3,0,0,2,2)
end

function TIC()
  cls(CHANGE_COL)
  print("OVR() example", 85, 3, 12)
  print("Press up or down to move the sprite", 22, 10, 12)
  if btn(0) then y=y-1 end
  if btn(1) then y=y+1 end
end
```

![OVR_BDR_demo](https://github.com/nesbox/TIC-80/assets/26139286/a5756c32-a5e8-40b4-babf-da2ef6ff4019)
