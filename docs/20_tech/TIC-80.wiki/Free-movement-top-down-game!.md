# Free movement top down game!
In this tutorial I will teach you how to make a free movement top down game with TIC-80.
I assume you know how to use TIC-80 and some JavaScript syntax.

### You can play my demo here: https://tic80.com/play?cart=1792

Let's start with one big question:
## What the heck is a top down game???
### A top down game is a game where the camera stays on top of the player.
Many top down games actually place there camera at a 60 degree angle (so you can see the top and front side of objects, rather than just top)
Wherever you decide you want your camera to be, the engine is essentially the same.
Here's a visual example. This is a dirt block from 2 different angles:

![Dirt block](https://i.ibb.co/7RnB1V4/dirt-Block.gif)

The first dirt block is seen from the top (all you can see is grass)
On the second block you can see grass and some dirt.

Here's another big question:
## What is free movement???
### Free movement means the player can move freely, and not just on a grid.
Many turn based games have the player move only on a grid, like this:

![Grid based movement](https://i.ibb.co/m9K5Vv9/grid-Based.gif)

In this tutorial, we'll focus on free movement, like this:

![Free movement](https://i.ibb.co/Y3MVwTC/free-Movement.gif)

**but...**
If you want to give grid based movement a go, the principles are very similar.
# Now let's write the engine!
The engine is fairly straightforward. First, we need a function to check for collisions, which can be tricky, because map coordinates are different than screen coordinates. Here's what I mean:
This shows 1, 1 on the map.

![map Coordinates](https://i.ibb.co/wC65Ywy/map-Coordinates.gif)

This shows 1, 1 on the screen (the red pixel in the top left corner is 1, 1 )

![screen Coordinates](https://i.ibb.co/YdWv80P/real-Screen-Coordinates.gif)

As you can see, they are very different. To compensate for this, we use a special function:

```
function solid(x,y) {
	return fget(mget(Math.floor(x/8),Math.floor(y/8)),0)
}
```

This function takes screen coordinates and adjusts them to fit the map.
Let's break it down a bit:
First, `fget()`. It is the function for checking sprite flags. At the end of the code, you can see `,0`. This means we will check for flag 0, so if flag 0 is activated on a sprite, and we place it on the map, it will be treated as solid.
Next, `mget()`. This returns the sprite number of a map tile. we divide by 8 to compensate for screen to map coordinates, and use `Math.floor()` to make sure we have a whole number
Now that we know how to check for collisions, we need an object to store some player variables:
```
var p={
	x:8,
	y:8
}
```
This is fairly easy to understand, but one thing to note is that these are **SCREEN COORDINATES** rather than **MAP COORDINATES**. If you forget this, your player won't show up in your level where you want him to.
Now that we've got everything ready, it's time to write the code in `TIC()`
```
function TIC() {
	if(btn(0)&&!solid(p.x,p.y-1)&&!solid(p.x+7,p.y-1))p.y--
	if(btn(1)&&!solid(p.x,p.y+8)&&!solid(p.x+7,p.y+8))p.y++
	if(btn(2)&&!solid(p.x-1,p.y)&&!solid(p.x-1,p.y+7))p.x--
	if(btn(3)&&!solid(p.x+8,p.y)&&!solid(p.x+8,p.y+7))p.x++
	cls()
	map()
	spr(2,p.x,p.y,5)
}
```
The only complicated part of this code is collisions, but we'll talk about that later. First, let's get a working version of your game running.
We've written all the code, but to play your game, there's a bit more you need to do.
_1._ **Add some sprites**
Make a solid map tile. It can be anywhere, but be sure to **ACTIVATE FLAG 0**. (to do this, you have to turn on advanced mode)

![Solid Block](https://i.ibb.co/T4SSDz5/solid-Block.png)

In the photo above, the advanced mode switch is circled in red and flags are circled in green.

Next, let's **Make a background sprite**
I drew some grass. **DON'T ACTIVATE ANY FLAGS**

![background sprite](https://i.ibb.co/hsM201w/background-Sprite.png)

Finally, let's **Make a player**
As you can see, I'm not the greatest pixel artist. **MAKE IT SPRITE #2**

![Player sprite](https://i.ibb.co/Gf6Fsh0/player-Sprite.png)

(I circled the sprite number)
_2._ **Make a level**
Draw a map using the map editor. Here's what I drew:

![my level](https://i.ibb.co/4Y7fJRg/myLevel.png)

## Now run your game!
If anything goes wrong, here's the final code:
```
// title:  Top down free movement demo
// author: 00Her0
// desc:   Top down free movement demo
// script: js
var p={
	x:8,
	y:8
}
function solid(x,y) {
	return fget(mget(Math.floor(x/8),Math.floor(y/8)),0)
}
function TIC() {
	if(btn(0)&&!solid(p.x,p.y-1)&&!solid(p.x+7,p.y-1))p.y--
	if(btn(1)&&!solid(p.x,p.y+8)&&!solid(p.x+7,p.y+8))p.y++
	if(btn(2)&&!solid(p.x-1,p.y)&&!solid(p.x-1,p.y+7))p.x--
	if(btn(3)&&!solid(p.x+8,p.y)&&!solid(p.x+8,p.y+7))p.x++
	cls()
	map()
	spr(2,p.x,p.y,5)
}
```
Now let's talk about how collision detection works here. Basically, we use  8 collision points located on all sides of the player. The points are illustrated below:

![Collision points](https://i.ibb.co/8BKm1yw/collision-Points.png)

Each colored pixel is a collision point. The 2 collision points with arrows pointing toward them are used for collisions when moving upward. 8 points might seem like a lot, but they are the minimum amount. For example, this is a GIF of my player without one of the top collision points.

![Not enough collision](https://i.ibb.co/74ftbmv/not-Enough-Collision.gif)

(The player goes up partially through a few blocks)
If you want to see the collision points in action, add this code in `TIC()`
```
        pix(p.x,p.y-1,1)
	pix(p.x+7,p.y-1,2)

	pix(p.x,p.y+8,3)
	pix(p.x+7,p.y+8,4)

	pix(p.x-1,p.y,5)
	pix(p.x-1,p.y+7,6)

	pix(p.x+8,p.y,7)
	pix(p.x+8,p.y+7,8)
```
Well, it looks like this guide is over.
For any further questions, leave a comment here: https://tic80.com/play?cart=1792
Feel free to use any portion of this code.