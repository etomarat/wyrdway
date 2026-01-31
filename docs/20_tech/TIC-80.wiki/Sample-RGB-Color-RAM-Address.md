# Edit the palette with poke

You can edit the [palette](palette) directly by poking into [RAM](ram).

```
-ADDR-
0x3FC0 - Index 0 - Red component
0x3FC1 - Index 0 - Green component
0x3FC2 - Index 0 - Blue component
```

To learn more please see [RAM: Palette](ram#palette).

## Examples

### Swapping two colors
You can swap two colors of the palette to use an alternative version of a sprite or tile and swap it back afterward.
```lua
initial_color=12 --initial color of your sprite you want to change
new_color=3 --color you want to use
poke4(0x3FF0*2+initial_color,new_color) -- swaps initial_color and new_color
sprite(...)
poke4(0x3FF0*2+initial_color,initial_color) -- change it back

```

### Red

```lua
function TIC()
  cls()
  -- make the first palette entry RED
  poke(0x3FC0, 255)
end
```

![](https://i.ibb.co/wrxLK00/red.gif)

### Green

```lua
function TIC()
  cls()
  -- make the first palette entry GREEN
  poke(0x3FC1,255)
end
```


![](https://i.ibb.co/cty36Y6/green.gif)

### Blue

```lua
function TIC()
  cls()
  -- make the first palette entry BLUE
  poke(0x3FC2,255)
end
```

![](https://i.ibb.co/8PP1wPh/blue.gif)

### Pal Function
Sets the palette index i to specified r,g,b, or return the colors if no r,g,b values are declared.

```lua
--sets the palette indice i to specified rgb
--or return the colors if no rgb values are declared.
function pal(i,r,g,b)
	--sanity checks
	if i<0 then i=0 end
	if i>15 then i=15 end
	--returning color r,g,b of the color
	if r==nil and g==nil and b==nil then
		return peek(0x3fc0+(i*3)),peek(0x3fc0+(i*3)+1),peek(0x3fc0+(i*3)+2)
	else
		if r==nil or r<0 then r=0 end
		if g==nil or g<0 then g=0 end
		if b==nil or b<0 then b=0 end
		if r>255 then r=255 end
		if g>255 then g=255 end
		if b>255 then b=255 end
		poke(0x3fc0+(i*3)+2,b)
		poke(0x3fc0+(i*3)+1,g)
		poke(0x3fc0+(i*3),r)
	end
end
```
Other languages in the [snippets](https://github.com/nesbox/TIC-80/wiki/code-examples-and-snippets#pal-function) page.