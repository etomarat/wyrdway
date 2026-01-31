`keyp([code, [hold period]]) -> pressed`

## Parameters
* **code** : the key code we want to check (1..65) (see codes [here](https://github.com/nesbox/TIC-80/wiki/key#parameters))
* **hold** : time in ticks before autorepeat
* **period** : time in ticks for autorepeat interval

## Returns

* **pressed** : key is pressed (true/false)

## Description

This function returns `true` if the given key is pressed but wasn't pressed in the previous frame. If no keycode is specified, it will return `true` if any key is pressed but wasn't in the previous frame. Refer to [btnp](btnp) for an explanation of the optional **hold** and **period** parameters.

## Input Tag
Set the [metadata](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata#the-input-tag) `input` tag to `keyboard` to display only the on-screen keyboard on Android devices and hide the gamepad.

## Example

``` lua
-- title:  text input example
-- author: nesbox

function gets()
	A="abcdefghijklmnopqrstuvwxyz0123456789-=[]\\;'`,./ "
	S="ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*(_+{}|:\"~<>? "
	for i=0,3 do
		local c=peek(0xff88+i)
		if c>0 and c<=#A and keyp(c,20,3) then
			return key(64)and S:sub(c,c)or A:sub(c,c)
		end
	end
	return nil
end

input="Enter text:"

function TIC()
	c=gets()
	if c then input=input..c end
	cls()
	print(input)
end
```