*SCN has been deprecated as of 0.9 - please use [BDR](BDR) instead.*

The **SCN** callback allows you to execute code _between_ the rendering of each scan line. The primary reason to do this is to manipulate the [palette](palette).  Doing so makes it possible to use a different palette for each scan line, and therefore [more than 16 colors at a time](Palette#more-than-16-colors).

## Usage

``` lua
function SCN(scanline)
  -- your code here
end
```

## Parameters

* **scanline** : The scan line about to be drawn (0..135)

## Example

The following example displays all 256 possible shades of gray. This can be done with any color.

``` lua
-- title:  256 shades of gray
-- author: Marcuss2, fixed by nesbox
-- desc:   Showoff of grayscale
-- script: lua
-- input:  mouse

ADDR = 0x3FC0
palette = 0

function addLight()
 for i=0, 15 do
  for j=0, 2 do
   poke(ADDR+(i*3)+j, palette)
  end
  palette = palette + 1
 end
end

function SCN(scnline)
 if scnline % 8 == 0 then
  addLight()
 end
end

function init()
 for i=0, 16 do
  rect(i*15, 0, 15, 240, i)
 end
end

init()

function TIC()
 palette = 0
end
```