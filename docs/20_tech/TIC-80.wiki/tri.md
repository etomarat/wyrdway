`tri(x1, y1, x2, y2, x3, y3, color)`

## Parameters

* **x1, y1** : the [coordinates](coordinate) of the first triangle corner
* **x2, y2** : the coordinates of the second corner
* **x3, y3** : the coordinates of the third corner
* **color**: the index of the desired color in the current [palette](palette)

## Description

This function draws a triangle filled with **color**, using the supplied vertices.

## Example

![Example](https://imgur.com/McGVad3.gif)

``` lua
-- title:  triangle demo
-- author: Filippo
-- desc:   wiki demo for tri
-- script: lua
-- input:  gamepad
-- pal: ARNE16

function Pir(x,y,w,h,cx,cy)
 tri(x,y,w/2+cx,h/2+cy,x+w,y,1)
 tri(x+w,y,w/2+cx,h/2+cy,x+w,y+h,2)
 tri(x,y,w/2+cx,h/2+cy,x,y+h,8)
 tri(x,y+h,w/2+cx,h/2+cy,x+w,y+h,15)
end

cls()
function TIC()
 for x=0,240,28 do
  for y=0,136,28 do
   cx=12*math.sin(time()/30000*(x+y+1))
   cy=12*math.cos(time()/30000*(x+y+1))
   Pir(x,y,25,25,x+cx,y+cy)
  end
 end
end
```
