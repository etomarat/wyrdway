This tutorial deals with "grid movement"

![grid_movement](https://user-images.githubusercontent.com/32113404/31607301-749d1930-b231-11e7-92f4-6b6c80a176d1.gif)

as opposed to "free movement"
![free-movement](https://user-images.githubusercontent.com/32113404/31607365-a850cf2e-b231-11e7-8a78-509e0fb6bebc.gif)

It's a little simpler to handle, and I feel that grid movement has a more retro feel to it.

## you can play the completed game here: https://tic80.com/play?cart=248

If your more interested in free movement detection, then check out the
[Simple Platformer Tutorial](https://github.com/nesbox/TIC-80/wiki/Simple-Platformer-tutorial) by Tremelar.

It deals with free movement collision pretty well. That being said, let's go.

the basic code we will be using is:
``` lua

    -- title:  simple collision detection
    -- author: Bear Thorne
    -- desc:   Detecting Collision for Grid Movement
    -- script: lua

    --VARIABLES

    --sprite vars
    FLOOR=1  --the floor sprite will be stored in the 1 slot
    WALL=17  --the wall sprite will be stored in the 17 slot
    DUDE=33  --the player sprite will be stored in the 33 slot

    --game constants
    SCREEN_X=29
    SCREEN_Y=16

    --player object
    p={
     x=SCREEN_X//2, --center of screen x
     y=SCREEN_Y//2} --center of screen y

    --FUNCTIONS

    --player movement
    --we'll use the btnp() function to detect a single button press
    function move()
        --player presses "up"
        if btnp(0) then
         p.y=p.y-1

        end
        --player presses "down"
    	if btnp(1) then
         p.y=p.y+1

        end
        --player presses "left"
    	if btnp(2) then
         p.x=p.x-1

        end
        --player presses "right"
    	if btnp(3) then
         p.x=p.x+1
        end
    end

    --draw screen graphics
    function draw()
     cls()
     map(0,0,SCREEN_X+1,SCREEN_Y+1)

     --multiplying the player coors by 8 (the size of the map cells)
     --gives us grid movement
     spr(DUDE,p.x*8,p.y*8,0)
    end

    function TIC()
     move()
    	draw()
    end
```

This code can move the player around the screen, but it doesn't deal with collision yet. The player can walk through walls like a ghost at the moment. we'll deal with movement collision first.

the first step is to write a function for checking the map cell ahead of the player, and determining if it's clear or not. And to check that we need to include some direction constants like so...

``` lua

    --Direction constants
    U={x= 0,y=-1}, --up
    D={x= 0,y=+1}, --down
    L={x=-1,y= 0}, --left
    R={x=+1,y= 0}} --right

```
now we can write our function. We'll feed it the player's direction and it will check the cell ahead for obstacles.

``` lua
    --check ahead of player for obstacles
    function is_clear_ahead(dir)
     --log the directions x,y for convenience
     local x=dir.x
     local y=dir.y

     --the mget() function is the heart of the function. it takes an (x,y) coordinate, and checks the
     --map cell at that point. then it returns the sprite id. when I build a game i keep all the collidable
     --sprites past slot 17 on the sprite sheet, so if mget() returns anything less than 17 it won't
     --register as an obstacle.
     if mget(p.x+x,p.y+y)<WALL then

      --we'll return true...as in it is clear ahead.
      return true

     else
      return false
```

and now we can use this function to check for obstacles before we allow the player to move in that direction. Here's the updated move() function.

``` lua
    function move()
     --player presses "up" and up is clear
     if btnp(0) and is_clear_ahead(U) then
      p.y=p.y-1
     end
     --player presses "down" and down is clear
     if btnp(1) and is_clear_ahead(D) then
      p.y=p.y+1
     end
     --player presses "left" and left is clear
     if btnp(2) and is_clear_ahead(L) then
      p.x=p.x-1
     end
     --player presses "right" and right is clear
     if btnp(3) and is_clear_ahead(D) then
      p.x=p.x+1
     end
    end
```

This is "obstacle" collision detection. It makes it so the player can't walk into anything "solid". But what if we want the player to run into a coin? It shouldn't stop the player from moving, So we use another type of collision..."item" collision detection.

For this type of collision, we'll need another object to collide with...let's make a coin object.

``` lua
    --coin object
    coin={
     x=10,
     y=10}
```

Now let's write a function that takes two objects as arguments and checks if they have collided.

``` lua
    --check for collision between two objects
    function collision(obj1,obj2)
     --check both objects (x,y) coors and return true if they are in the same cell.
     if obj1.x==obj2.x and obj1.y==obj2.y then
      return true
     end
    end
```

and now using this function is even easier than writing it.

``` lua
    --check for collision between player and coin
    if collision(p,coin) then
     --we'll relocate coin to another random cell
     coin.x=math.random(2,27)
     coin.y=math.random(2,14)
    end
```

This is the two basic types of collision in games. It works much the same way with multiple objects, but spawning and managing multiple objects is something I will deal with in another tutorial.

Here's a screenshot of the completed game running:
![collision_tut](https://user-images.githubusercontent.com/32113404/31607387-b56962e8-b231-11e7-8658-612e8dbb8425.gif)

Here's the complete (and debugged) script.

``` lua
    -- title:  Collision Tutorial
    -- author: Bear Thorne
    -- desc:   Basic Collision Detection
    -- script: lua

    --VARIABLES

    --sprite vars
    FLOOR=1
    COIN=2
    WALL=17
    DUDE=33

    --game constants
    SCREEN_X=29
    SCREEN_Y=16

    --Direction constants
    U={x= 0,y=-1} --up
    D={x= 0,y= 1} --down
    L={x=-1,y= 0} --left
    R={x= 1,y= 0} --right

    --player object
    p={
     x=SCREEN_X//2, --center of screen x
     y=SCREEN_Y//2} --center of screen y

    --coin object
    coin={
     x=10,
     y=10}


    --FUNCTIONS

    --check ahead of player for obstacles
    function is_clear_ahead(dir)
     --log the directions x,y for convenience
     local x=dir.x
     local y=dir.y

     --the mget() function is the heart of the function. it takes an (x,y) coordinate, and checks the
     --map cell at that point. then it returns the sprite id. when I build a game i keep all the collidable
     --sprites past slot 17 on the sprite sheet, so if mget() returns anything less than 17 it won't
     --register as an obstacle.
     if mget(p.x+x,p.y+y)<WALL then

      --we'll return true...as in it is clear ahead.
      return true

     else
      return false
     end
    end

    --check for collision between two objects
    function collision(obj1,obj2)
     --check both objects (x,y) coors and return true if they are in the same cell.
     if obj1.x==obj2.x and obj1.y==obj2.y then
      return true
     end
    end

    function move()
     --player presses "up" and up is clear
     if btnp(0) and is_clear_ahead(U) then
      p.y=p.y-1
     end
     --player presses "down" and down is clear
     if btnp(1) and is_clear_ahead(D) then
      p.y=p.y+1
     end
     --player presses "left" and left is clear
     if btnp(2) and is_clear_ahead(L) then
      p.x=p.x-1
     end
     --player presses "right" and right is clear
     if btnp(3) and is_clear_ahead(R) then
      p.x=p.x+1
     end
    end

    --draw screen graphics
    function draw()
     cls()
	map(0,0,SCREEN_X+1,SCREEN_Y+1)
	spr(DUDE,p.x*8,p.y*8,0)
     spr(COIN,coin.x*8,coin.y*8,0)
    end

    function TIC()

	move()
	draw()

     --check for collision between player and coin
     if collision(p,coin) then
      --we'll relocate coin to another random cell
      coin.x=math.random(2,27)
      coin.y=math.random(2,14)
     end

    end
```

feel free to use any portion of this code in your own projects, if you're feeling generous, put a credit to me at the top of your file!

If you've got questions, or requests for future tutorials, you can email me at bearknucklesketching@gmail.com