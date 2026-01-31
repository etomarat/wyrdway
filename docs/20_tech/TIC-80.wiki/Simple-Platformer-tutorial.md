# Simple Platformer Tutorial

Note: The completed project for this tutorial can be played in browser here:
 http://tic80.com/play?cart=101

In this tutorial we'll be learning the basics of map collisions with TIC-80 to create a simple platformer game. There are multiple ways to approach this, but I find the method used here to be straightforward and easy to follow. This guide was written for a reader who already has a decent understanding of the Lua language, but shouldn't​ be too hard to follow for beginners.

If you're​ coming from Pico-8, the lack of sprite flags in TIC-80 may be concerning at first. (Note: TIC-80 now has sprite flags, if you toggle on Advanced mode in the sprite editor.) If you're​ new to fantasy consoles, sprite flags allow you to set different “switches” on and off for each sprite index. Most Pico-8 users will simply dedicate a flag index as solid. For collisions they then read the player's coordinates, get the map sprite from the coordinates, and check if the sprite’s solid flag is true.

## Solution Without Flags
For TIC-80 I use a similar approach to sprite flags by storing all of my solid sprites in a table. There is a snippet on the TIC-80 wiki for sprite flags, I just find this method more straightforward.

```lua
local solids={[1]=true,[3]=true}
```

The list can be as long as you like, just try to keep it numeric order for easy reading. I like to declare my solids table near the top of my file, however some may prefer to define the table with a initialize function, or a function called at the start of the game:

```lua
function init()
    solids={[1]=true,[3]=true}
    p={
        x=0,
        y=0
    }
end
```

As you can see, I put my solids table and my player table (p) in the init() function, just be sure to call the function at the start of your code. TIC-80 does not call it automatically like similar engines would:

```lua
init() --calling our function after defining it
function TIC()
    --update and draw stuff here
end
```

## Setting up our Player
This section is the most basic of basic Lua. We're going to create table to store all of the player's properties in:

```lua
p={
    x=120,
    y=68,
    vx=0, --Velocity X
    vy=0, --Velocity Y
}
```

You may have your own variables you want to store for the player, like the sprite, flip and rotate properties. We're just going to keep it simple here though.

## Player Movement
For this sample game, we'll be making a simple platformer with gravity. The left/right arrows will move the player respectively​. For now we're just going to represent the player as an 8 by 8 white rectangle.

```lua
function TIC()

    if btn(2) then p.vx=-1
        elseif btn(3) then p.vx=1
        else p.vx=0
    end

    --we’ll deal with collisions in this area

    p.x=p.x+p.vx
    p.y=p.y+p.vy

    cls()
    map()
    rect(p.x,p.y,8,8,15)
end
```

If you ran our little game at this point you'd have a white rectangle that moves with the left and right arrows keys on a black background.

Now that we have our base for horizontal movement, we can start with gravity and collisions.

## Collision Checking and Gravity
Since our player is the same size of our map tiles, we only ever have to check collisions around the 4 corners of our player. We will attempt to never allow the player to be inside a solid tile, even by a single pixel.

The TIC-80 `mget(x,y)` function returns the sprite index of the map at the given cell coordinates. Keep in mind these coordinates are in cells, not pixels.

For the actual collision checking, we'll be writing our own little function that returns if the sprite is solid at the given coordinates, from pixels to cells:

```lua
function solid(x,y)
    return solids[mget((x)//8,(y)//8)]
end
```

Note the floor division operator `//` which the same as writing math.floor(x/8) in this example.

This function does away with tedious code patterns otherwise required for collision checking.

We're now ready to start designing a simple level and piece our code together. We'll start by dealing with horizontal collisions. Write this block where I designated in the player movement segment.

```lua
if solid(p.x+p.vx,p.y+p.vy) or solid(p.x+7+p.vx,p.y+p.vy) or solid(p.x+p.vx,p.y+7+p.vy) or solid(p.x+7+p.vx,p.y+7+p.vy) then
    p.vx=0
end
```

As you can see, we're checking collisions at the four corners of the player's boundaries. Our player now stops when he's touching a solid tile horizontally. We're going to have to do a very similar method for vertical collisions.

The player's vertical velocity will need to be increased by a gravity constant every frame if he's not on top of something. This means we only have to check collisions along the bottom of the player for now. I find it easier this way and add top collisions later.

```lua
if solid(p.x+p.vx,p.y+8+p.vy) or solid(p.x+7+p.vx,p.y+8+p.vy) then
    p.vy=0
else
    p.vy=p.vy+0.2
end
```

That's pretty much it for map collisions! Jumping is as simple as checking if the player’s y velocity is 0, then setting it to a constant value:

```lua
if p.vy==0 and btn(4) then p.vy=-2.5 end
```

And now that our players vertical velocity can be negative, we'll need to check for collisions along the top edge of the player:

```lua
if p.vy<0 and (solid(p.x+p.vx,p.y+p.vy) or solid(p.x+7+p.vx,p.y+p.vy)) then
    p.vy=0
end
```

## Wrapping it up

```lua
function solid(x,y)
    return solids[mget((x)//8,(y)//8)]
end

function init()
    solids={[1]=true,[3]=true}
    p={
    x=120,
    y=68,
    vx=0, --Velocity X
    vy=0, --Velocity Y
}
end

init()
function TIC()

    if btn(2) then p.vx=-1
        elseif btn(3) then p.vx=1
        else p.vx=0
    end

    if solid(p.x+p.vx,p.y+p.vy) or solid(p.x+7+p.vx,p.y+p.vy) or solid(p.x+p.vx,p.y+7+p.vy) or solid(p.x+7+p.vx,p.y+7+p.vy) then
        p.vx=0
    end

    if solid(p.x,p.y+8+p.vy) or solid(p.x+7,p.y+8+p.vy) then
        p.vy=0
    else
        p.vy=p.vy+0.2
    end

    if p.vy==0 and btnp(4) then p.vy=-2.5 end

    if p.vy<0 and (solid(p.x+p.vx,p.y+p.vy) or solid(p.x+7+p.vx,p.y+p.vy)) then
        p.vy=0
    end

    p.x=p.x+p.vx
    p.y=p.y+p.vy

    cls()
    map()
    rect(p.x,p.y,8,8,15)
end
```

Here is the completed code for our project. Feel free to use this code as a base for your first game with TIC-80. If you learned something from reading this of made a game with this tutorial I'd love to know! Now get back to making awesome games!