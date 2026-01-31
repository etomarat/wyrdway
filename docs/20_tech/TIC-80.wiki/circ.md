`circ (x, y, radius, color)`

## Parameters

* **x, y** : the [coordinates](coordinate) of the circle's center
* **radius** : the radius of the circle in pixels
* **color**: the index of the desired color in the current [palette](palette)

## Description

This function draws a filled circle of the desired **radius** and **color** with its center at **x**, **y**. It uses the _Bresenham_ algorithm.

## Example

![Example 1](https://imgur.com/OfTnuCD.gif)

``` lua
-- title:  circ demo
-- author: Filippo
-- desc:   circ wiki demo
-- script: lua
-- pal: 0000001b2632493c2bf7e26bbe263344891a31a2f2ffffff005784a46422ffffffeb8931a3ce27b2dcefbfce72ffffff

--init balls
balls={}
d=1
for i=0,50 do
 ball={x =math.random(10,220),
       y =math.random(10,126),
       dx=math.random(1,2)*d,
       dy=math.random(1,2)*d,
       r =math.random(6,12),
       c =math.random(1,6)}
 balls[i]=ball
 d=d*-1
end

function TIC()
 cls()
 for k,b in pairs(balls) do
  --move the ball
  b.x=b.x+b.dx
  b.y=b.y+b.dy
  --check right/left walls
  if b.x >= 240-b.r then
   b.x=240-b.r-1 --constraints inside the wall
   b.dx=-b.dx  --reverse direction
  elseif b.x < b.r then
   b.x=b.r
   b.dx=-b.dx
  end
 --check bottom/top walls
  if b.y >= 136-b.r then
   b.y=136-b.r-1
   b.dy=-b.dy
  elseif b.y < b.r then
   b.y=b.r
   b.dy=-b.dy
  end
  --draw balls
  circ(b.x,b.y,b.r,b.c)
  circ(b.x+b.r/4,b.y-b.r/4,b.r/4,b.c+7)
 end
end
```
## Example 2

![Example 2](https://imgur.com/LPwwrzM.png)

``` lua
-- title: circ example
-- author: Al Rado
-- desc: particular qualities 'circ'
-- script: lua

poke(0x3FF8,2)
cls(15)

SCREEN_WIDTH=240
SCREEN_HEIGHT=136
STEP=20

for radius=1, 6 do
 --vertical
 circ(radius,radius*STEP,radius,0)
 circ(SCREEN_WIDTH-radius-1,radius*STEP,radius,0)-- minus one!
 --horizontal
 circ(radius*STEP,radius,radius,0)
 circ(radius*STEP,SCREEN_HEIGHT-radius-1,radius,0)-- minus one!
end

function TIC() end
```