# textri

_This API was added in version 0.46._

`textri(x1, y1, x2, y2, x3, y3, u1, v1, u2, v2, u3, v3, [use_map=false], [trans=-1])`

## Parameters

* **x1, y1** : the screen [coordinates](coordinate) of the first corner
* **x2, y2** : the screen coordinates of the second corner
* **x3, y3** : the screen coordinates of the third corner
* **u1, v1** : the UV coordinates of the first corner
* **u2, v2** : the UV coordinates of the second corner
* **u3, v3** : the UV coordinates of the third corner
* **use_map** : if false (default), the triangle's texture is read from `SPRITES` RAM. If true, the texture comes from the `MAP` RAM.
* **trans** : index (or array of indexes 0.80) of the color(s) that will be used as transparent

### A note on UV Coordinates

These can be thought of as the window inside `SPRITES` or `MAP` RAM. Note that the sprite sheet or map in this case is treated as a single large image, with U and V addressing its pixels directly, rather than by sprite ID. So for example the top left corner of sprite #2 would be located at `u=16` (horizontal), `v=0` (vertical).


## Description

This function draws a triangle filled with texture from either `SPRITES` or `MAP` [RAM](ram).

### Use in 3D graphics

This function does **not** perform perspective correction, so it is not generally suitable for 3D graphics (except in some constrained scenarios). In particular, if the vertices in the triangle have different 3D depth, you may see some distortion.

## Example

``` lua
-- title:  triangle demo
-- author: MonstersGoBoom
-- desc:   wiki demo for textri
-- script: lua
-- input:  gamepad

usize = 32
vsize = 32
function TIC()
  cls(1)
  if btn(0) then usize=usize-1 end
  if btn(1) then usize=usize+1 end
  if btn(2) then vsize=vsize-1 end
  if btn(3) then vsize=vsize+1 end

-- draw a scaling view into the map ram

  textri(0,0,
         64,0,
         0,64,
         0,0,
         usize,0,
         0,vsize,
         true,
         14)
  textri(64,0,
         0,64,
         64,64,
         usize,0,
         0,vsize,
         usize,vsize,
         true,
         14)
end
```
[UV show](https://tic80.com/play?cart=554)