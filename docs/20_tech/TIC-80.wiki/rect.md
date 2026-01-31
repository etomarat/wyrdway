`rect(x, y, width, height, color)`

## Parameters
* **x, y** : [coordinates](coordinate) of the top left corner of the rectangle
* **width** : the width the rectangle in pixels
* **height** : the height of the rectangle in pixels
* **color** : the index of the color in the [palette](palette) that will be used to fill the rectangle

## Description

This function draws a filled rectangle at the specified position.

See also:

- [rectb](rectb) - draw only the border of the rectangle

## Example

![Example](https://imgur.com/CxKY5A2.gif)

``` lua
-- rect demo
x=120
y=68
dx=7
dy=4
col=1

cls()
function TIC()
--Update x/y
 x=x+dx
 y=y+dy
 --Check screen walls
 if x>240-6 or x<0 then
  dx=-dx
  col=col%15+1
 end
 if y>136-6 or y<0 then
  dy=-dy
  col=col%15+1
 end
 --Draw rectangle
 rect (x,y,6,6,col)
end
```