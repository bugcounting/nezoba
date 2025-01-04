# Nez-Oba: a custom button-only game controller

The Nez-Oba[^1] project provides the schematics of a fully-programmer
all-button wired game controller board, as well as software to program
the controller's behavior to emulate a standard gamepad, and to
reconfigure its button layout.

The controller software works with Nintendo Switch (as a Pro
Controller), as well as with PC/Raspberry PI (as a generic USB
controller). While it can be used, in principle, for any game, it is
primarily intended to play 2D games that require precise button and
D-pad input &mdash; such as platformers.


## Why a custom controller?

Proficiency at 2D platforming games (Super Mario Maker 2, Celeste,
Super Meat Boy, Levelhead, Super Mario Bros. Wonder, Slime-san, Super
One More Jump, ...)  requires being able to precisely enter complex
button and directional inputs. A standard gamepad is not ideal for
this because:[^2]

- It usually has membrane button switches, which provide a suboptimal
  feedback and may not be as precise as mechanical switches.
  
- Its button layout requires to frequently move fingers (especially
  thumbs) from one button to the other. In contrast, an
  all-button/button-only/[hitbox style
  controller](https://ougaming.com/3/7198/a-quick-look-at-the-hitbox-vs-arcade-stick-de)
  minimizes hand and finger movement, and simplifies reliably entering
  complex presses.

There are numerous all-button controllers for PCs, and a few even work
with the Nintendo Switch. In particular, I like the [Junk Food
Arcades' Snack Box
Micro](https://junkfoodarcades.com/collections/snack-box-micro), as
well as [8bitdo's Arcade Stick](https://www.8bitdo.com/arcade-stick/)
[modded](https://www.youtube.com/watch?v=Yn7xL-vFdPc) with
[MyrzArcade's L-shaped
T-Spin](https://www.etsy.com/listing/733030620/t-spin-pcb-only-diy-tetromino-shaped)
(see also [OmniArcade's Odin](https://www.etsy.com/shop/OmniArcade) if
you like the WASD layout). The [Edgeguard keyboard
adapter](https://keyboard.gg/) also looks great. However, none of
these options supports switching between different programmable button
layouts without reconfiguring the board's software; their default
layout is not ideal for games like SMM2; and the distance between
buttons is somewhat wide, which can make repeatedly pressing certain
button combinations unconformable in the long run.

Hence, I went down this rabbit hole starting in the fall of 2021. The
first (and, so far, only) two fully working Nez-Oba game controllers
were completed in March 2022, and I've been using them with gusto ever
since.

After that, I worked on and off to improve the software, develop a
usable web-based GUI for definining the custom mappings, and to
provide detailed documentation. While there are still plenty of things
that could be improved, this is the first public release of the whole
project.[^3]


This is what the Nez-Oba game controller looks like IRL (this is the
version with black case and red linear Kahil low-profile switches):

![the Nez-Oba game controller in black](/hw/pics/NezOba_black_front.jpg)

Its main features:

- Game controller board with twelve mechanical switches (as well as
  three auxiliary switches) and tight, comfortable physical layout.
  
- Fully remappable layout with capacity to store sixteen different
  button-to-key-press mappings.

- Each physical button can map to a combination of up to three
  simultaneous key presses.
  
- Support for turbo functionality (fast repeated key presses).


## Usage

The Nez-Oba projects includes both hardware and software components.

### Build the board

Under [hw/kicad/](/hw/kicad/) you will find:

- PCB schematics of the Nez-Oba board and how to manufacture them

- A list of components that have to be soldered onto the board

You will also need a USB-micro-to-USB-A cable to connect the board's
controller to the Switch or PC.

### Print the case

Under [hw/case/](/hw/case/) you will find 3D models of a case for
the game controller board, which you can 3D-print.

### Install the software

The Nez-Oba software is actually in two parts:

- An Arduino project in C/C++ with the software that runs on the
  board's microcontroller.
  
- A Python project to configure the button-to-key-press mappings that
  the on-board software supports.
  
The Python project is the single entry point to all software, since it
also provides commands to configure, compile, and upload the
microcontroller software.

You install this software as a regular Python project. As usual, it's
recommended that you create a virtual environment to install
dependencies more easily:

```sh
python3 -m venv venv
source vent/bin/activate
python3 -m pip install --upgrade pip
```

Then, there are different options to install the software:

1. Directly from GitHub:

```sh
python3 -m pip install git+https://github.com/bugcounting/nezoba
```

2. From a local copy the Git repository:

```sh
git clone https://github.com/bugcounting/nezoba
cd nezoba
python3 -m pip install .
```

3. From the release wheel:

Download
[/releases/latest/](latest
release wheel `nezoba*.whl`) and install it:

```sh
python3 -m pip install "$NEZOBA.whl"
```

You can also avoid downloading dependencies by using the
[/releases/latest/](`nezoba*.wheels.tgz`):

```sh
tar xf "$NEZOBA.wheels.tgz"
python3 -m pip install wheels/nezoba-*.whl --find-links=./wheels
```

### Use the software

Command `nezoba` is the entry point for using the whole
software. Start with `nezoba -h`.

A common workflow:

1. Have a look at the default button-to-key-presses mappings that I
   defined for 2d platformers: `nezoba show`.
   
2. If you want to define your own mappings, start the GUI with:
    `nezoba gui` (the GUI will appear at
    `http://127.0.0.1:8000/`). Alternatively, there's a simpler CLI
    shell that supports similar functionality: `nezoba cli $MAPPINGS_YAML`.
	
3. Setup the Arduino compiler and libraries with `nezoba setup
   "$SYSTEM_DIR"`, where `$SYSTEM_DIR` is the directory where you want
   to install them.
   
   Alternatively, among the [/releases/latest/](release files) you
   will also find an archive `arduino-cli-4nez.tar.xz` that includes a
   fully setup environment for Linux systems. Unpacking the content of
   that archive under `$SYSTEM_DIR` is an equivalent way of setting up
   your system.
   
4. Deploy the controller's software with your YAML mappings
   `$MAPPINGS`: `nezoba deploy "$SYSTEM_DIR" "$MAPPINGS"`. If you omit
   `$MAPPINGS`, the default mappings for 2d platformers will be
   deployed.
   
The `deploy` command will finally upload to the board. For this to
work, the board has to be plugged in to a USB port of the computer,
and it may have to be reset. See the [troubleshooting
section](/src/README.md#upload-troubleshooting) for a few practical
tips.
   
### Testing/development

If you want to test the installation of the Nez-Oba software, and
possibly change or extend its functionalities:

```sh
# Install the `test` target in editable mode
python3 -m pip install -e .[test]
# Run the Python tests
cd test/nezoba
pytest .
# Run the Arduino software tests
cd test/board
make test
./test
```


[^1]: What does the acronym "Nez-Oba" mean? I'm afraid I don't
    remember :-/

[^2]: Of course, top players make the most out of regular
    controller. On the other hand,
    [Niftski](https://en.wikipedia.org/wiki/Niftski), the
    [top](https://www.youtube.com/watch?v=i_9Hj--VfbY) Mario
    Bros. speedrunner at the time of writing, often uses a mechanical
    keyboard!

[^3]: The dev repository includes nearly 900 commits in 120 days over
    more than 3 years!
