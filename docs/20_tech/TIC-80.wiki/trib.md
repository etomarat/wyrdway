_This was added to the API in version 0.90._

`trib(x1, y1, x2, y2, x3, y3, color)`

## Parameters

* **x1, y1** : the [coordinates](coordinate) of the first triangle corner
* **x2, y2** : the coordinates of the second corner
* **x3, y3** : the coordinates of the third corner
* **color**: the index of the desired color in the current [palette](palette)

## Description

This function draws a triangle with **color**, using the supplied vertices. But unlike tri, trib only draws an outline (border).