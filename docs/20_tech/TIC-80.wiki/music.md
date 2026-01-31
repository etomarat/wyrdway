_This function was enhanced in version 0.90._


`music([track=-1], [frame=-1], [row=-1], [loop=true], [sustain=false], [tempo=-1], [speed=-1])`

...or to stop the music:

`music()`

## Parameters

* **track** : the id of the track to play (0..7)
* **frame** : the index of the frame to play from (0..15)
* **row** : the index of the row to play from (0..63)
* **loop** : loop music (true) or play it once (false)
* **sustain** : sustain notes after the end of each frame or stop them (true/false)
* **tempo** : play track with the specified tempo, _(added in version 0.90)_
* **speed** : play track with the specified speed, _(added in version 0.90)_

## Description

This function starts playing a **track** created in the [Music Editor](https://github.com/nesbox/TIC-80/wiki/Music-Editor).

### Tip

If you call music() within `TIC()`, the specified track will restart 60 times per second - probably not what was intended! You'll need to add conditional logic to ensure that the track isn't continuously restarted, for example:

```lua
musicplaying = false

function TIC()
    -- ensure we only start the music a single time
    if not musicplaying then
        music(0)
        musicplaying = true
    end
end
```
