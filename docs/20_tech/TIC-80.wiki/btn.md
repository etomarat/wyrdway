- `btn(id) -> is_pressed`
- `btn() -> GAMEPADS data` (see [RAM](RAM))

## Parameters
* **id** : id (0..31) of the key we want to interrogate (see the [key map](key-map) for reference or type `help buttons` in console).

## Returns
* **is_pressed** : button is pressed (true/false)
* **GAMEPADS data** : 32-bit value that represents current state of all GAMEPAD button inputs

## Description
This function allows you to read the status of TIC's controller buttons. It returns `true` if the button with the supplied **id** is currently in the pressed state and remains `true` for as long as the button is held down. To see if a button was _just_ pressed, use [btnp](btnp) instead.

## Input Tag
Set the [metadata](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata#the-input-tag) `input` tag to `gamepad` to display only the on-screen gamepad on Android devices and hide the keyboard.

## Example

The following example displays the state of all buttons during each frame:

![Example](https://i.imgur.com/uIeRJHR.gif)

```lua
--Key Test Project
--By Rain_Effect,pixelbath
local ox=70
local oy=15
local btnLabel={"Up","Down","Left","Right","Btn A","Btn B","Btn X","Btn Y"}

function printBtnLabels(x, y, headingText)
  print(headingText,x,y,8)
  for i=1,8 do
    print(btnLabel[i],x,y+i*10,12)
  end
end

function printInputState(x, y, headingText, startIdx)
  print(headingText,x,y,8)
  for i=1,8 do
    if btn(i-1+startIdx) then
      print("On",x,y+i*10,6)
    else
      print("Off",x-3,y+i*10,1)
    end
  end
end

function TIC()
  cls(0)

  print("Key Test Project",ox,oy,12)

  printBtnLabels(ox-30, oy+15, "Btn")
  printInputState(ox+20, oy+15, "1P", 0)
  printInputState(ox+50, oy+15, "2P", 8)
  printInputState(ox+80, oy+15, "3P", 16)
  printInputState(ox+110, oy+15, "4P", 24)
end
```