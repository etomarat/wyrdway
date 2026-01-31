Crostini is a Linux container with a minimal Debian setup as the operating system.

Follow these steps to install TIC-80 on your ChromeOS-based system via Crostini.

# Requirements

* A recent Chromebook/Chromebox/Chromebit/etc. (2020 or later)
* If ChromeOS is managed, you might not be able to enable Crostini

# Install

**NOTE: If updating TIC-80, do not follow these steps! Instead, follow [these steps](#updating).**

1. Open the Settings application. Select "Advanced", then "Developers".
2. Click "Turn on" to enable Linux via Crostini. Follow the steps on the screen.
3. Be patient. When you get a terminal window, exit it.
4. [Download TIC-80](https://github.com/nesbox/TIC-80/releases) (download the Linux build). Open the file you downloaded and click "Install".
2. TIC-80 will be located in the **Linux apps** folder. Open it (it's indicated by a penguin icon because Crostini does not know TIC-80's icon) and start creating games in a tiny computer.

## Additional support fixes

I recommend enabling these hidden support addons which can be found in `chrome://flags`. Search them up with their names or IDs:

* Crostini GPU Support (`crostini-gpu-support`): Fixes a few issues with software-based graphics, such as wobbling.
* Crostini IME Support (`crostini-ime-support`): Uses your keyboard method to type TIC-80 inputs, instead of the Linux kernel's default `en-US`.
* Crostini Virtual Keyboard Support (`crostini-virtual-keyboard-support`): Only required if you use tablet mode or On-Screen Keyboard. Enables you to use the virtual keyboard to type TIC-80 inputs. This can be useful if you use tablet mode.

## Updating

1. Open **Terminal** and select **`penguin`**. Run this command to backup configuration:

   ```bash
   cp -r $HOME/.local/share/com.nesbox.tic $HOME/ticbackup
   ```
   
2. Remove TIC-80 with one of these methods:
  
   * With a GUI:

      1. Press **Search**/**Launcher**.
      2. Open the "Linux apps" folder. Right-click on TIC-80.
      3. Click **Uninstall** and confirm.
   
   * With `apt`:
     ```bash
     sudo apt purge tic80 --yes
     ```

3. [Download TIC-80](https://github.com/nesbox/TIC-80/releases) (download the Linux build). Open the file you downloaded and click "Install".

4. Restore configuration:

   ```bash
   rm -r $HOME/.local/share/com.nesbox.tic
   cp -r $HOME/ticbackup $HOME/.local/share/com.nesbox.tic
   ```

5. Delete the backup:
   
   ```bash
   rm -r $HOME/ticbackup
   ```

# Known issues

Please edit this page if you run into an issue ;)

## Crostini

### "Turn on" is greyed out

The ChromeOS installed on your system cannot run Linux.

**Bug in TIC-80?** No.

**Bug in ChromeOS?** No.

## Rendering

### Fullscreen breaks ChromeOS rendering

Enabling full screen causes a problem with rendering ChromeOS.

**Bug in TIC-80?** Yes.

#### Possible fix

This issue appears to be a bug in SDL2, causing incompatibility and breakages with fullscreen in virtual machines that share VM windows with the host, such as Crostini.

The only known fix is to remove the TIC-80 configuration folder, forcefully resetting TIC-80:

1. Press **Search**/**Launcher** and type "terminal", then press **Enter**.
2. Click the Terminal icon on the shelf with two fingers (or hold it), and click "Shut down Linux". TIC-80 will close.
3. Click "penguin" to start Linux.
4. Wait until you get a shell prompt, then run the following command:
   
   ```bash
   rm -r $HOME/.local/share/com.nesbox.tic
   ```
   
   **Warning:** This resets TIC-80 to default preferences. You should back up this folder,
   ideally with:
    
   ```bash
   cp -r $HOME/.local/share/com.nesbox.tic $HOME/ticbackup_$RANDOM
   ```
   
   The command above will back up the current TIC-80 configuration to your Linux home directory.
5. Close the terminal and run TIC-80 again. TIC-80 configuration will be recreated.