`trace(message, [color=15])`

## Parameters

* **message** : the string to print.
* **color** : a color index (0..15)

## Description

This is a service function, useful for debugging. It prints the supplied string or variable to the [console](console) in the (optional) color specified.

_Tips:_

1. The Lua concatenation operator is `..` (two periods)
2. Use the console [cls](cls) command to clear the output from trace
3. Simple variables are automatically converted to strings

## Example

![Example](https://i.imgur.com/Pk31XXa.png)

``` lua
-- trace demo
cls()
function TIC()
	trace('Hello console:'..time())
	trace('This text is blue',8)
end
```

GIF example:

![trace_debugging_example](https://github.com/nesbox/TIC-80/assets/26139286/a0d2129e-89af-42f6-b3a1-44d460a20c15)