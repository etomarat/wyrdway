`circb (x, y, radius, color)`

## Parameters

* **x, y** : the [coordinates](coordinate) of the circle's center
* **radius** : the radius of the circle in pixels
* **color**: the index of the desired color in the current [palette](palette)

## Description

Draws the circumference of a circle with its center at **x**, **y** using the **radius** and **color** requested.
It uses the _Bresenham_ algorithm.

## Example

![Example](https://imgur.com/LxXbA1H.gif)

``` lua
-- title:  circb demo
-- author: Filippo
-- desc:   circb wiki demo
-- script: lua
-- pal: arne16

a=0
space=10
function TIC()
 cls()
 for i=0,200,space do
  circb(120+80*math.sin(a),
        68+40*math.cos(a),
        i+time()/40%space,
        8)
  circb(120+80*math.sin(a/2),
        68+40*math.cos(a/2),
        i+time()/40%space,
        8) end
 a=a+math.pi/240
end

```
