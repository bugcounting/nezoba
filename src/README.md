# The Nez-Oba software

This directory contains all parts of the Nez-Oba software.

   - Directory [board/](/src/boards/) includes an Arduino project in
     C++, which is the program running on the board and emulates a
     gamepad. The `README` there outlines the code's structure and
     functionality.
	 
   - One of the libraries needed by the the Arduino project have to be
     patched to work with the used hardware. Directory [libs/](/src/libs/)
     includes patch a file to do so.
	 
   - Directory [data/](/src/data/) includes a sample mappings in YAML
     format. This includes several button-to-key-presses mappings that
     are useful to play 2D platformers on the Nintendo Switch or on a
     PC.
	 
   - Directory [nezoba](/src/nezoba/) includes the Python code
     implementing all of the functionality at the user's end,
     including a web-based GUI and a simple command-line interface to
     program the board. The `README`s there outline each package's
     functionality.
	 
   - Directories [src/remapper/](src/remapper/) and
     [test/remapper/](test/remapper/) include the Python
     implementation of a simple interactive shell and its tests. The
     shell can be used to define the button mappings that will be
     uploaded to the controller. See the `README` in those directories
     for details about how the shell is implemented and tested.
	 
   - The current directory's [nez-sw.py](nez-sw.py) is a Python script
     that can setup the Arduino compiler, install all dependencies,
     run the shell to define button mappings, and compile and deploy
     the controller software with the defined button mappings.
	 
The rest of this document describes some low-level details mainly
useful for future portability.
 

## Environment

This software has been developed and tested on a GNU/Linux Ubuntu
22.04 system. It should work without issues on any other Linux system,
and arguably also on other flavors of Unix. It should also be
adjustable to work on Windows systems without major hassle; however, I
didn't have a chance to test compatibility with that operating system,
and I will probably never care to do it.


## Portable Arduino frameworks
 
