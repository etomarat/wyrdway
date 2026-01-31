![SFX Editor Screen Capture](https://i.imgur.com/RzsmGRy.png)

You can define and customize up to 64 sound effects which also can be used in the [Music Editor](Music-Editor) as instruments. Created SFX can be played using the [sfx](sfx) API function.

Notes can be played in the SFX Editor using the `Z` `S` `X` `D` `C` `V` `G` `B` `H` `N` `J` `M` keys. The keys are mapped to the bottom row of a standard QWERTY layout as one octave of a piano (C-4 through B-4), with sharps and flats on the home row. Pressing `SPACE` will play the last played note, which is indicated in the on-screen piano keyboard by a red dot. The currently pressed key will be highlighted in red.

The SFX editor is divided into the following sections: SFX Library, Wave Library, and the three editors on the right side for Data, Arpeggiation, and Pitch.

In the three Editor sections, the playhead speed is controlled by the SPD value in the Library. All editor sections support looping, with the left loop control defining the start point, and the second defining the loop length. All editors support independent loop points from each other.

Each SFX can be cut, copied, and pasted using the buttons at the top of the editor window or with the normal copy and paste keyboard shortcuts.

## SFX Library

This section is a grid of buttons that change the currently selected instruments. Unused instruments will be dark grey, and instruments with data will be a lighter grey.

The currently selected instrument is highlighted green, as well as the index number (IDX) of the instrument in the top left (00-63). The speed (SPD) of each instrument can also be set here (0-7).

## Wave Library

This section can be used to select from some predefined wave shapes, or can be completely drawn from scratch. Wave shapes with all Y values at zero play as noise.

By default, the first four wave types are predefined as square, triangle, sawtooth, and noise. The remaining default slots are defined as noise.

## Editors
### Data Editor
At the top of the right column of editors is the Data Editor. The VOL/WAV button toggles between volume data and wave data respectively.

In volume (VOL) mode, the Y value of each column represents the volume of the SFX at any given time. To smoothly ramp the volume up or down, a gentle slope or curve can be drawn by dragging the mouse across the value grid. The left and right channels can be independently turned on or off using the L and R buttons below the VOL indicator.

In wave (WAV) mode, each vertical tick mark on the value grid represents a wave in the Wave Editor. The corresponding wave selection will be highlighted in the Wave Editor when the mouse is moved over each tick in the value grid. In this way, any of the 16 wave presets can be played as the playhead moves over them.

### Arpeggio Editor
This editor is for transposing notes up or down. Each vertical value represents a single semitone higher than the original pitch, unless DOWN is selected, then the opposite is true.

### Pitch Editor
The Pitch Editor shifts the notes within a single semitone. In 16x mode, the pitch variation is increased greatly.

## Bankswitching

[PRO version](https://github.com/nesbox/TIC-80/wiki/PRO-Version) allows to use 8 [memory banks](https://github.com/nesbox/TIC-80/wiki/Bankswitching) to use more sfx.

## Hotkeys
```
SPACE                   Play last played note.
Z,X,C,V,B,N,M           Play notes corresponding to one octave (bottom row of QWERTY layout).
S,D,G,H,J               Play notes corresponding to sharps and flats (home row of QWERTY layout).
```
The [general hotkeys](https://github.com/nesbox/TIC-80/wiki/Hotkeys#general) are available in the sfx editor too.