_This was added to the API in version 0.60._

`reset()`

Resets the TIC virtual "hardware" and immediately restarts the cartridge.

To simply return to the console, please use [exit](https://github.com/nesbox/TIC-80/wiki/exit).

See also:

- [exit](exit)

## Example

```lua
-- title:  reset API Command Demo (Lua)
-- author: StinkerB06
t=0
function TIC()
  if btn(4) then reset() end
  cls()
  print("Press Z to reset counter.",1,1)
  print(t,1,8)
  t=t+1
end
```