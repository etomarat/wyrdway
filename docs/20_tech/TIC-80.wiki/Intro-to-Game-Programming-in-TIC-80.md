In this tutorial I will cover the basics of game programming using tic-80. It won't teach any programming, and assumes you already know some lua. 


## You can play the completed game here: https://tic80.com/play?cart=247

Game programming follows a basic structure:.

    VARIABLES 
    FUNCTIONS 
    INITIALIZE 
    GAME LOOP 
        CHECK FOR USER INPUT 
        UPDATE GAME DATA 
        DRAW GAME GRAPHICS 
        CHECK FOR GAME OVER 

This is a loose template, but the majority of games follow something along these lines. Let's go over each section.

## VARIABLES
This is where you'll declare the majority of the game variables. These will contain game data such as character stats and inventories, or global variables like the game speed or size of the game board. Not every variable will be declared here, but the important ones should be.

(EXAMPLE)
``` lua
    --VARIABLES
    GAMESPEED=100
    Time=0
    Name="Levant"
    Capturelevel=50
    Inventory={
              weapon="dagger",
              armor ="leather vest"
              item  ="mugwort"}
    player={
           x=15,
           y=8, }
```
Here you can see a global variable GAMESPEED typed in all caps. These will never be altered during the game. 
We have the time, name and capture level. These may change as the game progresses. 
And finally we have a dictionary to log inventory, and another to log players coordinates. These will be updated as the game character moves.

## FUNCTIONS
This is where we declare the functions we will use during the game. 
They can be blocks of code we will be using repeatedly (such as calculating a players coordinates)  
or blocks of code that work together to do some specific task (such as drawings each bad guy in a level).
And all functions help to make your code easier to read and debug. 

(EXAMPLE)
``` lua
    --FUNCTIONS
    function moveplayer() --update players coordinates according to input
     if btn(3) then --if the player is pressing "right"
      player.x = player.X + playerVelocity
     elseif btn(2) then --if the player is pressing "left"
     player.x = player.x - playerVelocity
     end
    end

    function isOutOfBounds(n)      --check if "n" is out of game bounds
     If (n.x > 10 or n.x < 0) then --board is 10x10
      return true
     elseif (n.y > 10 or n.y < 0) then
      return true
     else
      return false
```
Here is two examples of functions. moveplayer() is a function that will only be called once each game loop, but packing all these commands under the descriptive name "moveplayer" makes everything easier to read. 
As for isOutOfBounds(), it will likely be used multiple times to check if anything has left the game board. And packing all these commands into a function saves you from typing all that code each time you need to check that.

## INITIALIZE 
This is a common section in game programming. It is simply a section where the game is set up (or _initialized_) for the first time, or for restarting a game. Most languages/game engines will use the function init() which will be called automatically whenever the game run, and contains all the code you want run at the start of a game. However, tic-80 does not do this. Instead we have to manually call init() before starting the game loop. 
   
Remember, you don't have to use init() at all. It just makes starting/resetting a game simpler.

(EXAMPLE)
``` lua
    Function init() --define our init() function
     score=0 --set score to zero
     player={
            x=0,
            y=0,} --set player at (0,0)
     lives=3 --set players lives to three
```

Now we can simply call init() before the game loop starts, and whenever we want to reset the game.

## GAME LOOP
This is where the game code actually gets executed.
In tic-80, the game loop is defined as "function TIC()" and it will be run automatically when the game starts. This is where the game listens for user input, modifies the game data, and updates the graphics. A typical game loop might look like this:

(EXAMPLE)
``` lua
    --VARIABLES
    Important variables here

    --FUNCTIONS
    Useful functions here
    Init() function defined here

    Init() --game initialized
    function TIC() --start of game loop
     If not player.dead then
      moveplayer()
      moveenemies()
      If gotCoin(player) then
       score = score + 500
      end
      if collision(player,enemy)
       if player.invincible == true then
        respawn(enemy)
        score = score + 1000
       else
        player.lives = player.lives - 1
        if player.lives == 0 then
         player.dead = true
        else
         respawn(player)
       end
      end
     elseif player.dead == true then
      print("game over")
      print("score: ".. score)
       init()
     end
     drawGraphics(). --update the game graphics
     clock = clock+1 --update game clock
    end
```
This is a rough idea, and some stuff has been simplified for easier reading. You can see where taking the time to write all of the functions beforehand made coding the actual game loop a piece of cake! 


