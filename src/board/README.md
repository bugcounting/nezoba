# The Nez-Oba gamepad controller board's software

This document overviews the structure and logic of the Arduino gamepad
controller board's software, which is included in this directory.


## Configuration numbers

First, a reminder of how users of the board specify which
button-to-key-presses mapping should be used.

The game controller board includes a 4-bit switch in the top-right
corner. The positions of the four microswitches determine the
controller's *configuration number*; each configuration number
corresponds to a different button-to-key-presses mapping.

Thus, a configuration number is an integer in the range from 0 to 15
(included); thus, the controller stores up to 16 different button
mappings.  To select configuration number `N`, move the microswitches
so that they spell out `N` as a four-digit binary number: a
microswitch in the upper position indicates binary digit `1`, and a
microswitch in the lower indicates binary digit `0`. For example,
configuration number `5` (`0101` in binary) is selected when the first
and third microswitches are low, and the second and fourth
microswitches are high.

If you use the Nez-Oba GUI, it wil display the configuration number as
it should appear on the board.


## Main file: `board.ino`

The entry point of the board software is Arduino project file
`board.ino`.  The program is not that long, but it's broken down into
several included files so that it's easier to navigate and modify, and
so that it can be more easily tested.

By default, the `#define DEBUG` definition is commented out, so that
the software is ready for deployment. If you uncomment it, when the
program runs on the board it will print what it's doing in each step
on the `Serial` interface. You can use this to check the buttons
before actually connecting the board to the host. (Printing on
`Serial` doesn't interfere with the controller's functionality, so you
can also use a debug build on the host.)


## File `debug.h`

File `debug.h` is included next.  This defines the macro `debug()`,
which prints its argument on `Serial` (if `TESTING` is not defined) or
on standard output. The offline testing program (in directory `test`)
defines `TESTING` to use the latter; the standard debugging behavior
uses `Serial` as described above.

Macro `debug()` is always defined, instead of being removed by the
preprocessor if `DEBUG` is not defined. This has the advantage of
ensuring that the debugging code remains consistent with the deployed
code (or at least that it can be compiled). Then, we rely on the
optimizing compiler to remove the `debug()` statements (which are
never executed when `DEBUG` is undefined).  This is the reason why
`debug()` is written as a `do ... while` loop: it should make it
easier for the compiler to recognize it as dead code. Indeed, you can
check that the compiled program size in non-debug mode remains the
same, even if we define macro `debug()` as empty.

The other macros `init_time()` and `loop_end()` implement basic
measures of performance. Macro `init_time()` should be called at the
end of the controller's setup to save the absolute time then. Macro
`loop_end()` should be called at the end of each iteration of the main
control loop; it will update and print the average time it took to
complete a control loop.

These macros are meant for online testing (`DEBUG` defined but
`TESTING` undefined); however, they work also during offline testing
to check that they do not interfere with the rest of the control
program.


## File `keys.h`

File `keys.h` defines several constants that identify the various
buttons and keys of the controller.

A **button** is a physical button on the nez-oba.
There are `N_BUTTONS` such buttons, each identified by an integer in the 
range `[0..N_BUTTONS-1]`.

The comment above the definition of `N_BUTTONS` shows how the buttons
are to be numbered in any mapping. It's important that function
`nezoba.remapper.encoding.Exporter.encode` encodes buttons in the same
order. If you need to change this order, you'll have to adjust the
definition of `BUTTONS2CMP` in `globals.h` consistently.

A **key** is an event that can be triggered on the emulated gamepad
(a key press);
there are `N_KEYS` such events in total, 
each identified by an `enum` integer in the range `[0..N_KEYS-1]`.
There are several categories of keys, identified by macro predicates.

- Keys `n` that satisfy `IS_NOOP(n)` correspond to a "no op", used to
  map controller buttons that are disabled.
	 
- Keys `b` that satisfy `IS_BUTTON(b)` correspond to regular gamepad
  buttons, that is everything other than a directional input.
	 
- Keys `d` that satisfy `IS_DP(d)` correspond to 9 D-pad directions:
  up, up right, right, down right, down, down left, left, up left, and
  centered (neutral).
	 
- Keys `l` that satisfy `IS_LS(l)` correspond to 9 left-stick
  directions (the same as the D-pad).

- Keys `r` that satisfy `IS_RS(r)` correspond to 9 right-stick
  directions (the same as the D-pad).
	 
