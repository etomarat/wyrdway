_This was added to the API in version 1.00._

The **BOOT** function is called a single time when your cartridge is booted. It should be used for startup/initialization code.  For scripting languages that allow code in the global scope (Lua, etc.) using `BOOT` is preferred rather than including source code in the global scope. 

``` lua
-- script: lua
function BOOT()
  -- Put your bootup code here
end
```

## Examples in other languages


``` moonscript
-- script: moon
export BOOT=->
  -- Put your stuff here
```

``` js
// script: js
function BOOT() {
  // Put your stuff here
}
```

```js
// script: wren
class Game is TIC {
  construct new() {
  }
  BOOT(){
    // Put your stuff here
  }
}
```

``` fennel
;; script: fennel
(global TIC
  (fn boot []
    ;; Put your stuff here
  )
)


;;alternate fennel
(var t 0)
(fn _G.BOOT []
  ;; use for init stuff
  (set t 100))

(fn _G.TIC []
  (print t))
```

``` squirrel
// script: squirrel
function BOOT() {
  // Put your stuff here
}
```

``` ruby
# script: ruby
def BOOT
  # Put your stuff here
end
```

```janet
# script: janet
(var t 0)
(defn BOOT
  # put your stuff here
  (set t 10))
```

``` python
# script: python
def BOOT():
  # Put your code here
```