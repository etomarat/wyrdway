So, here's the first part of a tutorial serie that should hopefully cover all about making the racing game Warm Wheels.
So to make a racing game, however arcade, you need some kind of physics engine (a simple one obviously), and to make a physics engine, you'll need some math, in particular vector math. So i'll introduce some utility functions over which it will be easy to build our wonky physics. I'd like to say "don't worry there will be no formulas and little math on this article" but no, it's all about math and formulas. But at least we won't be talking about matrices.

If you have an hard time understanding some of the stuff, please go to the demo and experiment a bit, try poking around in the code of the [Fun With Vectors](https://tic80.com/play?cart=558) cart, and get a feel of how stuff work.

First, a vector is, informally, a couple of X and Y coordinates forming a line from the origin, and thus denoting a position on the screen:

![length_2d_vector](https://user-images.githubusercontent.com/2278103/41181165-166b5e04-6b71-11e8-9cac-9631aa3f9d66.gif)

We are all used to basic vectors, as using coordinates to put stuff on screen is literally the first thing you do on TIC-80 (or on any other game development system). Now if we want to represent a car on a racing game, we'll obviously need to have a "position vector" that is, where the car is on the play area, but we also need to have a "direction" to which the car is heading. And now you could ask: how do i implement a "direction"? will it be a single "angle" value, or perhaps another vector?

![car_vectors](https://user-images.githubusercontent.com/2278103/41181181-22a4171a-6b71-11e8-8279-29505c71d5f3.jpg)

Well, that's a good question and strictly speaking, the two things are equivalent and interchangeable, but sometimes it's easier to reason with angles, other times with vectors. For example, if you want to steer you car left and right, you'll prefer to have an angle, so you can just decrement or increment it by a fixed value. So we most surely need functions to translate from angles to vectors and vice versa.

So let's google "vector rotation", we end up on wikipedia or other pages, and skipping all the matrix stuff we spot this formula:

![formula](https://user-images.githubusercontent.com/2278103/41181185-2c6a2172-6b71-11e8-980e-c9387a9ec082.png)

Let's implement it in lua:

``` lua

function rotate(x,y,a)
 return
  x*math.cos(a)-y*math.sin(a),
  x*math.sin(a)+y*math.cos(a)
end

```

Since it's just two values, we avoid using tables and use the "multiple return values" feature of Lua instead, so we can call this function like so:

``` lua

local x1,y1 = rotate(x,y,myangle)

```

Note that all math functions uses radians instead of degrees, so we'll be using them too. If you don't know what a radian is, it's just a different scale to indicate angles: where degrees go from 0 to 360, radians go from 0 to 2Pi, which is about 6.283. There are pro and cons to choose both representations, but we'll stick to radians to avoid converting back and forth.

So now that we have our rotate function, let's try it. We define a "character" with a position vector (x,y) and an angle (a), and we use the function to draw a point in the direction the character is facing, and we'll rotate it with left and right buttons:

``` lua

-- our character position and orientation
x=120
y=68
a=0

function rotate(x,y,a)
 return
  x*math.cos(a)-y*math.sin(a),
  x*math.sin(a)+y*math.cos(a)
end

function TIC()

 if btn(2) then a=a-0.05 end
 if btn(3) then a=a+0.05 end

 cls(0)

 -- draw our "character"
 pix(x,y,15)

 -- rotate an "up" vector by our angle
 local x1,y1 = rotate(0,-20,a)

 -- draw another point at the rotating vector
 local dotx = x + x1
 local doty = y + y1
 pix(dotx, doty, 14)

 print("angle: "..a,0,0, 15, true)
end

```

Let's see what we did: first we increment or decrement our character angle with buttons, by very small amounts becouse radians are small and we don't want it to rotate too fast. Then we do the magic: we take a vector (0,-20) and we rotate it by "a", to move to the correct position. Where do the (0,-20) comes from? Well it's just customary that a "0" angle point towards up, so (0,-20) is just up, that is, a vector of length 20 at 0 rotation.
So we take this vector and we rotate it by "a" and this orients it as we like. We then plot the point of this vector by putting a pixel there, relative to the (x,y) coordinates of the character. We also print the angle to get a feedback.

Here's the result:

![rotate_point](https://user-images.githubusercontent.com/2278103/41181207-43ae4f48-6b71-11e8-8afd-bf60958c8161.gif)

Looks great! Note that we can go lower than 0 and higher than 2pi, that's becouse trigonometric functions don't really care how many turns you do, they'll wrap around correctly. Later we'll need to stay in 0..2pi so we'll enforce that, but for now no worries.

Now how do we do the inverse, that is, given a vector how do we find its angle? We may need this, for example, if we want our character to point to a target point (another character maybe, to follow him). Well if you remember some trigonometry from school, you'll know how to reverse our "rotate" function, and you'll end up with some arctangent stuff and you'll give up. Luckly, there's some ready made function right in Lua (and other languages), that's called atan2(), short for arctangent2. It's the smarter cousing of "atan()", and really does all the work: you give it your (x,y) vector and it spits out the angle. Differently from the simple "atan()", atan2() also takes into consideration the sign of the coordinates to get the right quadrant. So our function is this:

``` lua

function angle(x,y)
 return math.atan2(x,y) -- don't use this yet...
end

```

just a shortcut really! So we'll now perform this test: given the previous example, we'll convert back from the vector to angle and see if the second angle is exacly like the first one (so something like angle -> vector -> angle).

Here's the code:

``` lua
-- our character position and orientation
x=120
y=68
a=0

function rotate(x,y,a)
 return
  x*math.cos(a)-y*math.sin(a),
  x*math.sin(a)+y*math.cos(a)
end

function angle(x,y)
 return math.atan2(x,y) -- don't use this yet...
end

function TIC()

 if btn(2) then a=a-0.05 end
 if btn(3) then a=a+0.05 end

 cls(0)

 -- draw our "character"
 pix(x,y,15)

 -- rotate an "up" vector by our angle
 local x1,y1 = rotate(0,-20,a)

 -- draw another point at the rotating vector
 local dotx = x + x1
 local doty = y + y1
 pix(dotx, doty, 14)

 -- calculate back our angle to check if it's consistent with atan2
 local verifyAngle = angle(x1,y1)
 print("angle: "..a.."\natan2: "..verifyAngle,0,0, 15, true)

end

```

Let's try it and:

![wrong_atan2](https://user-images.githubusercontent.com/2278103/41181229-5486e9ce-6b71-11e8-99b7-7e5e57f2b543.gif)

And it doesn't work! It does for some directions and goes wrong for others. The reason is that applying clean math formulas on gamedev always means receiving kicks on the teeth and wasting weeks to adjust and readjust our increasingly dirty formulas. In this case, the reason is simple: the math world usually agrees that, on a cartesian plane, the x coordinates grow on the right and the up coordinate grows on up, placing (0,0) at the bottom-left corner. Instead, the computer world decided that y grows down, so placed the (0,0) origin at the top-left, creating unnecessary confusion for generations of developers.
In our case tho, the solution is simple: we keep our rotate() unchanged and adjust our angle(). We could simply use "-y" instead of "y", but instead we'll make it the following way becouse it has the added benefit of moving the range of the result to 0..pi2, so we don't have to:


``` lua
function angle(x,y)
 return math.pi - math.atan2(x,y) -- correct!
end
```

Since we are there, let's introduce another function to keep angles in the same range when we add/subract from them:

``` lua
-- adds two angles ensuring the
-- result is in the 0..2pi range
function angleAdd(a, d)
 a=a+d
 -- ensure angle is in 0..2pi range
 if a<0 then
   a=a+pi2
 elseif a>=pi2 then
   a=a-pi2
 end
 return a
end

...
...

 if btn(2) then a=angleAdd(a,-0.05) end
 if btn(3) then a=angleAdd(a,0.05) end
```

As you see, now instead of doing a=a-0.05, we call angleAdd() and our value is safe.
Also, since is typical to construct vectors from a length and a direction, like we did with "rotate(0,-20,a)", we introduce a more straightforward helper function:

``` lua
-- gets a vector of given length
-- oriented on the given angle
function vector(length, angle)
 return rotate(0, -length, angle)
end
```

Obviously this could be optimized becouse rotate does 4 trigonometric functions but with x=0 you only need two, but this is left as an exsercise for the reader.

Since angle() is tipically used to find the angles between two points, we introduce its sister angle2(), that takes two position vector and give the angle (note: this is not the angle between two vectors, it's the angle that points from the first point to the other). As you can see the implementation is straightforward as it's just a matter of moving the origin on the "from" point.

``` lua
-- give the angle from a certain point
-- to another point
function angle2(fromx,fromy, tox, toy)
 return angle(tox-fromx, toy-fromy)
end
```

Another things you probably want to do is interpolating angles. Like, you have a monster that points up on the top left corner, and you're on the bottom right. Now you know how to calculate the desired angle, but you don't want to assign that angle directly to the monster, as it'll turn instantly, while you probably want to rotate at a given pace. Given the desired angle and the current angle, you might be tempted to think that you could simply interpolate them, slowly increasing your current angle if it's smaller than the desired, or decreasing it otherwise.
Unfortunately, it's not that easy. Suppose you're heading at 6.1 rads, so right at the end of the circle, and your target is at an angle of 0.1, so right at the beginning. Now, if you start decreasing 6.1 to reach 0.1, you're doing almost a full circle, while if you actually INCREASE it, getting away from 0.1, you actually wrap around 2pi and reach your target much quicker. So we need some way to determine which direction is better to go from an angle A to reach another angle B. Introducing, angleDir():

``` lua
-- calculates if an angle is closer
-- to a given angle in the positive
-- direction rather than the negative
-- returns -1, 0 or +1
function angleDir(from, to)
 local diff = to-from
 if math.abs(diff) < 0.00001 then return 0 end -- avoid rounding errors that will prevent settling
 if diff > math.pi then
   return -1
 elseif diff < -math.pi then
   return 1
 else
   return diff>0 and 1 or -1
 end
end
```

This function returns -1 if you should decrease the angle "from" to reach the angle "to", 1 if you should increase (if they're equal, returns 0). So you can simply multiply your absolute rotation (say 0.01) to that 1/-1/0 value and add to your angle. This is how you use it:

``` lua

 -- find the direction of the difference between follower and player angles
 local d = angleDir(follower, a)
 -- add a small amount in that direction
 follower = angleAdd(follower, 0.01 * d)

 -- print the dot at 10 pixel of distance
 local xf,yf = vector(10,follower)
 pix(x + xf, y + yf, 11)

```

Here's the result. The green dot is now following the yellow dot, but slowly. Notice that when i go right behind it and cross the 90° of difference, it switches direction and tries to catch up on the opposite side, just as we desired. Note: this function is the reason why we need to stay in the 0..2pi range, otherwise it wouldn't work (or better, it would need to be a little more complicated).

![follower](https://user-images.githubusercontent.com/2278103/41181256-64c0e7ea-6b71-11e8-9eb0-b426fd09979b.gif)

The last thing we'll see is a very basic requirement, that is: moving an entity by an arbitrary length in a given direction. So if you have a car that's heading in a particular direction, you most probably want to move it in that direction by a small amount each frame. This is easily done using the functions we just developed:

``` lua
-- our character position and orientation
x=120
y=68
a=0

....

-- this is the speed, how much we want to move this frame
local speed=0.1
-- the displacement is simply speed oriented at our angle
local displacement = vector(speed, a)
-- now just add displacement to our position
x = x + displacement.x
y = y + displacement.y
```

Ok, that's it, we developed a complete toolbox of vector math that let us manipulate entities based on their orientation. In the next article we'll see how to apply this stuff to create a car driving model, perhaps not nearly physically correct, but good enought for our arcade needs.

You can find a cart, [Fun With Vectors](https://tic80.com/play?cart=558), on the store with all the demos we discussed here. Please write any feedback to this article there.

![vectors](https://user-images.githubusercontent.com/2278103/41181568-7cc2b08e-6b72-11e8-92cc-3184fb834871.gif)

Continue with the second part of the tutorial here: [[Driving-Model]]