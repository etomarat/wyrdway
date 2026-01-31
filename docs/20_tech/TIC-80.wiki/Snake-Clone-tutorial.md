You can play the completed project for this tutorial in browser here:

# https://tic80.com/play?cart=152

A snake clone is the first game that truly made me think outside the box. I needed a simple solution to what seemed like a difficult problem. In the classic snake game, every link of the snake follows the path of the snake’s head, moving at a constant rate, where the snake only changes direction when the player tells him to. When the snake finds a piece of food, he grows one link on his body. In this tutorial we'll attempt to mimic the original snake game mechanics as close as possible. If you're new to Lua and game programming in general, I suggest reading some beginner tutorials before following along. This is meant more as a mechanics tutorial than an introduction.
Setting things up
In our snake clone, we'll be using a table to store all of the different links of our snake. To start things out, we'll make a snake with 3 links; the head, neck, and tail. Well also create a second table for the food the snake will attempt to pick up.

```lua
function init()
    t=0 --time
    score=0
    snake={
        {x=15,y=8}, --tail
        {x=14,y=8}, --neck
        {x=13,y=8} --head
    }
    food={x=0,y=0}
    dir=dirs[0]
end
```

It is important to define the tail first and the head last as we'll be working directly with table indexes for manipulating our snake.

## Drawing Stuff
Although the different parts of the snake will be made up of 8 by 8 rectangles, we’ll draw each part of the snake times 8 so we can easily work with single increments for the game logic.

```lua
function draw()
    cls(2)
    for i,v in pairs(snake) do
        rect(v.x*8,v.y*8,8,8,15)
    end
    rect(food.x*8,food.y*8,8,8,6)
end
```
## Snake Movement
When I first thought of how to implement snake movement, I thought of how I could store all of the different link positions, then move each one individually. How would we keep track of moving each segment along the snake’s original path? A method like this wasn't going to work. The idea behind movement for our snake game will work as follows:

1. Check the direction to move the snake

2. Place a new head link in front of our snake's current head, the original head now becomes the neck.

3. If the snake didn't find a piece of food, remove the tail link.

This method is very simple to implement, and works very well. By shifting the indices of our snake every update, we're very easily able to recreate snake-like movement. A new problem we face is we don't want to move the snake every time the TIC function is called. Since the TIC function is called roughly 60 times per second, we can slow gameplay down to a certain rate by writing a simple update function for this:

```lua
function update()
return t%10==0
end
```

By wrapping most of our game mechanics inside a conditional for this function we can make the snake move at a 1/10th second interval. We will use the function something like this:

```lua
function TIC()
    t=t+1
    if update() then
        --core game logic here
    end
end
```

## Queueing a Direction
Although our snake will only move when the update function returns true, we will want the player to decide the direction for our snake to move at any moment. When the player presses an arrow key, the direction is stored for when the snake should move next. The player may choose to change the direction multiple times between update calls so we should do this outside of our update if block.

The first thing to do is make a table as a reference for the relative coordinate to move the snake head to, the table indices will match the btn indices according. Lua’s table indices start at 1 by default, so we can force the table to use 0 by explicitly writing each index. This can be outside of the init function because we will only be referencing it, never changing its contents.

```lua
dirs={
[0]={x= 0,y=-1}, --up
[1]={x= 0,y= 1}, --down
[2]={x=-1,y= 0}, --left
[3]={x= 1,y= 0} --right
}
```

Because our snake is made up of a table, we’ll be working with specific table indices to move the snake around. Using the following variables we can make the code alot easier to read. This chunk should be placed in the TIC function to be called every update.

```lua
head = snake[#snake]
neck = snake[#snake-1]
tail = snake[1]
```

We can easily change which direction the snake will move with the following chunk of code. If the place the player would move to is not the snake’s neck, set the new direction. This way the snake cannot move inside itself.

```lua
local last_dir=dir
if btn(0) then dir=dirs[0]
elseif btn(1) then dir=dirs[1]
elseif btn(2) then dir=dirs[2]
elseif btn(3) then dir=dirs[3]
end
if head.x+dir.x==neck.x and head.y+dir.y==neck.y then
dir=last_dir
end
```

## Food Checking and Setting
Every update call the tail of the snake will be removed since we are inserting a new head, keeping the size of the snake the same. If we simply choose not to remove the tail when he finds some food, we can have him grow by one segment. Once he does find the food, A new piece should spawn at a random location on the map. A recursive function is a function that calls itself. Our setFood() function will continue to call itself until the food spawns in a location not occupied by part of the snake.

```lua
function gotFood()
    if head.x==food.x and head.y==food.y then
        return true
    end
end

function setFood()
    food.x=math.random(0,29)
    food.y=math.random(0,16)
    for i,v in pairs(snake) do
        if v.x==food.x and v.y==food.y then
            setFood()
        end
    end
end
```

## Wrapping things up
We’re now ready to start putting everything together. When the snake hits the side of the screen he should wrap around to the other side. Using the modulo % operator we can easily contain the different parts of the snake within the screen without requiring any additional checks. Movement works by replacing the snake’s head with a new head position plus the queued direction we determined above. We also want to exit the game if the snake’s head collides with any other part of the snake. A simple for loop can take care of this.

```lua
dirs={
[0]={x= 0,y=-1}, --up
[1]={x= 0,y= 1}, --down
[2]={x=-1,y= 0}, --left
[3]={x= 1,y= 0} --right
}

function init()
    t=0 --time
    score=0
    snake={
        {x=15,y=8}, --tail
        {x=14,y=8}, --neck
        {x=13,y=8} --head
    }
    food={x=0,y=0}
    dir=dirs[0]
end

function update()
return t%10==0
end

function gotFood()
    if head.x==food.x and head.y==food.y then
        return true
    end
end

function setFood()
    food.x=math.random(0,29)
    food.y=math.random(0,16)
    for i,v in pairs(snake) do
        if v.x==food.x and v.y==food.y then
            setFood()
        end
    end
end

function draw()
    cls(2)
    for i,v in pairs(snake) do
        rect(v.x*8,v.y*8,8,8,15)
    end

    rect(food.x*8,food.y*8,8,8,6)
end

init()
setFood()
function TIC()
    t=t+1
    head = snake[#snake]
    neck = snake[#snake-1]
    tail = snake[1]
    if update() then

        for i,v in pairs(snake) do
            if i~=#snake and v.x==head.x and v.y==head.y then
                trace("Game OVER!")
                trace("Score: "..score)
                exit()
            end
        end

        table.insert(snake,#snake+1,{x=(head.x+dir.x)%30,y=(head.y+dir.y)%17})
        if not gotFood() then
            table.remove(snake,1)
        else
            setFood()
            score=score+1
        end

    end

    local last_dir=dir

    if btn(0) then dir=dirs[0]
        elseif btn(1) then dir=dirs[1]
        elseif btn(2) then dir=dirs[2]
        elseif btn(3) then dir=dirs[3]
    end

    if head.x+dir.x==neck.x and head.y+dir.y==neck.y then
        dir=last_dir
    end

    draw()
end
```
