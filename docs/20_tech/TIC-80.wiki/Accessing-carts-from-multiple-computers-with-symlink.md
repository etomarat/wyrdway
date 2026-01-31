This tutorial is only for Linux Machines & Windows PCs at the moment.

You will learn a hacky way to access and edit your TIC carts from multiple computers without copying and pasting!

1. Make a new directory for tic files to a cloud storage folder, say `Drive\TIC-80\` or `~/cloud/TIC-80/`
2. Create a directory with name `appdata` (or whatever suits you) in that folder.
3. Open TIC-80 and use command `folder` to go to TIC's appdata folder (it's where TIC carts are stored.)
4. Go one folder up (to folder `Appdata/roaming/com.nesbox.tic/` on Windows)
5. Rename folder TIC-80 to TIC-80-temp or something, you won't be using it anymore...
6. Make a symlink ([symbolic link](https://en.wikipedia.org/wiki/Symbolic_link)) to your previously created folder with command (you can copy the exact folder names by clicking the address panel in File Explorer).
   * Windows:
      * (You'll need an elevated (admin) command prompt! open it by right-clicking Command Prompt -> run as administrator)
      * Use the command `Mklink /D C:\Users\your_username\AppData\Roaming\com.nesbox.tic\TIC-80 "C:\Users\your_username\Drive\TIC-80\appdata"`
    * Linux:
       * `mkdir TIC-80`
       * Use the command `ln -s /path/to/original/TIC-80 /path/to/cloud/folder/TIC-80/appdata`


Now TIC-80 will use the folder in your cloud storage as its appdata folder and you can run your carts from any computer!