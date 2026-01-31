While the gamepad is the go to thing for games...some games like match-3 or card games, can become a hassle with a controller. Enter Touch/Mouse logic!!!

Getting mouse events in TIC-80 is ridiculously easy!
It's all handled with the the mouse() function.

**NOTE**
To enable mouse/touch functionality in TIC-80, alter the cart's metadata to look like this:
``` lua
-- title:  Game Title
-- author: Developer
-- desc:   Short Game Description
-- script: lua
-- input:  mouse
```
**this will disable the gamepad completely.**

If you read the TIC-80 api then you'll see [mouse](https://github.com/nesbox/TIC-80/wiki/mouse) returns three values:
``` lua
{mouse_x_coordinate, mouse_y_coordinate, mouse_pressed_state}
```
in that order.

The **mouse_pressed_state** returns true if the mouse button is pressed, and false if the mouse button isn't pressed.
The way to catch all these values is to do a multiple variable declaration:
``` lua
var1, var2, var3= val1, val2, val3
```
This is the same as typing:
``` lua
var1=val1
var2=val2
var3=val3
```
In this way we'll catch all three values:
``` lua
mx,my,md=mouse()
```
this assigns the **mouse_x_coordinate** to **mx**, the **mouse_y_coordinate** to **my** and the **mouse_pressed_state** to **md**.
A common thing to do with this is to assign **mx** and **my** to variables when the mouse is clicked, or the screen is touched:
``` lua
mx,my,md=mouse()

if md then
 x=mx
 y=my
end
```
From here you would do what you needed to with the (x,y) returned from the mouse click.
Although you could use the current mx and my directly:
``` lua
if md then
 pix(mx,my,15)
end
```
This code is a rudimentary paint program. It will place a white pixel anywhere you touch.
![rudi_paint](https://user-images.githubusercontent.com/32113404/32138875-7ce974ac-bc00-11e7-814f-955f40d33c27.gif)

Another handy thing to do is to be able to read a map cell at the point clicked.
To do this we need to take the pixel value and floor divide by 8 to get the map cell coordinate:
**example**
you click at (102,86)
102/8=12.75
 86/8=10.75

floor division ignores the decimal so:
102//8=12
 85//8=10

In this way we know the player clicked the map cell at (12,10)
``` lua
mx,my,md=mouse()

if md then
 x=mx//8
 y=my//8
 mset(x,y,1)
end
map(0,0,30,17)
```
This code will assign the map cell that's been clicked to the sprite in slot [1].
![mapsetting](https://user-images.githubusercontent.com/32113404/32139185-c3c898ce-bc07-11e7-846a-cda19167dfd9.gif)

But what about swiping, precious?! What about swiping?!
Good question...
The concept of registering a swipe is:
1. log the first mouse coordinate
2. after a given amount of time log the second mouse coordinate
3. check the difference between the two to determine swipe direction

The first thing to do is make a delay between logging the first x and the second x.
While this could be done by a type of delay function...
an easier method is to just check the second coordinate, _before_ logging the first.
This checks the mouse coordinates from the last cycle against the mouse coordinates of the current.
That way we use the TIC() function's built in delay to check the mouse coordinate every 60th of a second.

While that may seem complicated...let's just look at an example in TIC-80:
```lua
--vars to log swipe and direction of a swipe
direction=nil
swipe=false

function TIC()

 ------basic drawing functions----------
 cls()
 print("SWIPE IN A DIRECTION",8*8,2*8,6)
 print(direction,13*8,8*8,13)

 -------swipe evaluation code----------

 mx,my,md=mouse()


 -------second coordinate checking----------
 --if a swipe happened then evaluate the direction
 if swipe then
  if mx>startx+10 then
   direction="right"
  elseif mx<startx-10 then
   direction="left"
  elseif my>starty+10 then
   direction="down"
  elseif my<starty-10 then
   direction="up"
  end
 end

 -------first coordinate checking---------
 --if a touch happened then log the coors
 --and allow swipe checking
 if md then
  startx=mx
  starty=my
  swipe=true
 else
  swipe=false
 end
end
```
![g_20171028_1040334](https://user-images.githubusercontent.com/32113404/32135949-ae7c9db6-bbcc-11e7-9e45-3568aca14273.gif)
Notice that by assigning **swipe** true or false we can avoid checking the second value against an old value.
Also notice that we checked the new coordinate against the old coordinate+-10.
This means we'll check if the mouse has moved more than 10 from the last coordinate.
That way the player has to swipe fast enough and far enough to register.
It also stops the swipe from being too sensitive to diagonal swipes.
Just try changing it to 0 or 50 to see how it changes the behaviour of the swipe detection!

That covers the basics of handling mouse events!
feel free to use any portion of this code in your own projects! Just think about giving me a credit at the top of your file :)

if you have questions, or requests for future tutorials...email me at bearknucklesketching@gmail.com