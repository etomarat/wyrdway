Since version 1.2, the `resume` command can take an optional `reload`
argument which causes the code of the cart to be reloaded before
resuming the game.

This can be very useful during development; for instance if you
encounter a bug in your game that is difficult to reproduce, you can
pause the game, try to fix the bug, and `resume reload` to check to
see whether your bug fix actually worked. Or you can add `trace`
logging without starting your whole game over from the start.

### Gotchas

However, you will have to make a few changes to how your game
initializes in order to take advantage of this. For example, if you
store your game state in a `state` table, you can't do this:

```lua
local state = {x=64, y=128, shots={}, enemies={}}
for _=1,8 do table.insert(state.enemies, make_enemy()) end
```

If you do this, then the reload will replace your game state with a
newly-initialized `state` table, wiping out your original game
state. A reload-friendly approach would look more like this:

```
local state
if _G.state then
  state = _G.state
else
  state = {x=64, y=128, shots={}, enemies={}}
  for _=1,8 do table.insert(state.enemies, make_enemy()) end
  _G.state = state
end
```

Note that this is much easier if you put all your state in one table!
If you have state in multiple places, then they'd all need independent
checks for initialization, which is more error-prone.

If you have tables in your state table that have methods, they will
still have the old versions in them unless you update them yourself.

### Globals (in Lua and Lua-based languages)

The above example uses a single global as a "storage location" to
allow state to survive reloads. It also makes game state available to
the `eval` command for debugging from the console.

Of course, it's nice to reduce your use of globals as much as
possible, but there is an inherent tension between avoiding globals
and accommodating debugging , so having a single `_G.state` global
strikes a good compromise.

Of course, if you don't worry about it and use globals wherever you
feel like it, that's valid too, as long as you take care with 
initialization; for example:

```lua
if state == nil then
  state = {x=64, y=128, shots={}, enemies={}}
  for _=1,8 do table.insert(state.enemies, make_enemy()) end
end
```

This will make linters less useful for catching mistakes, but it's
less typing.