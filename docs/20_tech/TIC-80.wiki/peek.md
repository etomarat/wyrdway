# peek*

_This API was extended in version 0.9 and 1.0._

- `peek(addr) -> value`
- `peek(addr, [bits=8]) -> value` *added in 0.9*
- `peek4(addr4) -> val4`
- `peek2(addr2) -> val2` *added in 1.0*
- `peek1(bitaddr) -> bitval` *added in 1.0*

Or using `bits` argument:

- `peek(addr) -> byte` (default)
- `peek(addr4, bits=4) -> val4`
- `peek(addr2, bits=2) -> val2`
- `peek(bitaddr, bits=1) -> bitval`


## Parameters
* **addr** : the address of [RAM](RAM) you desire to read (segmented based on `bits`)
* **bits** : the number of bits to read (1, 2, 4, or 8) from address (default: 8)

## Returns

The range of value returned depends on the `bits` parameter:

- **byte** : a full byte (0..255) - `bits=8`
- **val4** : a nibble (4 bits) (0..15) - `bits=4`
- **val2** : two bits (0..3) - `bits=2`
- **bitval** : a single bit (0..1) - `bits=1`

## Description
This function allows you to read directly from RAM. It can be used to access resources created with the integrated tools, such as the sprite, map and sound editors, as well as cartridge data.

The requested number of bits is read from the address requested.  The address is typically specified in hexadecimal format.

See also:

- [poke](poke) - Write to a memory address


#### Addressing

Addressing is based on the `bits` parameter.

- 8 - addresses RAM byte by byte (0 to 0x18000)
  - e.g. `TILES` begins at address `0x4000`
- 4 - addresses by nibble (just as with [peek4](peek4))
  - e.g. `TILES` begins at address `0x8000`
- 2 - addresses by pairs of bits
  - e.g. `TILES` begins at address `0x10000`
- 1 - addresses memory one bit at address a time
  - e.g. `TILES` begins at address `0x20000`

#### Nibbles / peek4 / `bits=4`

With `peek4` and `poke4` (and `bits=4`) RAM is addressed in 4 bit segments (nibbles). To access the the RAM at byte address `0x4000` you would need to access **both** the `0x8000` and `0x8001` nibble addresses.

*Note:* Memory is sequenced with least significant nibbles first, which may be the opposite of what you expecting if you are reading the hexadecimal byte by byte.  A small example:

```lua
-- set byte address 0x4000 to the value 0xF1 (241)
poke(0x4000, 0xF1)

-- the low nibble (least significant bits)
peek4(0x8000) -- => 1  (0x01)
-- the high nibble (most significant bits)
peek4(0x8001) -- => 15 (0x0F)
```


Since the addressing varies with `bits`, these two calls function identically:

```lua
peek(0x2000,4)
peek4(0x2000)
```

#### Bit Pairs / peek2 /  `bits=2`

Given the following contents of RAM:

```
ADDR  VALUE
...   ...
2     0b00000000
3     0b01100000
4     0b00000000
```

If you wanted to peek just the 2 set bits of address 3:

```lua
-- byte address 3
-- address by bit pairs (* 4)
-- starting with the 6th bit (+ 5)
peek(3 * 4 + 5, 2)
-- or
peek2(3 * 4 + 5)
```


## Examples

- [peek/poke](#peek--poke)
- [peek4/poke4](#peek4--poke4)

### peek / poke

![peek_demo](https://github.com/nesbox/TIC-80/assets/26139286/76ba2f62-aa99-4003-80c1-6fe55491c3a6)

``` lua
-- lua demo peek/poke

-- use poke to create a sprite from a hexadecimal data string
img="0a0000a00a0ff0a0aaaaaaaaaaafaaa6faffaaaaaaaf6aaaaaaaaaaa33333333"
-- foreach of the 32 bytes in the sprite
for i=0,31 do
 --extract the data from the string 2 chars at time
 s = string.sub(img,i*2+1,i*2+2)
 --convert the hex string to a decimal number
 val = tonumber(s,16)
 --put the value in the RAM area dedicated to sprites, sprite number 4
 poke(0x4000+128+i,val)
end

-- read back the sprite data and print it to console
msg=''
-- foreach of the 32 bytes in the sprite
for i=0,31 do
 --read the byte value in decimal format
 val=peek(0x4000+128+i)
 -- convert the value in hexadecimal format
 s=string.format("%02x",val)
 -- concatenate the string to a final message
 msg=msg..s
end
-- print it to the console
trace(msg)
-- add sprite to TIC cartridge
sync(0,0,true)

function TIC()
 cls()
 print('Done.. have a look at the sprite editor.',0,10)
 print('And to the console also.',0,20)
end

```
This is the same as above written in Javascript. Make sure your script [cartridge metadata](https://github.com/nesbox/TIC-80/wiki#cartridge-metadata) is set to `// script: js`
``` javascript
// javascript demo peek/poke

// use poke to create a sprite from a hexadecimal data string
var img="0a0000a00a0ff0a0aaaaaaaaaaafaaa6faffaaaaaaaf6aaaaaaaaaaa33333333"
// loop over one byte at a time
// remember that 2 hex digits is 1 byte
for(var i=0; i < 64; i=i+2) {
 //extract byte and convert into a hex string
 val=parseInt(img.substring(i,i+2), 16)
 //put the value into RAM at sprite number 4
 poke(0x4080+(i/2),val)
}

// read back the sprite data and print it to console
// this is a regular expression to find a single hex digit
var regHex=/^[0-9a-fA-F]{1}$/
var msg=''
// loop over sprite #4, one byte at a time
for (var i=0; i < 64; i=i+2) {
 //extract byte and convert it to a hexadecimal
 val=(peek(0x4080+(i/2))).toString(16)
 /*pad the string with the regular expression
   if needed, and concatenate it to the message */
 msg=msg+val.replace(regHex,'0'+val)
}

// print it to the console
trace(msg)
// add sprite to TIC cartridge
sync(0,0,true)

function TIC(){
 cls()
 print('Done.. have a look at the sprite editor.',0,10)
 print('And to the console also.',0,20)
}

```

### peek4 / poke4

```lua
-- title:   poke4/peek4 example
-- author:  paul59
-- script:  Lua

-- This example reads and writes into
-- sprite memory so we can see the
-- effect directly

-- Sprites are stored from address
-- 0x04000 onwards. Memory can be
-- addressed in 8 or 4 bit form so
-- we can access sprite memory as follows:

-- byte address  |  nibble address
--  0x04000      |  0x08000 (low nibble)
--               |  0x08001 (high nibble)
--  0x04001      |  0x08002 (low nibble)
--               |  0x08003 (high nibble)


-- write color 5 to first pixel of sprite 0
poke4(0x08000,5)
-- write color 10 to next pixel of sprite 0
poke4(0x08001,10)

function TIC()
	cls(0)

	-- display sprite 0
	spr(0,0,0)
        -- the two pixels set by our poke4
        -- commands are visible

        -- display the 8 bit value stored at 0x04000
	print(peek(0x04000),30,30,4)
	-- prints '165'
	-- ie value of 10 shifted left by 4
	-- into the high nibble (10<<4=160)
	-- plus 5 in the low nibble

	-- show our color values using
	-- 4 bit addressing
	print(peek4(0x08000),30,40,4)
	print(peek4(0x08001),30,50,4)
end

```

See also: [Spritesheet editing example](code-examples-and-snippets#setget-spritesheet-pixel) in the examples page