Understanding the game logic is only half the story...the other half (and arguably the more important one) is the graphics.
After all, if the player can't see what's going on...what good is the game?!

So let's take a look at using the map and sprite editors, as well as the map() and spr() functions...

## SPRITE EDITOR
![sprites](https://user-images.githubusercontent.com/32113404/31863785-6170da18-b718-11e7-9ea1-69fa9cd80f7f.gif)

The Sprite editor is extremely simple. Just click on a slot and start drawing your sprite.
Be sure to try out all the different tools below the drawing area.
- **DRAW**
- **COLOR PICK**
- **SELECT**
- **FLOOD FILL**
- **MIRROR VERTICAL**
- **MIRROR HORIZONTAL**
- **FLIP**
- **DELETE ALL**

Take note of the **Sprite ID#** at the top:

![sprite_id](https://user-images.githubusercontent.com/32113404/31864407-74a33ea0-b722-11e7-9808-f2dfdc6409c8.jpg)

This is the number that refers to that exact slot you drew your sprite in.
We'll be using it to tell the spr() function what sprite to use where.

## MAP EDITOR
![map](https://user-images.githubusercontent.com/32113404/31863788-74bd9408-b718-11e7-9337-e896c253a975.gif)

The map editor is nearly as simple as the sprite editor...just use the **Sprite Pull-Down Menu** to pick a sprite...
![sprite_palette](https://user-images.githubusercontent.com/32113404/31864409-817320a0-b722-11e7-9678-9bf978044052.jpg)

and start drawing your map...
![map_editing](https://user-images.githubusercontent.com/32113404/31864412-9bd2a5d8-b722-11e7-9967-7f474e20a247.gif)

Here's the sprite sheet for this tutorial:
[watchtower_sprites](https://user-images.githubusercontent.com/32113404/31864649-8f9da002-b726-11e7-9c8f-c5a00b0c0e90.gif)

just download it, then open TIC-80 and type:

    >import sprites

Navigate to the watchtower_sprites and select it.
TIC-80 will load it into the sprite editor of the cart you have up.
Feel free to use it in any projects you want...just leave me a credit at the top of your file! :)
## MAP() FUNCTION
So at this point you should have a sprite sheet drawn, and a map built.

**NOTE**
if your map is larger than the screen area, you'll need to use a "camera" to follow your character.
Have a look at either of these tutorials to learn how to set that up:
[Camera Tutorial](https://github.com/nesbox/TIC-80/wiki/Camera-tutorial) by Trelemar
[Grid-Based Camera Movement](https://github.com/nesbox/TIC-80/wiki/Grid-based-Camera-Movement) By me :)

In order to draw your map onscreen we'll need to call the map() function in your script:
``` lua
map(start_x,start_y,width,height)
```
There are more arguments available in the map function. For an overview of using them, look [here](https://github.com/nesbox/TIC-80/wiki/map)

The start_x and Start_y is looking for the map cell coordinate to start drawing from.
To find that, go to the map editor and select the top left cell in your map:
![map_start](https://user-images.githubusercontent.com/32113404/31864820-fb6b52c2-b729-11e7-8fac-55c2f5f084de.jpg)
In this case I drew my map starting at the first cell (0,0) so that's:
```lua
map(0,0,width,height)
```
Now for the width and height...
TIC-80's screen can display a maximum of 30x17 map cells onscreen.
Since the map is intended to take up the whole screen we'll use 30 and 17:
```lua
map(0,0,30,17)
```
now the largest visible map area is being draw to the screen:
![screen](https://user-images.githubusercontent.com/32113404/31864841-6e0533fc-b72a-11e7-87a4-a1f17fbe8216.gif)

Next we need to use sprites for objects and characters:

## SPR() FUNCTION
The spr() function is how we can draw sprites to the screen.
It's called like this:
``` lua
spr(sprite_id,x,y,alpha)
```
The sprite id is the number I pointed out to you in the sprite editor.
Now the easiest way to keep all the numbers straight is to store them in variables with descriptive names:
``` lua
SPACE=0
FLOOR=1
WALL =17
DUDE =33
```
You'll notice I'm only putting the first floor sprite id into the variable **FLOOR**...
Same with the **WALL** variable...
This is for collision detection, which I already covered [here](https://github.com/nesbox/TIC-80/wiki/Simple-Collision-Detection) so don't worry about it.

So now we can call spr() like this:
``` lua
spr(DUDE,x,y,alpha)
```
This will draw the **DUDE** sprite at the x,y coordinates specified.
For those we can simply reference a player object:
```lua
p={x=8,y=10}

spr(DUDE,p.x,p.y)
```
Now for the **alpha** argument...
It specifies the color index to use as transparency.
for example:
![img_20171022_1439073](https://user-images.githubusercontent.com/32113404/31865612-2c59e0c6-b737-11e7-9255-6d57f8ec02ff.jpg)
Here the color I'm using for transparency is **Light Green**...
And you can find a colors index by counting the slots from left to right (starting with 0) until you get to your color. So:
Black is 0...
Purple is 1...
Blue is 2...
etc.
The index number for Light Green is 11. That means if we want TIC-80 to treat Light Green as transparent we do:
``` lua
spr(DUDE,p.x,p.y,11)
```
Now the background will show through wherever Light Green was used.
In my games I prefer to use Black, and if you need to use black in a sprite you can always use a different alpha index for that particluar sprite.

Now we know how to display map areas, and how to draw sprites to the screen. But if you were to run a game with these right now you'd get something like this:
![graphic_glitch](https://user-images.githubusercontent.com/32113404/31865747-7495326c-b739-11e7-85dd-3052567894c8.gif)

What's happening whenever you see this kind of thing, is the screen calls the sprite function repeatedly during   the game, and everytime it's called, it draws the sprite over the screen again, leaving a trail of everywhere it's ever been. The way to fix this is with...

## THE CLS() FUNCTION
This function clears the screen of any previous graphics. If you don't call this at least once, the game will be drawn over the TIC-80 console!
(could have potential I guess)

Calling it is incredibly easy:
``` lua
cls(color_index)
```
The color_index asks for a color to fill the screen with, as this is in fact how it "clears" the screen.
If no color is specified, it will use black (0) as a default.

So before we draw to the screen, we should clear it like so:
``` lua
cls()
map(0,0,30)
spr(DUDE,p.x,p.y,0)
```
Don't bother setting cls() to a color, because as soon as we call map() the color won't be seen anyway.

**NOTE**
If you are using the map() function, it can work like a type of clear function itself.
Instead of filling the screen with a specific color, it fills it with a map section,

## ORDER OF DRAWING
If you are making a game, and find that your sprites aren't showing up, or the text you're printing isn't visible...then you may be ignoring the "ORDER OF DRAWING" rule.

You want to place things onscreen in the order they should overlap.
This means that if you write this:
``` lua
spr(DUDE,10,10,0)
map(0,0,30,17)
```
you'll never see your dude because he's being drawn to screen, and then the map is being drawn OVER him!
you need to put it like this:
``` lua
map(0,0,30,17)
spr(DUDE,10,10,0)
```
Now the map is drawn, and then DUDE is placed on top of it.
This also applies to HUD elements.
So the ORDER OF DRAWING will be something like:
``` lua
map
sprites
HUD
text
```
This way nothing is covered by something else.
Anytime your sprites aren't displaying, check this rule.

And that about wraps up this tutorial on drawing screen graphics!

If you have questions, or requests for future tutorials...you can email me at bearknucklesketching@gmail.com