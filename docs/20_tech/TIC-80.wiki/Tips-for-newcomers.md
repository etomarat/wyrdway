People learn in different ways, and some enjoy finding things out on their own. This page aims to have the most important information everyone needs to begin well, a few tips that are easy to miss, not more.  
If you are new to programming, have a look at the [beginners tutorials](https://github.com/nesbox/TIC-80/wiki/tutorials#beginners-tutorials) instead.

## Display
TIC-80 has a native screen resolution of 240 pixels wide by 136 pixels tall. The screen origin is at top-left, with x coordinates running left to right and y coordinates from top to bottom.

![Display_axes](https://github.com/nesbox/TIC-80/assets/26139286/617db129-ce13-4521-872a-fbecb146b2bb)

## Console Commands
Here are some essential console commands:

```plaintext
`new lua`           Create a new cart using Lua (works with lua, python, ruby, js, moon, fennel, scheme, squirrel, wren, wasm, janet).
`save mycart`       Save and name the cart as "mycart" (Hotkey: CTRL+S).
`run`               Run the cart (Hotkey: CTRL+R/ENTER).
`folder`            Open the working directory in OS, where TIC files are saved.
`surf`              Open carts browser.
`eval`              Execute provided code.
```

[Find more console commands here.](https://github.com/nesbox/TIC-80/wiki/Console)

#### Example of `eval` Usage
To log the results use [trace](trace):

```bash
>eval trace("Floor division of 32 by 10 is "..32//10)
Floor division of 32 by 10 is 3
```

**Note**: Run a cart first to launch the virtual machine; otherwise, `eval` will output an empty string no matter what you do.

## Code
It is good practice to start cartridges by the [metadata](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata) tags. In particular, the `script` tag is required when another language than Lua is used for the virtual machine to know.  

At the core of every game is a loop that updates the game and renders new frames. In TIC-80, this is managed by the `TIC()` function:

```lua
-- # Metadata Tags:
-- title:   game title
-- author:  game developer, email, etc.
-- script:  lua --required to run cart

-- # Code outside TIC() runs once at program start.
-- Declare variables, functions, initialize

function TIC()
    -- # Code inside TIC() runs ~60 times per second.
    -- Handle inputs, update game state

    cls() -- Clear the screen
    -- Render graphics, characters, objects, backgrounds, etc.
end
```
**Note**: Not clearing the screen at every frame can result in [annoying artifacts](https://github.com/nesbox/TIC-80/issues/1911).

#### Debugging
Use [trace](https://github.com/nesbox/TIC-80/wiki/trace) in your code for debugging:
```lua
trace("x = "..x) -- Prints the value of x to the console
```

![trace_debugging_example](https://github.com/nesbox/TIC-80/assets/26139286/a0d2129e-89af-42f6-b3a1-44d460a20c15)

## Hotkeys
Useful hotkeys:

```plaintext
ESC                 Switch between console/editor or open menu while in-game.
ESC+F1              Switch to editor while in-game.
F1/F2/F3/F4/F5      Show code/sprite/map/sfx/music editor.
CTRL+R/ENTER        Run cart.
CTRL+S              Save cart.
CTRL+O              In code editor: show and navigate outline of code. One of the best ways to navigate through code in TIC-80.
```

![outline](https://github.com/nesbox/TIC-80/assets/26139286/b95fd503-4cfa-4dee-b46e-42672f264ff3)


[Find more hotkeys here.](https://github.com/nesbox/TIC-80/wiki/Hotkeys)

## Resources
Explore TIC-80 on the [wiki](https://github.com/nesbox/TIC-80/wiki), along with several [tutorials](https://github.com/nesbox/TIC-80/wiki/tutorials). Additionally, you can use the `help` command in the console.  

![help_example](https://github.com/nesbox/TIC-80/assets/26139286/0ad70564-b389-4a29-974a-29e46497d2b2)

You can start by learning about [print](https://github.com/nesbox/TIC-80/wiki/print), [spr](https://github.com/nesbox/TIC-80/wiki/spr), and [btn](https://github.com/nesbox/TIC-80/wiki/btn) to understand the [Hello World cartridge](https://github.com/nesbox/TIC-80/wiki/hello-world).

If you struggle to find something on the wiki use github search bar with "Wikis" filter.

![Capture d’écran du 2023-10-25 13-18-29](https://github.com/nesbox/TIC-80/assets/26139286/fc975754-882e-408c-b5bd-f9068698e528)

### Questions
If you have specific questions, you can find assistance on the [discord](https://discord.gg/HwZDw7n4dN), which is an active community, or on [telegram](https://t.me/tic80), [itch.io](https://nesbox.itch.io/tic80/community) and [github](https://github.com/nesbox/TIC-80/discussions).

### Lua
To quickly grasp the basics of Lua, [this tutorial](https://tylerneylon.com/a/learn-lua/) serves as an excellent introduction, if you already know programming.  
**Note**: `%` is modulo and `//` floor division.

### Cheatsheet
Here is a [cheatsheet by Skye Waddell](https://skyelynwaddell.github.io/tic80-manual-cheatsheet/).
