_This was added to the API in version 0.90._

`ellib(x, y, a, b, color)`

## Parameters

* **x, y** : the [coordinates](coordinate) of the ellipse's center
* **a** : the horizontal radius of the ellipse in pixels
* **b** : the vertical radius of the ellipse in pixels
* **color**: the index of the desired color in the current [palette](palette)

## Description

This function draws an ellipse border with the radiuses **a** **b** and **color** with its center at **x**, **y**. It uses the _Bresenham_ algorithm.

See also:

- [elli](elli) - draw a filled ellipse

## Example
See [elli()]( elli) for an example.