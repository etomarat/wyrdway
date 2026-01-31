### General
```
CTRL+R/ENTER            Run current project.
CTRL+S                  Save cart.
CTRL+X/C/V              Cut/copy/paste in the editors.
CTRL+Z/Y                Undo/redo changes in the editors.
F6                      Toggle CRT filter.
F7                      Assign cover image while in game.
F8                      Take a screenshot.
F9                      Start/stop GIF video recording.
F11/ALT+ENTER           Fullscreen/window mode.
CTRL+Q                  Quit the application.
```
More ways to assign cover image [here](https://github.com/nesbox/TIC-80/wiki/Cover-image).  
More about CRT filter description [here](https://github.com/nesbox/TIC-80/wiki/TIC%E2%80%9080-Menu#options).

### Navigation
```
ESC                     Switch console/editor or open menu while in game.
ESC+F1                  Switch to code editor while in game.
ALT+~                   Show console.
ALT+1/F1                Show code editor.
ALT+2/F2                Show sprite editor.
ALT+3/F3                Show map editor.
ALT+4/F4                Show sfx editor.
ALT+5/F5                Show music editor.
CTRL+PGUP/PGDOWN        Switch to previous/next editor mode.
```

All the F1-F5 hotkeys for editors work in the menu: ESC+F2, ESC+F3, ESC+F4, ESC+F5 switch to sprite, map, sfx, music editors respectively while in game.

<!-- ### Console
```
Gamepad X               Open Surf menu.
``` TODO Uncomment when v1.2 will be released-->

### Code Editor
```
CTRL+F                  Find. Note: while the Find bar is open, arrow keys will navigate to previous/next results.
CTRL+G                  Go to line.
CTRL+P/N                Move to previous/next line.
ALT/CTRL+LEFT           Move to previous word.
ALT/CTRL+RIGHT          Move to next word.
ALT/CTRL+BACKSPACE      Delete previous word.
ALT/CTRL+DELETE         Delete next word.
CTRL+K                  Delete end of line.
CTRL+D                  Duplicate current line.
CTRL+J                  Newline.
CTRL+A                  Select all.
CTRL+F1                 Bookmark current line.
F1                      Move to next bookmark.
CTRL+B                  Show bookmark list.
CTRL+O                  Show code outline and navigate functions.
CTRL+TAB                Indent line.
CTRL+SHIFT+TAB          Unindent line.
CTRL+/                  Comment/Uncomment line.
RIGHT CLICK             Drag.
SCROLL WHEEL            Vertical scrolling.
SHIFT+SCROLL WHEEL      Horizontal scrolling.
CTRL+L                  Center screen on cursor.
```
Outline usage:  
![outline](https://github.com/nesbox/TIC-80/assets/26139286/c70c8cee-770b-4465-9698-69e699fcfc7f)


### Sprite Editor
```
TAB                     Switch tiles/sprites.
[]                      Choose previous/next palette color.
-/=                     Change brush size.
SCROLL                  Canvas zoom.
1                       Select brush.
2                       Select color picker.
3                       Select selection tool.
4                       Select filling tool.
5                       Flip horizontally.
6                       Flip vertically.
7                       Rotate.
8/DELETE                Erase.
```
### Map Editor
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
### SFX Editor
```
SPACE                   Play last played note.
Z,X,C,V,B,N,M           Play notes corresponding to one octave (bottom row of QWERTY layout).
S,D,G,H,J               Play notes corresponding to sharps and flats (home row of QWERTY layout).
```

### Music Editor
```
SHIFT+ENTER             Play pattern from cursor position in the music editor.
ENTER                   Play frame.
SPACE                   Play track.
CTRL+F                  Follow.
Z,X,C,V,B,N,M           Play notes corresponding to one octave (bottom row of QWERTY layout) in tracker mode.
S,D,G,H,J               Play notes corresponding to sharps and flats (home row of QWERTY layout) in tracker mode.
A                       Insert note break (or "stop").
DELETE                  Delete selection / selected row.
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
F5                      Switch piano/tracker mode.
```

<img src="https://i.imgur.com/nG6D9vK.png" width="580">   

### Unsaved Changes Warning

![Unsaved_changes_yn_hotkey](https://github.com/nesbox/TIC-80/assets/26139286/98dbd7e9-5011-487c-969e-dae10cb331ce)

To avoid to navigate in this menu to close the editor when there are changes, you can just type "y" on "n".
```
Y                       Yes
N                       No
```

--------------------

With some 3rd party software it's also possible to [use these same keys on Android](https://github.com/nesbox/TIC-80/wiki/Hotkeys-Android).

# Keybind Modes
Keybind modes bring some of the most commonly used key bindings from Emacs or VI to the TIC-80 code editor. They can be turned on from the [menu](https://github.com/nesbox/TIC-80/wiki/TIC%E2%80%9080-Menu#editor-options).

## Emacs Mode
[Emacs](https://www.gnu.org/software/emacs/) is a very powerful code editor, which boast good productivity through a large set of keyboard bindings (among other things). Here is a list of the bindings that are supported:
| Key Binding | Functionality |
|-------------|---------------|
| ctl-a       | Beginning of line |
| ctl-e       | End of line |
| alt-<       | Beginning of document |
| alt->       | End of document |
| ctl-n       | Next line |
| ctl-p       | Previous line |
| ctl-f       | Forward char |
| ctl-b       | Backward char |
| alt-f       | Forward word |
| alt-b       | Backward word |
| ctl-d       | Delete char |
| alt-d       | Delete word |
| ctl-k       | Delete line |
| alt-k       | Duplicate line |
| ctl-j       | Newline |
| ctl-w       | Cut Selection |
| alt-w       | Copy Selection |
| ctl-y       | Paste |
| ctl-/ or ctl-_ | Undo |
| alt-/       | Redo (unconventional) |
| alt-;       | Comment line |
| ctl-space   | Toggle mark (keyboard driven selection) |
| alt-n       | Page down |
| alt-v       | Page up |
| ctl-l       | Cycle center line (center, top, bottom) |
| alt-g       | Goto line |
| alt-s       | Search code |

## VI Mode
[VI](https://en.wikipedia.org/wiki/Vi) is a powerful and efficient command-line text editor known for its precise control and seamless navigation. Here is a list of the bindings that are supported:

#### Motion Keys
Work in both normal and select mode.

    h - left one column
    k - up one row
    j - down one row
    l - right one column
    (arrow keys also work)

    g - start of file
    G - end of file

    0,Home - start of line
    $,End - end of line

    ctrl+u,pageup - up one screen
    ctrl+d,pagedown - down one screen
    K - up half screen
    J - down half screen

    b - back one word
    w - forward one word

    ^ - first non-whitespace character on line

    { - next empty line above current position
    } - next empty line below current position

    % - jump to matching delimiter

    f - seek forward in line to next character typed
    F - seek backward in line to next character typed

    ; - seek forward in line to next character under cursor
    : - seek backwards in line to next character under cursor


#### Insert Mode
    escape - switch to normal mode
    typing letters inserts text

#### Normal Mode
    
    escape - exit editor to console

    i - enter insert mode
    a - move right one column and enter insert mode 
    o - insert a new line below current line and enter insert mode on that line
    O - insert a new line above current line and enter insert mode on that line
    space - create a new line under the current line
    shift+space - create a new line above the current line
    v - enter select mode (visual mode from vi)
    / - find
    n - go to next occurance of found word
    N - go to previous occurance of found word
    # - go to next occurance of word under cursor
    r - find and replace
    u - undo
    U - redo
    p - paste, will place multi line blocks of code on line below
    P - paste, will place multi line blocks of code above current line

    1-9 - goto line, just type the line number and it will take you there

    [ - go to function definition if it can be found
    ? - open code outline

    m - mark current line
    M - open bookmark list
    , - goto previous bookmark
    . - goto next bookmark

    z - recenter screen

    -(minus) - comment line
    x - delete character under cursor
    ~ - toggle case of character under cursor

    d - cut current line
    y - copy current line

    W - save project
    R - run game

    c - delete word under cursor and enter insert mode
        if over a delimiter or quotation, delete contents contained and enter insert mode
    C - delete until the end of the line and enter insert mode

    > - indent line
    < - dedent line

    alt + f - toggle font size
    alt + s - toggle font shadow

#### Select Mode

    escape - switch to normal mode
    -(minus) - comment block
    y - copy block
    d - cut block
    p - paste over block
    c - delete block and enter insert mode
    > - indent block
    < - dedent block
    / - find populating current selection
    r - find and replace within block
    ~ - toggle case in block

