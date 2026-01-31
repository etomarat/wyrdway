`line(x0, y0, x1, y1, color)`

## Parameters

* **x0, y0** : the [coordinates](coordinate) of the start of the line
* **x1, y1** : the [coordinates](coordinate) of the end of the line
* **color**: the index of the color in the current [palette](palette)

## Description
Draws a straight line from point (x0,y0) to point (x1,y1) in the specified color.

## Example

![Example](https://imgur.com/xhdT0tb.gif)

``` lua
-- line demo
pi8=math.pi/8
pi2=math.pi*2

t=0
function TIC()
 cls()

 --lines
 for i=t%8,135,8 do
  line(i,0,0,135-i,8)
  line(i,135,135,135-i,6)
  t=t+0.01
 end

 --prism
 for i=t/16%pi8,pi2,pi8 do
  x=68+32*math.cos(i)
  y=68+32*math.cos(i)
  line(135,0,x,y,15)
  line(0,135,x,y,15)
 end

 --Border
 line(0,0,135,0,8)
 line(0,0,0,135,8)
 line(135,0,135,135,6)
 line(0,135,135,135,6)

end
```
