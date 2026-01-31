You can create your own theme by modifying the [configuration file](https://github.com/nesbox/TIC-80/wiki/config).  
It is possible to modify:
* Sprites like: cursor, fonts, virtual keyboard, buttons, icons…
* The palette
* The SFX
* The screen size…

## Use Shared Themes
Use other's themes by replacing your configuration cart by the theme cart.  
The path to the `config.tic` file is displayed by the `config` command. 

![Use_theme](https://github.com/nesbox/TIC-80/assets/26139286/0e1188ac-850a-43b5-a741-ff4d43453165)

You can also choose to use only part of the theme by using the `load` [function](https://github.com/nesbox/TIC-80/wiki/load) to load only the code, sprites, palette... to your `config.tic` cart.

## Example Themes
Share your theme here.

### Red Theme by Skeptim
I changed the palette keeping the Sweetie16 colors but reorganizing them, and I re-drew most of the sprites.<br>The theme cart is at https://tic80.com/play?cart=3609
<br>
<p align="center">
<img src="https://github.com/nesbox/TIC-80/assets/26139286/13a9d9c3-0271-495e-a7f4-ddf23056fb75" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/26139286/2fab4889-e201-4d73-8bda-afc65b0dddee" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/26139286/0daaa866-5b4b-4c12-a25d-58dd057700d9" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/26139286/ea4ba4c0-7b2c-4516-8a1d-8f30e65f4779" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/26139286/e6bed177-d62d-47c1-9a25-bfe251103621" width="410">
</p>

### MypkaXMAS by MypkaMax
This theme was designed to celebrate Christmas 2023.<br>
In addition to changing colour numbers used by the code editor, this theme also adds a custom palette, sound effects, font and even the keyboard graphic.<br>The theme cart is at https://tic80.com/play?cart=3639
<br>
<p align="center">
<img src="https://github.com/nesbox/TIC-80/assets/45672221/607ceedc-c923-4228-a0ae-e0e6607da385" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/45672221/ef94206d-1f3b-4510-9062-a47457cd707f" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/45672221/0eb796ac-611b-4bda-ad09-859ff03e8417" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/45672221/0c4be56f-6934-43e6-8810-62f5dbc82780" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/45672221/c7f4bf90-6864-40d6-b784-d611f24c9e6c" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/45672221/503ac583-5b4b-4598-8d07-30450f6b3b61" width="410">
<img src="https://github.com/nesbox/TIC-80/assets/45672221/60485836-2003-4676-bb5c-36c9dca05d4b" width="410">
</p>

## Editor screenshot as cover image
Running a cart with an empty `TIC()` function will display the cover, or if there is no cover, it will keep the screen as it is.
Therefore one can switch to the editor of choice, run the game with empty `TIC()` function to get the editor displayed in game and press F7 to get this editor as cover.
```lua
function TIC()
end
```
That works better with some editors than others.