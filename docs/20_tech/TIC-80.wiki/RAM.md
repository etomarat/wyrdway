# RAM & VRAM layout

The TIC-80 has a limited amount of "hardware" memory, mostly dedicated to memory mapped I/O of various devices and hardware registers.  This RAM is accessed via a contiguous address space starting at address `0x00000`.  Not every byte of RAM is currently mapped, but the entire first 96kb is  `RESERVED` for system use (not general variable storage).  Scripting cartridges should use the scripting runtime for variable storage, etc. (which is how things work by default)

```
.--------------------------------------.
|         96KB IO ADDRESS SPACE        |
|--------------------------------------|
| ADDR    | INFO              | BYTES  |
|---------+-------------------+--------|
| 0x00000 | <VRAM bank 0>     | 16,384 | 32kB Video RAM (see below)
|         |    ...or <bank 1> |        |
| 0x04000 | TILES             | 8,192  | 256 8x8 4-bit bg tiles - #0 to #255
| 0x06000 | SPRITES           | 8,192  | 256 8x8 4-bit fg sprites - #256 to #511
| 0x08000 | MAP               | 32,640 | 240x136 map - indexed by tile/sprite
| 0x0FF80 | GAMEPADS          | 4      | button state for 4 gamepads
| 0x0FF84 | MOUSE             | 4      | mouse state X / Y / buttons / scroll
| 0x0FF88 | KEYBOARD          | 4      | keyboard state, up to 4 pressed buttons
| 0x0FF8C | SFX STATE         | 16     |
| 0x0FF9C | SOUND REGISTERS   | 72     | ...
| 0x0FFE4 | WAVEFORMS         | 256    | 16 waveforms, each 32 x 4-bit values
| 0x100E4 | SFX               | 4,224  | ...
| 0x11164 | MUSIC PATTERNS    | 11,520 | ...
| 0x13E64 | MUSIC TRACKS      | 408    | ...
| 0x13FFC | SOUND STATE       | 4      | ...
| 0x14000 | STEREO VOLUME     | 4      |
| 0x14004 | PERSISTENT MEMORY | 1,024  | persistent RAM, per cartridge
| 0x14404 | SPRITE FLAGS      | 512    |
| 0x14604 | SYSTEM FONT       | 2,048  | 256 8x8 1-bit font (used by print)
| 0x14E04 | GAMEPAD MAPPING   | 32     | keycodes for gamepad mappings
| 0x14E36 | ** RESERVED **    | 12,764 |
'--------------------------------------'
```

*Note:* The second bank of VRAM which can be mapped in and out of address range `0x0000` to `0x3fff` using the [vbank](vbank) API.

## WASM cartridges

When running [WASM cartridges](wasm) the "hardware" memory is increased to 272kb, of which 256kb is directly addressable and 160kb is free for cartridge use.  This difference accounts for the fact that there is no separate "runtime" vs "hardware" memory available with WASM... only a single large address space.

```
.---------------------------------------.
|          256KB ADDRESS SPACE          |
|              (WASM ONLY)              |
|---------------------------------------|
| ADDR    | INFO               | SIZE   |
|---------+--------------------+--------|
| 0x00000 | MEMORY MAPPED I/O  | 96 KB  | see base 96kb RAM map above
| 0x18000 | ** FREE RAM *      | 160 KB |
'---------------------------------------'
```
## VRAM

VRAM is double-banked, see [vbank](vbank) for additional details.  Since only a single bank is accessible at once the memory addresses of bank 0 and bank 1 are
the same.

### VRAM Bank 0

```
.------------------------------------.
|  ADDR  | INFO              | BYTES |
|--------+-------------------+-------|
| 0x0000 | SCREEN            | 16320 | 240x136 = 32,640 4-bit pixels
| 0x3FC0 | PALETTE           | 48    | 16 x 24bit RGB color values
| 0x3FF0 | PALETTE MAP       | 8     | 16 x 4-bit color indexes (palette swaps)
| 0x3FF8 | BORDER COLOR      | 1     | 4-bit color value
| 0x3FF9 | SCREEN OFFSET     | 2     | horz/vert screen offset [-128...+127]
| 0x3FFB | MOUSE CURSOR      | 1     | sprite to use for mouse pointer
| 0x3FFC | BLIT SEGMENT      | 1     | (lo nibble) 4-bit BLIT segment value
| 0x3FFC | RESERVED          | 1     | (hi nibble) 4-bit reserved for future
| 0x3FFD | RESERVED          | 3     | reserved for the future
'------------------------------------'
```

