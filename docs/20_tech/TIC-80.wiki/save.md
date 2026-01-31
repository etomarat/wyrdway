`save <cart>` Save cartridge to the local filesystem.  

## Parameters
Required:
* `<cart>` input cart name. `.tic` extension will be added if no extension is used.
    * Use `.png` file extension to save as [png cart](https://github.com/nesbox/TIC-80/wiki/save#save-as-png-cart).
    * Use `.lua`, `.py` `.rb`, `.js`, `.moon`, `.fnl`, `.nut`, `.wren`, `.wasmp` cart extension to save it in text format to use an [external editor](https://github.com/nesbox/TIC-80/wiki/External-Editor) [[PRO version](https://github.com/nesbox/TIC-80/wiki/PRO-Version)]. See [supported languages](https://github.com/nesbox/TIC-80/wiki/Supported-Languages) page for the full list of languages.

## Description
Save cartridge to the local filesystem.  
Hotkey: `CTRL+S`

## Related commands

Use [load](https://github.com/nesbox/TIC-80/wiki/load) command to load saved cartridge.

Use [export](https://github.com/nesbox/TIC-80/wiki/export) command to export cartridge as native build, HTML or to export part of the data.

## Save as png cart

Save as a png cartridge for easy sharing.  
You can drag this cart to tic80.exe as an example:

![motion](https://github.com/nesbox/TIC-80/assets/26139286/7fe03dd1-4af7-420b-898b-369be200a567)

The cart data are stored in the chunk of the png file therefore you can create your own image too like https://github.com/nesbox/TIC-80/discussions/2549.