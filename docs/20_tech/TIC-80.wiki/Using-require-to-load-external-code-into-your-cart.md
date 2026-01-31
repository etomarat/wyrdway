If you like to break out your source code into separate files during development you can use the Lua require function to import the code. Using the module example `mymath` from [Lua - Modules](https://www.tutorialspoint.com/lua/lua_modules.htm) we can do the following.

### Create our module
Below is the code for the module from the Lua website in `Lua` and `Fennel`
```lua
-- Lua module
local mymath =  {}

function mymath.add(a,b)
   print(a+b)
end

function mymath.sub(a,b)
   print(a-b)
end

function mymath.mul(a,b)
   print(a*b)
end

function mymath.div(a,b)
   print(a/b)
end

return mymath
```

```fennel
;; Fennel module
(local mymath {})

(fn mymath.add [a b]
  (print (+ a b)))

(fn mymath.sub [a b]
  (print (- a b)))

(fn mymath.mul [a b]
  (print (* a b)))

(fn mymath.div [a b]
  (print (/ a b)))

mymath	
```

### Create our cart
We will use the demo cart here and just add some additional lines:
```lua
-- script:  lua

mymath = require("mymath")

t=0
x=96
y=24

function TIC()

	if btn(0) then y=y-1 end
	if btn(1) then y=y+1 end
	if btn(2) then x=x-1 end
	if btn(3) then x=x+1 end

	cls(13)
	spr(1+t%60//30*2,x,y,14,3,0,0,2,2)
	print("HELLO WORLD!",84,84)
        mymath.add(1,1) -- call the function from the module which will print the result to screen
	t=t+1
end


```


```fennel
;; script:  fennel
;; strict:  true

(local mymath (require "mymath"))	

(var t 0)
(var x 96)
(var y 24)

(fn _G.TIC []
  (when (btn 0) (set y (- y 1)))
  (when (btn 1) (set y (+ y 1)))
  (when (btn 2) (set x (- x 1)))
  (when (btn 3) (set x (+ x 1)))
  (cls 0)
  (spr (+ 1 (* (// (% t 60) 30) 2))
       x y 14 3 0 0 2 2)
  (print "HELLO WORLD!" 84 84)
  (mymath.add 1 1) ;; call the function from the module which will print the result to screen
  (set t (+ t 1)))
```

### Where to locate our module files?
* Open up `tic80` and at the console type `folder`. 
* This will show you where the tic80 data folder is.
* Create a folder inside this one named `lua`
* Place your `module.lua` or `module.fnl` file here. This is where tic80 looks for the files.

### Next?
Just run your cart now and you should see the `mymath.add` print the sum of the arguments you supplied

### Caveats
You need to have access to the external files for the cart to work. If tic80 can't find the files the cart will fail. For example if you export to Windows `.exe` you will need to make sure that you also supply the `lua` directory that includes your modules with the `.exe` file. You can't just ship the `.exe` alone. 

This may not be an issue for you but it is something to be aware of.

When sharing your cart, you could copy the contents of the files into your cart at the end, so its 1 giant cart.
