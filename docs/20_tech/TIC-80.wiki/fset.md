_This API was added in version 0.80._

`fset(sprite_id, flag, bool)`

## Parameters

* **sprite_id** : sprite index (0..511)
* **flag** : index of flag (0-7) to set
* **bool** : state to set (true/false)

## Description

This function sets the sprite flag to a given boolean value. Each sprite has eight flags which can be used to store information or signal different conditions. For example, flag 0 might be used to indicate that the sprite is invisible, flag 6 might indicate that the sprite should be drawn scaled etc.

To read the value of sprite flags, see [fget](fget).  
Persistent flags can also be set from the [sprite editor advanced mode](https://github.com/nesbox/TIC-80/wiki/Sprite-editor#advanced-mode).


## Example
``` lua
-- title:  fset/fget example
-- author: paul59
-- script: lua

-- create a new cart
-- use keyboard 'z' and 'x' to toggle
-- flags 4 and 6 of sprite #1
-- between true/false

function TIC()
  cls(14)
  if btnp(4) then fset(1,4,not fget(1,4)) end
  if btnp(5) then fset(1,6,not fget(1,6)) end
  -- show sprite if flag 4 is true
  if fget(1,4) then
    -- scale up if flag 6 is true
    if fget(1,6) then
      spr(1,0,0,-1,2)
    else
      spr(1,0,0,-1,1)
    end
  end
end

```