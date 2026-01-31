Most games require objects to be dynamically created. It might be enemies that appear periodically, or coins that sprout out of boxes...either way you need a method for creating things, without having to manually place every one of them in a game. This tutorial deals with spawning and managing multiple objects.

We will write a game where sheep will spawn when the player presses A...each sheep will walk in their own direction. If they hit a wall they will change directions. If they fall in a hole, they will die and be removed from the game.
![spawning objects](https://user-images.githubusercontent.com/32113404/31679667-6b5badd0-b337-11e7-915f-5ad172b9decb.gif)

## You can play the completed game here: https://tic80.com/play?cart=249

We want the sheep to be able to move on their own, so we need to make some direction constants...

``` lua
    U={x= 0,y=-1} --up
    D={x= 0,y= 1} --down
    L={x=-1,y= 0} --left
    R={x= 1,y= 0} --right

    DIRS={U,D,L,R}
```
We need to make our objects and store them in a table...so let's make an empty table

``` lua
--create an empty table for storing our
--objects as we create them
sheeps={}
```

Now we can write some functions to handle building and updating the objects...
random numbers are used constantly throughout game logic. so having them easy to get is a must...

``` lua
    --before we do anything, I always make
    --a shortcut for getting random numbers
    -- make it a local function so it's
    -- faster to execute
    -- could also just write
    -- `local r=math.random`
    -- but for the sake of showing our work
    -- make it more explicit
    local function r(a,b)
	return math.random(a,b)
    end
```

now we need a function to build our objects. We want to test the object for certain flaws (like being spawned inside a wall or too close to the player) and log it into our table we wrote earlier.

``` lua
    function build_sheep()

     --we want the sheep to pop up in a random
     --spot when this function is called. so
     --let's pick a random (x,y) to start

	local tx=r(MINX,MAXX) --temporary x
	local ty=r(MINY,MAXY) --temporary y

	--now we need to check if the chosen
	--(x,y) is already occupied...
	--to do this we'll just read the map
	--cell at the given coor and check if
	--it's a "solid"
	if mget(tx,ty)>=WALL then

	 --the cell is solid so recall the
	 --build_sheep() function again to
	 --start over
	 return build_sheep()
     end

	--now that we tested the coors, let's
	--build a sheep.

	--store the sheep in the temporary "z"
	--variable...
	local z={
	       x=tx,
	       y=ty,
	       d=DIRS[r(1,4)]}

	--and now we can store it in the "sheeps"
	--table
	table.insert(sheeps,#sheeps+1,z)
    end
```

if you're confused about how I'm testing map cells for being "solid" then check out my other tutorial on collision detection. It will fill you in.
https://github.com/nesbox/TIC-80/wiki/Simple-Collision-Detection

now notice that each "sheep object" has three attributes, x coordinate, y coordinate, and direction. but an object can have as many attributes as you need. You can specify the sprite to use for it, the gender of the object, friend or enemy, health, speed, strength...etc. This is just a method of reading an objects unique attributes, and doing something different for each one.
So next let's write a function to move and kill them!

to do this, we need to use a for loop to read the info from each object.

``` lua
    --this move function will iterate
    --over all our sheep and update them
    --based on their personal information
    function move_sheep()

    for id,sheep in pairs(sheeps) do

    --first up, if a sheep somehow spawned
    --inside a wall...let's remove him
    if mget(sheep.x,sheep.y)>=WALL then
     table.remove(sheeps,id)
    end

    --log the sheeps next coors...
    --where he is plus where he's going
    local tx=sheep.x+sheep.d.x
    local ty=sheep.y+sheep.d.y

    --test for obstacles...
    if mget(tx,ty)>=WALL then

     --pick a new direction if the sheep
     --ran into a wall.
     sheep.d=DIRS[r(1,4)]

    else
     --the area is clear so move him there
     sheep.x=tx
     sheep.y=ty
    end

    --now we can check for a hole and
    --delete the sheep if he has fallen in
    if mget(sheep.x,sheep.y)==HOLE then

     --here we can use the id to remove a
     --specific sheep from the list.
     table.remove(sheeps,id)
    end
    end
    end
```

to understand what's going on here, we need to look at the pairs() function.
it takes a table as an argument, and returns the key, and the value. for example...

``` lua
    list={"spam","toast","blah"}
```

so if we called:

``` lua
    for key,item in pairs(list) do
```

the first time the for loop is executed...

``` lua
    key=1       --the index of the value
    item="spam" --the value of the index
```

the second time the for loop is executed...
```lua
    key=2
    item="toast"
```

in this way we can use the "key" variable to remove the current item.

this may be redundant for anyone fluent in lua, but I decided to include it because I hadn't used pairs() before working with TIC-80.

finally we can draw all of the updates to the screen for the player to see!

``` lua
    --last we need a draw() function for
    --updating the screen
    function draw()
     cls()
     map(0,0,MAXX,MAXY)

     --we need to iterate over the sheep and
     --draw each at their personal (x,y)
     if #sheeps>0 then
      for id,sheep in pairs(sheeps) do

       --multiply the coors by 8 to place
       --sheep correctly on the map
       spr(SHEEP,sheep.x*8,sheep.y*8,0)
      end
     end
    end
```

and now we can write the game loop (FINALLY!)

``` lua
    t=0 --time
    function TIC()
     t=t+1

     --every time we press a button it will
     --spawn a sheep!
     if btnp(4) then build_sheep() end

      --frameskipping to slow game down
      if t%8==0 then

       if #sheeps>0 then
 	move_sheep()
       end
       draw()
      end
     end
```

and here's the completed code (with all the parts included that don't have to do with spawning)

