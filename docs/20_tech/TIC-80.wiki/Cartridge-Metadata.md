Metadata is simply a small block of tagged comments that provides additional information to TIC-80.  It's good practice to declare metadata at the  very top of your source code.  
The `script` tag is **required** to run the cart, the virtual machine needs to know the programming language. If not specified, Lua will be used.  

Example:

```lua
-- title:  Worm
-- author: Bob Brown
-- desc:   A Clone of the classic Snake
-- script: lua

-- rest of your program goes here
```

_Note:_ If your code is in an external file, **dofile** must be placed in the very first line, **before** the metadata. (`dofile` is deprecated as of 0.80)


The full list of metadata tags:

``` lua
-- title:  game title                     -- The name of the cart.
-- author: game developer                 -- The name of the developer.
-- desc:   short description              -- Optional description of the game.
-- script: lua (or moon/wren/js/fennel)   -- Identifies the scripting language used; Lua is the default and most commonly used for TC-80 development.
-- input:  gamepad (or mouse or keyboard) -- Selects gamepad, mouse or keyboard input source. All input types are enabled by default.
-- saveid: MyAwesomeGame                  -- Allows save data to be shared within multiple games on a copy of TIC.
```

### The `title` and `author` Tags

The `title` and `author` tags (as well as a [cover image](https://github.com/nesbox/TIC-80/wiki/Cover-image)) are **required** for uploading to the official [website](tic80.com).

### The `desc` Tags

Should include a short description of your game.

### The `script` Tag

It is required to run the cart, the virtual machine needs to know the programming language. If not specified, Lua will be used.  
You can use any of the other scripting languages that TIC-80 supports by adding one the following to the metadata:

| Language       | Tag                   |
|----------------|-----------------------|
| For Fennel     | `;; script: fennel`   |
| For Javascript | `// script: js`       |
| For Lua        | `-- script: lua`      |
| For Moonscript | `-- script: moon`     |
| For Ruby       | `# script:  ruby`     |
| For Squirrel   | `// script: squirrel` |
| For Wren       | `// script: wren`     |
| For Janet      | `# script: janet`     |
| For Scheme     | `;; script:  scheme`  |
| For Python     | `# script: python`    |

### The `input` Tag

The `input` tag can be set to `gamepad` or `keyboard` to display only the on-screen gamepad or keyboard on Android devices. To disable them use `mouse`. The `gamepad` and `keyboard` tags will also hide the mouse pointer. If no `input` tag is set, both the gamepad and keyboard can be displayed on Android depending on the screen orientation.  
Note that this tag does not affect the ability to use [mouse](https://github.com/nesbox/TIC-80/wiki/mouse), [btn](https://github.com/nesbox/TIC-80/wiki/btn) or [key](https://github.com/nesbox/TIC-80/wiki/key) functions, a code with `--input: mouse` but using [key](https://github.com/nesbox/TIC-80/wiki/key) will work except for Android users relying on the on-screen keyboard.

### The `saveid` Tag

It's highly recommended if using [pmem](pmem) to use a unique `saveid`.  This will allow your cartridge's
persistent memory to persist even if you are still continuing to edit the code.  Otherwise a `saveid`
will be generated for you based on a MD5 hash of your code.

### The `menu` Tag

You can define Game Menu items using the `-- menu: ITEM1 ITEM2 ITEM3` tag and handle them in the `MENU(index)` callback.  
The game menu is a sub-menu of the [TIC-80 menu](https://github.com/nesbox/TIC-80/wiki/TIC%E2%80%9080-Menu), they should not be confused.  

More details in the [MENU](MENU) page.  

### The Fennel `strict` Tag

[TODO](https://github.com/nesbox/TIC-80/pull/1653)