Now let's look at coding a simple game in tic-80
``` lua
    -- title:  Coin Grab
    -- author: Bear Thorne
    -- desc:   Grab the coin before the cpu does
    -- script: lua

    --VARIABLES

    --we will be defining the directions
    --in the game for moving the enemy.
    DIRECTIONS={
               {x= 0,y=-1}, --up
               {x= 0,y= 1}, --down
               {x=-1,y= 0}, --left
               {x= 1,y= 0}} --right

    --we will be skipping frames to reduce
    --the game speed. GAMESPEED just says
    --how many frames to skip.
    GAMESPEED = 8

    --tic-80 references its 16 color pallete
    --by number, so we will be assigning each
    --colors number to a variable with the
    --appropriate name. this will make using
    --colors in our code easier.
          BLACK=0
       DARK_RED=1
      DARK_BLUE=2
      DARK_GRAY=3
          BROWN=4
     DARK_GREEN=5
            RED=6
     LIGHT_GRAY=7
     LIGHT_BLUE=8
         ORANGE=9
      BLUE_GREY=10
    LIGHT_GREEN=11
          PEACH=12
           CYAN=13
         YELLOW=14
          WHITE=15

    --this will be the coordinates we use
    --to place the player when respawning
    PLAYER_RESPAWN_POINT={x=2,y=2}

    --this is the coordinates for the
    --enemys spawn point
    ENEMY_RESPAWN_POINT={x=28,y=15}

    --to save some typing, i usually define
    --the init() function in the variables
    --section. now i can declare the variables
    --and initialize them at the same time.
    --so here goes...
    function init()
     gameover=false
     player={
          id="player",
           x=2,
           y=2,
       lives=3,
       score=0}

      enemy={
         id="enemy",
           x=28,
           y=15,
       score=0}

      coin={
         x=0,
         y=0,}

    clock=0

    spawncoin()
    --we will be defining spawncoin() in a
    --minute, but we will have to perform
    --this whenever the game starts.
    end

    --FUNCTIONS

    --we will be passing players and coins
    --or players and enemies to this function
    --and asking wether they are occupying
    --the same map coordinates. that's how
    --we can check for collision.
    function collision(body1,body2)

     if (body1.x == body2.x and body1.y == body2.y) then
     return true --true means they have collided

     else
      return false--false means they haven't collided
     end
    end

    --we need to randomly spawn a coin on
    --the map, but not where the player or
    --enemy are. this function will do that
    function spawncoin()

    --the coins x coordinates will be
    --randomly chosen from 0-29, which is
    --the width of the game board.
     coin.x=math.random(0,29)

    --and the coins y coordinates will be
    --randomly chosen from 0-16, which is
    --the height of the game board.
    coin.y=math.random(0,16)

     --now we must make sure the coin isn't
     --colliding with the player or enemy.
     --we will call collision(). yeah, you
     --can call a function from inside
     --another function...inception, right?!
     if collision(coin,player) or collision(coin,enemy) then
      spawncoin()

     --this means it call itself and starts
     --over. respawning a coin in another spot
     --until it finds a free space.
     end
    end

    --now let's make a function to respawn
    --a player or enemy based on the
    --argument passed to it.
    function respawn(body)

    --if body is the player then...
     if body.id=="player" then

    --respawn player at PLAYER_RESPAWN_POINT
    body.x=PLAYER_RESPAWN_POINT.x
    body.y=PLAYER_RESPAWN_POINT.y

    --if body is the enemy then...
    elseif body.id=="enemy" then

    --respawn enemy at ENEMY_RESPAWN_POINT
    body.x=ENEMY_RESPAWN_POINT.x
    body.y=ENEMY_RESPAWN_POINT.y
     end
    end

    --now we need to move the enemy
    function moveenemy()

    --pick a random direction from DIRECTIONS
     random=math.random(1,4)
     dir=DIRECTIONS[random]
    --check if the enemy will move out of the screen
    if enemy.x+dir.x < 29 and enemy.x+dir.x > 0 and
    enemy.y+dir.y < 16 and enemy.y+dir.y > 0 then

     --move enemy in the approved direction
     enemy.x=enemy.x+dir.x
     enemy.y=enemy.y+dir.y

    --if the move isn't valid then...
    else
     --call moveenemy() again.
     moveenemy()
    end
    end

    --now we will make a function that will analyze input,
    --check if the move is valid, and then move the player
    --accordingly.
    function moveplayer()
    --if the player presses 'up' and they
    --aren't at the top already then...
    if btn(0) and player.y>0 then

    --move player up by 1
     player.y=player.y-1

    --if the player presses 'down' and
    --they aren't at the bottom already.
    elseif btn(1) and player.y<16 then

     --move player down by 1
     player.y=player.y+1

    --if the player presses 'left' and
    --they aren't at the far left.
    elseif btn(2) and player.x>0 then

    --move player left by 1
    player.x=player.x-1

    --if the player presses 'right' and
    --they aren't at the far right.
    elseif btn(3) and player.x<29 then

    --move player right by 1
    player.x=player.x+1
    end
    end

    --now we will write a function for drawing
    --the game graphics.
    function draw()

     --first we need to clear the screen of
     --all previous graphics and fill it
     --with light grey
     cls(BLUE_GREY)

    --place a blue 8x8 square at the players
    --current position.
    rect(player.x*8,player.y*8,8,8,LIGHT_BLUE)

    --place a red 8x8 square at the enemys
    --current position
    rect(enemy.x*8,enemy.y*8,8,8,RED)

     --place a yellow 3x5 circle at the coins
     --current positio
     circ(coin.x*8+4,coin.y*8+4,3,YELLOW)

     --last we want to draw the scores of
     --the player and enemy. plus the lives
     --of the player remaining.
     print("P="..player.score,3,3,LIGHT_BLUE)
     print("E="..enemy.score,220,3,RED)
     print("Lives="..player.lives,3,9,LIGHT_BLUE)

    --you'll notice that we're multiplying
    --the coordinates by 8. this is just
    --because we are displaying a 16x29
    --board on a 128x232 display. so if we
    --multiply the coordinates by 8 we get
    --the appropriate pixel coordinates.
    --if you're confused then try changing
    --it from 8 to something smaller.
    end

    --now let's put everything together in
    --the game loop!!!

    --initialize the game first
    init()
    function TIC()

    --this is where we use frame skipping
    --to bring the game speed down to a
    --reasonable level.
    --this works by dividing clock by
    --GAMESPEED and only executing the game
    --loop if the remainder is zero.
    if clock%GAMESPEED==0 then

    --this is the main part of the game loop

    --if a game over hasn't happened.
    if not gameover then

     --move the player
     moveplayer()

     --move the enemy
     moveenemy()

     --check for player/coin collision
     if collision(player,coin) then

     --add 1 to the player score
     player.score=player.score+1

     --spawn another coin
     spawncoin()

    --respawn player at spawn point
    respawn(player)

    --check for enemy/coin collision
    elseif collision(enemy,coin) then

    --add 1 to the enemys score
    enemy.score=enemy.score+1

    --spawn another coin
    spawncoin()

    --respawn enemy at spawn point
    respawn(enemy)

    --check for enemy/player collision
    elseif collision(player,enemy) then

    --respawn player and enemy
    respawn(player)
    respawn(enemy)

    --subtract a life from player
    player.lives=player.lives-1

    --check for game over
    if player.lives==0 then
     gameover=true
    end
    end

    --else if a game over has happened
    elseif gameover then

    --reset the game
    init()

    end

    --now that all the data is updated we
    --will call the draw() function to
    --update the game graphics.
    draw()

    end

    --add 1 to clock before finishing the
    --game loop
    clock=clock+1
    end
```

you'll see that this game is incredibly simple, and not really that fun to play. but the idea is just to understand how the code works for game programming.

everything is about using variables to store game data,
use functions to alter and update the data,
and finally a way to draw that data to the screen for the player to see.

Feel free to use any portion of this code in your own projects. If you're feeling generous, leave a credit for me in the top of your file!

If you've got questions or requests for another tutorial... You can email me at bearknucklesketching@gmail.com