`eval <code>` or `= <code>`

## Parameters
* `<code>` the code you want to run. It should use the same language used by the cart.

## Description
Run code in the console.
Use [trace](https://github.com/nesbox/TIC-80/wiki/trace) to log the results.

You need to run a cart first to launch the virtual machine, otherwise you'll get an empty string.

## Example

```bash
>eval trace("Hello World")
Hello World
>eval t=8

>eval trace("Floor division of 32 by 10 is "..32//10)
Floor division of 32 by 10 is 3
```