# Bankswitching

Bankswitching is the ability to increase memory capacity. (However, not the accessible memory, see [RAM](ram)).

In the case of TIC-80, it has 8 accessible memory banks and can individually bankswitch each of the different areas of RAM:

- tiles
- sprites
- map
- sfx
- music
- palette
- flags
- screen

Note that the code size increases without need to switch banks in the code editor.

To switch banks in code, see [sync](sync).

## Switching banks in the editors
This is a feature of the [PRO version](PRO-Version).  

You can edit contents of different banks by pressing the "Switch bank" button on the top bar of the TIC-80 pro editor and then choosing bank 0-7.

On the right side of bank numbers, there's a **pin button**. When the pin button is pressed (red), switching the bank will set all the editors (sprites, map, etc) to the chosen bank. When it's not pressed (gray), only the bank of the currently viewed editor will change. This will allow for e.g. editing multiple map banks with the tiles of just one sprite sheet bank.

![pin button usage in the editor](https://user-images.githubusercontent.com/1101448/34250447-ebe1b32a-e64d-11e7-8e66-436e84ae433f.gif)



---

Useful tip:

`sync` is also accessible for users who do not have the PRO version of TIC-80, so it is possible to save and edit these memory banks by switching between bank 0 and banks 1 to 7 with toCart parameter set to true.