`print(text[,x=0][,y=0][,color=15][,fixed=false][,scale=1][,smallfont=false]) -> width`

## Parameters
* **text** : any string to be printed to the screen
* **x, y** : [coordinates](Display#coordinate-system) for printing the text
* **color** : the [color](Palette) to use to draw the text to the screen
* **fixed** : a flag indicating whether fixed width printing is required
* **scale** : font scaling
* **smallfont** : use small font if true

## Returns
* **width** : returns the width of the text in pixels.

## Description
This will simply print text to the screen using the font defined in config. When set to true, the fixed width option ensures that each character will be printed in a 'box' of the same size, so the character 'i' will occupy the same width as the character 'w' for example. When fixed width is false, there will be a single space between each character. Refer to the examples for an illustration.

The text is scale×6 pixels high.

* To use a custom rastered font, check out [font](font).
* To print to the console, check out [trace](trace).


## Examples

### Centred Text

![Example 1](https://i.imgur.com/FBEiXYY.png)

``` lua
-- title:  print centered
-- author: Vadim
-- desc:   print text perfectly centered
-- script: lua
-- input:  gamepad

cls()
local string="my perfectly centered text"
local width=print(string,0,-6)
print(string,(240-width)//2,(136-6)//2)

function TIC()end

```
```lua
--Prints text where x is the center of text.
function printc(s,x,y,c)
    local w=print(s,0,-8)
    print(s,x-(w/2),y,c or 15)
end
```
### Fixed Width

![Example 2](https://i.imgur.com/lR279OS.png?2)

```lua
-- title:  Fixed width demo
-- author: paul59
-- desc:   Show effect of fixed width flag
-- script: Lua

function TIC()
  cls(0)
  print('FIXED',0,0,15,true)
  print('FIXED',0,8,15,false)
  print('width',0,32,15,true)
  print('width',0,40,15,false)
  for i=0,30,6 do
    line(i,0,i,6,8)
    line(i,8,i,16,9)
    line(i,32,i,40,8)
    line(i,40,i,48,9)
  end
end
```

### Extended print function
Extended print function that automatically goes to line, align text in various ways and much more. See the demo [cart](https://tic80.com/play?cart=3600) and the [documentation](https://github.com/nesbox/TIC-80/wiki/Extended-Print-Function).

![extended_print_v2](https://github.com/nesbox/TIC-80/assets/26139286/6782697f-8000-4fbe-86c0-1e07f8a69397)

You can directly copy-paste this in your code to use it:

```lua
--MIT License
-------------------
--EXTENDED PRINT
-------------------
--[[
  _   _   _           _     ___    ___ ___  _       
 | \ / \ /  | | |\/| |_ |\ | |  /\  |   |  / \ |\ | 
 |_/ \_/ \_ |_| |  | |_ | \| | /--\ |  _|_ \_/ | \| 

`eprint(text, [x=0], [align_x=-1], [y=0], [align_y=-1], [color=15], [fixed=false], [scale=1], [smallfont=false], [offset=0], [interline=1*scale], [allow_smallfont=false], [shadow_col=false]) -> text_width, text_height`

## Parameters
- x, y: [Coordinates](https://github.com/nesbox/TIC-80/wiki/Display#coordinate-system) for printing the text.
They can be:
  - Integer: it will align from this position.
  - Table with two values: it will limit the text between these two positions, going to line if it is too long or switching to smallfont if `allow_smallfont` is true.
  - Empty table: it will limit the text to stay on screen, going to line if it is too long or switching to smallfont if `allow_smallfont` is true.
- align_x, align_y: Determine how the text is aligned vertically and horizontally.
They can take the values:
  - `-1` to align to the left/top.
  - `0` to center.
  - `1` to align to the right/bottom.
- color: The [color](Palette) to use to draw the text to the screen.
- fixed: A flag indicating whether fixed width printing is required.
- scale: Font scaling.
- smallfont: Use small font if true.
- offset: Space between the border of the frame or screen and the text. Not used when aligned on a point.
- interline: Vertical space between two lines.
- allow_smallfont: If `true` it will switch to small font when the text does not fit horizontally or vertically.
- shadow_col: Add shadow with the color `shadow_col`. Set to false to not have shadow.

## Returns
- text_width: returns the width of the text in pixels.
- text_height: returns the height of the text in pixels.
]]--

char_height=6

--return a table of the position of each space. It also marks the end of the string as a space.
function get_spaces(text)
 local spaces={}
 for char_id=1,#text,1 do
  if text:sub(char_id,char_id)==" " then --look for spaces
   table.insert(spaces,char_id)
  end
 end
 if text~='' then
  table.insert(spaces,#text+1) --mark end of line as a space
 end
 return spaces
end

--get the width of the text
function get_text_width(text,fixed,scale,smallfont,shadow)
 fixed=fixed or false
 scale=scale or 1
 smallfont=smallfont or false
 shadow=shadow or false
 local text_width=print(text,10000,-10000,15,fixed,scale,smallfont)
 if shadow then
  text_width=text_width+scale
 end 
 return text_width
end

--As print does not output the height, I split newline with \n myself. It also allows to set the interline spacing.
function split_newline(text)
 local split_string={}
 while string.match(text,'\n') do
  local newline_id=string.find(text,'\n')
  table.insert(split_string,text:sub(1,newline_id-1).." ")
  text=text:sub(newline_id+1,#text)
 end
 table.insert(split_string,text)
 return split_string
end

--split text to fit in `width_max`
function split_text(text,width_max,fixed,scale,smallfont,shadow)
 local split_txt={}
 local l_widths={}

 local split_txt_nl=split_newline(text)

 for l_id=1,#split_txt_nl,1 do
  local txt_line=split_txt_nl[l_id]
  local spaces=get_spaces(txt_line)
  while #spaces>0 do
   for ii=#spaces,1,-1 do
    local line_=txt_line:sub(1,spaces[ii]-1)
    local l_width=get_text_width(line_,fixed,scale,smallfont,shadow)
    if l_width<=width_max or ii==1 then
     table.insert(split_txt,line_)
     table.insert(l_widths,l_width)
     txt_line=txt_line:sub(spaces[ii]+1,#txt_line)
     spaces=get_spaces(txt_line)
     break
    end
   end
  end
 end
 return split_txt,l_widths
end

--return true if one of the lines is longer than `max_width`
function too_wide(l_widths,max_width)
 for ii=1,#l_widths,1 do
  if l_widths[ii]>max_width then
   return true
  end
 end
 return false
end

--Get position used to print
function get_pos(pos,align,size)
 --Get reference position that will be used to get print position
 local ref_pos=0
 if type(pos)=='table' then
  if #pos==0 then --if empty table we align on screen
   trace("Error: #pos should be >0 as offset should be included before using get_pos.")
   return nil
 
  elseif #pos==1 then --if table of one value we change that to a number
   ref_pos=pos[1]
 
  elseif #pos==2 then
   if align==-1 then
    ref_pos=pos[1]
   elseif align==0 then
    ref_pos=(pos[1]+pos[2])/2
   elseif align==1 then
    ref_pos=pos[2]
   end
  end
 else
  ref_pos=pos
 end

 --Get position that will be used in the print
 local pos=0
 if align==-1 then --left/up align x/y
  pos=ref_pos
 elseif align==0 then --center x/y
  pos=ref_pos-math.floor(size/2)
 elseif align==1 then --right/low align x/y
  pos=ref_pos-size
 end
 return pos
end

--See documentation line 15.
--eprint(text, [x=0], [align_x=-1], [y=0], [align_y=-1], [color=15], [fixed=false], [scale=1], [smallfont=false], [offset=0], [interline=1*scale], [allow_smallfont=false], [shadow_col=false]) -> text_width, text_height
function eprint(text,x,align_x,y,align_y,color,fixed,scale,smallfont,offset,interline,allow_smallfont,shadow_col)
 x=x or 0
 align_x=align_x or -1
 y=y or 0
 align_y=align_y or -1
 color=color or 15
 fixed=fixed or false
 scale=scale or 1
 scale=math.floor(scale)
 smallfont=smallfont or false
 offset=offset or 0
 interline=interline or 1*scale
 allow_smallfont=allow_smallfont or false
 shadow_col=shadow_col or false
 --Align on screen becomes align on frame with the size of the screen
 if type(x)=='table' then
  if #x==0 then
   x={offset,240-offset}
  elseif #x==2 then
   x={x[1]+offset,x[2]-offset}
  end
 end
 if type(y)=='table' then
  if #y==0 then
   y={offset,136-offset}
  elseif #y==2 then
   y={y[1]+offset,y[2]-offset}
  end
 end
 
 local l_widths={}
 local l_height=math.floor(char_height*scale)
 if shadow_col then
  l_height=l_height+scale
 end
 --Align on frame (or screen): split text
 if type(x)=='table' and #x==2 then
  local splitted_text={}
  splitted_text,l_widths=split_text(text,x[2]-x[1],fixed,scale,smallfont,shadow_col)
  if not smallfont and allow_smallfont and (too_wide(l_widths,x[2]-x[1]) or (type(y)=='table' and #y==2 and (#splitted_text*(l_height+interline)-interline>y[2]-y[1]))) then
   smallfont=true
   splitted_text,l_widths=split_text(text,x[2]-x[1],fixed,scale,smallfont,shadow_col)
  end
  text=splitted_text
 end

 --Aligned on point:
 if type(text)=="string" then
  local width=get_text_width(text,fixed,scale,smallfont,shadow)
  x=get_pos(x,align_x,width)
  y=get_pos(y,align_y,l_height)
  if shadow_col then
   print(text,x-scale,y+scale,shadow_col,fixed,scale,smallfont)
  end
  print(text,x,y,color,fixed,scale,smallfont)
  
 --Aligned on frame (or screen):
 elseif type(text)=="table" then --if text is splitted in lines
  local y_high=get_pos(y,align_y,(l_height+interline)*#text-interline)
  for line_=1,#text,1 do
   local x_line=get_pos(x,align_x,l_widths[line_])
   local y_line=y_high+(line_-1)*(l_height+interline)
   if shadow_col then
    print(text[line_],x_line,y_line+scale,shadow_col,fixed,scale,smallfont)
    print(text[line_],x_line+scale,y_line,color,fixed,scale,smallfont)
   else
    print(text[line_],x_line,y_line,color,fixed,scale,smallfont)
   end
  end
 end

 --Return width, height
 local text_width=0
 if #l_widths > 0 then
  text_width=math.max(table.unpack(l_widths))
 end
 local text_height=#l_widths*l_height+(#l_widths-1)*interline
 return text_width,text_height
end


--------------------------
--END OF EXTENDED PRINT
--------------------------
```

### Demo Scale

![Example 4](https://imgur.com/tu6CEbp.gif)

``` lua
-- title:  print demo scale
-- author: Filippo
-- desc:   scale print
-- script: lua
-- input:  gamepad

t=0
txt="[TIC]"

function TIC()
 for i=1,15 do
 local of=3*i
  poke(0x3FC0+of,100+i*10)
  poke(0x3FC0+of+1,i*5)
  poke(0x3FC0+of+2,32+32*math.sin(t/100))
 end

 cls()
 for z=15,0,-1 do
  y=12*z*math.sin(z/5+t/50)
  w=print(txt,0,-100,z,false,z)
  print(txt,(240-w)/2,
       68+y/1.5,
       15-z,false,z)
 end
 t=t+1
end
```