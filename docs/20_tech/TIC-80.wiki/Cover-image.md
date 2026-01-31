The cover image is the image that will be displayed in the [official website](https://tic80.com/) or in the `surf` menu.

It is necessary for your cart to have a cover image before being uploaded to the TIC-80 website, as well as `title` and `author` tags in the [metadata](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata).  

# Add a cover image
## From the game
Run the game, press F7 to take a screenshot which will be your cover image, and then save.  
On mobile you might need to change the [input tag](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata#the-input-tag) to display the keyboard.

You can also do it programmatically using `sync(128,0,true)` in your code.

## From an external image
Use [import](https://github.com/nesbox/TIC-80/wiki/import) command to import an image you want to use as cover image. To use `file.png` as cover, in the console use `import screen file.png` command. The image should be in PNG format and 240×136 pixels size.  
Note that you can use [external tools](https://github.com/nesbox/TIC-80/wiki/Tools) to convert a high resolution image to TIC-80 format.

## From another cart
Open your cart in TIC-80 and then [load](https://github.com/nesbox/TIC-80/wiki/load) the cover of another cart with `load other_cart.tic screen`.

## About import/load
While importing images or loading from another cart, colors are merged to the closest color of the palette.  
For example, with default palette, this image:  

![easter](https://github.com/nesbox/TIC-80/assets/26139286/a317730e-0f5d-44c0-8ef3-5790314f0d42)  

becomes:  

![import_screenshot](https://github.com/nesbox/TIC-80/assets/26139286/2f9ec2fe-5ca7-4592-b429-e25b0a555094)

# Show Cover Image
There is two ways to check the cover image of a cartridge before uploading to the website.

### Display Cover Image
Running a cart with an empty `TIC()` function will display the cover image if there is one.
```lua
function TIC()
end
```

### Export Cover Image
To export the cover image, load the cartridge and do `export screen my_cover`.