### VRAM Bank 1 ("overlay")

The bank 1 layout is identical to bank 0 with the exception of `0x3FF8`.

```
.------------------------------------.
|  ADDR  | INFO              | BYTES |
|--------+-------------------+-------|
| ...... | ...               | ..... |
| 0x3FF8 | OVR TRANSPARENCY  | 1     | 4-bit color value
| ...... | ...               | ..... |
'------------------------------------'
```

See also: [vbank](vbank)

## Palette

`PALETTE` stores the currently active [palette](palette).  Each entry in the palette includes a red, green, and blue component - allowing over 16 million colors (24-bit color).

```
.----------------------------------.
|              PALETTE             |
|----------------------------------|
| .-------------------------.      |
| | red component    | 8bit |      |
| | green component  | 8bit | x 16 | = 48 bytes
| | blue component   | 8bit |      |
| '-------------------------'      |
'----------------------------------'
```

## Palette Map

`PALETTE MAP` controls how [palette](palette) indexes are applied when writing to VRAM.  This can be used to easily swap palette colors.  The mapped color index (not the original) is written to the `SCREEN`.  With sprite-drawing functions (`spr`, `map`, `ttri`), this color swap is done when reading the color from sprite memory.

In practice, this merely redefines the color assigned to a given index and does not interact with `transparent` index parameters. For example, if transparency is set to color index 1, then you swap colors 1 and 2, the pixels in the sprite originally set to color #1 before the swap will still be transparent, and pixels originally set to color #2 will draw as color #1.

