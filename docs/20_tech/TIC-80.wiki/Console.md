![console_example](https://github.com/nesbox/TIC-80/assets/26139286/64797a31-06a0-499e-a315-9f049e0fa9a4)

## Available Commands

#### Cart Editing

| Command  | Description                                          | Usage                                                       |
|----------|------------------------------------------------------|-------------------------------------------------------------|
| `new`    | Creates a new [Hello World cartridge](hello-world).  | `new  < lua \| python \| ruby \| js \| moon \| fennel \| scheme \| squirrel \| wren \| wasm \| janet >` |
| `load`   | [Load](https://github.com/nesbox/TIC-80/wiki/load) cartridge <cart> from the local filesystem (there's no need to type the .tic extension). You can also load just the data (sprites, map etc) from another cart. | `load <cart> [ code \| tiles \| sprites \| map \| sfx \| music \| palette \| flags \| screen ]` |
| `save`   | [Save](https://github.com/nesbox/TIC-80/wiki/save) cartridge <cart> to the local filesystem, use `.lua .py .rb .js .moon .fnl .nut .wren .wasmp` cart extension to save it in text format to use an [external editor](https://github.com/nesbox/TIC-80/wiki/External-Editor) **[[PRO version](PRO-Version)]**. Use `.png` to save it in a png cartridge. | `save <cart>` |
| `edit`   | Switches to the code editor.                         | `edit`                                                      |
| `run`    | Run current project.                                 | `run`                                                       |
| `resume` | Resume last loaded project. Accepts [reload](Reload) argument in 1.2 or later. | `resume [reload]`                   |
| `import` | [Import](https://github.com/nesbox/TIC-80/wiki/import) code/images from an external file. See [Importing Images](#importing-images). Use `load` to import code/sprites/music/… from another cart. | `import [ binary \| tiles \| sprites \| map \| code \| screen] <file> [bank=0 x=0 y=0 w=0 h=0 vbank=0]` |
| `eval` / `=` | Run code. See [Evaluating Code](#evaluating-code). | `eval` / `=`                                              |

#### File System interaction
| Command      | Description                                       | Usage                                                             |
|--------------|---------------------------------------------------|-------------------------------------------------------------------|
| `dir` / `ls` | Show list of local files.                         | `dir` / `ls`                                                      |
| `mkdir`      | Make directory.                                   | `mkdir`                                                           |
| `cd`         | Change directory.                                 | `cd`                                                              |
| `del`        | Delete <file> from the filesystem.                | `del <file>`                                                      |
| `folder`     | Open working directory in OS (Windows, Linux, Mac OS). | `folder`                                                     |
| `add`        | Show file open dialog to add file to TIC [browser version]. | `add`                                                   |
| `get`        | Show file save dialog to download file [browser version]. Save the cart first if you don't find the file. | `get <file>` |
| `export`     | [Export](https://github.com/nesbox/TIC-80/wiki/export) currently loaded cart to HTML or as a native build, export sprites or cover as image, or export sfx and music to wav files (0.80), export help in a markdown file. `<outfile>` argument is the output file name. Use `alone=1` to export the game without the editors **[[PRO version](PRO-Version)]**. | `export [ win \| winxp \| linux \| rpi \| mac \| html \| binary \| tiles \| sprites \| map \| mapimg \| sfx \| music \| screen \| help] <outfile> [bank=0 vbank=0 id=0 alone=0]` |


#### Miscellaneous

| Command         | Description                                       | Usage                                                             |
|-----------------|---------------------------------------------------|-------------------------------------------------------------------|
| `help`          | Show current version, welcome message, specs, 80K [RAM](RAM) layout, 16K [VRAM](RAM#vram) layout, list of available commands, api commands, keys, buttons and their corresponding codes, startup options, terms, license. | `help [<text> \| version \| welcome \| spec \| ram \| vram \| commands \| api \| keys \| buttons \| startup \| terms \| license]` |
| `config`        | Show **[config](https://github.com/nesbox/TIC-80/wiki/config)** file editor when used without parameter, use **reset** param to reset current configuration, use **default** to [edit default cart template](https://github.com/nesbox/TIC-80/wiki/Hello-World#edit-hello-world-template). | `config [reset \| default]` |
| `menu`          | Show [menu](https://github.com/nesbox/TIC-80/wiki/TIC%E2%80%9080-Menu) where you can setup keyboard/gamepad buttons mapping, change editor options and much more. | `menu`                                       |
| `surf`          | Open carts [browser](https://github.com/nesbox/TIC-80/wiki/surf).        | `surf`                                                            |
| `cls` / `clear` | Clear screen.                                     | `cls` / `clear`                                                   |
| `exit` / `quit` | Exit the application.                             | `exit` / `quit`                                                   |
| `demo`          | Install demo carts.                               | `demo`                                                            |

For those operating systems that support it, tab completion and command history is available in the console.

## Evaluating Code

Example of `eval` usage.  
To log the results use [trace](trace).  
*Note* that you need to run a cart first to launch the virtual machine, otherwise you'll get an empty string whatever you do.

```
> eval trace("Hello World")
Hello World
> eval t=8

> eval trace(t%3)
2
```

## Importing Images
Put your file to import in the `TIC-80/` folder and not the folder where your exe file is. Find the `TIC-80` folder by typing `folder` in the console.

While importing images, colors are merged to the closest color of the palette.  
For example, with default palette, this image:  

![easter](https://github.com/nesbox/TIC-80/assets/26139286/a317730e-0f5d-44c0-8ef3-5790314f0d42)  

becomes:  

![import_screenshot](https://github.com/nesbox/TIC-80/assets/26139286/24a08632-2ce5-4ea2-b35a-3e8a1533083e)

Note that if the palette is all black (like default bank1) the imported image will be all black.