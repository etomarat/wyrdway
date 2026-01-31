![Map Editor Demo](https://user-images.githubusercontent.com/1101448/105969223-11cf6780-6099-11eb-9dbb-48609c43c568.gif)

The map editor provides a set of tools to design and customize your game world efficiently. They are localized on the top right of the screen.

* **Draw** enables you to place tiles or sprites onto the map canvas.
* **Drag map** lets you move around the map canvas. You can also use the arrow keys of your keyboard.
* **Selection tool** allows you to select specific areas of the map. This is useful for copying, moving, or modifying groups of tiles.
* **Filling tool** often referred to as the paint bucket tool, lets you fill an enclosed area with a chosen tile or sprite, making it efficient for creating large sections of uniform terrain.
* **Tiles preview** displays a preview of the available tiles in the tilesheet, showing the graphical elements that you can select and place on the map. It allows to switch from tilesheet to spritesheet as well as from 4 [bits per pixel](https://github.com/nesbox/TIC-80/wiki/Bits-Per-Pixel) to 2 or 1.

More on the left there are two other options:
- **Show/Hide Grid** toggle the visibility of the grid overlay on the map.
- **Full World Map** switch to a full world map view for a broader perspective.

## Map coordinates
The map can be up to 240 cells wide by 136 deep, each cell being 8×8 pixels. Only 30x17 cells appear on screen at a time.

![XYmap_coordinates](https://github.com/nesbox/TIC-80/assets/26139286/e83ef43a-07f1-480c-9da1-9888406d3d47)

## Bankswitching

[PRO version](https://github.com/nesbox/TIC-80/wiki/PRO-Version) allows to use 8 [memory banks](https://github.com/nesbox/TIC-80/wiki/Bankswitching) for larger map space.

## Hotkeys
```
SHIFT                   Show tilesheet.
CTRL+CLICK              Replace all identical tiles (when the Fill tool [4] is selected).
`                       Show/hide grid.
TAB/SCROLL              Switch to full world map.
1                       Select draw.
2                       Select drag map.
3                       Select selection tool.
4                       Select filling tool.
```
The [general hotkeys](https://github.com/nesbox/TIC-80/wiki/Hotkeys#general) are available in the map editor too.