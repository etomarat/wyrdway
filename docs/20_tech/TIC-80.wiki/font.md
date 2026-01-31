`font(text, x, y, [transcolor], [char width=8], [char height=8], [fixed=false], [scale=1], [alt=false]) -> text width`

## Parameters
* **text** : The string to be printed.
* **x, y** : [Coordinates](coordinate) of print position.
* **transcolor** : The [palette](palette) index to use for transparency.
* **char width** : Distance between start of each character, in pixels.
* **char height** : Distance vertically between start of each character, in pixels, when printing multi-line text.
* **fixed** : Indicates whether the font is fixed width (defaults to false ie variable width).
* **scale** : Font scaling (defaults to 1).
* **alt** : If set to `true`, the second 128 foreground tiles (#384–511) are used for the font rather than the first 128 (#256-383) as if set to `false`.
## Returns
* **text width** : Returns the width of the rendered text in pixels.
## Description
This function will draw text to the screen using the foreground spritesheet as the font. Sprite #256 is used for ASCII code 0, #257 for code 1 and so on. The character 'A' has the ASCII code 65 so will be drawn using the sprite with sprite #321 (256+65). See the example below or check out the [In-Browser Demo](https://tic80.com/play?cart=20).

* To simply print text to the screen using the [system font](ram#font), please see [print](print).
* To print to the console, please see [trace](trace).
* There may never be more than 128 ASCII characters within a single **font()** call. The first 32 ASCII characters, which serve as object characters, are unused by text, therefore effectively only 96 characters are available for text.

For list of ASCII codes, please refer to [this link](https://simple.m.wikipedia.org/wiki/ASCII#Extended_ASCII).

## Font color
You can change the font color with `poke4` by swapping the color of the font sprites before using `font` and swapping back afterward.
```lua
initial_color=12 --color of your font sprites in sprite editor
new_color=3 --color you want to use
poke4(0x3FF0*2+initial_color,new_color) -- swaps initial_color and new_color in palette
font(...)
poke4(0x3FF0*2+new_color,initial_color) -- change it back

```

## 1 Bit Per Pixel
Save sprite space by using the 1 [bit per pixel](https://github.com/nesbox/TIC-80/wiki/Bits-Per-Pixel) setting.

* In sprite editor advanced mode chose the 1BPP setting and draw your font here.
* Then define functions to switch to 1bpp or 4bpp:
```lua
function set1bpp()
 poke4(2 * 0x3ffc, 8) -- 0b1000
end

function set4bpp()
 poke4(2 * 0x3ffc, 2) -- 0b0010
end
```
* Use these function before and after using font
```lua
set1bpp()
font("Hello font!", 84, 84)
set4bpp()
```

![video21](https://github.com/nesbox/TIC-80/assets/26139286/2b356fff-d76d-4719-ba75-8e053dd3d16c)


## Example
![Example](https://i.imgur.com/2DVaG8J.png)

``` lua
-- title:  Font Demo
-- author: paul59
-- desc:   Shows the working of font()
-- script: lua


function TIC()
	cls()
	-- The # character is ascii code 35
	-- so the sprite with ID 256+35 (#291)
	-- will be used to draw that character

	-- A and B have ascii codes 65 and 66.
	-- Sprites 256+65 (#321) and 256+66
	-- (#322) will be used to draw those
	-- letters

	font('#AB',20,20,2,9,9,true,3)

	-- The above prints '#AB' at position
	-- 20,20. The sprites use color 2 as
	-- transparency colorkey, are drawn 9
	-- pixels apart with fixed width and
	-- scaled up by a factor of 3
end
```

