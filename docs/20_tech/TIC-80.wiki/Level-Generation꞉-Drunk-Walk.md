Lately I've been interested (<--read "obsessed") with procedural level generation.
A method of creating levels where instead of spending time building game levels yourself, you spend time teaching the software to build them for you.

It actually started when I had an idea for a puzzle runner that needed unlimited, random levels.
sort of like a bigger, badder version of [Push-em](https://tic80.com/play?cart=251)

well pretty soon the game became a side project, and writing level generators took precedence!
Here's my first, and simplest generator.
![drunk_walk](https://user-images.githubusercontent.com/32113404/31851393-7f805950-b62a-11e7-8902-93aa1ccb4175.gif)

It's an algorithm I found called the "Drunk Walk" algorithm. (for obvious reasons)

**Here's how it works:**
fill the level with walls
spawn a bot in the area
bot walks randomly without leaving the level
wherever the bot walks "carve" pathways
stop when the desired amount of floor space is reached
eliminate unnecessary wall blocks

Now let's look at how to make each step happen

## FILL THE LEVEL WITH WALLS
To do this we need to iterate over every cell in the level.
I like to log the level area into variables for flexibility:
```lua
MINX=0   --start of x cells
MAXX=29  --end of x cells
MINY=0   --start of y cells
MAXY=16  --end of y cells
```
in this way you can scale your map just by changing these values

now we iterate by using "nested for loops":
```lua
--for every x cell
for x=MINX,MAXX do
 --for every y cell
 for y=MINY,MAXY do
  --set the current cell to wall
  mset(x,y,WALL)
 end
end
```
"WALL" is just a variable with the id for the wall sprite.

## SPAWN A BOT
Spawning a bot in a random spot is super simple.
First let's create an easy way to get random numbers:
```lua
function r(a,b)
 return math.random(a,b)
end
```

Now we just randomize the bot's (x,y) when we initialize him:
```lua
 bot={
   x=r(MINX+2,MAXX-2)
   y=r(MINY+2,MAXX-2)
  ld=nil} --last direction...don't worry about it right now
```
Notice we added added a 2 cell buffer around the border to keep the bot from spawning too close to the edge

## BOT WALKS RANDOMLY WITHOUT LEAVING LEVEL
To do this we need four things:
a table of directions
a function for retrieving a random direction
define what "leaving the board" means
move the bot without "leaving the board"

**TABLE OF DIRECTIONS**
``` lua
DIRS={
 {x= 0,y=-1},--up
 {x= 0,y= 1},--d0wn
 {x=-1,y= 0},--left
 {x= 1,y= 0},--right
 {x=-1,y= 0},--left
 {x= 1,y= 0}}--right

--adding left and right twice makes the
--bot more likely to move sideways
--resulting in a level that fits better
--in the screen
```

**FUNCTION TO RETRIEVE RANDOM DIRECTION**
``` lua
function get_dir()
 local td=DIRS[r(1,6)]
 if bot.ld==nil then
  return td
 else
  if bot.ld==td then
   get_dir()
  else
   return td
  end
 end
end
```
Here I decided to not let the bot pick the same direction he just came from.
this makes the bot move around the level instead of dancing back and forth between two tiles

**DEFINE "LEAVING THE BOARD"**
``` lua
--check if the move is within the board
--boundaries
function move_is_valid(d)
 if bot.x+d.x>MAXX-2 or bot.x+d.x<MINX+1
 or bot.y+d.y>MAXY-2 or bot.y+d.y<MINY+1 then
  return false
 else
  return true
 end
end
```
So we can feed the bot's current direction into the function, and it tests if the next cell is out of bounds.
From there it returns TRUE or FALSE so we can use it for "if" statement testing.

**MOVE THE BOT WITHOUT LEAVING THE BOARD**
``` lua
function move()

 --make it 1 in 4 chance for the bot
 --to travel in the same direction
 if r(1,2)==r(1,2) or d==nil then
  d=get_dir()
 end

 if move_is_valid(d) then
  bot.d=d
  bot.x=bot.x+d.x
  bot.y=bot.y+d.y
 end
end
```
Notice that I made it more likely for the bot to keep moving in his current direction than to change directions.
If you leave this out the levels turn out more open with less walkways.
Also see how I used the **move_is_valid()** function.

## CARVE PATHWAYS WHERE THE BOT WALKS
to do this we need to add a single line of code into the bot's move() function:
```lua
mset(bot.x,bot.y,FLOOR)
```
We'll put this in before we make him move. So he sets the map cell he's standing on to floor.
If he walks over the same cell twice, it's already set to floor so setting it again does nothing.
Here's the updated move() function:
``` lua
function move()
 mset(bot.x,bot.y,FLOOR)
 --make it 1 in 2 chance for the bot
 --to travel in the same direction
 if r(1,2)==r(1,2) or d==nil then
  d=get_dir()
 end

 if move_is_valid(d) then
  bot.d=d
  bot.x=bot.x+d.x
  bot.y=bot.y+d.y
 end
end
```

## STOP WHEN THE DESIRED AMOUNT OF FLOOR SPACE IS REACHED
To do this we will make a global variable for the amount of floor tiles we want to end up with:
``` lua
MAX_FLOORS=200 --how many tiles in the level
```

Now we can iterate over every cell and count how many are floor tiles:
``` lua
function count()
 local temp=0
 for x=MINX,MAXX do
  for y=MINY,MAXY do
   if mget(x,y)==FLOOR then
    temp=temp+1
   end
  end
 end
 floors=temp
end
```
Everytime this is called it sets temp to 0, and increments it for every floor tile.
Once it's checked every cell it assigns temp to floors.
This way we can test how many floor tiles are in the level.

## REMOVE UNNECESSARY WALL BLOCKS
The point of this is more or less asthetic. It'll make a clean perimeter by removing the extra wall blocks.
The way we do this is pretty simple, once again we iterate over every cell, this time we test if it has any floor tiles immediatly around it.
If it does than it's either a floor tile, or a perimeter wall.
any cell that doesn't meet this criteria is set to empty space.
``` lua
function wallbreak()
 for x=MINX,MAXX do
  for y=MINY,MAXY do

      --check adjacent cells
   if mget(x-1,y+0)~=FLOOR and --left
      mget(x+1,y+0)~=FLOOR and --right
      mget(x+0,y+1)~=FLOOR and --bottom
      mget(x+0,y-1)~=FLOOR and --top

      --also check diagonals
      mget(x-1,y-1)~=FLOOR and --top-left
      mget(x+1,y-1)~=FLOOR and --top-right
      mget(x-1,y+1)~=FLOOR and --bottom-left
      mget(x+1,y+1)~=FLOOR then--bottom-right

    --set the cell to empty
    mset(x,y,0)
   end
  end
 end
end
```

## PUTTING IT ALL TOGETHER
Last we write a function that bundles all of these steps together.
``` lua
function build_level()
 ::redo::
 move()
 count()

 if floors<MAX_FLOORS then
  goto redo
 end

 mode="initializing"
end
```
You can see that as long as the floor count is less than we asked for, it will continue to loop over move() and count(). Be careful about asking for more floor tiles than is in the level because then the bot will be doomed to wander aimlessly for eternity! forever doing a task he can never complete!! OH YOU EVIL OVERLORD!!
(plus it'll just crash TIC-80)

After the level is complete, the **mode** is changed to "initializing". This is the step where we clean up the walls and add anything we need to before letting the player start. (coins, enemyies, etc...)

That's is all the steps involved. Here's the completed code to demonstrate how they're used.
``` lua
-- title:  D-Walk
-- author: Bear Thorne
-- desc:   drunk walk algorithm
-- script: lua


---------------------------------------
---beginning of the generator script---
---------------------------------------

--sprite constants
FLOOR=1
WALL=17
DUDE=33

MINX=0
MAXX=29
MINY=0
MAXY=16

MAX_FLOORS=200 --how many tiles in the level

--directions
DIRS={
 {x= 0,y=-1},--up
 {x= 0,y= 1},--d0wn
 {x=-1,y= 0},--left
 {x= 1,y= 0},--right
 {x=-1,y= 0},--left
 {x= 1,y= 0}}--right

--adding left and right twice makes the
--bot more likely to move sideways
--resulting in a level that fits better
--in the screen

function init()
 mode="generating"
 t=0
 bot={
   x=r(MINX+2,MAXX-2),
   y=r(MINY+2,MAXY-2),
  ld=nil}

 floors=0

 --set the level to all walls
 for x=MINX,MAXX do
  for y=MINY,MAXY do
   mset(x,y,WALL)
  end
 end

end

--random number shorthand
function r(a,b)
 return math.random(a,b)
end

--get a direction from the DIRS table
function get_dir()
 local td=DIRS[r(1,6)]
 if bot.ld==nil then
  return td
 else
  if bot.ld==td then
   get_dir()
  else
   return td
  end
 end
end

--check if the move is within the board
--boundaries
function move_is_valid(d)
 if bot.x+d.x>MAXX-2 or bot.x+d.x<MINX+1
 or bot.y+d.y>MAXY-2 or bot.y+d.y<MINY+1 then
  return false
 else
  return true
 end
end

--move the carving bot
function move()
 mset(bot.x,bot.y,FLOOR)
 --make it 1 in 2 chance for the bot
 --to travel in the same direction
 if r(1,2)==r(1,2) or d==nil then
  d=get_dir()
 end

 if move_is_valid(d) then
  bot.d=d
  bot.x=bot.x+d.x
  bot.y=bot.y+d.y
 end
end

--count the floor tiles in the level
function count()
 local temp=0
 for x=MINX,MAXX do
  for y=MINY,MAXY do
   if mget(x,y)==FLOOR then
    temp=temp+1
   end
  end
 end
 floors=temp
end

--remove large blocks of walls to make
--a clean perimeter
function wallbreak()
 for x=MINX,MAXX do
  for y=MINY,MAXY do

      --check adjacent cells
   if mget(x-1,y+0)~=FLOOR and --left
      mget(x+1,y+0)~=FLOOR and --right
      mget(x+0,y+1)~=FLOOR and --bottom
      mget(x+0,y-1)~=FLOOR and --top

      --also check diagonals
      mget(x-1,y-1)~=FLOOR and --top-left
      mget(x+1,y-1)~=FLOOR and --top-right
      mget(x-1,y+1)~=FLOOR and --bottom-left
      mget(x+1,y+1)~=FLOOR then--bottom-right

    --set the cell to empty
    mset(x,y,0)
   end
  end
 end
end


function build_level()
 ::redo::
 move()
 count()

 if floors<MAX_FLOORS then
  goto redo
 end

 mode="initializing"
end

--------------------------
--end of generation code--
--------------------------

--update the onscreen graphics
function draw()
 cls()
 map(MINX,MINY,MAXX+1,MAXY+1)
end

init()
function TIC()

 if mode=="generating" then
 --level generation code
  build_level()

 elseif mode=="initializing" then
 --level initializing code
  wallbreak()
  mode="game"

 elseif mode=="game" then
 --game code here--
  draw()
 end
 t=t+1
end
```

As great as this generator turned out, it sadly didn't build suitable levels for my game...So instead I've started making a dungeon crawler built around it!...I'll link to it here when it's done!
And the search for that perfect Level Generator continues!!!

Please fell free to use any portion of this code in you own projects! Just throw a credit to me at the top of your file and we'll be cool. :)

if you have questions or requests for future tutorials, email me at bearknucklesketching@gmail.com