- `btnp(id, [hold], [period]) -> is_pressed`
- `btnp() -> GAMEPADS data`

## Parameters
* **id** : the id (0..31) of the button we wish to interrogate - see the [key map](key-map) for reference
* **hold** : the time (in ticks) the button must be pressed before re-checking
* **period** : the amount of time (in ticks) after **hold** before this function will return `true` again.

## Returns
* **is_pressed** : button is pressed now but not in previous frame (true/false)
* **GAMEPADS data** : 32-bit value that represents a bitwise AND of the current and prior state of GAMEPADS data (see [RAM](RAM)).  Ie, a bitmask of buttons that were released in the prior frame yet currently held.

## Description
This function allows you to read the status of one of TIC's buttons. It returns `true` only if the key has been pressed since the last frame.

You can also use the optional **hold** and **period** parameters which allow you to check if a button is being held down. After the time specified by **hold** has elapsed, btnp will return *true* each time **period** is passed if the key is still down. For example, to re-examine the state of button '0' after 2 seconds and continue to check its state every 1/10th of a second, you would use btnp(0, 120, 6). Since time is expressed in ticks and TIC runs at 60 frames per second, we use the value of 120 to wait 2 seconds and 6 ticks (ie 60/10) as the interval for re-checking.

## Input Tag
Set the [metadata](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata#the-input-tag) `input` tag to `gamepad` to display only the on-screen gamepad on Android devices and hide the keyboard.

## Example

![Example](https://imgur.com/jo323fP.gif)

``` lua
-- btnp demo: move the rectangle in 10 pixels step,
-- every time one direction keys is pressed.
-- Keep the key pressed for more than 1 second to have
-- the rectangle move every tenth of seconds.

x=120
y=80

cls(12)
function TIC()

    if btnp(0,60,6) then y=y-10 end
    if btnp(1,60,6) then y=y+10 end
    if btnp(2,60,6) then x=x-10 end
    if btnp(3,60,6) then x=x+10 end

    rect(x,y,10,10,8)
end
```
