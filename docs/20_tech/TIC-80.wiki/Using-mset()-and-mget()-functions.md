In it's most basic form, the map is a way of organizing graphics.
You can draw in your sprites in the map editor...but that's only half the story.
There wouldn't be much point if you couldn't read data back from the map.
To do this we use:
``` lua
mget(cell_x,cell_y)
```
This takes map coordinates as arguments, and returns the ID number of the sprite put in that cell.
In this way we can alter game behaviour based on sprites. Some options include:
* collision detection
* trip wires
* alter player speed based on terrain
* damage inflicting tiles
These gameplay mechanics are common in a variety of games.

Another useful thing to do with the map is alter the sprites.
To do that we use:
``` lua
mset(cell_x,cell_y,sprite_ID)
```
This takes cell coordinates, and a sprite ID, and places that sprite in that cell.
Some uses for this include:
* opening/closing doors
* breakable walls
* spiked floor traps
Again some very old stand-bys in games.

Often times you'll use both of these together.
one to read the map and the other to modify it.
Let's look at a few examples:

## DETECTING TILE PROPERTIES
The easiest way to assign properties to sprites is to arrange similar tiles together.
For example:
![sprite_properties](https://user-images.githubusercontent.com/32113404/32290575-7c145424-bf08-11e7-9262-d6a32bd23fcb.gif)
The non-solid floor sprites are placed in the 1st row...slots 01-15
The non-solid damaging sprites are placed in the 3rd row...slots 33-47
The solid wall tiles are placed in the 5th row slots...slots 66-79

Now we can test for sprite properties by checking it's ID:
``` lua
--first we'll take the tile the player is standing on and log it into "tile"
tile=mget(player.x, player.y)

--now we'll test it for damage properties...remember they're stored between 33-47
if tile>=33 and tile<=47 then
 reduce_player_health()
end
```
I will only place solid tiles after the solids row (or decorative tiles the player will never encounter such as menu or HUD sprites)
This makes checking collision easier:
``` lua
FIRST_SOLID_SPRITES=66 --the sprite ID of the first wall
if mget(player.x, player.y) < FIRST_SOLID_SPRITE then
 --allow player to move
end
```
for a full walkthrough on collision detection, check out my tutorial on it [here](https://github.com/nesbox/TIC-80/wiki/Simple-Collision-Detection)

These can be expanded or reduced for as many properties as you need, and as many sprites as you need.
I have made games with as few as three sprites, but still end up placing them in rows out of protocol.

## OPENING DOORS
For this example we'll assume all the doors will always be on the right side.
``` lua
--first we'll put the door sprite ID into a variable
DOOR=slot_you_put_door_in

--and we'll put the open door sprite into another variable
OPEN_DOOR=slot_you_put_open_door_in

--check if the player is by a door and has pressed (A)
if mget(player.x+1, player.y)==DOOR and btnp(4) then
 --set the door tile to "OPEN_DOOR"
 mset(player.x+1, player.y,OPEN_DOOR)
end
```
The way this works is the **CLOSED DOOR** sprite is placed among the solid wall tiles, and the **OPEN DOOR** sprite is placed among the floor tiles.
This means that the player's collision detection will prevent the player from walking through the closed door (given it's sprite placement)
but will ignore the open door because it's placed among the floor tiles.

## BUILDING LEVELS FROM BLUEPRINTS
One really cool thing you can do with these functions is level building.
The way this works is to use *nested for loops* to iterate over an area of the map and read each cell. from there we can build a level from it.
I've used this method in [Lights Off](https://tic80.com/play?cart=280) So that the game board could be in the same spot, and the variations of the game board could be saved on the map, and loaded into place.
![lights_off](https://user-images.githubusercontent.com/32113404/32300210-741e1af2-bf26-11e7-9f0b-805740e75a0d.gif)
Here's a screenshot of level 1

![map_templates](https://user-images.githubusercontent.com/32113404/32293428-1b10f9da-bf11-11e7-9c2f-954717be63d6.gif)
here's a view of all the levels arranged on the map.

and last here's the code I wrote to read a map:
``` lua
--build a level given the level coor
--a level is 17x17 tiles
function build_level(L)
 local level=LEVELS[L]
 local levelx=level[1]
 local levely=level[2]
 for y=0,16 do
  for x=0,16 do
   --read the current tile in the level template
   local tile=mget(x+levelx,y+levely)
   --set the current tile in the game
   --level to the same value
   mset(x,y,tile)
  end
 end
end
```
This function takes a list as an argument, in this case it is a list of the (x,y) coordinates of a level, and reads it like a book, and copies it to the game board.

These are just a few of the things you can do with the mset() mget() functions.

If you have questions or requests for future tutorials, then email me at bearknucklesketching@gmail.com