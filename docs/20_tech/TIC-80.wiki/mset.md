`mset(x, y, tile_id)`

## Parameters

* **x, y** : map coordinates.
* **tile_id** : tile index (0-255).

## Description

This function writes the specified background tile **tile_id** into the map at the given position. By default, changes to the map are lost when execution ends but they can be made permanent using [sync](sync).

The map coordinates are not to be confused with the screen coordinates. One screen can contain 30×17 cells.

![XYmap_coordinates](https://github.com/nesbox/TIC-80/assets/26139286/a524edaa-b923-4465-bf62-a5711b61a07a)

### Related

* [map](map)
* [mget](mget)
* [sync](sync)
* [MAP](ram#map)
* [Using mset() and mget() functions](https://github.com/nesbox/TIC-80/wiki/Using-mset()-and-mget()-functions)