```lua
    -- title:  Spawning
    -- author: Bear Thorne
    -- desc:   Spawning and managing objects
    -- script: lua

    --lonliness is my protege and binds me
    --to myself -

    --VARIABLES

    --first let's declare some sprite vars
    SPACE=0
    GRASS=1
    HOLE=2
    WALL=17
    SHEEP=33

    --and to move the sheep around aimlessly,
    --we'll want some direction constants

    U={x= 0,y=-1} --up
    D={x= 0,y= 1} --down
    L={x=-1,y= 0} --left
    R={x= 1,y= 0} --right

    DIRS={U,D,L,R}

    --these help keep track of map size, and
    --makes scaling the code up or down a cinch.

    MINX=0  --minimum x coordinate
    MAXX=29 --maximum x coordinate
    MINY=0  --minimum y coordinate
    MAXY=16 --maximum y coordinate

    --create an empty table for storing our
    --objects as we create them
    sheeps={}

    --FUNCTIONS

    --before we do anything, I always make
    --a shortcut for getting random numbers
    function r(a,b)
     return math.random(a,b)
    end

    --this function will build our objects,
    --test them, and if they pass, build 'em
    function build_sheep()

        --we want the sheep to pop up in a random
	--spot when this function is called. so
	--let's pick a random (x,y) to start

	local tx=r(MINX,MAXX) --temporary x
	local ty=r(MINY,MAXY) --temporary y

	--now we need to check if the chosen
	--(x,y) is already occupied...
	--to do this we'll just read the map
	--cell at the given coor and check if
	--it's a "solid"
	if mget(tx,ty)>=WALL then

	 --the cell is solid so recall the
	 --build_sheep() function again to
	 --start over
	 build_sheep()
        end

	--now that we tested the coors, let's
	--build a sheep.

	--store the sheep in the temporary "z"
	--variable...
	local z={
	       x=tx,
	       y=ty,
               d=DIRS[r(1,4)]}

     --and now we can store it in the "sheeps"
     --table
     table.insert(sheeps,#sheeps+1,z)
    end

    --next we can write a function to iterate
    --over all our sheep and update them
    --based on their personal information
    function move_sheep()

     for id,sheep in pairs(sheeps) do

      --first up, if a sheep somehow spawned
      --inside a wall...let's remove him
      if mget(sheep.x,sheep.y)>=WALL then
       table.remove(sheeps,id)
      end

      --log the sheeps next coors...
      --where he is plus where he's going
      local tx=sheep.x+sheep.d.x
      local ty=sheep.y+sheep.d.y

      --test for obstacles...
      if mget(tx,ty)>=WALL then

       --pick a new direction if the sheep
       --ran into a wall.
       sheep.d=DIRS[r(1,4)]

      else
       --the area is clear so move him there
       sheep.x=tx
       sheep.y=ty
      end

      --now we can check for a hole and
      --delete the sheep if he has fallen in
      if mget(sheep.x,sheep.y)==HOLE then

       --here we can use the id to remove a
       --specific sheep from the list.
       table.remove(sheeps,id)
      end
     end
    end

     --last we need a draw() function for
     --updating the screen
     function draw()
     cls()
     map(0,0,MAXX,MAXY)

     --we need to iterate over the sheep and
     --draw each at their personal (x,y)
     if #sheeps>0 then
      for id,sheep in pairs(sheeps) do

       --multiply the coors by 8 to place
       --sheep correctly on the map
       spr(SHEEP,sheep.x*8,sheep.y*8,0)
      end
     end
    end

    t=0 --time
    function TIC()
     t=t+1
     --every time we press a button it will
     --spawn a sheep!
     if btnp(4) then build_sheep() end

     --frameskipping to slow game down
     if t%8==0 then

      if #sheeps>0 then
       move_sheep()
      end
      draw()
     end
    end
```

Feel free to use any portion of this code in your own projects, if you're feeling generous, put a credit to me at the top of your file!

if you have questions or requests for future tutorials...you can email me at bearknucklesketching@gmail.com