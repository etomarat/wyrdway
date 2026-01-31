Note: The engine can be found here: https://tic80.com/play?cart=2367

## What is Platform Engine?
The goal of Platform Engine is help quickly build and setup a side-scrolling platformer by having the most common mechanics setup; in an easy and extensive way. Enabling a programmer or designer to worry more about graphics and level design. The code is commented with how it is used/implemented to help make changes easier. It is best used for 16x16 sprites for the player, though with some changes to the collision variables it could be made to use 8x8.

## What mechanics are included?
A player that can move, jump, duck, and crawl.
Ability to move through platforms.
Easy to adjust player collision detection.
Collectibles.
Simple high score save system.
Sample enemies that damage the player.
Sample mouse code.
Camera code for different scenarios (may break enemy placement).
State machine by turning functions into variables.
Win and non-win conditions.

This engine touches on many aspects that are found in platforming games, but is not a full set of gameplay mechanics. It is a foundation to start on your own games.

## Is there anything cool in the engine?
One massive tool included in the engine is the dynamic collision detector for the player. Below is the variables. The points that represent these can be see around the player from the information in game. (Pressing I in game)

```lua
coll={
    tlx=1, --Defines where the left collider is
    tly=1, --Defines where the top collider is
    trx=14,--Defines where the right collider is
    cly1=7,--Defines where the left top mid collider is 
    cly2=8,--Defines where the left bottom mid collider is
    cry1=7,--Defines where the right top mid collider is
    cry2=8 --Defines where the right bottom mid collider is
}

```
Changing these variables will allow the player to have different collisions. These can be changed during runtime, which enables things such as crawling.