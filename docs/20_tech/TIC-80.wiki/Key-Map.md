TIC supports input from up to 4 players. The keymap can be changed in the **Game Menu** which can be accessed by issuing the 'menu' command in the console or pressing escape during play in an exported cart. From the Game Menu, select 'Gamepad Config' then choose the desired tab, #1 to #4, for the relevant player.

[btn](btn)(id) returns true if button is pressed in the current frame.
[btnp](btnp)(id) returns true if pressed in the current but wasn't pressed in the previous frame.

Here's a table that summarizes the ID's to interrogate:

|Action |P1 ID |P2 ID |P3 ID |P4 ID |
|:-----:|:----:|:----:|:----:|:----:|
|Up     |0     |8     |16    |24    |
|Down   |1     |9     |17    |25    |
|Left   |2     |10    |18    |26    |
|Right  |3     |11    |19    |27    |
|A      |4     |12    |20    |28    |
|B      |5     |13    |21    |29    |
|X      |6     |14    |22    |30    |
|Y      |7     |15    |23    |31    |

**Note: Specifying any button index below 0 or above 31 will wrap around the value consecutively.**

The default keymapping for Player 1 is:

|Action |Key (QWERTY)|
|:-----:|:----------:|
|Up     |Up Arrow    |
|Down   |Down Arrow  |
|Left   |Left Arrow  |
|Right  |Right Arrow |
|A      |Z           |
|B      |X           |
|X      |A           |
|Y      |S           |

**Note: The Android version of TIC-80 only has access to the first game pad. It ignores key bindings and places virtual buttons on the screen. Any TIC-80 programs that use key bindings as the basis must be what is in the table above.**