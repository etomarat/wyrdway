`config` Open `config.tic` file in the code editor to configure TIC-80.  
`config [reset | default]`

## Parameters
* `reset` reset current configuration file.
* `default` edit [default cart](https://github.com/nesbox/TIC-80/wiki/Hello-World) template.

## Description

TIC-80 can be modified by editing the configuration file. Save the file to apply modifications.

![config_demo](https://github.com/nesbox/TIC-80/assets/26139286/c4870ea9-efa1-4586-a853-125040cc499c)

The `config` command also allows to edit the Hello World default cart thanks to the `default` parameter.


# Configuration parameters
## Color Parameters

```lua
BG     =15, --background
FG     =12, --foreground ie text
STRING =4,
NUMBER =11,
KEYWORD=3,  --function, if, true... 
API    =5,  --TIC, print, cls...
COMMENT=14,
SIGN   =13, --*, -, =, (...
SELECT =14,
CURSOR =2,
```

#### Example

![config_color](https://github.com/nesbox/TIC-80/assets/26139286/392ea49d-d0ff-424c-a192-076448732435)

## Font Parameters
```lua
SHADOW =true,
ALT_FONT=false,
```
`ALT_FONT=true` sets the small font in the code editor as default.

## Delimiters Parameters
```lua
MATCH_DELIMITERS=true,
AUTO_DELIMITERS=false,
```
`MATCH_DELIMITERS` allows to highlight delimiters matching the one under the cursor.  
`AUTO_DELIMITERS` allows to autocomplete delimiters. When a `(` is written, the corresponding `)` is added, etc.

## Others
```lua
CHECK_NEW_VERSION=true
```
Check if a newer version of TIC-80 exists and displays a message in console if TIC-80 should be updated.

```lua
UI_SCALE=4
```
Sets the size of the TIC80 window at startup.

```lua
SOFTWARE_RENDERING=false
```
Switch from SDLGPU to SDL2 rendering which may be more stable but does not allow to use CRT effect. Linked to issue [#1566](https://github.com/nesbox/TIC-80/issues/1566).

```lua
GAMEPAD=
{
  TOUCH=
  {
    ALPHA=180,
  },
},

```
Sets the transparency of the gamepad buttons showing on screen on Android. The value can be [0,255], 0 is fully transparent and 255 is totally opaque.

# Sprites and SFX
You can also change TIC-80 sound effects, palette as well as sprites like the cursor or the fonts.

![config_editors_demo](https://github.com/nesbox/TIC-80/assets/26139286/b28b77fe-17ae-45ef-b366-d7dbb533555e)

Note: To change a game specific cursor use [poke](https://github.com/nesbox/TIC-80/wiki/poke#examples) in your code instead.

#### Custom Tab Character
If you are using indentation-sensitive languages like python, you might want the tab and space characters to be different. You can do so by modifying sprite #265 (and #393 for small font) of the configuration file.

![custom_tab](https://github.com/nesbox/TIC-80/assets/26139286/e5c51cf3-a3ad-445d-86da-3a8590a96176)

NOTE that it will change how tabs appear everywhere, not only in the code editor.

# Themes
You can deeply modify your configuration file by editing the [palette, sprites, font, SFX](https://github.com/nesbox/TIC-80/wiki/config#sprites-and-sfx) and [parameters](https://github.com/nesbox/TIC-80/wiki/config#color-parameters) to create a [theme](https://github.com/nesbox/TIC-80/wiki/Themes) that you can [share with others](https://github.com/nesbox/TIC-80/wiki/Themes#example-themes).

<img src="https://github.com/nesbox/TIC-80/assets/26139286/cfdad03e-a25c-41d8-befc-5c7c34f812a5" width="510">


# Keeping Configuration after TIC-80 Updates
When TIC-80 is updated to a new version, the configuration file is reset as it can be updated too.
In order to keep your previous configuration, you need to copy-paste your previous configuration file to the new version.

The path to the `config.tic` file is displayed by the `config` command. This path is `.local/<version_number>/` in the `TIC-80` folder that you can access by typing `folder` in the console. `.local` is an hidden folder. Ways to access hidden folders depends on your operating system.