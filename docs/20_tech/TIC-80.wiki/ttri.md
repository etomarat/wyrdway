`ttri(x1, y1, x2, y2, x3, y3, u1, v1, u2, v2, u3, v3, [texsrc=0], [chromakey=-1], [z1=0], [z2=0], [z3=0])`

## Parameters

* **x1, y1** : the screen [coordinates](coordinates) of the first corner
* **x2, y2** : the screen coordinates of the second corner
* **x3, y3** : the screen coordinates of the third corner
* **u1, v1** : the [UV coordinates](#a-note-on-uv-coordinates) of the first corner
* **u2, v2** : the UV coordinates of the second corner
* **u3, v3** : the UV coordinates of the third corner
* **texsrc** : if 0 (default), the triangle's texture is read from `SPRITES` RAM. If 1, the texture comes from the `MAP` RAM.<br>If 2, the texture comes from the screen RAM in the next VBANK (the one following the VBANK on which the `ttri()` is set to be displayed) (e.g., a `ttri()` on `vbank(0)` with the texsrc=2 will use `vbank(1)` as its texture at the time of its execution and vice versa).
* **chromakey** : index (or array of indexes 0.80) of the color(s) that will be used as transparent
* **z1, z2, z3** : depth parameters for perspective correction and depth buffer

### A note on UV Coordinates

![UV_coordinates_montage](https://github.com/nesbox/TIC-80/assets/26139286/81bb264f-123f-4c6e-a60f-2bb2fbb123fd)

The letters "U" and "V" denote the axes of the 2D texture because "X", "Y" are already used.
These can be thought of as the window inside `SPRITES` or `MAP` RAM. Note that the sprite sheet or map in this case is treated as a single large image, with U and V addressing its pixels directly, rather than by sprite ID. So for example the top left corner of sprite #2 would be located at `u=16` (horizontal), `v=0` (vertical).

## Description

This function draws a triangle filled with texture from either `SPRITES` or `MAP` [RAM](ram) or VBANK.

### Depth Buffer

A depth buffer is implemented in ttri when `z1, z2, z3` arguments are set. The depth buffer can be cleared using the `cls()` [function](https://github.com/nesbox/TIC-80/blob/main/src/core/draw.c#L397).

## Examples

``` lua
-- title:  triangle demo
-- author: MonstersGoBoom
-- desc:   wiki demo for ttri
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

  ttri(0,0,
         64,0,
         0,64,
         0,0,
         usize,0,
         0,vsize,
         true,
         14)
  ttri(64,0,
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

![demo 3D](https://user-images.githubusercontent.com/1101448/160176923-acfbc5fe-2dbf-422b-b958-8667b5c19972.gif)

- Sprite x,y,z rotation with ttri [here](https://github.com/nesbox/TIC-80/wiki/Code-examples-and-snippets#ttri-xyz-rotation)

![ttri_rotation_demo](https://github.com/nesbox/TIC-80/assets/26139286/24464fa0-82ed-42de-a3c1-4433e5ff1b4e)
