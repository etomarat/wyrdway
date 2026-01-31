I know there's already another tutorial on a scrolling camera...
https://github.com/nesbox/TIC-80/wiki/Camera-tutorial

the above tutorial is really good, and even shows you how to make a "passive" camera!
but I prefer Grid-based Movement for my games. and it didn't work well for me to use a smooth moving camera when my character simply jumps from one tile to the next. So Here's a quick tutorial on camera movement for a Grid-based game.

## You can play the Complete Demo here: https://tic80.com/play?cart=250

First, Here's the full code:

```lua
-- title:  Grid-Based Camera
-- author: Bear Thorne
-- desc:   Scrolling Camera demo
-- script: lua

MAXX=30
MAXY=17

c={x=-7,y=2}  --cam
p={x=8,y=10}  --player
e={x=20,y=10} --npc
function TIC()

 if btnp(0,6,6) and mget(p.x,p.y-1)<1 then
  p.y=p.y-1
  c.y=c.y-1
 end
 if btnp(1,6,6) and mget(p.x,p.y+1)<1 then
  p.y=p.y+1
  c.y=c.y+1
 end
 if btnp(2,6,6) and mget(p.x-1,p.y)<1 then
  p.x=p.x-1
  c.x=c.x-1
 end
 if btnp(3,6,6) and mget(p.x+1,p.y)<1 then
  p.x=p.x+1
  c.x=c.x+1
 end

 --here we draw the screen graphics
 cls(3)
 map(p.x-15,p.y-8,MAXX,MAXY)
 spr(256,15*8,8*8,0)
 spr(272,(e.x-c.x)*8,(e.y-c.y)*8,0)
end
```

Here's how it works...notice our player object:
``` lua
p={x=8,y=10}
```

This keeps track of our player...sure that's normal. but look at the spr() function in charge of drawing the player to the screen:
```lua
spr(256,15*8,8*8,0)
```
It doesn't change to show the players current position! it just draws the player floating in the center of the screen! (30x17 visible map area...half is about 15x8...multiply by 8 for cell size to get the pixel coordinates)

now look at the map function:
```lua
map(p.x-15,p.y-8,MAXX,MAXY)
```

this is where the magic happens. The map() function is told to draw the map starting at 15 cells to the left of the player, and 8 cells above the player. since that agrees with our player sprite's position...the "static" sprite always floats over our hero,

but what about items, and NPCs and bad guys?! How do we draw them so they move with the map?
unfortunately, the drawing functions in TIC-80 draw things in screen coordinates, not map coordinates, so if you draw them on a portion of the map that's off-screen, they'll never be seen because they're actually drawn off the screen!

That's why we have a camera object.
```lua
c={x=-7,y=2}
```

now before you ask why it's (-7,2), I don't really know. Just by trial and error I found that if the camera offset is (-7,2) then the objects will be drawn at the correct place.

**Update**
I get it now...it depends on where you place the player to start out. Camera minus Player has to equal the offset we used on the map. in this case:
``` lua
p= {  x= 8,  y=10}
c= {  x=-7,  y=2 }
map(p.x-15,p.y-8, MAXX,MAXY)

--the map offset is 15x8

p.x- c.x  =map x offset
 8 - (-7) = 15

p.y-c.y=map x offset
10 - 2 = 8
```
So if you put the player at (0,0) then start the camera at (15,8)
That puts the camera at the relative zero for the screen.

The way this works is that everytime we move our character, we log the change with our camera. Then we just subtract our camera coordinates from the objects coordinates:
``` lua
spr(272,(e.x-c.x)*8,(e.y-c.y)*8,0)
```

so if we move up once, it moves the object down once to keep it correctly placed on the map.
This should also work for things that walk around...like enemies and NPCs

feel free to use any of the above code in your own projects, and if you're feeling generous, leave a credit for me at the top of your file!

if you have questions, or requests for future tutorials, you can email me at bearknucklesketching@gmail.com