A **mapping** associates each button to up to three keys.
The *current* mapping is stored in three arrays `KEY1`, `KEY2`, and `KEY3`:
`KEY1[b]`, `KEY2[b]`, and `KEY3[b]` are the three key events that
are triggered (simultaneously) when button `b` is pressed.

In most cases, you only want to trigger one key event per
button. Then, just set one mapping slot to the key event, and the
other two slots to `K_NOOP`.

If you want to **turbo** a key event `K`, set the mapping to `-k`.
Turboing a key means that the controller will rapidly toggle pressing
`K` with a small delay. Turbo is only applicable to regular buttons,
not to directional inputs.

Multi-dimensional array `MAPPINGS` combines 16 `3 * N_BUTTONS`-element
arrays, one for each of the 16 remappings that the controller software
supports.  File `remapNN.h` stores remapping number `NN` (numbered
from `00`) as an initializer of a `3 * N_BUTTONS` array, whose
elements are the remapping's key values in the same order as the
button numbering.  Therefore, the elements at indexes `3*b`, `3*b + 1`, 
and `3*b + 2` are the three keys mapped to button `b`. Again,
`nezoba.remapper.encoding.Exporter.encode` produces an encoding 
consistent with this format.

To change a mapping directly, edit the corresponding `remapNN.h`
maintaining this structure. Use `K_NOOP` for each remapping slot that
you don't want to use. In most cases, though, you won't need to edit
these files directly. If you do, though, command `nezoba decode` can
translate the files `remapNN.h` back into an instance of `Mappings`
used by the Python software.


## File `mcp.h`

File `mcp.h` introduces several macros useful to access the MCP unit
using the I2C protocol through library `Wire`. 

