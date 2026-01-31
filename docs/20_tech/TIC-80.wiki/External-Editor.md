### Version 0.80 and later (PRO feature)
This is a feature of the **[PRO version](PRO-Version)**.  
As of version 0.80, you can save (and load) your game directly as a Lua (or other script) file rather than a *.tic cart, for example:

`save mygame.lua`

The saved file will include your code and at the end, all resources (sprites, sfx etc) within XML-style tags. Care should be taken to avoid manually editing this data (unless intentionally required). TIC will automatically re-load any changes in the script file.

A typical workflow might be:
* Create sprites, map, sfx and music in TIC's various resource editors and save in lua format from the console eg `save mygame.lua`
* Open mygame.lua in your editor of choice; the resources created in the previous step will appear within XML style tags at the end of the file. Add your code **at the top** of the file.
* If TIC is open, it will detect changes to the file whenever it's saved and automatically reload it. Switch to TIC to run your game or edit resources.
* If TIC is not open, start it and use `load mygame.lua` to load your code and resources to further edit or run your game.

To avoid losing work, care should be taken to avoid making unsaved changes in an external editor and within TIC's resource editors at the same time!

### Versions prior to 0.80:

There are two methods by which you can run code from an external Lua file:
1. add `dofile('game.lua')` as the first line of the built-in editor and place `game.lua` in the correct location:
  * For Windows, the file should be in the same folder as your executable.
  * For Unix/Linux it should be in the directory from which you started the `tic` binary.
  * For Android you need to specify the full path to your Lua file. For example, `dofile('/sdcard/game.lua')`.
2.  use `tic cart.tic -code game.lua` [command line parameters](#command-line-arguments) to inject your code to the cartridge



### Extensions/packages for text editors

* Visual Studio Code

  * [Visual Studio Code extension](https://marketplace.visualstudio.com/items?itemName=Gi972.tic80-vscode) for TIC-80 made by [@Gi972](https://github.com/Gi972)
  * [VSCode Extension for TIC-80 Pro Users](https://marketplace.visualstudio.com/items?itemName=justinwash.tic80-pro-vscode) made by [@Trifectuh](https://github.com/Trifectuh), forked from Gi972's extension above.
  * [API user snippets for Visual Studio Code](https://gist.github.com/Viza74/40a180155049dd26af378f51a92b6033) made by [@Viza74](https://github.com/Viza74)
  * [Visual Studio Code settings for TIC-80 game developers](https://github.com/AlRado/Visual-Code-TIC-80) - settings, user snippets, docs. Made by [@AlRado](https://github.com/AlRado)

* Sublime Text

  * [Sublime Text 3 package](https://github.com/AlRado/Sublime-TIC-80) - Syntax highlighting and auto-complete TIC-80 functions in Sublime Text. By [@AlRado](https://github.com/AlRado)

* Atom

  * [TIC-80 package for Atom Editor](https://github.com/ViChyavIn/atom-tic80/) with tools to edit/run games, terminal that duplicates TIC's console output, some handy snippets, datatips and autocompletion feature for TIC's API. Also, includes some syntax highlighting. Made by [@ViChyavIn](https://github.com/ViChyavIn/)

* Geany

  * [Config files](https://github.com/paul59/TIC-80-Geany-Syntax-Highlighting) by [@paul59](https://github.com/paul59/) to enable syntax highlighting in the lightweight programmer's editor [Geany](https://www.geany.org/)