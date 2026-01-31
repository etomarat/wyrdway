The Hello World cartridge is the default cart created by the `new` command.

## Code
### Lua
```lua
t=0
x=96
y=24

function TIC()

	if btn(0) then y=y-1 end
	if btn(1) then y=y+1 end
	if btn(2) then x=x-1 end
	if btn(3) then x=x+1 end

	cls(13)
	spr(1+t%60//30*2,x,y,14,3,0,0,2,2)
	print("HELLO WORLD!",84,84)
	t=t+1
end
```

## Sprite Animation Explanation
The first argument of the `spr` function corresponds to the sprites indices. The formula  `1+t%60//30*2` switches from one sprite to the other to animate the character.  

Let's explain it:  
The two sprites have indices 1 and 3 so we need something that switches from 1 to 3 regularly.  

In lua `%` is the modulo operator, it returns the remainder of the division.
```bash
> eval trace(154 % 60)
34
```
Because 154 is 2×60+34.  
So mechanically `t%60` increases with t from 0 to 59 and then restart at 0 when t is a multiple of 60.  

`//` is the floor division, it divides the number, then truncates it.  
```bash
> eval trace(34//30)
1
```
So `t%60//30` will be 0 when `t%60`<30 and 1 else.  
Therefore `1+t%60//30*2` switches between 1 and 3.

## Edit Hello World Template
The default Hello World cartridge template can be modified using `config default` command. That can be used to use a custom palette for all your projects. Do not forget to save.