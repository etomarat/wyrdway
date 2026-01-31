# Text Only Game

A simple text only game. Similar to those early 80's basic games for Atari or Commondore 64. This is a simple `key` and `keyp` demostration.

```lua
-- title:  console.tic
-- author: clsource, simplified by joshgoebel
-- desc:   simple game with text input
-- script: lua


input = {
  buffer = "",
  rows = {},
  codes = {
    enter = 50,
    backspace = 51,
    shift = 64,
    capslock = 62,
    lbracket = 39,
    rbracket = 40,
    comma = 45,
    period = 46,
    space = 48,
    tab = 49,
    equals = 38,
    ctrl = 63
  }
}

keys = input.codes

function input:bufferReset()
    input.buffer = ""
end

function input:rowsReset()
    input.rows = {}
end

function input:reset()
  trace("console: buffer reset")
    input.bufferReset()
    input.rowsReset()
end

function input:getkey()

  local letter = nil

  -- loop to handle the easy cases: A to Z, 0 to 9
  for i = 1,36 do
    if(keyp(i)) then
      if i <= 26 then -- letter
        letter = string.char(i+97-1) -- 65 is `a` in ascii
      else -- number
        letter = string.char(i-26+48-1) -- 48 is `0` in ascii
      end
      return letter
    end
  end

  if(keyp(keys.space)) then
    letter = " "
  elseif(keyp(keys.tab)) then
    letter = "	"
  elseif(keyp(keys.comma)) then
    letter = ","
  elseif(keyp(keys.period)) then
    letter = "."
  elseif(keyp(keys.lbracket)) then
    letter = "["
  elseif(keyp(keys.rbracket)) then
    letter = "]"
  elseif(keyp(keys.equals)) then
    letter = "="
  end

  return letter
end

function input:read()
  local letter = input:getkey()

  if (letter) then
    if(key(keys.shift) or key(keys.capslock)) then
      letter = string.upper(letter)
    end
    input.buffer = input.buffer ..letter
  end

  -- enter
  if(keyp(keys.enter)) then
    if(#input.rows > 100) then
      input:reset()
    end
    if(#input.buffer > 0) then
     trace("console: " ..input.buffer)
      table.insert(input.rows,input.buffer)
      input:bufferReset()
    end
  end

  -- backspace
  if(keyp(keys.backspace)) then
    input.buffer = input.buffer:sub(1,-2)
  end

  if(key(keys.ctrl)) then
    if(key(keys.backspace)) then
      input:reset()
    end
  end

end

function input:history(reverse)
  local out = ""
  local value = ""
  local index = 1

  -- most recent first
  if(reverse) then
    for index = #input.rows, 1, -1 do
      value = input.rows[index]
      out = out .." " ..index .." " ..value .."\n"
    end

    return out
  end

  for index = 1, #input.rows do
    value = input.rows[index]
    out = out  .." " ..value .."\n"
  end

  return out
end

function input:log(reverse)
  return input:history(reverse)
end

function input:last()
  local rows = input.rows
  return rows[#rows] or ""
end

function input:draw(params)
  params = params or {}
  local x = params.x or 4
  local y = params.y or 120
  local color = params.color or 11

  print(input.buffer, x, y)
  if(time() % 800 > 400) then
    -- draw the cursor blink
    local length = #input.buffer * 8

    local cursor = #input.buffer * 2

    local deltaX = x + length - cursor

    rect(
      deltaX,
      y,
      7,
      6,
      color
    )
  end
end

function input:text(params)
  input:read()
  local draw = true
  if(params) then
   draw = params.draw
  end

  if(draw) then
    input:draw(params)
  end
  return input:last()
end

function TIC()
  cls(0)

  print("Hello What's your name?", 4, 8, 11)

  name = input:text()
  if not (name == "") then
    print("Hello " ..name, 4, 24, 11)
  end

  rectb(0, 0, 240, 100, 8)
  rectb(0, 110, 240, 25, 8)
end
```
