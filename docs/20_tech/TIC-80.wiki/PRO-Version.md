To help support TIC-80 development, we have a PRO Version.  This version has a few additional features and binaries can only be downloaded [via our Itch.io page](https://nesbox.itch.io/tic80).  
Please, consider supporting the developer by buying the PRO version or by becoming a [sponsor](https://github.com/sponsors/nesbox).

For users who can't spend the money, we made it easy to [build](https://github.com/nesbox/TIC-80#build-instructions) the pro version from the source code: (`cmake .. -DBUILD_PRO=On`)

## Pro features

- Save/load cartridges in text format, and create your game in any [external editor](https://github.com/nesbox/TIC-80/wiki/External-Editor) you want, also useful for version control systems.
- Even more memory banks: instead of having only 1 memory bank you have 8. You can [switch banks](https://github.com/nesbox/TIC-80/wiki/Bankswitching) in the editors or in code using [sync](https://github.com/nesbox/TIC-80/wiki/sync). The code is not split into banks, so you get 8 times longer code size directly in the editor.
- Export your game without editors, and then publish it to app stores using the `alone=1` parameter of the [export command](https://github.com/nesbox/TIC-80/wiki/Console#file-system-interaction).
