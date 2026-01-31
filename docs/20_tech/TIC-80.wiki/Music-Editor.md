The Music Editor has two separate views that can be toggled using the top buttons in the top right: Piano Mode and Tracker Mode. Both views can be used to create music: there are no functional differences between the two, just the visual representation differs.

* TIC-80 can store up to 8 **tracks** (0 to 7) that act like separate pieces of music.  
* A track is composed from 1 to 16 **frames**, each of which can hold 1 to 4 **patterns** on the four sound **channels**.
* The **tempo** and **spd** parameters define together how fast the music will play back, with `tempo = 120` and `spd = 3` resulting in 120 beats per minute. See [this](#Calculating-the-BPM) for a more thorough explanation.
* The number of **rows** determines how many notes can be played on every pattern of a given track, to a maximum of 64.

Tracks created in the Music Editor can be played using the [music](music) command.

## Piano Mode
![Music Editor Screen Capture - Piano Mode](https://i.imgur.com/LvHS62i.png)

In the piano mode, the left column represents frames. Each frame will contain a series of notes (shown in the middle column) specified in the Rows count. Like in the tracker mode, up to four patterns can be simultaneously playing in a given track. The pattern currently being edited is highlighted in white. Left-clicking on the pattern number increments it by one, and right-clicking decrements it by one.

At the bottom of the frame columns, the individual columns can have their mute status toggled.

The note entry columns become active once the frame number is created/specified by typing its number into the appropriate column. Note that frame index count begins at `01`.

A note break (or "stop") can be inserted by right-clicking on a row in the current frame. Stops are indicated by a horizontal line of red dots in the piano column.

### Commands
The commands in the command column are available when an active pattern is selected in the frame column. The commands are: **M**aster volume, **C**hord play, **J**ump to frame/beat, **S**lide, **Pitch** shift, **V**ibrato, and **D**elay trigger. Additionally, you can remove previously set command without deleting the note by setting the command to **0**.


Commands are parameterized by using the X and Y values in the column to the right, in hexadecimal. Only a single command can be applied in each row.


* `Mxy`: Master volume
  * x and y values change the volume of the current note: left (x) and right (y) channel from 0 to f.
  * `Mff` plays the note on full volume on both channels, `Mf0` only on left channel.

* `Cxy`: Chord play
   * Chord plays three notes quickly in succession: the note specified by the note column, and `note + x` and `note + y`. The values of x and y are in semitones from 0 to f.
   * `C37`, with the note `C-3`, plays the notes `C-3`, `D#3` and `G-3`, a C minor chord!
   * The command stays on, so remember to reset it afterwards with `C00`.

* `Jxy`: Jump to frame/beat
   * Jumps to frame (pattern) x, beat (row) y.
   * `J00` jumps to the beginning of the song, so if you use it, remember to remove the rule before exporting the music track.

* `Sxy`: Instead of playing the specified note immediately, slide from the previous note to current note in xy ticks (in hex).
   * First, play a note without using this command. On the next beat, add a new note that uses this command. This is the note you want to slide to!
   * `S1f` takes 31 ticks to slide to the note.
   * After using the command, remember to reset it afterwards with S00.

* `Pxy`: Pitch shift
   * Apply a small change to the pitch of the current note.
   * `P80` makes no changes,
   * `P84` changes the pitch a bit upwards,
   * `P7C` the same amount downwards.

* `Vxy`: Vibrato
   * x is period and y is depth (amount) of the effect. (`x=1` has no effect!).
   * `V2f` creates a very fast and very noticeable effect,
   * `Vf1` a very slow and not that noticeable effect.

* `Dxy`: Delay trigger
   * Delays playing the current note by xy ticks.

## Tracker Mode
![Music Editor Screen Capture - Piano Mode](https://i.imgur.com/EARkaE1.png)

This mode may be familiar to users of previous TIC-80 versions, as well as those used to creating music on limited-resource systems.

To enter a note, click on a cell (or move to it using the arrow keys) and press a key on the bottom row of the keyboard similar to the [SFX Editor](SFX-Editor). You can also enter notes from the next octave apart. Once a note is entered, it will play until the next note or note stop.

A note break (or "stop") can be entered by pressing `A`. Stops are indicated by blank values in the note region instead of dashes.

### Notes
A note on the track has three components: **note**, **SFX**, and **command**.

![Note on a track](https://i.imgur.com/FR6uJnh.png)

The note component is a letter from A to G indicating the actual note value. Sharp values are indicated by `#` after the letter. The number next to the note value is the octave that note belongs to.

The SFX component is an orange number in the range of `00` to `63`. This number is the index of the voice (or instrument) created in the [SFX Editor](SFX-Editor) that will be played.

The command component consists of two parts: the command itself, and the X/Y parameters for the command. For more information, see the [Commands](#Commands) section of Piano Mode.

## Bankswitching

[PRO version](https://github.com/nesbox/TIC-80/wiki/PRO-Version) allows to use 8 [memory banks](https://github.com/nesbox/TIC-80/wiki/Bankswitching) to compose more musics.

## Keys
Most keyboard shortcuts are usable in both modes in the Music Editor, as well as the [SFX Editor](SFX-Editor).

![Music Editor Hotkeys](https://i.imgur.com/nG6D9vK.png)

```
SHIFT+ENTER             Play pattern from cursor position in the music editor.
ENTER                   Play frame.
SPACE                   Play track.
CTRL+F                  Follow.
Z,X,C,V,B,N,M           Play notes corresponding to one octave (bottom row of QWERTY layout) in tracker mode.
S,D,G,H,J               Play notes corresponding to sharps and flats (home row of QWERTY layout) in tracker mode.
A                       Insert note break (or "stop").
DELELTE                 Delete selection / selected row.
BACKSPACE               Delete the row above.
INSERT                  Insert rows below.
CTRL+F1                 Decrease notes by Semitone.
CTRL+F2                 Increase notes by Semitone.
CTRL+F3                 Decrease octaves.
CTRL+F4                 Increase octaves.
CTRL+RIGHT              Jump forward one frame.
CTRL+LEFT               Jump backward one frame.
TAB                     Go to next channel.
SHIFT+TAB               Go to previous channel.
+                       Next pattern.
-                       Previous pattern.
CTRL+UP                 Next instrument.
CTRL+DOWN               Previous instrument.
```
The [general hotkeys](https://github.com/nesbox/TIC-80/wiki/Hotkeys#general) are available in the music editor too.

## Calculating the BPM

The relationship of the Tempo and Spd parameters can be confusing. In simplest terms, the BPM (Beats per minute) of a given track is equal to

```
BPM = 3 * TEMPO / SPD
```

This equation assumes a beat is equal to 8 rows on a pattern. For a more general case, use

```
BPM = (24 * TEMPO) / (rowsPerBeat * SPD)
```

With this equation, we can estimate the duration of a track:

```
durationAsTicks = (120 * ROWS * FRAMES * SPD * 60) / (16 * 3 * TEMPO)
                = (150 * ROWS * FRAMES * SPD) / TEMPO
```
where FRAMES tells how many frames the track has. Naturally, this equation does not work if the `Jxx` command is used.

## Crash course tracking music in TIC-80

[https://www.youtube.com/watch?v=V9oAccwjeDA](https://www.youtube.com/watch?v=V9oAccwjeDA)

[![Video](https://img.youtube.com/vi/V9oAccwjeDA/0.jpg)](https://www.youtube.com/watch?v=V9oAccwjeDA)
