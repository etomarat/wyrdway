- `key(code) -> is_pressed`
- `key() -> is_any_pressed`

## Parameters
* **code** : the key code to check (1..65), see the table below or type `help keys` in console.

## Returns
* **pressed** : a Boolean value which indicates whether or not the specified key is **currently** pressed. 
* **is_any_pressed** : If no keycode is specified, returns a Boolean value indicating if any key is pressed.

**Keycodes:**

| Letters | Digits | Characters        | Edits / <br />Directions | Modifiers / <br />Function Keys | Numeric Keypad      |
|---------|--------|-------------------|--------------------------|---------------------------------|---------------------|
| 01 = A  | 27 = 0 | 37 = MINUS        | 50 = RETURN              | 62 = CAPSLOCK                   | 79 = NUMPAD0        |
| 02 = B  | 28 = 1 | 38 = EQUALS       | 51 = BACKSPACE           | 63 = CTRL                       | 80 = NUMPAD1        |
| 03 = C  | 29 = 2 | 39 = LEFTBRACKET  | 52 = DELETE              | 64 = SHIFT                      | 81 = NUMPAD2        |
| 04 = D  | 30 = 3 | 40 = RIGHTBRACKET | 53 = INSERT              | 65 = ALT                        | 82 = NUMPAD3        |
| 05 = E  | 31 = 4 | 41 = BACKSLASH    |                          |                                 | 83 = NUMPAD4        |
| 06 = F  | 32 = 5 | 42 = SEMICOLON    | 54 = PAGEUP              | 66 = ESC                        | 84 = NUMPAD5        |
| 07 = G  | 33 = 6 | 43 = APOSTROPHE   | 55 = PAGEDOWN            | 67 = F1                         | 85 = NUMPAD6        |
| 08 = H  | 34 = 7 | 44 = GRAVE        | 56 = HOME                | 68 = F2                         | 86 = NUMPAD7        |
| 09 = I  | 35 = 8 | 45 = COMMA        | 57 = END                 | 69 = F3                         | 87 = NUMPAD8        |
| 10 = J  | 36 = 9 | 46 = PERIOD       | 58 = UP                  | 70 = F4                         | 88 = NUMPAD9        |
| 11 = K  |        | 47 = SLASH        | 59 = DOWN                | 71 = F5                         | 89 = NUMPADPLUS     |
| 12 = L  |        | 48 = SPACE        | 60 = LEFT                | 72 = F6                         | 90 = NUMPADMINUS    |
| 13 = M  |        | 49 = TAB          | 61 = RIGHT               | 73 = F7                         | 91 = NUMPADMULTIPLY |
| 14 = N  |        |                   |                          | 74 = F8                         | 92 = NUMPADDIVIDE   |
| 15 = O  |        |                   |                          | 75 = F9                         | 93 = NUMPADENTER    |
| 16 = P  |        |                   |                          | 76 = F10                        | 94 = NUMPADPERIOD   |
| 17 = Q  |        |                   |                          | 77 = F11
| 18 = R  |        |                   |                          | 78 = F12
| 19 = S  | 
| 20 = T  | 
| 21 = U  | 
| 22 = V  | 
| 23 = W  | 
| 24 = X  | 
| 25 = Y  | 
| 26 = Z  | 


```
.-----------------------------------------------------------------------------------------.
| ESC |  F1  |  F2  |  F3  |  F4  |  F5  |  F6  |  F7  |  F8  |  F9  |  F10 |  F11 |  F12 |
.-----------------------------------------------------------------------------------------.  .----------------------.  .------------------------------.
|  `  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  |  0  |  -  |  =  |  Backsps  |  |  Ins  |  Home | PgUp |  | NumLck | NP/ | NP* |   NP-   |
|-----------------------------------------------------------------------------------------|  |----------------------|  |------------------------------|
|  Tab   |  Q  |  W  |  E  |  R  |  T  |  Y  |  U  |  I  |  O  |  P  |  [  |  ]  |   \    |  |  Del  |  End  | PgDn |  |   NP7  | NP8 | NP9 |         |
|-----------------------------------------------------------------------------------------|  '----------------------'  |--------------------|   NP+   |
|  CapsLck  |  A  |  S  |  D  |  F  |  G  |  H  |  J  |  K  |  L  |  ;  |  '  |    Enter  |                            |   NP4  | NP5 | NP6 |         |
|-----------------------------------------------------------------------------------------|          .-------.         |------------------------------|
|  Shift       |  Z  |  X  |  C  |  V  |  B  |  N  |  M  |  ,  |  .  |  /  |       Shift  |          |   Up  |         |   NP1  | NP2 | NP3 |         | 
|-----------------------------------------------------------------------------------------|  .----------------------.  |--------------------| NPEnter |
|  Ctrl  |  Alt  |                                                       |  Alt  |  Ctrl  |  |  Left |  Down | Rght |  |       NP0    | NP. |         |
'-----------------------------------------------------------------------------------------'  '----------------------'  '------------------------------'
```

**Note**: Esc, F7-F9 and F11 already are functional [hotkeys](https://github.com/nesbox/TIC-80/wiki/Hotkeys#general) in game.

## Description
The function returns *true* if the key denoted by *keycode* is pressed otherwise it returns **false**.


## Download key map
[keycodes.txt](https://github.com/nesbox/TIC-80/files/13694793/keycodes.txt)


## Input Tag
Set the [metadata](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata#the-input-tag) `input` tag to `keyboard` to display only the on-screen keyboard on Android devices and hide the gamepad.