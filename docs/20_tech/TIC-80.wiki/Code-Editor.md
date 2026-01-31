![demo_code_editor_v1 1](https://github.com/nesbox/TIC-80/assets/26139286/a6663f6a-3ba6-41e9-932e-a62896906f75)

TIC-80 includes a powerful built-in code editor to assist with game development. It's entirely possible to design, code, and maintain a game without ever leaving the TIC-80 environment.

On top right of the code editor several buttons allow to:
* **Switch font**. The code editor uses two [fonts](https://github.com/nesbox/TIC-80/wiki/system-font) and allows to switch from the default larger font to the alternative smaller one.
* **Show shadow** of the font.
* **Run** cart (hotkey: CTRL+R).
* **Drag** tool.
* **Find** provided text.
* **Go to line** number provided.
* Show **Bookmark** list.
* Show code **Outline**.

## Custom Colors

Colors used in the code editor can be customized using the [configuration file](https://github.com/nesbox/TIC-80/wiki/config#color-parameters).

![config_color](https://github.com/nesbox/TIC-80/assets/26139286/392ea49d-d0ff-424c-a192-076448732435)

# Code Structure

It is good practice to start cartridges by the [metadata](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata) tags. In particular, the `script` tag is required when another language than Lua is used for the virtual machine to know.  

At the core of every game is a loop that updates the game and renders new frames. In TIC-80, this is managed by the `TIC()` function:

```lua
-- # Metadata Tags:
-- title:   game title
-- author:  game developer, email, etc.
-- script:  lua --required to run cart if not lua

-- # Code outside TIC() runs once at program start.
-- Declare variables, functions, initialize

function TIC()
    -- # Code inside TIC() runs ~60 times per second.
    -- Handle inputs, update game state

    cls() -- Clear the screen
    -- Render graphics, characters, objects, backgrounds, etc.
end
```
Look at the [Hello World cartridge](https://github.com/nesbox/TIC-80/wiki/Hello-World) as an example of TIC-80 code.

**Note**: Clearing the screen at every frame is not necessary but avoids [annoying artifacts](https://github.com/nesbox/TIC-80/issues/1911).

Please see [API Reference](API) for a full list of built-in functions or to download a quick function reference cheat sheet.

# Code Editor Hotkeys
```
CTRL+F                  Find.
CTRL+G                  Go to line.
CTRL+P/N                Move to previous/next line.
CTRL+F1                 Bookmark current line.
F1                      Move to next bookmark.
CTRL+B                  Show bookmark list.
CTRL+O                  Show code outline.
RIGHT CLICK             Drag.
CTRL+TAB                Indent line.
CTRL+SHIFT+TAB          Unindent line.
CTRL+/                  Comment/Uncomment line.
```
The [general hotkeys](https://github.com/nesbox/TIC-80/wiki/Hotkeys#general) are available in the code editor too.

# Using an External Editor

The [PRO version](PRO-Version) allows to use an [external editor](external-editor) to write your code, if that is your preference.