The [board's software](/src/board/) targets the Arduino ecosystem, and
was written using the [Arduino
IDE](https://www.arduino.cc/en/software). In order to compile and use
it, you also need to install the Arduino framework.

The main app `nezoba` takes care of installing the framework with all
dependencies under path `$SYSTEM_DIR`:
 
 ```sh
 nezoba setup "$SYSTEM_DIR"
 ```
 
The outcome of successfully running the `setup` command is the
command-line version of a [portable
IDE](https://www.arduino.cc/en/Guide/PortableIDE). This means that if
you save the keep the content of `$SYSTEM_DIR`, you can use it to
recompile and redeploy the controller software at any time in the
future, even after some of the dependencies are no longer available.
 
If you prefer to have the full Arduino IDE (for instance, to debug
changes of functionality in the software), [below I
describe](#portable-arduino-ide-with-dependencies) the manual steps to
do that. The `setup` command does exactly the same things but
automatically and using the CLI version of the Arduino framework;
therefore, the steps detailed below also serve as a documentation of
the behavior of the `setup` command.

In turn, these instructions are derived from the [NSGadget
project](https://github.com/gdsports/NSGadget_HID/tree/master/examples/NSGamepad),
which I found to be the one with the clearest and up-to-date
documentation among the several open-source projects that deal with
Nintendo Gamepad emulation. I adapted and updated the NSGadget's setup
to make it work with the MCP module and with my specific
configuration.


## Upload troubleshooting

When you `deploy` a mappings and the controller software onto a board,
the final upload step is often the most delicate. Here's how to deal
with common issues.

### Plug in the board

Make sure that the board is plugged in to a USB port before uploading.
You should see a port (usually, `/dev/ttyACM0`) pop up after the board
is connected.  There's no need to "activate" the board by pressing a
button.

### Port permissions

If you get an error `Opening port at 1200bps: Permission denied`, it
probably means that your user doesn't have access to the right groups
to access the port:

- Check whether groups `dialout` and `tty` are among the user's
  groups:

```sh
groups
```

- If they are not, add the user to the groups:

```sh
sudo usermod -a -G dialout,tty $USER
```

- This change of groups only works after the next login. To add the
  user to the groups right away:
  
```sh
newgrp tty
newgrp dialout
```

- If all else fails, you can try to change the permissions of the port:

```sh
sudo sudo chmod a+rw /dev/ttyACM0
```
### Resetting the board

After the first upload of the modified firmware, it should also no
longer be needed to reset the board to upload to it. Should you need
to reset the board, double-click on the reset button before launching
the upload. (The reset button is reachable from the little hole in the
back of Nez-Oba's case. After you reset, the led should [go from
purple to
green](https://learn.adafruit.com/adafruit-trinket-m0-circuitpython-arduino/circuitpython)).


## Portable Arduino IDE with dependencies

Here is the list of steps to setup a portable Arduino IDE with all
dependencies to compile and deploy the nez-oba controller software.

   1. Download the Arduino IDE for your computer as a zip file
      `arduino-ide.tar.xz`.
   
      - I used version
        [1.8.19](https://www.arduino.cc/en/Main/OldSoftwareReleases#previous)
        but more [recent versions](https://www.arduino.cc/en/software)
        should also work.
	   
      - The script installs [Arduino CLI
        0.21.0](https://github.com/arduino/arduino-cli/releases).
	   
   2. Install the IDE in portable mode to `$INSTALL_TO`, and launch it.
   
   ```bash
   tar xvf arduino-ide.tar.xz
   mv arduino-ide/ $INSTALL_TO
   cd $INSTALL_TO
   mkdir portable
   ./arduino
   ```
   
   3. Under **File -> Preferences**:

      - Uncheck **Check for updates on startup**
	  
	  - Add
        <https://adafruit.github.io/arduino-board-index/package_adafruit_index.json>
        to **Additional Board Manager URLs** (or follow other
        instructions from [Adafruit's
        documentation](https://learn.adafruit.com/adafruit-metro-m0-express-designed-for-circuitpython/arduino-ide-setup)).
		
   4. Under **Tools -> Board -> Boards Manager**:
   
      - Install **Arduino SAMD Boards** version 1.8.12 (more recent
        versions should still work).
		
	  - Install **Adafruit SAMD Boards** version 1.5.14 (more recent
        versions do not work with the `NSGadget_HID` library we'll use!).
		
   5. Restart the IDE.
   
   6. Download project https://github.com/NicoHood/HID version (tagged release) 
      2.8.3. This is the key library that performs controller
      emulation. This is a very actively maintained project (at the
      time of writing); more recent versions may work, but the patch
      that we'll apply has to be compatible with the changes.
	  
      - Download the project as zip file, and install it in Arduino
        IDE by selecting the zip under **Sketch -> Include Libraries ->
        Add .ZIP library**.
		
      - After installing, download the other project
        https://github.com/gdsports/NSGadget_HID commit
        `dfdcb35a07`. This is an extension of the HID project that
        supports emulation of Nintendo Switch gamepads. (The project
        also has an installation script with Arduino CLI, but here we
        simply get the files that we are going to use.) More recent
        versions may also work, but if the HID API undergoes breaking
        changes we may have to also refactor our controller software.
		
	  - Anyway, after downloading the `NSGadget_HID` project, copy the
        content of directories `src/SingleReport` and `src/HID-APIs`
        to the corresponding directories in the installed HID project
        (at `$INSTALL_TO/portable/sketchbook/libraries/HID/`). This
        should copy 4 files in total, 2 in each directory.
		
      - Edit file
        `$INSTALL_TO/portable/sketchbook/libraries/HID/src/HID-Project.h`
        by adding the following after `#include "SingleReport/SingleGamepad.h"`:
		
		```cpp
		#include "SingleReport/SingleNSGamepad.h"
		```
		
		Equivalently, patch it with file `libs/HID-Project.h.patch`. 
		This modification includes the `NSGadget_HID`'s extension headers 
		into the HID library.
		
   7. Edit the SAMD boards file
      `$INSTALL_TO/portable/packages/adafruit/hardware/samd/1.5.14/boards.txt`
      so that the uploaded image will use vid and pid numbers that
      are recognized as a Nintendo-compatible gamepad:
	  
      - Find the following two lines and comment them out with `#`:
	  
	  ```
	  adafruit_trinket_m0.build.vid=0x239A
      adafruit_trinket_m0.build.pid=0x801E
	  ```
	  
	  - Add the following two lines just below the commented out lines:
	  
	  ```
	  adafruit_trinket_m0.build.vid=0x0F0D
      adafruit_trinket_m0.build.pid=0x00C1
	  ```
	  
   8. That's it! Now the portable Arduino IDE has all the
      dependencies and options needed to compile and install the
      nez-oba controller software. Remember to switch to 
	  **Tools -> Board -> Adafruit SAMD -> Adafruit Trinket M0**
	  before compiling.
