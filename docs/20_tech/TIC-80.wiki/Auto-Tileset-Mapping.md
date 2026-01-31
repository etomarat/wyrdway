
So you've spent alot of time drawing you're tileset for your game...you have all the parts you need!
Now comes the hard part...piecing your level together a tile at a time :(
![bit_mapping_tile_by_tile](https://user-images.githubusercontent.com/32113404/32666017-c1aadd42-c5fb-11e7-8dcf-d9811c82dae5.gif)
**AAAAAAAHHH I CAN'T TAKE THIS ANYMORE!!!**

Well don't worry...I have good news for you. You can automate the whole process.
That's right! with some binary math...and a little ♩♩Lua Lua (whoa whoa)♩♩
We can have TIC-80 pick the correct tile for us!
![bit_mapping_demo](https://user-images.githubusercontent.com/32113404/32668314-d27ecafa-c602-11e7-8e4f-7a2f65f32b9d.gif)
(Here I'm just touching the screen where I want a wall and TIC-80's assigning the tiles)

I've heard this process refered to as *bit mapping* or *bit masking* or *binary mapping*...
I'm not sure which is correct...but whatever it's called, the process is still the same.

## HOW IT WORKS
The way this works is this:
1. Iterate over every tile in the map
2. for each tile:
   a. check which adjacent cells are "walls"
   b. for each neighbor...add a specific number
   c. once all neighbors have been added...
      find the tile with that matching number!

Okay...maybe sounds more complex than it really is...Let's take it a step at a time.
The first step is to convert every possible pattern of neighbors into binary.

## HOW BINARY WORKS
If you already understand binary...then please skip ahead to avoid frustration :)

Binary is a base 1 number system...
As opposed to our usual number system...which is base 10.
This means four digit numbers are represented as such:
```thousands hundreds tens ones```
and every time we reach a nine (the highest number in our system)
we go back to 0 and add a 1 to the next column over.  observe:
```
0000
0001
0002
0003
0004
0005
0006
0007
0008
0009
0010 --notice it's back to zero and add one to the next column
```

But binary only has 0 and 1...
So it's numbers are exponents of 2 (because there's only two numbers available)
so four digit binary numbers are represented like this:
```eights, fours, twos, ones```
and every time we reach 1 (the highest number in binary)
we go back to 0 and add a 1 to the next column over. Observe:
```
0000  --zero
0001  --one
0010  --two   (notice it's back to one and add a 1 to the next column)
0011  --three
0100  --four  (ticked over two columns here)
0101  --five
0110  --six   (ticked over one column)
0111  --seven
1000  --eight (ticked over three columns)
1001  --nine
1010  --ten   (ticked over another column)
1011  --eleven
1100  --twelve(and two columns)
```
You get the idea...

## APPLYING BINARY TO THE TILESET
So now let's wrap the binary columns (8's 4's 2's 1's) clockwise around a tile:
![binary_map_values](https://user-images.githubusercontent.com/32113404/32667303-f58fffd0-c5ff-11e7-96c5-3b07ef6c1013.gif)
In this way...we can assign every pattern of neighbors as a binary number...
Here would be the first ten positions:
![bit_mapping_binary](https://user-images.githubusercontent.com/32113404/32665510-1fa1500e-c5fa-11e7-975d-f7aa1963f8eb.gif)
Notice I've written the binary number below each one.
And if you're confused, try adding the values you see in the surrounding boxes!

And Here's the basic Tileset I drew to match these positions:
![bit_mapping_line_sprites](https://user-images.githubusercontent.com/32113404/32665520-27e6a8fe-c5fa-11e7-8848-64f6278fae44.gif)

So try this yourself...Look at the first ten positions...and pick one.
1. Add up the numbers in the blue boxes around it. we'll call this the "OFFSET"
2. Start at the "0" tile in the Tileset above.
3. count over as many times as your OFFSET
4. notice the tile you're pointing to matches the pattern of neighbors you chose!
   (in fact it actually looks like the pattern you chose!)

So if we draw our tilesets to match this pattern...we can call them with binary!

## GETTING THE RIGHT TILE
Now this is where Lua comes in...
We'll write a simple function that will check the neighbors of every tile and get the correct binary number...
Then get the tile out of the tileset with that same number...
and finally set that tile into the current map cell.

Here's the bit_map() function:
``` lua
--first some constants

--map size
MINX=0
MAXX=30
MINY=0
MAXY=17

--sprite info
SOLID=1
WALL=16

--so if it's the first sprite it's a "solid"
--and the 0th tile in my tileset is in slot 16

function bit_map()

 --here I'm making a list of the binary columns
 --for easy reference...we could use the exponent
 --function but this is so much easier!
 local BINARY={1,2,4,8}

 --iterate over every cell
 for x=MINX, MAXX do
  for y=MINY, MAXY do

   --if the current cell is "solid" then
   --let's work on it...this makes the
   --function ignore floor tiles.
   if mget(x,y)>=SOLID then

    --and here's the four adjacents around our tile
    local u=mget(x  ,y-1)  --up
    local d=mget(x  ,y+1)  --down
    local l=mget(x-1,y  )  --left
    local r=mget(x+1,y  )  --right

    --and we put them into a list...
    --!!notice their in order of the binary columns!!
    --up is 1st
    --right is 2nd
    --down is 3rd
    --left is 4th
    --clockwise remember?
    local adjacents={u,r,d,l}

    --here we give the function the 0th tile in our tileset
    --if you have your tileset start at a different slot...
    --just specify the starting slot in the WALL variable.
    local tile=WALL

    --here we have to use the ipairs() function
    --the pairs() function does not iterate through
    --a list in order! and we need that order to do
    --our binary math!!
    --ipairs() iterates through a list in order. :)
    for i,k in ipairs(adjacents)do

      --if the current neighbor is a solid then
      if k>=SOLID then

       --add the correct binary value
       tile=tile+BINARY[i]

       --this is where we use the BINARY list
       --if we're on the first neighbor (up)
       --then we'll add the first value in BINARY (1)
       --but if we're on the fourth neighbor (left)
       --then we'll add the fourth value in BINARY (8)

       --once the for loop has dealt with all the neighbors...
       --the "tile" variable now holds the sprite id for the
       --correct tile in our tileset!
      end
     --finally we assign that tile to the current cell
     mset(x,y,tile)
    end
   end
  end
 end
end
```

Here's an example map...I've just drawn the "solids" in the map editor:
![bit_mapping_plain](https://user-images.githubusercontent.com/32113404/32665545-41031fac-c5fa-11e7-95c1-2b3f9a0b6456.gif)

And here I've used the bit_map() to assign my tileset:
![bit_mapping_lines](https://user-images.githubusercontent.com/32113404/32665535-36ef572e-c5fa-11e7-9989-5aab0565db54.gif)

But this still looks boring...how about a rocky wall tileset?!
![bit_mapping_stone](https://user-images.githubusercontent.com/32113404/32665563-5485ff90-c5fa-11e7-95ce-01776709a039.gif)

And if we call bit_map() on every game cycle...any map changes will also affect the tile sprites!
![bit_mapping_realtime](https://user-images.githubusercontent.com/32113404/32665582-6757dce2-c5fa-11e7-86dd-a7aa07a6badf.gif)

And by calling '''sync()''' on every cycle, we can save our finished map to the cartridge for further work!
![bit_mapping_map_sync](https://user-images.githubusercontent.com/32113404/32665609-81038600-c5fa-11e7-8c95-441ccacad98b.gif)

This is the basics of bit (binary) mapping.
I have used it for a snake game to make the segments display correctly.

Feel free to use any portion of the above coffee in your own projects. Just sick a small credit to me at the top of your file and we're good.

If you have questions or requests for future tutorials, email me at bearknucklesketching@Gmail.Com
