`cls([color=0])`

## Parameters

* **color** : index (0..15) of a color in the current [palette](palette) (defaults to 0)

## Description

This function clears/fills the entire screen using **color**. If no parameter is passed, index 0 of the palette is used.

The function is often called inside TIC(), clearing the screen before each frame, but this is not mandatory.  If you're drawing to the entire screen each frame (for example with sprites, the map or primitive shapes) there is no need to clear the screen beforehand however it can result in [annoying artifacts](https://github.com/nesbox/TIC-80/issues/1911).

_Tip:_ You can create some interesting effects by not calling cls(), allowing frames to stack on top of each other - or using it repeatedly to "flash" the screen when some special event occurs.

## Example

![Example](https://imgur.com/IoKDAi0.gif)

``` lua
-- cls demo
c=0
function TIC()
	--Use Up/Down to change color
	if btnp(0) then c=c+1 end
	if btnp(1) then c=c-1 end

	--Clear with the color
	cls(c)

	--Make a background for the text
	rect(0,0,240,8,0)
	--Ouput a text with function call
	print('cls('..c..')  --Use Up/Down to change color')
end
```