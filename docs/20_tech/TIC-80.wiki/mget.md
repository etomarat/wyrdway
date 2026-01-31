`mget(x, y) -> tile_id`

## Parameters

* **x, y** : map coordinates

## Returns

* **tile_id** : tile index

## Description

This function returns the index of the tile at the specified map coordinates, the top left cell of the map being (0, 0). The map coordinates are not to be confused with the screen coordinates. One screen can contain 30×17 cells.

![XYmap_coordinates](https://github.com/nesbox/TIC-80/assets/26139286/a524edaa-b923-4465-bf62-a5711b61a07a)

### Related

* [map](map)
* [mset](mset)
* [Using mset() and mget() functions](https://github.com/nesbox/TIC-80/wiki/Using-mset()-and-mget()-functions)