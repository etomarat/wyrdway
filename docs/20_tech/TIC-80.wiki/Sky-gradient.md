### ScreenShot:

![](https://i.ibb.co/bLbpQg5/sky.gif)

### Example Code:

```lua
-- title:  Sky Gradient
-- author: masternama
-- script: lua

--[[

	Color Gradient looks like e.g
	(sky, lava, water & shadow)

	Result will be smooth gradient...

]]

function SCN(scn)
 --poke(0x3fc0,scn) -- Unused Sky Color
	poke(0x3fc1,scn)
	poke(0x3fc2,scn+120)
end

function TIC()
 cls()
end
```