Here's the second tutorial on how to make a racing game! This time, less math and more fun (and more physics too). If you missed part one, you can find it here [[Fun-With-Vectors]]. Also check the companion demo/tool [here](https://tic80.com/play?cart=569)!

In this article we'll use our vector skills to create a driving model, that is, a mathematical model of how our cars will react to acceleration, steering, etc. It will be a VERY simple model, suitable to an arcade racing game with no velleity of realism whatsoever.

So, as you probably already guessed, we'll use an angle and a position to define our car, like in the previous tutorial, and we'll start with the exact same code to move the car around.

``` lua

car = {
 x=120,
 y=68,
 a=0
}

-- Vector functions from previous tutorial
...

function drawCar(c)
 circb(c.x, c.y, 3, 15)
 local x1,y1 = vector(10,c.a)
 line(c.x, c.y, c.x+x1, c.y+y1, 15)
end

function TIC()

 -- rotate our direction
 if btn(2) then car.a=angleAdd(car.a,-0.05) end
 if btn(3) then car.a=angleAdd(car.a,0.05) end

 cls(0)

 drawCar(car)

 if btn(4) then
  local ax,ay = vector(1,car.a)
  car.x=car.x+ax
  car.y=car.y+ay
 end
end

```

This buys us the following:

![tut2_1](https://user-images.githubusercontent.com/2278103/41541286-5ce7afc4-7312-11e8-81d4-7f4ecf46146d.gif)

As you can see, we're not dealing with graphics yet, we'll use a circle with a point as a placeholder for now. But more importantly you can see that it doesn't feel like car driving at all: the cars has only two speeds: full speed and completely still, and switch between the two instantly. Also the car always go exacly the direction of its angle without ever drifting.

Let's solve all this problems by adding some physics. The root of our problem is that we acted on x and y that are the *position* of the car, but in reality we want to act on the *velocity* of the car. So let's add another vector to the car, the velocity vector. When the player is accelerating, we'll change that vector instead of the position, and then we'll update the position based on the velocity in a second step. Here's the code, i also introduced some "constants" to keep all numbers together, so it's easier to tweak our parameters.

``` lua

TURN_RADIUS = 0.05    -- how much the car turn when pressing left or right
ACCEL_VALUE = 0.02    -- acceleration when pressing z

car = {
 x=120, y=68, -- position
 vx=0, vy=0, -- velocity
 a=0 -- angle
}

function drawCar(c)
 circb(c.x, c.y, 3, 15)
 local x1,y1 = vector(10,c.a)
 line(c.x, c.y, c.x+x1, c.y+y1, 15)
end

function TIC()

 -- rotate our direction
 if btn(2) then car.a=angleAdd(car.a,-TURN_RADIUS) end
 if btn(3) then car.a=angleAdd(car.a,TURN_RADIUS) end

 cls(0)

 drawCar(car)

 if btn(4) then
  local ax,ay = vector(ACCEL_VALUE,car.a)
  car.vx=car.vx+ax -- change velocity this time
  car.vy=car.vy+ay
 end

 -- add velocity to car
 car.x=car.x+car.vx
 car.y=car.y+car.vy

end
```

And here's how it looks:

![tut2_2](https://user-images.githubusercontent.com/2278103/41541307-6ad4964c-7312-11e8-97ed-39d530dcf2fc.gif)

We accidentally created Asteroids. Indeed with no kind of friction in place, the car will mantain its speed indefinitely and we can only "brake" by rotating the other way around and accelerating again. We want to automatically decrease the speed of the car so that it will come to a rest in a bunch of seconds. This is easily done by multiplying the velocity by a factor slightly less than 1 each tic, like so (i'm not putting the full code here for brevity):

``` lua
FRICTION = 0.98       -- how much the car decelerate on asphalt

......
......

 if btn(4) then
  local ax,ay = vector(ACCEL_VALUE,car.a)
  car.vx=car.vx+ax
  car.vy=car.vy+ay
 end

 -- apply friction
 car.vx = car.vx * FRICTION
 car.vy = car.vy * FRICTION

 -- add velocity to car
 car.x=car.x+car.vx
 car.y=car.y+car.vy

```

Notice that we're *multiplying* the speed with friction, while we're just *adding* to it with acceleration. This has the nice effect (beside being physically correct i think) that friction grows bigger and bigger as the speed increase. At a certain point, the amound of speed we're removing with friction will balance the amount we're adding with acceleration, and the car will reach a natural top speed and won't accelerate any further. We could still add an explicit, arbitrary top speed limit if we want to have smaller friction (ie we're simulating ice or oil) or smaller top speed. But for now it will do. Here's how it looks:

![tut2_3](https://user-images.githubusercontent.com/2278103/41541330-747c093c-7312-11e8-9498-119dae9b7d36.gif)

Obviously as you already guessed, we can increase friction to simulate offroad terrains and decrease top speed (that's exacly how it's done in the final game):

``` lua
DIRT_FRICTION = 0.95  -- deceleration on dirt
FRICTION = 0.98       -- how much the car decelerate on asphalt

......
......

 rect(120,0,120,136,5) -- draw some grass

 -- apply friction
 local fr = car.x > 120 and DIRT_FRICTION or FRICTION
 car.vx = car.vx * fr
 car.vy = car.vy * fr

```

Now half of the screen is grass/dirt and has higher friction than the "asphalt" side.

![tut2_4](https://user-images.githubusercontent.com/2278103/41541345-7f5de046-7312-11e8-9bb5-aea6fdae0f9f.gif)

An even bigger friction could simulate a brake to be used when player press the second button.

So it already looks pretty driveable with a nice drift effect, the only problem is that when we are not accelerating, the direction of the car is completely unaffected by the steering. In other words, if the car is going top speed in a direction and we stop accelerating, we can use the left and right buttons to spin the car freely without changing the movement direction. It's kind of hard to explain in words but if you give it a try, it should be evident. In reality we want the direction to be dependent on the steering even in absence of acceleration. Obviously nothing instantaneous, we just want our movement direction to slowly correct to match the car direction. To do this we have to resort to our trusty "angle direction finder" function angleDir(). Here's the full code to recap:

``` lua
TURN_RADIUS = 0.05    -- how much the car turn when pressing left or right
ACCEL_VALUE = 0.02    -- acceleration when pressing z
FRICTION = 0.98       -- how much the car decelerate on asphalt
DIRT_FRICTION = 0.95  -- deceleration on dirt
ALIGNEMENT = 0.02     -- how fast the velocity catch up with direciton

-- our character position and direction
car = {
 x=120, y=68, -- position
 vx=0, vy=0, -- velocity
 a=0 -- angle
}

function drawCar(c)
 circb(c.x, c.y, 3, 15)
 local x1,y1 = vector(10,c.a)
 line(c.x, c.y, c.x+x1, c.y+y1, 15)
end

function TIC()

 -- rotate our direction
 if btn(2) then car.a=angleAdd(car.a,-TURN_RADIUS) end
 if btn(3) then car.a=angleAdd(car.a,TURN_RADIUS) end

 cls(0)
 rect(120,0,120,136,5)
 drawCar(car)

 if btn(4) then
  local ax,ay = vector(ACCEL_VALUE,car.a)
  car.vx=car.vx+ax -- change velocity this time
  car.vy=car.vy+ay
 end

 -- apply friction
 local fr = car.x > 120 and DIRT_FRICTION or FRICTION
 car.vx = car.vx * fr
 car.vy = car.vy * fr

 -- slowly rotate velocity to match car direction
 local v = angle(car.vx, car.vy) -- v is the angle of the velocity
 local d = angleDir(v, car.a) -- direction to go to align (-1 or 1)
 car.vx, car.vy = rotate(car.vx, car.vy, ALIGNEMENT * d)

 -- add velocity to car
 car.x=car.x+car.vx
 car.y=car.y+car.vy

end
```

We use a small ALIGNEMENT coefficient that tells how much to correct the velcity angle, that is how fast to align it with the car angle. Increasing the coefficient mean less drift and fastest correction, decreasing it gives more drift and slowest correction. Here's the comparison with and without the angle correction:

![tut2_turn](https://user-images.githubusercontent.com/2278103/41541385-97c32d30-7312-11e8-96a4-8192e7c3da90.gif)

So our final "car driving model" steps are:

* turn the car angle with left and right key
* if accelerating, add to the velocity
* apply friction
* correct the velocity to match the car angle
* add velocity to position

All the "constants" can be played with to give more or less drift, speed, etc. If you feel like, you can experiment with them on [the companion cartridge](https://tic80.com/play?cart=569).

Well that's our driving model, in the next installment we'll add other cars and we'll bounce them together. Yes, it's collision and bouncing time!

### Bonus

As a bonus for today, we'll remove our ball and pointer and put a proper sprite. We'll use @Fubuki wonderful production that comes in 4 basic directions, and we'll rotate them to cover 16 directions, which is enought directions to feel continuous.

![sprite](https://user-images.githubusercontent.com/2278103/41541530-f9dd2c78-7312-11e8-8c0e-2407046d8761.gif)

So how do we turn a radian angle to a 16-based angle and select the right sprite with rotation and everything? With this carefully handwrittern two liners (rou() is the round function that's surprisingly missing from lua):

``` lua
local idx = rou(car.a*16/pi2) % 16
spr(256 + (idx % 4), flr(car.x)-4, flr(car.y)-4,3, 1,0, idx // 4)

function flr(a) return math.floor(a) end
function rou(x) return x + 0.5 - (x + 0.5) % 1 end
```

How does it work? The first line converts the angle to our 16-based value (consider it something like degress but instead of 360, there's only 16. So each value is 22.5 degrees). This is simply a matter of changing the scale, but notice the important use of the round function. It helps center our 22.5 degrees slice on the angle instead of having it starts off on it. If you haven't understand the previous phrase, don't worry. It's impossible to exaplain with words, just try to change rou() to flr() and see the difference.

The second line use a trick to simultaneously pick the right one of the 4 sprites and the right rotation. Since the rotation parameter of the spr() API is oriented clockwise at 90° increments, we simply divide our idx by 4 to find the right rotation, and use the remainder (idx % 4) to select the right sprite of the four.

![tut2_final](https://user-images.githubusercontent.com/2278103/41541362-8b565a86-7312-11e8-8868-12cb83b73c90.gif)

Here's our drivable little car!

PS if you have any question, you can reach me on Discord or Twitter!