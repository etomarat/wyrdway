`rectb(x, y, width, height, color)`

## Parameters
* **x, y** : [coordinates](coordinate) of the top left corner of the rectangle
* **width** : the width the rectangle in pixels
* **height** : the height of the rectangle in pixels
* **color** : the index of the color in the [palette](palette) that will be used to color the rectangle's border.

## Description

This function draws a one pixel thick rectangle border.

See also:

- [rect](rect) - draws a filled rectangle

## Example

![Example 1](https://imgur.com/MN3cnaB.gif)

``` lua
-- 'rectb' demo
x=104
y=60

function TIC()
 cls()
 for s=280,0,-4 do
  s2=s/2
  sd=500/s
  x=sd*math.sin(time()/1000)
  y=sd*math.cos(time()/1000)
  rectb(120+x-s2,68+y-(s2/2),s,s2,8)
 end
end
```

## Second example

![Example 2](https://imgur.com/uDzfyeI.gif)

``` lua
-- 'rectb' demo by Filippo, refactored by Al Rado

HALF_SCR_W = 240/2
HALF_SCR_H = 136/2
DEVIATION = 150
SPEED = 1/500
RECT_COUNT = 70
RECT_STEP = 4
RECT_COLOR = 8

function TIC()
 cls()
 for i = 1, RECT_COUNT do
  width = i*RECT_STEP
  height = width/2
  slowedTime = time()*SPEED
  x = math.sin(slowedTime) * DEVIATION/i - width/2
  y = math.cos(slowedTime) * DEVIATION/i - height/2
  rectb(HALF_SCR_W+x, HALF_SCR_H+y, width, height, RECT_COLOR)
 end
end
```