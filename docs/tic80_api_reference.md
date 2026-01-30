You can download a quick API reference sheet suitable for viewing or printing here: [PDF (OUTDATED)](https://github.com/nesbox/TIC-80/files/12447661/tic-80_cheatsheet.pdf).  The Wiki also includes a [Cheatsheet](Cheatsheet) for fast reference. And you can use `export help <file>` to export all help information into a markdown file.

## Callbacks

Callbacks are functions that your game defines and that TIC-80 calls automatically.  Every game at a minimum must define a `TIC` function.

* [TIC](TIC) - Called 60 times per second (60 FPS); the main update/draw callback. **Required.**
* [BOOT](BOOT) - Called once when yout cartridge is first booted
* [SCN(n)](SCN) - *(deprecated as of 0.90, use `BDR(n)` now instead)*
* [BDR(n)](BDR) - Called prior to each scanline/borderline render (allowing for palette swaps, etc).
* [OVR](OVR) - Called last and draws to a separate layer (using a separate palette).
* [MENU](MENU) - Used to handle custom items in the Game Menu (introduced in 1.0)

### Sequencing

```
-- cartridge is booted
   BOOT()

-- frame begins (at 60 frames per second)

   TIC()
   OVR()
   BDR(0..143)

-- frame ends
```

`SCN` callsbacks are not included in the above table because `SCN` has been deprecated.  You should now use [BDR](BDR) instead of `SCN`.


## Functions

#### Drawing

* [circ](circ) - Draw a filled circle
* [circb](circb) - Draw a circle border
* [elli](elli) - Draw a filled ellipse (0.90)
* [ellib](ellib) - Draw an ellipse border (0.90)
* [clip](clip) - Set the screen clipping region
* [cls](cls) - Clear the screen
* [font](font) - Print a string using foreground sprite data as the font
* [line](line) - Draw a straight line
* [map](map) - Draw a map region
* [pix](pix) - Get or set the color of a single pixel
* [print](print) - Print a string using the [system font](ram#font)
* [rect](rect) - Draw a filled rectangle
* [rectb](rectb) - Draw a rectangle border
* [spr](spr) - Draw a sprite or composite sprite
* [tri](tri) - Draw a filled triangle
* [trib](trib) - Draw a triangle border (0.90)
* [textri](textri) - *(deprecated as of 1.0, use `ttri` now instead)*
* [ttri](ttri) - Draw a triangle filled with texture

#### Input

* [btn](btn) - Get gamepad button state in current frame
* [btnp](btnp) - Get gamepad button state according to previous frame
* [key](key) - Get keyboard button state in current frame
* [keyp](keyp) - Get keyboard button state relative to previous frame
* [mouse](mouse) - Get XY and press state of mouse/touch

#### Sound

* [music](music) - Play or stop playing music
* [sfx](sfx) - Play or stop playing a given sound

#### Memory

* [memcpy](memcpy) - Copy bytes from one location in RAM to another
* [memset](memset) - Set sequential bytes in RAM to a given value
* [pmem](pmem) - Access or update the persistent memory
* [peek](peek) - Read a byte from an address in RAM
* [peek1](peek) - Read a single bit from an address in RAM (1.0)
* [peek2](peek) - Read two bit value from an address in RAM (1.0)
* [peek4](peek) - Read a nibble (4bit) value from an address RAM
* [poke](poke) - Write a byte value to an address in RAM
* [poke1](poke) - Write a single bit to an address in RAM (1.0)
* [poke2](poke) - Write a two bit value to an address in RAM (1.0)
* [poke4](poke) - Write a nibble (4bit) value to an address in RAM
* [sync](sync) - Copy [banks](bankswitching) of RAM (sprites, map, etc) to and from the cartridge
* [vbank](vbank) - Switch the 16kb of banked video RAM

#### Utilities

* [fget](fget) - Retrieve a sprite flag (0.80)
* [fset](fset) - Update a sprite flag (0.80)
* [mget](mget) - Retrieve a map tile at given coordinates
* [mset](mset) - Update a map tile at given coordinates

#### System

* [exit](exit) - Interrupt program and return to console
* [reset](reset) - Reset game to initial state (0.60)
* [time](time) - Returns how many milliseconds have passed since game started
* [tstamp](tstamp) - Returns the current Unix timestamp in seconds (0.80)
* [trace](trace) - Print a string to the Console

see full version at `/docs/TIC-80.wiki`