`clip` Unsets the clipping region (draws to the full screen)

`clip(x, y, width, height)` Sets the clipping region

**Parameters**

* **x**, **y** : [coordinates](coordinate) of the top left of the clipping region
* **width** : width of the clipping region in pixels
* **height** : height of the clipping region in pixels

## Description

This function limits drawing to a clipping region or 'viewport' defined by `x`,`y`, `width`, and `height`.
Any pixels falling outside of this area will not be drawn.

Calling `clip()` with no parameters will reset the drawing area to the entire screen.

## Example

![clip_demo](https://github.com/nesbox/TIC-80/assets/26139286/ab89b05a-2b2d-4f73-834f-66a21de0272c)

``` lua
-- clip example
-- author: paul59
-- script: lua

t=0
x=96
y=24
local BLACK=0
local BLUE=13
local c=false

function TIC()

	if btn(0) then y=y-1 end
	if btn(1) then y=y+1 end
	if btn(2) then x=x-1 end
	if btn(3) then x=x+1 end
	cls(BLUE)

	if c then
		cls(BLACK)
		-- limit drawing to a 100 pixel wide/high
		-- region, with top left at 60,20
		clip(60,20,100,100)
		-- cls() is also affected by
		-- the clipping region
		cls(BLUE)
	else
		-- reset to entire screen
		clip()
	end

	spr(1+t%60//30*2,x,y,14,3,0,0,2,2)
	print("Press 'Up' To",76,84)
	print("Toggle Clipping",72,94)
	if btnp(0) then c=not c end

	t=t+1

end
```