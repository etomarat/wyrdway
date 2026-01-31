`memset(addr, value, length)`

## Parameters

* **addr** : the address of the first byte of [RAM](RAM) you want to write to
* **value** : the value you want to write (0..255)
* **length** : the length of the memory block you want to set

## Description

This function sets a continuous block of [RAM](RAM) to the same value.
The address is specified in hexadecimal format, the value in decimal.

## Example

``` lua
-- title:  memset demo
-- author: paul59
-- desc:   demonstrate the use of memset
-- script: Lua

local v=0

function TIC()

  -- the screen occupies the first 16320 bytes of TIC's RAM
  -- (240x136 pixels, 4 bits per pixel)
  -- we can clear the screen by writing a value to this block of memory
  memset(0x0000,v,16320)

  -- since we are writing two pixels with each byte we can
  -- easily obtain a striped effect
  -- use button 'A' (keyboard 'z') to toggle the value
  if btnp(4) then
    if v==0 then
      -- prepare to write colors 1 and 6
      v=(1<<4)+6
    else
      -- use color 0
      v=0
    end
  end

end
```