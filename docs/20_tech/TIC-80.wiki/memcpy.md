`memcpy(to, from, length)`

## Parameters

* **to** : the address you want to write to
* **from** : the address you want to copy from
* **length** : the length of the memory block you want to copy (in bytes)

## Description

This function copies a continuous block of [RAM](RAM) from one address to another.
Addresses are specified in hexadecimal format, values are decimal.

## Example

![Example](https://imgur.com/azJq4Ak.png)

``` lua
-- demo memcpy
function TIC()
	cls()

	-- draw something to the screen
	for y=1,16 do
		line(0,y,240,y,y-1)
	end

	-- copy the drawing to an another place a couple of times
	for i=1,4 do
		memcpy((i*28)*120, 0x0000, 2400)
	end

end
```