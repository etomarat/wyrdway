In this tutorial we'll build a simple menu with a "PLAY" button and a "SETTINGS" button.
Like this:
![clingy_menu](https://user-images.githubusercontent.com/32113404/31818303-35993672-b55d-11e7-84ef-bd31539aa382.gif)

**You can play CLINGY here: https://tic80.com/play?cart=253**

The basic method for creating menu screens, or minigames, or anything like that...
is to create an if/elseif statement, and a mode variable to keep track of the current state.

``` lua
mode="menu"

function TIC()
 if mode=="menu" then
  -----------------------------------------------
  ----------menu mode script here----------------
  -----------------------------------------------

 elseif mode=="settings" then
  -----------------------------------------------
  ---------settings mode script here-------------
  -----------------------------------------------

 elseif mode=="game" then
  -----------------------------------------------
  ----------game mode script here----------------
  -----------------------------------------------

 elseif mode=="game_over" then
  -----------------------------------------------
  --------game over mode script here-------------
  -----------------------------------------------
```

You can see that depending on the string we assign to "mode", a different block of code will be executed.
The menu has two options, "PLAY" and "SETTINGS". The way a menu should work is the player presses in the direction of the option they want, a cursor highlights the current option, and then push (A) to select the current option.
To make this work we first need a list of coordinates for cursor placement on the screen:
```lua
--cursor placement constants
PLAY={x=12*8-1,y=9*8-1}
SETTINGS={x=16*8-1,y=9*8-1}
```

These are just the pixel coordinates that match with the "buttons" I drew onscreen. When you make your own menu, these will be different based on your layout.  Now let's take a look at the menu logic.

```lua
if mode=="menu" then
-------------------------------------
--------menu screen code-------------
-------------------------------------

 --clear the screen
 cls()

 --i drew the menu on the map starting at position (30,0)
 map(30,0,60,17)

 --now print the name of the game!
 print("CLINGY",13*8,3*8,2)

 --if the player presses left then assign the PLAY cursor
 --placement coordinates to the variable cursor
 if btnp(2) then cursor=PLAY end

 --if the player presses right the do the same for SETTINGS
 if btnp(3) then cursor=SETTINGS end

 --now we draw our cursor. I chose a light-blue square
 --outline that floats around the button. we'll want to
 --draw it at the current cursor placement.
 rectb(cursor.x,cursor.y,18,18,13)

 --if the player presses (A) then assign the appropriate
 --string to mode.
 if btnp(4) then
  if cursor==PLAY then mode="game" end
  if cursor==SETTINGS then mode="settings" end
 end
```

This is pretty easy because we only have two options. If you need three or more options, then it would be easier to assign the cursor placements to a list:
``` lua
options={PLAY,SETTINGS,MINIGAME,TUTORIAL,CREDITS}
```

then assign the current cursor position to a variable, and make sure it doesn't go out of bounds:
```lua
--btn(0) is "UP" and
--there's only five options in this list
if btn(0) and position<5 then
 position=position+1
end

--btn(1) is "DOWN" and
--we don't want to go past 1
if btn(1) and position>1 then
 position=position-1
end
```

and then call the cursor placement by index:
```lua
cursor=options[position]
```

finally, assign mode the correct value depending on the cursor's placement:
``` lua
if btn(4) then
 if cursor==PLAY then mode="game" end
 if cursor==SETTINGS then mode="settings" end
 if cursor==MINIGAME then mode="minigame" end
 if cursor==TUTORIAL then mode="tutorial" end
 if cursor==CREDITS then mode="credits" end
end

```
Now we'll code the settings menu. It'll look like this:
![clingy_settings](https://user-images.githubusercontent.com/32113404/31818312-406594ba-b55d-11e7-8803-2ebfc381b08a.gif)

The basic idea of a settings menu is to change some constants in your code to alter the way the game works.
The only option I have is the game speed.

``` lua
elseif mode=="settings" then
-------------------------------------
--------settings screen code---------
-------------------------------------

--again we start by clearing the screen
cls()

--I drew the settings screen on the map
--starting at position (60,0)
map(60,0,90,17)

--now we'll draw the settings elements
print("SETTINGS",12*8,3*8,6)
print("GAME SPEED: ",10*8,9*8+2,6)
rect(18*8,9*8,15,8,15)
print(temp,18*8+2,9*8+2,6)
print("Press A to Accept",9*8,13*8,6)

--The maximum speed is 10...which is
--1 frame skipped per loop. so let's
--not let them go over 10
if btnp(0,6,3) and temp<10 then
 temp=temp+1
end

--the minimum speed is 1, which is
--actually 10 frames skipped per loop
--any slower and the game drags too slow
if btnp(1,6,3) and temp>1 then
 temp=temp-1
end

--press (A) to accept
if btnp(4) then
 mode="menu"

 --the frame skipping is the remainder
 --of 11 minus the position...
 --so position 10 is 11-10=1 frame skip
 --and position 5 is 11-5 =6 frame akips
 --and position 1 is 11-1=10 frame skips
 gamespeed=11-temp
end
```

Next comes the game loop. It'll look like this:
![clingy](https://user-images.githubusercontent.com/32113404/31818327-4a1a3e20-b55d-11e7-8043-8d19fb32f4e1.gif)

Here's the code:
``` lua
elseif mode=="game" then
--------------------------------------
----------game screen code------------
--------------------------------------

 --first comes player movement
 if btnp(0,6,10) and mget(p.x,p.y-1)~= 17 then p.y=p.y-1 end
 if btnp(1,6,10) and mget(p.x,p.y+1)~= 17 then p.y=p.y+1 end
 if btnp(2,6,10) and mget(p.x-1,p.y)~= 17 then p.x=p.x-1 end
 if btnp(3,6,10) and mget(p.x+1,p.y)~= 17 then p.x=p.x+1 end

 --The frame skipping is only applied to
 --slow down the enemies movment.
 if t%gamespeed==0 then
  if e.x>p.x and mget(e.x-1,e.y)~=17 then
   e.x=e.x-1
  elseif e.x<p.x and mget(e.x+1,e.y)~=17 then
   e.x=e.x+1
  elseif e.y>p.y and mget(e.x,e.y-1)~=17 then
   e.y=e.y-1
  elseif e.y<p.y and mget(e.x,e.y+1)~=17 then
   e.y=e.y+1
  end
 end

 --now we can draw the game graphics
 cls()
 map(0,0,30,17)
 spr(33,p.x*8,p.y*8)
 spr(34,e.x*8,e.y*8)

--last we have game over conditions

--if the enemy reaches the player
if e.x==p.x and e.y==p.y then
 mode="game_over"
end

--if the enemy steps in a hole
if mget(e.x,e.y)==18 then
 rect(13*8,7*8,5*8,8,1)
 print("WINNER",13*8+3,7*8+1,6)
 mode="game_over"
end

--if the player steps in a hole
if mget(p.x,p.y)==18 then
 mode="game_over"
end
```

I'm not worrying about going into too much detail on the game loop, as it's just for demonstration anyway.
Just place your own game code in that block and your good to go.

Last we have the game over code. This just make the player stop moving and displays some graphics.

``` lua
 elseif mode=="game_over" then
  --------------------------------------
  -----------game over code-------------
  --------------------------------------

  --draw rectangles behind text
  rect(12*8,3*8,7*8,8,1)
  print("GAME OVER",12*8+2,3*8+1,6)

  rect(9*8,14*8,12*8,8,1)
  print("Press A for Menu",9*8+4,14*8+1,6)

  rect(9*8,15*8,12*8,8,1)
  print("Press B to Retry",9*8+4,15*8+1,8)

  --if the player decides to retry then we
  --want to assign the speed they chose for
  --the last game to the next game.
  retry_speed=gamespeed

  --pressing (A) goes back to menu
  if btnp(4) then init() end

  --pressing (B) restarts the game
  if btnp(5) then
   init()
   mode="game"
   gamespeed=retry_speed
  end
 end
```

And Here's the complete code:

```lua
-- title:  Clingy
-- author: Bear Thorne
-- desc:   A Demo for menu/setting screens
-- script: lua

--notice the defaults assigned in the init()
--function...
function init()
 t=0
 gamespeed=10
 mode="menu"
 p={x=8 ,y=1 }
 e={x=21,y=15}
 temp=1
 cursor=PLAY
end

--cursor placement constants
PLAY={x=12*8-1,y=9*8-1}
SETTINGS={x=16*8-1,y=9*8-1}

init()
function TIC()

 if mode=="menu" then
  -------------------------------------
  --------menu screen code-------------
  -------------------------------------

  cls()
  map(30,0,60,17)
  print("CLINGY",13*8,3*8,2)

  --press left for game
  if btnp(2) then cursor=PLAY end
  --press right for settings
  if btnp(3) then cursor=SETTINGS end

  --draw the cursor
  rectb(cursor.x,cursor.y,18,18,13)

  --press (A) to select current option
  if btnp(4) then
  if cursor==PLAY then mode="game" end
  if cursor==SETTINGS then mode="settings" end
 end
 -------------------------------------
 --------settings screen code---------
 -------------------------------------
 elseif mode=="settings" then
  cls()
  map(60,0,90,17)
  print("SETTINGS",12*8,3*8,6)
  print("GAME SPEED: ",10*8,9*8+2,6)
  rect(18*8,9*8,15,8,15)
  print(temp,18*8+2,9*8+2,6)
  print("Press A to Accept",9*8,13*8,6)

  if btnp(0,6,3) and temp<10 then
   temp=temp+1
  end

  if btnp(1,6,3) and temp>1 then
   temp=temp-1
  end

  --press (A) to accept
  if btnp(4) then
   mode="menu"
   gamespeed=11-temp
  end

 elseif mode=="game" then
  --------------------------------------
  ----------game screen code------------
  --------------------------------------

  if btnp(0,6,10) and mget(p.x,p.y-1)~= 17 then p.y=p.y-1 end
  if btnp(1,6,10) and mget(p.x,p.y+1)~= 17 then p.y=p.y+1 end
  if btnp(2,6,10) and mget(p.x-1,p.y)~= 17 then p.x=p.x-1 end
  if btnp(3,6,10) and mget(p.x+1,p.y)~= 17 then p.x=p.x+1 end

  if t%gamespeed==0 then
   if e.x>p.x and mget(e.x-1,e.y)~=17 then
    e.x=e.x-1
   elseif e.x<p.x and mget(e.x+1,e.y)~=17 then
    e.x=e.x+1
   elseif e.y>p.y and mget(e.x,e.y-1)~=17 then
    e.y=e.y-1
   elseif e.y<p.y and mget(e.x,e.y+1)~=17 then
    e.y=e.y+1
   end
  end

 cls()
 map(0,0,30,17)
 spr(33,p.x*8,p.y*8)
 spr(34,e.x*8,e.y*8)

 if e.x==p.x and e.y==p.y then
  mode="game_over"
 end

 if mget(e.x,e.y)==18 then
  rect(13*8,7*8,5*8,8,1)
  print("WINNER",13*8+3,7*8+1,6)
  mode="game_over"
 end

 if mget(p.x,p.y)==18 then
  mode="game_over"
 end

 elseif mode=="game_over" then
  --------------------------------------
  -----------game over code-------------
  --------------------------------------
  rect(12*8,3*8,7*8,8,1)
  print("GAME OVER",12*8+2,3*8+1,6)

  rect(9*8,14*8,12*8,8,1)
  print("Press A for Menu",9*8+4,14*8+1,6)

  rect(9*8,15*8,12*8,8,1)
  print("Press B to Retry",9*8+4,15*8+1,8)

  retry_speed=gamespeed

  if btnp(4) then init() end
  if btnp(5) then
   init()
   mode="game"
   gamespeed=retry_speed
  end
 end
 t=t+1
end
```

as always feel free to use any portion of the code in your own projects. Just give me a credit at the top of your file and we'll be good :)

if you have questions, or requests for future tutorials then email me at bearknucklesketching@gmail.com