For an example see [Swapping Palette Colors](Palette#swapping-palette-colors).


## Blit Segment

`BLIT SEGMENT` controls how sprite drawing functions will read sprites in memory. It specifies the amount of [bits per pixel](Bits-Per-Pixel) and the position of the spritesheet.

See [Blit Segment](blit-segment) and [BPP](https://github.com/nesbox/TIC-80/wiki/Bits-Per-Pixel#bpp-bits-per-pixel) for more information.


## Mouse Cursor
`MOUSE CURSOR` specifies which cursor to use:
```
0 = Disabled
1...127 = Sprite (#257 to #383 in 4bpp mode)
128 = ARROW
129 = HAND
130 = IBEAM
131...255 = Reserved
```
It gets reset to 128 on vblank, so if you want to use a custom cursor you need to `poke()` it on every call to `TIC`; setting it on `BOOT` is not sufficient.

## Tiles/Sprites
SPRITES: Each sprite/tile is laid out sequentially in memory. Each sprite/tile is 32 bytes long, so sprite #i starts at `0x4000+(32*i)`. Each byte in the sprite represents a pair of pixels (since each pixel is 4 bits). The low 4 bits are the _left_ pixel, and the high 4 bits are the _right_ pixel. Pixels are laid out from left to right, top to bottom row.
```
Example sprite          Representation
(each hex digit
represents a pixel)
   01234567             0x10 0x32 0x54 0x76
   89abcdef             0x98 0xba 0xdc 0xfe
   01234567             0x10 0x32 0x54 0x76
   89abcdef             0x98 0xba 0xdc 0xfe
   01234567             0x10 0x32 0x54 0x76
   89abcdef             0x98 0xba 0xdc 0xfe
   01234567             0x10 0x32 0x54 0x76
   89abcdef             0x98 0xba 0xdc 0xfe
```

Sprites 0 to 255 are "background sprites" that can be part of a map; 256 to 511 are "foreground sprites" that cannot be on the map (but can still be drawn by `spr` and other means.) Background sprites are also called "tiles".

## Map

The `MAP` is a grid of 240x136 tiles. Each byte represents a single tile of the map. Like the sprites, the map's tiles are laid out from left to right, top to bottom row. Convenience functions [mset](mset) and [mget](mget) are provided for working with map data.

## Mouse
```
.-------------------.
|       MOUSE       |
|-------------------|
| x position | 8bit |
| y position | 8bit |
| left       | 1bit |
| middle     | 1bit | = 4 bytes
| right      | 1bit |
| h scroll   | 6bit |
| v scroll   | 6bit |
| relative   | 1bit |
'-------------------'
```
The X and Y position values represent _where_ in the TIC-80 screen the mouse is pointing to, but they may exceed the 240x136 range of the screen.

The H and V scroll values are used for the horizontal and vertical mouse wheel deltas. These represent the amount of "steps" they had moved in the last frame. These are two's complement numbers, with their sign indicating which direction they're scrolling.

This data is most easily accessed using the [mouse](mouse) function.

If the `relative` bit is set to 0 (default), it will be in "absolute mode" and in "relative mode" if set to 1. This is also the only value not returned by the [mouse](mouse) function.

## Sound Registers
```
.-----------------------.
|     SOUND REGISTER    |
|-----------------------|
| frequency | 12bit     | x 4 channels = 72 bytes
| volume    | 4bit      |
| waveform  | 32 x 4bit |
'-----------------------'
```
The frequency value is converted to a period value (clamped to 10...4096) suited for a virtual 2,088,960 Hz clock. This period value produces an update frequency that is close to `32*frequency` (for waveform envelopes) or `16*frequency` (for noise output). At the update frequency, the 32-step counter pointing to the current waveform step will increment, or the noise [LFSR](https://en.wikipedia.org/wiki/Linear-feedback_shift_register) will update.

TIC-80 updates the volume value in correspondence with SFX volume envelopes only, independent of the `sfx()` volume parameter and `Mxy` commands in the tracker.

Noise output occurs when the waveform is either empty (zero-filled) or full (fifteen-filled). This produces a pseudo-random binary output sequence, with a length of 32,767 samples.<br>The first noise sequence is white noise and is the same as the NES/Famicom's "white noise" mode. The second noise sequence is periodic noise. Filling the waveform with any other value will produce a flat waveform.

You can update the Sound Registers every tick (60 times per second) to generate sound independently from the built-in API functions. To read the frequency and volume, use the following code:
```lua
value = peek(0xFF9C+18*channel+1)<<8|peek(0xFF9C+18*channel)
frequency = (value&0x0fff)
volume = (value&0xf000)>>12
```

## SFX
```
.--------------------------.
|           SFX            |
|--------------------------|
|                          |
| .-----------------.      |
| | volume   | 4bit |      |
| | wave     | 4bit | x 30 |
| | arpeggio | 4bit |      |
| | pitch    | 4bit |      |
| '-----------------'      |
|                          |
| .---------------------.  |
| | octave       | 3bit |  |
| | pitch16x     | 1bit |  |
| | speed        | 3bit |  | x 64 = 4224 bytes
| | reverse      | 1bit |  |
| | note         | 4bit |  |
| | stereo_left  | 1bit |  |
| | stereo_right | 1bit |  |
| | temp         | 2bit |  |
| '---------------------'  |
|                          |
| .--------------.         |
| |     LOOP     |         |
| |--------------| x 4     |
| | start | 4bit |         |
| | size  | 4bit |         |
| '--------------'         |
|                          |
'--------------------------'
```
Volume is inverted, so volumes 15...0 in the volume macro editor are treated as values 0...15 in these volume values.

The octave value is one lower than described in the editor. As such, values 0...7 correspond with SFX octaves 1...8.

The speed value and the pitch values are all two's complement numbers.

Note numbers 0...11 are mapped to C...B. Note numbers 12...15 are mapped to C...D# on the next higher octave, which is an "unintended" SFX feature.

`stereo_left` and `stereo_right` force the left/right playback volume of the SFX to be 0 when set.

There are four loop fields, each with a start index and loop size. The order of the fields is:
Wave, Volume, Arpeggio, Pitch

## Music Patterns

The `MUSIC PATTERNS` stores the tracker pattern data.

```
.---------------------------.
|        MUSIC PATTERN      |
|---------------------------|
|                           |
| .------------------.      |
| |    PATTERN ROW   |      |
| |------------------|      |
| | note      | 4bit |      |
| | param1    | 4bit | x 64 | x 60 = 11520 bytes
| | param2    | 4bit |      |
| | command   | 3bit |      |
| | sfx       | 6bit |      |
| | octave    | 3bit |      |
| '------------------'      |
|                           |
'---------------------------'
```

Please also see the source for [tic_track_row](https://github.com/nesbox/TIC-80/blob/v0.80.1344/src/tic.h#L242).

`note` describes which note to play.

```
0 = No Action
1 = Note Off
2,3 = Reserved (same as 0)
4...15 = Notes C...B
```

`command` is a SFX command (such as volume, slide, pitch, etc). [See the source](https://github.com/nesbox/TIC-80/blob/master/src/tic.h#L228).

`param1` and `param2` are the `X` and `Y` parameters for the various SFX commands.

`sfx` refers to the SFX id of the sound to use to play the given note.

One should be careful when setting/reading `sfx` with simple bit shifts (as it crosses a byte boundary).  Bit offset 15 contains the high bit of `sfx` while bit offsets 16-20 contain the remaining bits. If done incorrectly you'll end up with the LSB in offset 15, instead of the MSB, which is incorrect.  For example, SFX indexes `05` and `33` in the tracker come back as 10 and 3 when read incorrectly.

The `octave` value is one lower than described in the tracker. As such, values 0...7 correspond with octaves 1...8.

## Music Tracks

The `MUSIC TRACKS` stores the track data.

```
.-----------------------------.
|         MUSIC TRACK         |
|-----------------------------|
|                             |
| .--------------------.      |
| | pattern ch0 | 6bit |      |
| | pattern ch1 | 6bit | x 16 |
| | pattern ch2 | 6bit |      |
| | pattern ch3 | 6bit |      |
| '--------------------'      | x 8 tracks = 408 bytes
|                             |
| .--------------.            |
| | tempo | 8bit |            |
| | rows  | 8bit |            |
| | speed | 8bit |            |
| '--------------'            |
|                             |
'-----------------------------'
```
The `TEMPO` (32..255) of the music track is 150 plus the value of `tempo`.

The number of `ROWS` (1..64) in the music track is 64 minus the value of `rows`.

The `SPD` (1..31) of the music track is 6 plus the value of `speed`.


## Sound State
```
.--------------------.
|    SOUND STATE     |
|--------------------|
| track | 8bit       |
| frame | 8bit       |
| row   | 8bit       |
|--------------------|
|                    |
| .----------------. | = 4 bytes
| |     FLAGS      | |
| |----------------| |
| | mode    | 3bit | |
| | sustain | 1bit | |
| | ...     | 4bit | |
| '----------------' |
|                    |
'--------------------'
```
The track value is 255 (-1) when no track is playing.

The mode value affects how music tracks are played and looped:
```
0,1 = Music stopped
2 = Play single frame once
3 = Loop single frame
4 = Play track once
5 = Loop track
6,7 = Reserved (same as 3)
```

## Stereo Volume

Stores the left and right volumes of each channel.
```
.-------------------------------.
|         STEREO VOLUME         |
|-------------------------------|
|                               |
| .--------------.              |
| | left  | 4bit | x 4 channels | = 4 bytes
| | right | 4bit |              |
| '--------------'              |
|                               |
'-------------------------------'
```

## Sprite Flags

Stores the sprite flags in RAM.  Each byte corresponds to a sprite, in order, with the bits of each byte representing a flag.  While advanced mode is on in the sprite editor, the value under the sprite flag buttons is the value of the byte.  See [fset](fset) and [fget](fget).

<a id="#font"></a>
## System Font

Stores the default system font which is used by [print](print).  A game can modify this font by simply updating this area of RAM.

* 256 characters (default includes two fonts, the second in ASCII 128-255)
* 1 bit, 8x8 pixel font (ie, 8 bytes per character)

```
The letter 'A'.

 Binary        Lit Pixels
00000100       .....*..
00001010       ....*.*.
00011111       ...*****
00010001       ...*...*
00010001       ...*...*
00000000       ........
00000000       ........
00000000       ........
```

See the [font demo](system-font).

## Persistent Memory

Every cartridge has 1 KB of persistent memory.  This is useful for saving high-scores, level advancement or achievements.  This memory can be updated directly using [poke](poke) and  automatically persists across restarts of your cartridge.

This memory can also be retrieved and updating using the [pmem](pmem) function.  The pmem function divides this RAM into 256 individual 32-bit slots storing unsigned integers (from 0 to 4294967295).

## Gamepad Mappings

This memory stores the [keycodes](key#returns) of the [gamepad button mappings](key-map). Games can read this section of memory to determine what keyboard buttons are assigned to which gamepad buttons.