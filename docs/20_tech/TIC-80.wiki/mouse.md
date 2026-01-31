`mouse() -> x, y, left, middle, right, scrollx, scrolly`

## Returns
* **x y** : [coordinates](coordinate) of the mouse pointer
* **left** : left button is down (true/false)
* **middle** : middle button is down (true/false)
* **right** : right button is down (true/false)
* **scrollx** : x scroll delta since last frame (-31..32)
* **scrolly** : y scroll delta since last frame (-31..32)

## Description
This function returns the mouse coordinates, a boolean value for the state of each mouse button (with true indicating that a button is pressed) and any change in the scroll wheel. Note that scrollx values are only returned for devices with a second scroll wheel, trackball etc.

## Reference

- [Mouse data in RAM](RAM#mouse)

## Input Tag
Set the [metadata](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata#the-input-tag) `input` tag to `mouse` if you do not use [btn](https://github.com/nesbox/TIC-80/wiki/btn)/[btnp](https://github.com/nesbox/TIC-80/wiki/btnp) or [key](https://github.com/nesbox/TIC-80/wiki/key)/[keyp](https://github.com/nesbox/TIC-80/wiki/keyp) to hide the on-screen gamepad and keyboard on Android devices.

## Examples

![mouse_example1](https://github.com/nesbox/TIC-80/assets/26139286/c997c8d4-9969-48d1-8063-7ec355fe9b99)

```lua
-- title:  mouse position and buttons
-- author: paul59
-- script: lua
-- input:  mouse

local GR,YE,WH=6,4,12
local barx,bary=10,10

function TIC()
	local x,y,left,middle,right,scrollx,scrolly=mouse()
	
	barx=barx+scrollx
	bary=bary+scrolly
	if barx<1 then barx=1 end
	if bary<1 then bary=1 end	

	cls(0)
	print('Move Mouse:',10,10,YE)
        print('Position '..string.format('x=%03i y=%03i',x,y),100,10,WH)

	print('Press Buttons:',10,20,YE)
	print('Left '..tostring(left),100,20,WH)
	print('Middle '..tostring(middle),100,40,WH)
	print('Right '..tostring(right),100,30,WH)

	print('Scroll Wheel:',10,80,YE)
	print('Scroll X',100,80,WH)
	print('Scroll Y',160,80,WH)
	rect(100,136/2-barx,8,barx,GR)
	rect(160,136/2-bary,8,bary,GR)

end
```


### Relative mode

If the `relative` bit is set to 0 (default), the mouse will be in "absolute mode", meaning the mouse is not bound to the confines of the TIC-80 window returned mouse coordinates correspond to where the cursor is within that space. If it's set to 1, the mouse will go into "relative mode", meaning it's captured to be kept at a fixed point within the TIC-80 window, therefore cannot be moved out of the window and the returned mouse coordinates are relative to the cursor's location in the previous frame. This is also the only value not returned by the [mouse](mouse) function.

Useful for 3D games such as a first-person shooter. In relative mode the cursor is hidden, the mouse is captured to be kept within the TIC-80 window and `mouse()` returns the offset relative to its previous location. Works even if the mouse is at the edge of the window.
`mouse()` will output (0,0) if mouse is pending.

- Enable: `poke(0x7FC3F, 1, 1)`
- Disable: `poke(0x7FC3F, 0, 1)` (default behavior)

![video26](https://github.com/nesbox/TIC-80/assets/26139286/f1112dc8-10e1-42cd-9164-ee3080485e0d)

```lua
-- script:  lua

abs_mode=true

function flip(val)return val>0 and 0 or 1 end

function TIC()
  if btnp(4)then 
    -- here we enable/disable relative mode bit 0x0FF84*8+7=0x7FC3F
    poke(0x7FC3F,flip(peek(0x7FC3F,1)),1)
    abs_mode= not abs_mode
  end	
		
  cls()
  if abs_mode then
    print("Absolute mode",85,50,3)
  else
    print("Relative mode",85,50,3)
  end
  local x,y=mouse()
  print("x : y = "..x.." : "..y,85,60,3)
end
```
