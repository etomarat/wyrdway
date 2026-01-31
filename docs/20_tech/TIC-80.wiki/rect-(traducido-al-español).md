# rect
`rect(x, y, ancho, alto, color)`
## Parámetros

* **x, y** : [Coordinadas](coordinate) de la parte superior izquierda del rectángulo
* **ancho** : La anchura del rectángulo en pixeles
* **alto** : La altura del rectángulo en pixeles
* **color** : El color especificado en la [Paleta de colores indexada](palette) que va a usar como color del relleno

## Descripción
Esta función dibuja un rectángulo rellenado en la posición especificada

Ver también:

* [rectb (en ingles)](rectb) Dibuja solamente el borde del rectángulo

## Ejemplo

![Example](https://imgur.com/CxKY5A2.gif)

``` lua
-- rect demo
x=120
y=68
dx=7
dy=4
col=1

cls()
function TIC()
--Update x/y
 x=x+dx
 y=y+dy
 --Check screen walls
 if x>240-6 or x<0 then
  dx=-dx
  col=col%15+1
 end
 if y>136-6 or y<0 then
  dy=-dy
  col=col%15+1
 end
 --Draw rectangle
 rect (x,y,6,6,col)
end
```

# Créditos
**El contenido visto en la pagina le pertenece a la pagina [rect (en ingles)](https://github.com/nesbox/TIC-80/wiki/rect) de la wiki de TIC80 hecha por "HomineLudens"**