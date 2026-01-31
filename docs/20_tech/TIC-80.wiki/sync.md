`sync([mask=0], [bank=0], [tocart=false])`

The [PRO version](PRO-Version) of TIC-80 contains 8 memory banks. For more information, see [bankswitching](Bankswitching). To switch between these banks, `sync` can be used to either load contents from a memory bank to runtime, or save contents from the active runtime to a bank. The function can only be called once per frame.

## Parameters
* **mask** : mask of sections you want to switch:
``` lua
tiles   = 1<<0 -- 1
sprites = 1<<1 -- 2
map     = 1<<2 -- 4
sfx     = 1<<3 -- 8
music   = 1<<4 -- 16
palette = 1<<5 -- 32
flags   = 1<<6 -- 64
screen  = 1<<7 -- 128 (as of 0.90)
```

`0` - will switch all the sections
`1 | 2 | 4` - will switch only `TILES`, `SPRITES` and `MAP` sections, for example

* **bank** : memory bank (0..7)
* **tocart** : `true` - save memory from runtime to bank/cartridge, `false` - load data from bank/cartridge to runtime.

## Description

Use `sync()` to save data you modify during runtime and would like to persist, or to restore runtime data from the cartridge.  For example, if you have manipulated the runtime memory (e.g. by using [mset](mset)), you can reset the active state by calling `sync(0,0,false)`. This resets the whole of runtime memory to the contents of bank 0.

Note that `sync` is never used to load _code_ from banks; this is done automatically.  All data is restored from cartridge on every startup.

_Note:_ In older versions of TIC-80, calling `sync` was not required to save runtime map and sprite data. Sync should be called any time changes to the sprites and map are made during runtime if you'd like the changes to be applied.


---

## Prior to 0.60

### sync
`sync [tocart=true]`

### Parameters
* **tocart** : `true` - save sprites/map/sound from runtime to cart, `false` - to restore data from cart (can be useful to reset all the data)

## Example
`sync(128,0,true)` will add the current screen as [cover image](https://github.com/nesbox/TIC-80/wiki/Cover-image).
