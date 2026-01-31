_This function was added to the API in version 0.80._

`tstamp() -> timestamp`

## Returns

* **timestamp** : the current Unix timestamp in _seconds_

## Description

This function returns the number of _seconds_ elapsed since January 1st, 1970.  This can be quite useful for creating persistent games which evolve over time between plays.

## Example

![Example](https://i.imgur.com/dCUa09x.gif)

``` lua
-- title: timestamp demo

elapsed = -1

function TIC()
  cls(15)

  -- Display the current time stamp
  current = tstamp()
  print('Timestamp: ' .. current, 10, 10, 1)

  -- Calculate how long ago they last played
  last = pmem(0)
  if last <= 0 then
    last = current
  end
  if elapsed == -1 then
    elapsed = current - last
  end
  pmem(0, current)

  -- Display the elapsed time away
  print('Time away: ' .. elapsed, 10, 24, 1)
end
```