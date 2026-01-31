`spr(id, x, y, [colorkey=-1], [scale=1], [flip=0], [rotate=0], [w=1], [h=1])`

## Parameters

* **id** : index of the [sprite](sprite) (0..511)
* **x, y** : screen [coordinates](coordinate) of top left corner of sprite.
* **colorkey** : index (or array of indexes) of the color in the [sprite](sprite) that will be used as transparent color.  Use -1 if you want an opaque sprite.
* **scale** : scale factor applied  to [sprite](sprite).
* **flip** : flip the [sprite](sprite) vertically or horizontally or both.
* **rotate** : rotate the [sprite](sprite) by 0, 90, 180 or 270 degrees.
* **w** : width of composite sprite
* **h** : height of composite sprite

## Description

Draws the [sprite](sprite) number **index** at the **x** and **y** [coordinate](coordinate).

You can specify a **colorkey** in the [palette](palette) which will be used as the transparent color or use a value of -1 for an opaque sprite.

The sprite can be **scaled** up by a desired factor. For example, a scale factor of 2 means an 8x8 pixel sprite is drawn to a 16x16 area of the screen.
Fractional factors are floored to integers, and both a factor of 0 and negative factors cause the sprite to not get drawn.

You can **flip** the sprite where:
* 0 = No Flip
* 1 = Flip horizontally
* 2 = Flip vertically
* 3 = Flip both vertically and horizontally

When you **rotate** the sprite, it's rotated clockwise in 90° steps:
* 0 = No rotation
* 1 = 90° rotation
* 2 = 180° rotation
* 3 = 270° rotation

**Important:** If you combine **flip** and **rotate** in the same sprite, take into account that **rotate** is applied _prior_ to **flip** (the order matters).

You can draw a **composite** sprite (consisting of a rectangular region of sprites from the sprite sheet) by specifying the **w** and **h** parameters (which default to 1).

## Example

![Example](https://imgur.com/q4QSxEq.gif)

``` lua
-- spr demo

--Build sprite from text
data = "D000000D" .. "D0C00C0D" ..
  "DDDDDDDD" .. "DDCDDD2D" ..
  "DCCCDDDD" .. "DDcdd2dd" ..
  "DDDDDDDD" .. "EEEEEEEE"
for i=0,64 do
 poke4(0x4000*2+64+i,
  tonumber(string.sub(
  data,i+1,i+1),16))
end

p={
 x={val=100,min=0,max=240},
 y={val=68,min=0,max=136},
 colorkey={val=0,min=-1,max=15},
 scale={val=1,min=0,max=256},
 flip={val=0,min=0,max=3},
 rotate={val=0,min=0,max=3},
}
sel=next(p,nil)


function TIC()

 --Keys
 if btnp(0,30,6) then
  for n=0,4 do
   sel=next(p,sel) or next(p,nil)
  end
 end
 if btnp(1,30,6) then
  sel=next(p,sel) or next(p,nil)
 end

 if btnp(2,30,6) then
  p[sel].val=p[sel].val-1
 end
 if btnp(3,30,6) then
  p[sel].val=p[sel].val+1
 end

 --Clamp
 if p[sel].val>p[sel].max then
   p[sel].val=p[sel].max
 end
 if p[sel].val<p[sel].min then
   p[sel].val=p[sel].min
 end

 cls(0)
 print("Use up/down  to select parameter",0,0)
 print("left/right to change its value:",0,10)

 --Build menu with cursor
 r=0
 for k,v in pairs(p) do
  cur=(k==sel) and '>' or ' '
  print(cur..k..':'..v.val,0,30+10*r)
  r=r+1
 end

 --Draw Sprite
 spr(1,
    p.x.val,
    p.y.val,
    p.colorkey.val,
    p.scale.val,
    p.flip.val,
    p.rotate.val)

end
```

### Color Swapping Sprites
You can substitute one color of the palette for another to use an alternative version of a sprite or tile.
> [!Tip]
> Make sure to set the palette back to how it was afterwards.
```lua
initial_color=12 --initial color of your sprite you want to change
new_color=3 --color you want to use
poke4(0x3FF0*2+initial_color,new_color) -- set new_color in place of initial_color
spr(...)
poke4(0x3FF0*2+initial_color,initial_color) -- change it back

```