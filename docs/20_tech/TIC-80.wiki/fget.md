_This function was added to the API in version 0.80._

`fget(sprite_id, flag) -> bool`


## Parameters

* **sprite_id** : sprite index (0..511)
* **flag** : flag index to check (0..7)


## Returns

* whether the flag was set (true/false)


## Description

Returns `true` if the specified flag of the sprite is set. Each sprite has eight flags which can be used to store information or signal different conditions. For example, flag 0 might be used to indicate that the sprite is invisible, flag 6 might indicate that the sprite should be drawn scaled etc.

To set the value of sprite flags, see [fset](https://github.com/nesbox/TIC-80/wiki/fset) or the [sprite editor advanced mode](https://github.com/nesbox/TIC-80/wiki/Sprite-editor#advanced-mode).

See also:

* [fset](fset) (0.80)