# !!!PAGE UNDER CONSTRUCTION!!!
![columns](https://user-images.githubusercontent.com/32113404/32440645-b87e3bc8-c2b9-11e7-9e37-0e21414d6b70.gif)
This Level Generator is one I wrote myself.
The goal was to end up with a "braid" maze.
Which is just a maze without any dead-ends.

Here's how it works:
1. pick a **random point** in the level
2. evaluate it by certain rules
3. then decide wether to build a wall there or leave it blank

This is opposite from the Drunk Walk Generator in that it starts with a blank room and adds the walls.
So the first step will be to make the blank room.

We need to fill the level with floor tiles.
We'll use nested for loops to do that:
``` lua
--map size constants
MAXX=29
MAXY=16
MINX=0
MINY=0

--fill the screen with floor tiles
function floor()
 for x=MINX,MAXX do
  for y=MINY,MAXY do
   mset(x,y,TILE)
  end
 end
end
```
This is simple...iterate over every map cell and make it a floor.

Next we'll add the perimeter wall.
``` lua
--create a perimeter wall
function perimeter()
 for x=MINX,MAXX do
  for y=MINY,MAXY do

   --if x is 0 or 29 then it's a side wall
   --and we want to put walls there
   if x==MINX or x==MAXX then
    mset(x,y,WALL)

   --if y is 0 or 16 then it's a top or bottom wall
   --and we want to put walls there too
   elseif y==MINY or y==MAXY then
    mset(x,y,WALL)
   end
  end
 end
end
```
Here's the result of these two functions:
![blank_room](https://user-images.githubusercontent.com/32113404/32466867-0cfaf25a-c30e-11e7-9ebb-8fbebf881f07.gif)

Now we'll code the rules the generator uses to decide wether or not to build a wall.
It works by checking certain tiles around the given cell.
That pattern is:
![rules_01](https://user-images.githubusercontent.com/32113404/32440735-0f17490c-c2ba-11e7-9d56-907e5d58789c.gif)
Here the red "X" shows the areas that must be clear if it will build a wall.
In the first rule it's:
Three above and Three below
In the second rule it's:
Three to the left and three to the right.

if either of these rules are true then a wall is built.
The tiles without an "X" are ignored completely.
Here's the code to do this:
``` lua
--check tile for buildability
function tile_is_good(n)
 --extract the (x,y) coors from the given cell.
 local x=n[1]
 local y=n[2]

 if --top three are clear and
    mget(x  ,y-1)<WALL and --top
    mget(x+1,y-1)<WALL and --top right
    mget(x-1,y-1)<WALL and --top left
    --bottom three are clear or
    mget(x  ,y+1)<WALL and --bottom
    mget(x+1,y+1)<WALL and --bottom right
    mget(x-1,y+1)<WALL or  --bottom left

    --left three are clear and
    mget(x-1,y  )<WALL and --left
    mget(x-1,y-1)<WALL and --left top
    mget(x-1,y+1)<WALL and --left bottom
    --right three are clear then
    mget(x+1,y  )<WALL and --right
    mget(x+1,y-1)<WALL and --right top
    mget(x+1,y+1)<WALL then--right bottom
  return true
 else
  return false
 end
end

```

Now you could have the generator randomly pick any tile to build on...
but it would be repeatedly checking the same tiles.
This is inefficient and will end up making the generator take longer than necessary.
(I used this method in my first version...and I gave up waiting for it to finish!)
The way to get around this is to build a list of all available tiles:
``` lua
--first declare the empty tile list
tiles={}

--now more nested for loops to
--build a table of available tiles
function log_all_tiles()
 for x=MINX,MAXX do
  for y=MINY,MAXY do
   --if the current cell is a floor tile then
   if mget(x,y)==TILE then
    --log it into the tiles list
    table.insert(tiles,#tiles+1,{x,y})
   end
  end
 end
end
```
And now we can randomly pick tiles from the list...then remove them as we use them.
In this way we will never check the same tile twice!

We'll use this in the next function...
It's where we actually build the walls:
``` lua
--lay a wall at a random point
function lay_wall()
 --pick a random index within the range of the "tiles" list
 local index=math.random(1,#tiles)
 --get the tile at that index and log it into "cell"
 local cell=tiles[index]
 --get the (x,y) for easier use
 local x=cell[1]
 local y=cell[2]

 --here we evaluate the tile
 if tile_is_good(cell) then
  --if it passed then we build a wall there
  mset(x,y,WALL)
 end
 --last we remove that tile...even if we didn't build a wall on it.
 table.remove(tiles,index)
end
```
As you can see, once the function evaluates a tile it either:
builds a wall then removes it from the list,
or simply removes it from the list.

Here's I've drawn red dots to show every tile still in the list.
Watch them get removed as they're checked!
![tile_list_vis](https://user-images.githubusercontent.com/32113404/32462021-8ca1c27e-c2fd-11e7-9d62-1688c1dcbeeb.gif)
once the "tiles" list is empty...you're done!

Last we'll make a function to bundle all these steps together:
``` lua
--build the game map
function build_map()
 --put a wall at a random point
 lay_wall()
 --if the "tiles" list isn't empty then
 if #tiles>0 then
  --do it again
  build_map()
 end
end
```
Calling this function will build the level instantly...
(or as fast as your system can crunch those numbers)

As you can see, this generator only makes rows and columns...
But you can change that by simply modifying the rules it follows!

Here's an alternate set of rules:
![rules_02](https://user-images.githubusercontent.com/32113404/32440844-92b2640e-c2ba-11e7-8a82-2948ca986d6f.gif)

And here's the result of those rules:
![braids_2](https://user-images.githubusercontent.com/32113404/32440757-270ced28-c2ba-11e7-874e-90a423c09278.gif)

This set of rules allows corners, but also allows dead ends.
So by definition it isn't a "braid" maze.
However, you can try different rules to create different results!

I have written a better (and more complicated) generator that generates *true* braid mazes...
But it will be covered in another tutorial.

Here's the complete code for this generator:
``` lua
-- title:  Braid Maze
-- author: Bear Thorne
-- desc:   Random Point Level Generator
-- script: lua

TILE=1
WALL=17
DUDE=33

MAXX=29
MAXY=16
MINX=0
MINY=0

tiles={}
--fill the screen with floor tiles
function floor()
 for x=MINX,MAXX do
  for y=MINY,MAXY do
   mset(x,y,TILE)
  end
 end
end

--create a perimeter wall
function perimeter()
 for x=MINX,MAXX do
  for y=MINY,MAXY do
   if x==MINX or x==MAXX then
    mset(x,y,WALL)
   elseif y==MINY or y==MAXY then
    mset(x,y,WALL)
   end
  end
 end
end

--build a table of available tiles
function log_all_tiles()
 for x=MINX,MAXX do
  for y=MINY,MAXY do
   if mget(x,y)==TILE then
    table.insert(tiles,#tiles+1,{x,y})
   end
  end
 end
end

--check tile for buildability
function tile_is_good(n)
 local x=n[1]
 local y=n[2]

 if --top three are clear
    mget(x  ,y-1)<WALL and
    mget(x+1,y-1)<WALL and
    mget(x-1,y-1)<WALL and
    --bottom three are clear
    mget(x  ,y+1)<WALL and
    mget(x+1,y+1)<WALL and
    mget(x-1,y+1)<WALL or

    --left three are clear
    mget(x-1,y  )<WALL and
    mget(x-1,y-1)<WALL and
    mget(x-1,y+1)<WALL and
    --right three are clear
    mget(x+1,y  )<WALL and
    mget(x+1,y-1)<WALL and
    mget(x+1,y+1)<WALL then
  return true
 else
  return false
 end
end

--lay a wall at a random point
function lay_wall()
 local index=math.random(1,#tiles)
 local cell=tiles[index]
 local x=cell[1]
 local y=cell[2]
  if tile_is_good(cell) then
   mset(x,y,WALL)
  end
 table.remove(tiles,index)
end

--build the game map
function build_map()
 lay_wall()
 if #tiles>0 then
  build_map()
 end
end

--draw screen
function draw()
 cls()
 map(MINX,MINY,MAXX+1,MAXY+1)
end

function init()
 floor()
 perimeter()
 log_all_tiles()
 build_map()
end

init()
function TIC()
 draw()
 --press (A) to build another maze
 if btnp(4) then
  init()
 end
end
```

Feel free to use any portion of the above code in your own projects!
Just put a credit to me at the top of your file and we be having no problems :)

If you have questions or requests for future tutorials then email me at bearknucklesketching@gmail.com