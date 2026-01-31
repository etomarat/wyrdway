`pmem(index) -> val32` Retrieve value from persistent memory

`pmem(index, val32) -> prior_val32` Save new value to persistent memory, retrieve prior value.

## Parameters

* **index** : an index (0..255) into the persistent memory of a cartridge.
* **val32** : the 32-bit integer value you want to store. Omit this parameter to read vs write.

## Returns

* **val32** : the current/prior value saved to the specified memory slot.

## Description
The name "pmem" means **persistent memory**. This function allows you to save and retrieve data in one of the 256 individual 32-bit slots available in the cartridge's persistent memory. This is useful for saving high-scores, level advancement or achievements. Data is stored as unsigned 32-bit integer (i.e. in the range 0 to 4294967295, default is 0).

When writing a new value, the previous value is returned.

### Memory Persistence
* pmem depends on the cartridge hash (md5) and therefore **existing data will be erased if the script is changed**.
* Specifiying *saveid:* with a personalized string in the header [metadata](https://github.com/nesbox/TIC-80/wiki/Cartridge-Metadata) will override the default MD5 calculation. This allows the user to update a script without losing saved data.

### Memory Save Location
pmem saves the data in a folder on the user's computer, which is different depending on the host operating system;
* Windows: `%APPDATA%\com.nesbox.tic\TIC-80\.local`
* MacOS: `~/Library/Application Support/com.nesbox.tic/TIC-80/.local`
* Linux: `~/.local/share/com.nesbox.tic/TIC-80/.local`

The filename will be the MD5 hash either computed from the file or of the saveid.

## Example
Use pmem to save how many times the cart has been started.

![pmem_demo](https://github.com/nesbox/TIC-80/assets/26139286/6099ede8-f5f6-4fd4-ba2b-6e6f5c39c14e)

``` lua
--pmem demo
--load saved value at slot zero and save it back
--incremented by 1
pmem(0,pmem(0)+1)

function TIC()
 cls()
 print("Started "..pmem(0).." times");
end

```