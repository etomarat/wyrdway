# init

TIC's core API does not include any type of initialization function that is called a single time when your cartridge is first started.  Luckily, it's very easy to add this yourself:


```lua
function init()
   --init your stuff here
    t=0
end

-- executed only once
init()

-- executed 60 times every second
function TIC()
    cls(12)
    print("HELLO WORLD!",84,64)
    t=t+1
end
```

Basically it's enough to define a function (with the name you prefer), and call it outside your `TIC` function.