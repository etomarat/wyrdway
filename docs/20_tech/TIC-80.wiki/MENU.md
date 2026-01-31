You can define Game Menu items using the `-- menu: ITEM1 ITEM2 ITEM3` [metatag](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata) and handle them in the `MENU(index)` callback.  
Note that MENU indexing starts at 0.  

The Game Menu is a sub-menu of the [TIC-80 Menu](https://github.com/nesbox/TIC-80/wiki/TIC%E2%80%9080-Menu).

## Notes 

- To add **spacebar** in the item name, use Tab (`-- menu: ITEM<Tab>1 ITEM<Tab>2 ITEM<Tab>3`) like in example below.
- You cannot edit permanent memory with `pmem` from the `MENU` callback. Set a temporary variable instead and do the `pmem` calls inside `TIC`.

## Example

![menu_demo](https://github.com/nesbox/TIC-80/assets/26139286/e11644f5-66b2-473a-8fdb-cdb13fbb329c)

```lua
-- menu: ITEM	1 ITEM	2 ITEM	3

function ITEM1()trace("Item 1")end
function ITEM2()trace("Item 2")end
function ITEM3()trace("Item 3")end

GameMenu={ITEM1,ITEM2,ITEM3}

function MENU(i)
 GameMenu[i+1]()
end

function TIC()
	cls(13)
	print("HELLO WORLD!",84,84)
end
```