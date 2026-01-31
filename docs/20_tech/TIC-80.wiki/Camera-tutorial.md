You can try out the completed project for this tutorial here:

## https://tic80.com/play?cart=161


Using a camera system in TIC-80 may not be as difficult as you may think. Other programs like pico-8 and love2d provide you easier ways to translate the draw coordinates on the screen, however by simply drawing everything with their base coordinates plus the camera coordinates you could simply roll your own camera.

## Center Camera
This camera will follow our player, with no lerping. It is simple and great for both top-down and side-scrolling games. For this tutorial I'll just use basic top down movement to keep the code clean.

First off we're going to make two variables in a table for our camera coordinates. Also we'll define our player and the frame count.

```lua
function init()
 t=0 --frame count or time
 p={x=32,y=32,spr=256} --player
 cam={x=120,y=68}
end
```

This will start our camera off in the center of the screen, since TIC's screen resolution is 240 by 136.

While doing any draw calls, we want to draw everything by their original coordinates minus the camera coordinates. We also want to update the camera coordinates every frame if we want the camera to follow our player.

```lua
init()
function TIC()

 cam.x=120-p.x
 cam.y=68-p.y

 if btn(0) then p.y=p.y-1 end
 if btn(1) then p.y=p.y+1 end
 if btn(2) then p.x=p.x-1 end
 if btn(3) then p.x=p.x+1 end

 spr(p.spr,p.x-cam.x,p.y-cam.y)

end
```

The map is the only draw call that gets treated differently. We simply draw the map by *negative* camera coordinates.

```lua
map(0,0,240,136,-cam.x,-cam.y)
```

## Efficiency is key

Drawing the entire map though wouldn't be very efficient. For turn based games it should be fine, but action games you will immediately notice slow down. Since only a 30 by 17 slice of the map is visible at any given moment, we will only draw the minimum number of map cells required to have everything look fine. This takes a bit of planning and math though. Our end result for this tutorial will be drawing a 31 by 18 chuck of the map every frame. This is the minimum amount we can do without having any edge clipping. Below is an example of the edge clipping I'm talking about.

![clipping](https://user-images.githubusercontent.com/24630549/28901037-8e199170-77c3-11e7-926f-446e700d2ae5.gif)

```lua
cam.x=math.min(120,120-p.x)
cam.y=math.min(64,64-p.y)
local ccx,ccy=cam.x/8,cam.y/8 -- camera cell x and y
map(ccx-15,ccy-8,32,17,(cam.x%8)-8,(cam.y%8)-8)
```

Because the map cells we draw will be constantly changing, drawing our map with the camera offsets will not work anymore. We can also use `math.min` to disable scrolling when the player is less than half way from the center of the screen relative to the map coordinates. This way there isn't and black space on the screen. Also note that I draw the map with `(cam.x%8)-8` because we "overdraw" an extra map cell to avoid more clipping.

We can use the modulo `%` operator to get the remainder of dividing the coordinates by 8, then drawing our map cells with this remainder offset. The modulo method works great, except when our camera's target's coordinates divide evenly by 8. The effect looks like the entire map gets shifted by a cell and needs a resolution. Below is an example of the jerky effect.

![jitter](https://user-images.githubusercontent.com/24630549/28901062-aeb064b8-77c3-11e7-977c-0258b9e31f8a.gif)

```lua
local ccx=cam.x/8+(cam.x%8==0 and 1 or 0)
local ccy=cam.y/8+(cam.y%8==0 and 1 or 0)
```

This works because each cell is a 8 by 8 pixel square. If our camera's x coordinate is 12 for example, `cam.x % 8` would return 4 because 12 can only be divided by 8 once, leaving 4 left over. These 4 pixels would then be used to offset our camera position. So each time our actual map cells change, this number gets reset back to 0. Pretty neat, huh? To deal with the jitter when our coordinates divide evenly by 8 we can shift `ccx` and `ccy` if this case is true.

![right](https://user-images.githubusercontent.com/24630549/28901084-cb287554-77c3-11e7-95bd-2d1e00a79b1c.gif)

This is the **most efficient** way I have found to draw your maps and will be a huge performance increase over drawing large chunks of maps.

### Drawing relative to map coordinates

With the example above, drawing everything besides our map will no longer work by `x+cam.x` for example. We need to account for the screen's center coordinates as well.

```lua
function Enemy:draw()
	spr(self.sprite,cam.x-120+self.x,cam.y-64+self.y)
end
```

Instead of typing out the camera coordinates minus the screen center, I would suggest storing it as a `draw_x` variable to avoid typing it out too much.

## Lerp Camera

![lerpy](https://user-images.githubusercontent.com/24630549/28901093-d8bfae08-77c3-11e7-96c3-26db5128c5a0.gif)

There isn't too much to add when we want our camera movement to be gradual. We want the camera to follow the player, but not be exactly locked on the center of the player every frame. Using a lerped camera we can achieve this, and the results look very nice. This adds a new depth of polish to your game and most modern 2d games use something similar. All we have to do is implement a lerp function while updating our `cam.x` and `cam.y` variables.

```lua
function lerp(a,b,t) return (1-t)*a + t*b end

function TIC()
	cam.x=math.min(120,lerp(cam.x,120-p.x,0.05))
	cam.y=math.min(64,lerp(cam.y,64-p.y,0.05))
end
```

Adjusting the last argument will make the camera slower or faster. I used `0.05` for this example but feel free to use whatever you prefer.