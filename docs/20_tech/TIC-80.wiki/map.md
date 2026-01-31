`map([x=0], [y=0], [w=30], [h=17], [sx=0], [sy=0], [colorkey=-1], [scale=1], [remap=nil])`

## Parameters
* **x, y** : The coordinates of the top left map cell to be drawn.
* **w, h** : The number of cells to draw horizontally and vertically.
* **sx, sy** : The screen coordinates where drawing of the map section will start.
* **colorkey** : index (or array of indexes 0.80.0) of the color that will be used as transparent color. Not setting this parameter will make the map opaque.
* **scale** : Map scaling.
* **remap**: An optional function called before every tile is drawn. 

### Remap Function
Using this callback function you can show or hide tiles, create tile animations or flip/rotate tiles during the map rendering stage.
``` lua
callback [intile [x y] ] -> [outtile [flip [rotate] ] ]
```
#### Parameters:
* **intile** : The sprite number from the map
* **x, y** : The coordinates of the map cell

#### Return Values:
* **outtile** : The sprite number to be drawn
* **flip** :  
  * 0 - no flipping
  * 1 - flip horizontal
  * 2 - flip vertical
  * 3 - flip both
* **rotate** :
  * 0 - no rotation
  * 1 - 90 deg right
  * 2 - 180 deg
  * 3 - 270 deg right (90 deg left)

***

## Description

The map consists of cells of 8x8 pixels, each of which can be filled with a tile using the [map editor](https://github.com/nesbox/TIC-80/wiki/Map-Editor).

The map can be up to 240 cells wide by 136 deep. This function will draw the desired area of the map to a specified screen position. For example, `map(5,5,12,10,0,0)` will draw a 12x10 section of the map, starting from map co-ordinates (5,5) to screen position (0,0). `map()` without any parameters will draw a 30x17 map section (a full screen) to screen position (0,0).

![XYmap_coordinates](https://github.com/nesbox/TIC-80/assets/26139286/e83ef43a-07f1-480c-9da1-9888406d3d47)

The map function’s last parameter is a powerful callback function​ for changing how each cells is drawn. It can be used to rotate, flip or even replace tiles entirely. Unlike `mset`, which saves changes to the map, this special function can be used to create animated tiles or replace them completely. Some examples include changing tiles to open doorways, hiding tiles used only to spawn objects in your game and even to emit the objects themselves.

The tilemap is laid out sequentially in RAM - writing 1 to 0x08000 will cause tile #1 to appear at top left when `map` is called. To set the tile immediately below this we need to write to 0x08000 + 240, ie 0x080F0

## Examples

``` lua
-- title:  map() example
-- author: Paul59

-- start a new cart before running this example
-- (so we have Ticsy's sprite available)

-- fill some of the map with the top left quarter of Ticsy's sprite
-- (sprite id#1)
for x=0,30 do
	for y=0,30 do
		mset(x,y,1)
	end
end

function TIC()
	cls(13)
	-- draw a 12x10 section of the map to screen pos (0,0)
	map(5,5,12,10,0,0)
end
```

```lua
-- title:  Remap demo
-- author: AnastasiaDunbar, Lua translation by StinkerB06
-- desc:   Draw a map with animated waterfall

--Note that `yourWaterfallTile` and `frames` aren't defined here. This is up to you.
yourWaterfallTile= --Index of the waterfall tile in sprite editor.
speed= -- The value of `speed` should be greater than 0 but less than or equal to 1.
frames= -- Number of frames/tiles in the waterfall animation. The animation tiles indices should follow yourWaterfallTile.

gameTicks=0
function remap(tile,x,y)
	local outTile,flip,rotate=tile,0,0
	if tile==yourWaterfallTile then
		outTile=outTile+math.floor(gameTicks*speed)%frames
	end
	return outTile,flip,rotate --or simply `return outTile`.
end
function TIC()
	cls()
	map(0,0,30,17,0,0,-1,1,remap) --The `remap()` function is used here.
	gameTicks=gameTicks+1
end
```


``` lua
-- title:  draw map according to camera
-- author: borbware

cam={x=0,y=0} --camera
plr={x=30,y=20}--player

function mapdrw()--draw map according to camera coordinates
    map(
        cam.x//8,
        cam.y//8,
        31,
        18,
        -(cam.x%8),
        -(cam.y%8)
    )
end

function TIC()
	cls(13)
	mapdrw()-- draw a 31x18 section of the map to camera position 
	spr(1,plr.x-cam.x,plr.y-cam.y)--draw player after map
end
```

![demo_camera_map](https://github.com/nesbox/TIC-80/assets/26139286/1065ecdc-7001-4236-a0a4-2d557b27bfc9)

``` lua
-- title:  scroll depending on boundaries following camera 
-- author: Popolon adding full example to Bobware example
W,H = 240,136 -- screen width/height
bdd = 30 -- scroll bounding distance
-- scroll bounding box 
minx,miny = bdd,bdd
maxx,maxy = W-bdd,H-bdd

cam={x=0,y=0} --camera
plr={x=30,y=20}--player

-- tile #0 fill background by default
sprmap = 0x04000 --poke draw a random tile shape on it
for i=1,20 do
 poke4(sprmap*2 +math.random(0,8*8), math.random(0,15))
end

for y=0,33 do -- place empty (tile #16) borders on tilemap
 mset(0,y,16) mset(59,y,16)
end
for x=0,59 do
 mset(x,0,16) mset(x,33,16)
end

function mapdrw()--draw map according to camera coordinates
    map(
        cam.x//8, cam.y//8, -- source tiles
        31, 18, -- destination pixels
        -(cam.x%8),-(cam.y%8) -- smoothing modulo
    )
end

function rebound(step) -- recompute boundings
 bdd = bdd + step -- change bounding from step
 minx,miny = bdd,bdd
 maxx,maxy = W-bdd,H-bdd
end

function TIC()
-- vertical tests and scroll
 if btn(0) then
  -- move player up if > bound
  if plr.y > 0 then plr.y = plr.y - 1 end
  -- move camera if player at scroll bound
  --  and camera not at playfield limit
  if plr.y - cam.y < miny and cam.y > 0 then
   cam.y = cam.y - 1 end
 end
 if btn(1) then
  -- limit scroll to 2*screen height - 8 pixel (player size)
  if plr.y < H * 2 - 8 then plr.y = plr.y + 1 end
  -- limit camera at 2*H (Height) - H (its own Height) = H
  if plr.y - cam.y > maxy - 8 and cam.y < H then
   cam.y = cam.y + 1 end
 end
-- same thing than vertically but horizontally
 if btn(2) then 
  if plr.x > 0 then plr.x = plr.x - 1 end
  if plr.x - cam.x < minx and cam.x > 0 then
   cam.x = cam.x - 1 end
 end
 if btn(3) then
  if plr.x < W * 2 - 8 then plr.x = plr.x + 1 end
  if plr.x - cam.x > maxx-8 and cam.x < W then
   cam.x = cam.x + 1 end
 end
 -- shrink/grow boundary distance to screen limit
 if btnp(4) and bdd > 0 then rebound(-5) end
 if btnp(5) and bdd < 50 then rebound(5) end 

 cls(13)
 mapdrw() -- draw a 31x18 section of the map to camera position
 spr(1,plr.x-cam.x,plr.y-cam.y) -- draw player after map
 rectb(minx,miny,maxx-minx,maxy-miny,12) -- draw bounding box
end
```
