The **TIC** function is the 'main' update/draw callback and **must** be present in every program. It takes no parameters and is called sixty times per second (60fps).

``` lua
-- script: lua
function TIC()
  -- Put your update and draw code here
end
```

## Examples in other languages


``` moonscript
-- script: moon
export TIC=->
  -- Put your stuff here
```

``` js
// script: js
function TIC() {
  // Put your stuff here
}
```

```js
// script: wren
class Game is TIC {
  construct new() {
  }
  TIC(){
    // Put your stuff here
  }
}
```

``` fennel
;; script: fennel
(global TIC
  (fn tic []
    ;; Put your stuff here
  )
)
;; or alternate way
(fn _G.TIC []
 ;; Put your stuff here
)
```

``` squirrel
// script: squirrel
function TIC() {
  // Put your stuff here
}
```

``` ruby
# script: ruby
def TIC
  # Put your stuff here
end
```

```janet
# script: janet
(defn TIC 
  # put your stuff here
)
```

``` python
# script: python
def TIC():
  # Put your stuff here
