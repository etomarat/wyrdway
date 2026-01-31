`exit()`

This function causes program execution to be terminated **after** the current `TIC` function ends. The entire function is executed, including any code that follows `exit()`. When the program ends you are returned to the [console](console).

See the example below for a demonstration of this behavior.


## Example

![Example](https://imgur.com/67HwOmp.gif)

```lua
-- title:  exit API Command Demo (Lua)
-- author: StinkerB06

function TIC()
  cls(0)
  print("Press Z to exit to console.",1,1)
  if btn(4) then
    exit()
    trace("This code still runs!")
  end
end
```