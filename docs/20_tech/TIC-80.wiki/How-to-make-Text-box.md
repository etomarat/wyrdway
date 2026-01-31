Hello how are you?  Hope you are ok, let's teach you how to make a text box using Lua!

![Textbox_working_in_game](https://raw.githubusercontent.com/ATSxp/My_games_in_TIC-80/main/ImagesWiki/video3.gif)

Before I start I want to credit this text box wonder to 「petet」 (game developer like "BALMUNG", also made on the TIC-80), if I hadn't taken a look at the BALMUNG source code I would never have learned how to do that.  Well, looks like we can get started.

## Workspace

Let's start by writing our desktop, it will look like this:
```lua
-- title:  How to Make a Text Box in Lua
-- author: (you)
-- desc:   Tutorial
-- script: lua

t=0

function TIC()
	cls()
	
	t=t+1
end
```
## Adding variables

Let's create three variables: `dialogue` a table responsible for storing the texts, `layer` as its name says it will take care of the table layers and `text_pos` which will be the position of the letters from beginning to end.
```lua
dialogues = {}
layer = 1
text_pos = 1
```
Next we will create a function named `addDialogues`, its parameters are a `table`.
```lua
function addDialogues(table)
	dialogues = table
end
```
Now is the time to create the textbox system.  In the `TIC` function, I'm going to create two ​​local variables, one carrying the strings and the other holding their length, for that we use the function (already built in Lua) `string.len (string)`, it returns the length of the text
```lua
-- error
local string = dialogues[layer]
local lenght = string.len(string)
-- error
```
But since Lua won't allow us to have a variable with the length of a string that doesn't exist (since `dialogues` is empty) let's put them inside an `if`:
```lua
if dialogues ~= nil and dialogues[layer] ~= nil then
	local string = dialogues[layer]
	local lenght = string.len(string)
end
```
Now we can continue, let's make an `if` statement saying "if this button is pressed and the text has not ended, end the text, otherwise, skip to the next dialog".  Practice time.
```lua
if dialogues ~= nil and dialogues[layer] ~= nil then
	local string = dialogues[layer]
	local lenght = string.len(string)
		
	if btnp(4) and text_pos >= 2 then
		
		if text_pos < lenght then
			text_pos = lenght
		else
			text_pos = 1
			layer = layer + 1
		end
			
	end
end
```
In this code we are saying "if you press the A/Z button and the letter position is greater than or equal to 2 then enter the second instruction", "if `text_pos` is less than its length then complete the dialog otherwise reset the position and skip to the next text". In a moment we will see the result of this code.

For a text box to be a text box what does it need?  From a box of course!  So let's draw our box.

In the same `if` statement we will create another statement, in it we will say "if the layer is less than or equal to the length of the dialog table then draw the box and the text".
```lua
if layer <= #dialogues then
	rect(0,68/2,240,68,15)
	rectb(0,68/2,240,68,12)
end
```
We draw the text with the `print` function, in it we will use the local variable we created up there at the beginning of the first statement:
```lua
if layer <= #dialogues then
	rect(0,68/2,240,68,15)
	rectb(0,68/2,240,68,12)
	print(string,5,68/2+5,13)
end
```
if you did everything right and run the cartridge you will see that there is nothing drawn on the screen as this is all a lie and there is no textbox tutorial, goodbye 'v'.

It did not leave the screen! The answer to this is because we didn't add any dialog, to add a dialog we need to call the `addDialogues` function like this:
```lua
addDialogues( { "Hello World!" } )
```
![draw_box](https://raw.githubusercontent.com/ATSxp/My_games_in_TIC-80/main/ImagesWiki/screen1%20(2).gif)

We're looking at our text box, but when we press A/Z it doesn't turn off, remember the `text_pos` variable?  So, we made an instruction saying that if its length were full the box would jump to another dialog.  So let's do this:
```lua
if layer <= #dialogues then
	rect(0,68/2,240,68,15)
	rectb(0,68/2,240,68,12)
	print(string,5,68/2+5,13)
			
	if text_pos < lenght then
		text_pos = text_pos + 1
	end
			
end
```
Now try... you saw how we managed to turn off the box, but seriously, you didn't think we created a global variable just to turn off a text box did you?  Now comes the fun idea!  Let's use the `string.sub()` function, as far as we know it replaces words from the desired string, so let's do the following in the `print` function:
```lua
print(string.sub( string , 1, text_pos),5,68/2+5,13)
```
Our text is being drawn little by little, if you are interested and want to understand `string` functions read the Lua documentation, did you find the letters too fast?  Try this in the statement where we update `text_pos`:
```lua
if text_pos < lenght and t % 4 == 0 then
		text_pos = text_pos + 1
end
```
So, if you want to write some text on the next layer just add a `,` in the table and write another string:
```lua
addDialogues( { "Hello World!" , "Good Night!", "Good Morning"} )
```
![Text_in_movement](https://raw.githubusercontent.com/ATSxp/My_games_in_TIC-80/main/ImagesWiki/video1%20(8).gif)

Final code:
```lua
-- title:  How to make a Text box in lua
-- author: @ATS_xp
-- desc:   Tutorial
-- script: lua

t=0

dialogues = {}
layer = 1
text_pos = 1

function addDialogues(table)
	dialogues = table
end

addDialogues( { "Hello World!" , "Good Night!", "Good Morning"} )
function TIC()
	cls()
	
	if dialogues ~= nil and dialogues[layer] ~= nil then
		local string = dialogues[layer]
		local lenght = string.len(string)
		
		if btnp(4) and text_pos >= 2 then
		
			if text_pos < lenght then
				text_pos = lenght
			else
				text_pos = 1
				layer = layer + 1
			end
			
		end
		
		if layer <= #dialogues then
			rect(0,68/2,240,68,15)
			rectb(0,68/2,240,68,12)
			print(string.sub( string , 1, text_pos),5,68/2+5,13)
			
			if text_pos < lenght and t % 4 == 0 then
				text_pos = text_pos + 1
			end
			
		end
	end
	
	t=t+1
end
```

Bye!