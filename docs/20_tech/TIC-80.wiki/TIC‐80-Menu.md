`menu`  
or press ESC while in game (if DEV MODE is disabled).

# Description

![TIC80_menu_demo](https://github.com/nesbox/TIC-80/assets/26139286/a674d92d-92aa-4ee5-a42d-b41dcdcef123)

The TIC-80 menu is composed of the following options:

* **GAME MENU** is specific to the running game, it appears if the running game uses the [MENU](MENU) callback with `menu` tag in the [metadata](Cartridge-Metadata).
* **RESUME GAME**.
* **RESET GAME**.
* **CLOSE GAME** to switch to console. Note that instead of using CLOSE GAME you can switch from game to Code Editor using **ESC+F1** [hotkey](https://github.com/nesbox/TIC-80/wiki/Hotkeys#navigation).
* **OPTIONS** offer several configurations choices for TIC-80, detailed below.
* **QUIT TIC-80**.

## OPTIONS
* **CRT MONITOR** Turns on the CRT (cathode-Ray Tube) filter for a retro look. Note: The CRT filter does not show on the TIC-80 screen capture GIFs. Also it does not work when SOFTWARE_RENDERING option of the [configuration file](https://github.com/nesbox/TIC-80/wiki/System-Configuration-Cartridge#others) is set to `true`.
* **DEV MODE** Disable TIC-80 menu so that you can switch from game to editor with escape. To access the menu while dev mode is on, for instance to unset the dev mode, use the `menu` console command.
* **VSYNC** Vsync aligns your game's graphics with your screen's refresh rate, preventing tearing and flickering. With Vsync on, your game waits for the screen to start refreshing, then displays a complete frame, ensuring smoother visuals.
* **FULLSCREEN** Enables full screen.
* **INTEGER SCALE** If set to ON, the TIC-80 screen size can only be a multiple of 240×136 pixels. Set it OFF for small screens like playing on smartphones to use the full screen.
* **VOLUME** Volume of the TIC-80 sounds. From 0 to 15.

### EDITOR OPTIONS
These options apply on the code editor.
* **TAB SIZE** Size of the tab displayed.
* **TAB MODE**
  - TABS. Hitting Tab writes a Tab.
  - SPACES write spaces when you hit Tab. The number of spaces depends on the TAB SIZE option. Already existing Tabs will stay.
  - AUTO uses TABS except for indentation sensitive languages such as Python and Moonscript. (Default)
* **KEYBIND MODE** bring some of the most commonly used key bindings from Emacs with the [Emacs mode](https://github.com/nesbox/TIC-80/wiki/Hotkeys#emacs-mode) or VI with the [VI mode](https://github.com/nesbox/TIC-80/wiki/Hotkeys#vi-mode).

### SETUP GAMEPAD
Set up gamepad mapping to use with the [btn API](https://github.com/nesbox/TIC-80/wiki/btn).
Up to 4 gamepads in total.

* **SAVE MAPPING** to keep it after closing TIC-80.
* **CLEAR MAPPING**.
* **RESET TO DEFAULTS**.
