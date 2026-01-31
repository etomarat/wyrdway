# API Cheatsheet

Note: in js/Wren functions that return multiple values (`mouse`, optionally `remap` for `map`) return an Array/List.

`btn [id] -> pressed`

`btnp [[id, [hold], [period] ] -> pressed`

|Action |P1 ID |P2 ID |P3 ID |P4 ID |
|:-----:|:----:|:----:|:----:|:----:|
|Up     |0     |8     |16    |24    |
|Down   |1     |9     |17    |25    |
|Left   |2     |10    |18    |26    |
|Right  |3     |11    |19    |27    |
|A (Z)  |4     |12    |20    |28    |
|B (X)  |5     |13    |21    |29    |
|X (A)  |6     |14    |22    |30    |
|Y (S)  |7     |15    |23    |31    |

`clip [x y w h]`

`cls [color=0]`

`circ x y radius color`

`circb x y radius color`

`exit`

`elli x y a b color`

`ellib x y a b color`

`fget sprite_id flag -> bool`

`fset sprite_id flag bool`

`font text, x, y, [transparent], [char width], [char height], [fixed=false], [scale=1] -> text width`

`key [code] -> pressed`

`keyp [code [hold period] ] -> pressed`

01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---
A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z

27|28|29|30|31|32|33|34|35|36
---|---|---|---|---|---|---|---|---|---
0|1|2|3|4|5|6|7|8|9

37|38|39|40|41|42|43|44|45|46|47
---|---|---|---|---|---|---|---|---|---|---
minus|equals|leftbracket|rightbracket|backslash|semicolon|apostrophe|grave|comma|period|slash

48|49|50|51|52|53
---|---|---|---|---|---
space|tab|return|backspace|delete|insert

54|55|56|57|58|59|60|61
---|---|---|---|---|---|---|---
pageup|pagedown|home|end|up|down|left|right

62|63|64|65
---|---|---|---
capslock|ctrl|shift|alt

`line x0 y0 x1 y1 color`

`map [x=0 y=0] [w=30 h=17] [sx=0 sy=0] [colorkey=-1] [scale=1] [remap]`

- **remap** is a callback:  `tile [x y] -> tile [flip] [rotate]`

`memcpy toaddr fromaddr len`

`memset addr val len`

`mget x y -> id`

`mset x y id`

`mouse -> x y left middle right scrollx scrolly`

`music [track=-1] [frame=-1] [row=-1] [loop=true]`

`peek addr [bits=8] -> val`

`peek1 bitaddr -> bitval` (1.0)

`peek2 addr2 -> val2` (1.0)

`peek4 addr4 -> val4`

`pix x y [color] -> color`

`pmem index [val] -> val`

`poke addr val`

`poke1 bitaddr bitval` (1.0)

`poke2 addr2 val2` (1.0)

`poke4 addr4 val4`

`print text [x=0 y=0] [color=12] [fixed=false] [scale=1] [smallfont=false] -> text width`

`rect x y w h color`

`rectb x y w h color`

`reset`

`sfx id [note] [duration=-1] [channel=0] [volume=15] [speed=0]`

`spr id x y [transparent=-1] [scale=1] [flip=0] [rotate=0] [w=1 h=1]`

* `flip=1,2,3` to flip horizontally,vertically,both;
* `rotate=1,2,3` to rotate 90, 180, 270 degrees clockwise

`sync [mask=0 bank=0 tocart=false]`

- values for **mask**:

``` lua
tiles   = 1<<0 -- 1
sprites = 1<<1 -- 2
map     = 1<<2 -- 4
sfx     = 1<<3 -- 8
music   = 1<<4 -- 16
palette = 1<<5 -- 32
flags   = 1<<6 -- 64
screen  = 1<<7 -- 128 (as of 0.90)
```

`ttri x1 y1 x2 y2 x3 y3 u1 v1 u2 v2 u3 v3 [texsrc=0] [chromakey=-1] [z1=0] [z2=0] [z3=0]`

`time -> milliseconds`

`trace msg [color]`

`tri x1 y1 x2 y2 x3 y3 color`

`trib x1 y1 x2 y2 x3 y3 color`

`tstamp -> timestamp`

`vbank bank` (bank is `0` or `1`)

## Other Cheatsheets
- [TIC-80 Manual & Cheat Sheet by Skye Waddell](https://skyelynwaddell.github.io/tic80-manual-cheatsheet/)
- [PDF but outdated by ZenithSal](https://github.com/nesbox/TIC-80/files/12447661/tic-80_cheatsheet.pdf)
