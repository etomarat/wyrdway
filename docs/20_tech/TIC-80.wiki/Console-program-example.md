Using co-routines we can make a console simulation, accepting user input.
 

```lua
-- example imperative console program

function program()
   console.print("Hoeveel spelers?")
   local count=console.read()
   for i = 1,count do
      local name
      while true do
         console.newline()
         console.print("Speler " .. i .. "?")
         name=console.read()
         if (string.len(name)<2) then
            console.print("(minstens 2 letters)")
         else
            break
         end
      end

      console.print("Dag " .. name .. "!")
      console.newline()
   end
end

-- library functions below: just copy this part

local main=coroutine.create(function()
  cls()
  program()
  -- when program is done, stick here
  coroutine.yield(wait,"wait")
end)

local wait=coroutine.create(function()
  -- never actually resumed
end)

local input=coroutine.create(function()
  while true do
    console.newline()
    console.input=true
    coroutine.yield(wait,"wait")
  end
end)

local r,n=main,"main"

function TIC()
   while (not (n == "wait")) do
      s,r,n=coroutine.resume(r)
      trace(n)
   end
   r,n=console.run()
end

console = {
   x=0,
   y=0,
   h=6, -- row height in pixels
   r=120//6, -- number of rows
   line="",
   input=false,
   log={}
}

function console.run()
   if (console.input) then
      local c=getc()
      if (c)
      then
         rect(console.x,console.y,6,6,0)
         if (c=="enter")
         then
            console.input=false
            return main,"main"
         elseif c=="backspace" then
            local del=console.line:sub(#console.line,#console.line)
            local width=print(del,0,200)
            console.x=console.x-width
            rect(console.x,console.y,width,6,0)
            console.line=console.line:sub(1,#console.line-1)
         else
            console.print(c)
         end
         --console.status(console.x .. "," .. console.y .. " " .. console.line)
      end
      local color=6
      rect(console.x,console.y,6,6,color)
   end
   return wait,"wait"
end

function console.newline()
   table.insert(console.log,console.line)
   console.line=""
   console.x=0
   console.y=console.y+console.h
   if (console.y >= console.h*console.r) then
      rect(0,0,240,console.h*console.r,0)
      local offset=#console.log-console.r+2
      for i=1,console.r-2 do
         print(console.log[i+offset],0,i*console.h)
      end
      console.y=console.h*(console.r-1)
   end
end

function console.print(c)
   console.line = console.line .. c
   local width=print(c,console.x,console.y)
   console.x=console.x+width
end

function console.read()
   coroutine.yield(input,"input")
   local line=console.line
   console.newline()
   return line
end

function console.status(text)
   rect(0,120,240,128,1)
   print(text,0,120)
   print(#console.log,0,128)
end

keys = {
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

function getc()

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
   elseif(keyp(keys.enter)) then
      letter = "enter"
   elseif(keyp(keys.backspace)) then
      letter = "backspace"
   end

   return letter
end
```