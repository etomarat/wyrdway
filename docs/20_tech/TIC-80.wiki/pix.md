`pix(x, y, color)` Draw a pixel in the specified color

`pix(x, y) -> color` Retrieve a pixel's color

## Parameters

* **x, y** : [coordinates](coordinate) of the pixel
* **color** : the index of the [palette](palette) color to draw

## Returns

* **color** : the index (0-15) of the [palette](palette) color at the specified [coordinates](coordinate).

## Description

This function can read or write individual pixel color values. When called with a **color** argument, the pixel at the specified [coordinates](coordinate) is set to that color. When called with only **x y** arguments, the color of the pixel at the specified coordinates is returned.

## Examples

### Draw Pixels

![Example 1](https://imgur.com/ydW0Ttm.gif)

``` lua
-- demo pix
cls(0)
function TIC()
  for i = 0,6000 do
    x = math.random(240)
    y = math.random(136)
    --Put a math colored pixel at random place
    color = (time()//1000*x*y)%60
    pix(x,y,color)
  end
end
```

### Read a pixel's color

![Example 2](https://imgur.com/HpYZqSw.gif)

``` lua
--demo pix read
t=0
--Draw some background
cls(0)
for i=0,15 do
 rect(9*i,6*i,6*i,3*i,i)
end

function TIC()
 if(t>12)then --wait some time
  t=0
  for x=0,240,2 do   --every 2 pixel in width
   for y=0,136,2 do  --every 2 pixel in height
    c=pix(x,y)       --take color
    c=(c+1)%15       --change it
    pix(x,y,c)       --put it back
  end
 end
end
t=t+1
end

```