An earlier prototype of the nez-oba software used instead (an older
version of) [Adafruit's MCP23017 Arduino
library](https://github.com/adafruit/Adafruit-MCP23017-Arduino-Library)
together with a [debouncing library for
MCPs](https://github.com/cosmikwolf/Bounce2mcp). However, this just
introduced a significant overhead and, worse, a dependency on older
libraries. By rewriting everything using library `Wire` directly, the
current software is faster, simpler (and hence easier to modify) and
with minimal dependencies on legacy software.

An MCP 23017's 16 input/output pins are split into two banks `A` and
`B` of 8 pins each. Therefore, several registers are split into two
byte-size registers, one for each bank `A` and `B`; the 8 bits of a
byte define the state of the 8 pins in a each bank.

Initially, the file defines several register addresses:

- `MCP_ADDRESS` is the MCP's address on the I2C serial bus, when pins
  `A0`, `A1`, and `A2` of the MCP are all connected to ground. When
  using multiple MCP cascading units, one would change this address by
  setting some of those pins to a high value.

- `MCP_IODIRA` and `MCP_IODIRB` are the addresses of the registers
  used to configure the pins as input (value 1) or output (value 0).
	 
- `MCP_GPPUA` and `MCP_GPPUB` are the addresses of the registers use
  to enable the pull-up resistors (value 1) of any input pins.
	 
- `MCP_GPIOA` and `MCP_GPIOB` are the addresses of the registers that
  store the value (low 0, or high 1) of the pins (or set the value for
  pins configured as output).
	 
- `MCP_GPINTENA` and `MCP_GPINTENB` are used to turn on (value 1) or
  off (value 0) interrupt triggers for each pin.
	 
The MCP module has several other registers for functionality that the
nez-oba doesn't use. All addresses are from [version 1.3.0 of
Adafruit's MCP
library](https://github.com/adafruit/Adafruit-MCP23017-Arduino-Library/blob/1.3.0/Adafruit_MCP23017.h),
which was used in an older version of the controller board software. I
found some register addresses used in
[other](http://www.learningaboutelectronics.com/Articles/Read-input-from-an-MCP230xx-IO-port-expander-connected-to-an-arduino.php)
[MCP
guides](http://www.learningaboutelectronics.com/Articles/MCP23017-IO-port-expander-circuit-with-arduino.php)
not to work with the MCP units I have experimented with. If you find
issues with yours, you may want to check the MCP's spec sheet.

Another point to notice is that the nez-oba software still adopts the
pin ids used by Adafruit's MCP23017 library:

| Pin Name | MCP23017 Pin # | Pin ID |
|:--------:|:--------------:|:------:|
| GPA0     | 21             |  0     |
| GPA1     | 22             |  1     |
| GPA2     | 23             |  2     |
| GPA3     | 24             |  3     |
| GPA4     | 25             |  4     |
| GPA5     | 26             |  5     |
| GPA6     | 27             |  6     |
| GPA7     | 28             |  7     |
| GPB0     |  1             |  8     |
| GPB1     |  2             |  9     |
| GPB2     |  3             | 10     |
| GPB3     |  4             | 11     |
| GPB4     |  5             | 12     |
| GPB5     |  6             | 13     |
| GPB6     |  7             | 14     |
| GPB7     |  8             | 15     |

This is really just a legacy of the earlier version of the software,
but switching to a different scheme has no real advantages, and the
number scheme is anyway immaterial.

The following macros in `mcp.h` assume this numbering
scheme. 

- `IS_GPIOA_PIN` and `IS_GPIOB_PIN` determine if their argument is the
  id of a pin in bank `A` or `B`.
	 
- `PIN2REGISTER` evaluates to `MCP_GPIOA` or `MCP_GPIOB` according to
  whether its argument is the id of a pin in bank `A` or `B`.
	 
- `PIN2BITMASK` gives an 8-bit bitmask where all bits are 0 except for
  the one corresponding to the argument pin id (which is set to
  1). For example, `PIN2BITMASK(14)` is `01000000` (`64` in base 10),
  where the 7th bit from the right is `1` since 14 is the id of pin #7
  in bank `B`.
	 
Macro `MCP_WRITE` takes a register address `REGISTER` and a byte-size
`VALUE`, and writes `VALUE` to `REGISTER` using the I2C protocol: it
initiates the transmission, it sends the `REGISTER` address, it sends
the `VALUE` to be written on that register, and it terminates the
transmission.
 
Macro `MCP_READ` takes a register address `REGISTER` and reads a byte
from that register using the I2C protocol: it initiates the
transmission, it sends the `REGISTER` address to be read, it
terminates the transmission, and it sends a request of 1 byte (from
the register that was just selected). After these statements,
executing `Wire.read()` returns the byte read from the MCP unit.


## File `globals.h`

File `globals.h` defines global variables used by the control
software, and includes the necessary libraries.

Constant `TURBO_PERIOD` defines the delay (in milliseconds) between
toggling a button that is turboed. Then `TT` is just a boolean flag
that is toggled every `TURBO_PERIOD` milliseconds; its boolean value
determines if a pressed turboed button should be pressed on the host.
Currently, only a value of turbo period can be selected, corresponding
to 75 Herz. Any different turbo frequency will be treated as 75 Hz by
`nezoba encode`.

Array `BUTTONS2MCP` translates each button number into the id of the
corresponding MCP unit's pin the physical button is attached to. As
mentioned above, pin ids are as in Adafruit's MCP23017 library. The
names in comments correspond to the names that are printed on the PCB
for identification (although they can obviously be remapped to any key
presses). Remember that the order of elements in this array must be
consistent with the button ordering in the `remapNN.h` files.

Constant `DEBOUNCING` defines the debouncing time (in milliseconds).
Constants `P_CFG_N` define the pin number of the four configuration
bits that are defined on the DIP switch. The first three of them are
bits on the Trinket board; the fourth one is a pin on the MCP (just
because there were no more pins available on the Trinket).

Variable `CFG` will store the current configuration number, as an
integer between 0 and 15.

Then all needed libraries are imported. The `#include` are
conditional: when `TESTING` is set (which is used by offline testing),
some library stubs are imported instead.

Several variables of `byte` type (8 bits) are used for communications
with the MCP unit. Variables `GPIOA_state` and `GPIOA_previous` store
the current and previous state of the `A` pins in each iteration of
the control loop. Variables `GPIOB_state` and `GPIOA_previous` serve
the same purpose for the `B` pins.

Finally, `GPIOA_last_debounce_time` and `GPIOB_last_debounce_time`
record the absolute time (in milliseconds since when the controller
was turned on) when the `A` or `B` pins' state was *debounced*, as
we'll describe later. Using `unsigned long` as type ensures that
debouncing can work for up to more than 49 days of continuous
operation. After that, you may have to unplug and plug back in the
controller if it malfunctions :-)

Array `KEYS2PAD` maps each key to a corresponding named constant in
the `NSGamepad` API. Some of these named constants are the same
number, but it doesn't matter since they are supplied to different
methods of the API (in particular, regular buttonsvs D-pad
directions). At the moment, analog sticks are not supported, and hence
there is no mapping of the corresponding keys to analog stick
directions. Adding support for them should not be hard, but I didn't
implement it since I wouldn't be really using it. I may do so in the
future!


## File `setup.h`

File `setup.h` contains the body of Arduino's `setup()` function,
which is executed once when the board boots up.

The setup performs the following steps:

1. It starts the `Wire` library used to access the MCP unit.

2. It sets the four pins reading the four configuration bits (three on
   the Trinket and one on the MCP module) to *input* with *pullup*
   resistor.

3. It reads the four configuration bits, converts them to an integer
   configuration number `CFG`. The configuration first bit is the most
   significant one.
	  
4. Based on the value of `CFG`, it copies the corresponding mapping
   for each button into arrays `KEY1`, `KEY2`, and `KEY3`.
	  
5. It sets `N_BUTTONS` MCP pins to *input* with *pullup* resistor,
   creates a debouncer object for each of them, and stores the objects
   in array `BUTTONS`.
	  
6. It starts the gamepad module.

7. It records the current time at the end of setup (macro
   `init_time()`).

Since this setup is done only once the board is booted up, if you
change the configuration number you have to turn off and on again the
board for it to take effect.


## File `key_handler.h`

File `key_handler.h` contains the definition of macro `HANDLE_KEY()`,
which decodes a button press into presses or directional inputs on the
gamepad. This macro is used in each iteration of the main control loop
described below.

Macro `HANDLE_KEY`'s argument `KEYID` identifies one of the three
remapping arrays `KEY1`, `KEY2`, and `KEY3`. The other argument `B`
identifies the currently pressed button.

The macro first reads the key that `B` maps to in remapping `KEYID`,
and stores the key value into fresh variable `_k`.  If `_k` is negative, it
means that it corresponds to key `-_k` with turbo.  If this is the
case, it sets the `turboed` and `add_turbo_delay` flags, and changes
the sign of `_k` so that it correspond to a valid key.

If key `_k` is a regular button (not a directional input), the macro
presses it on the gamepad by calling function `press()` after
translating `_k` to the corresponding constant in the `NSGamepad` API.

The condition for calling `press()` is also that `!turboed || TT`:

- If `turboed` is false, the button is just pressed.
   
- If `turboed` is true, the button is pressed only in every other
  control loop cycle, as determined by the turbo-toggle flag `TT`.
	 
If key `_k` is a directional input, the macro combines this
directional inputs with the others into variables `dpad_x` and
`dpad_y`. These variables are initialized to `0` in each iteration of
the control loop. Each directional input changes these variables:
right and left correspond to `+1` and `-1` on `dpad_x` respectively;
up and down correspond to `+1` and `-1` on `dpad_y` respectively.

After reading all directional inputs, we want `dpad_x` and `dpad_y` to
be in the integer range `[-1..+1]`. To this end, macro `HANDLE_KEY`
also resets their values if they have exceeded this range. For
example, it may happen that two buttons are both associated with the
same direction *right*. Then, `dpad_x` would be set to `2`, and then
reset to `1` (which unambiguously identifies a right direction).

This logic also performs some basic SOCD cleaning. SOCD (Simultaneous
Opposite Cardinal Directions) is a problem that occurs when two
directional buttons corresponding to incompatible directions are
pressed simultaneously. For example, pressing *left* and *right*
cannot result in a valid directional input. The gamepad's API that we
are using requires a single 8-direction input for the D-pad, so we
have to resolve these possible inconsistencies. Even if the API
allowed SOCD input, it would still be advisable to avoid it, since it
may lead to inconsistent (possibly nondeterministic) behavior in
games. By using coordinates `dpad_x` and `dpad_y`, opposing
directional inputs reset the corresponding direction to `0` (center),
thus taking care of resolving inconsistencies.


## File `main_loop.h`

File `main_loop.h` contains the body of Arduino's `loop()` function,
which is executed in an infinite control loop.

Each iteration of the control loop performs the following steps:

1. It releases all gamepad keys.

2. It complements the turbo-toggle flag `TT`.

3. It goes through all buttons, and checks which have been
   pressed. For each pressed button, it executes macro `HANDLE_KEY`
   for each of the three keys mapped to the button.
	  
4. It sets a D-pad direction based on the horizontal and vertical
   coordinates `dpad_x` and `dpad_y`.
	  
5. If a key was turboed, it adds a delay.

6. It commits all presses to the gamepad module.

7. It computes and displays the average time to complete a loop
   iteration (macro `loop_end()`).
