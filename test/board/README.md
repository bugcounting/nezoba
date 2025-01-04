# Controller software offline testing

This directory contains several unit tests for the controller board's
software in [src/board/](/src/board/).

Before you test and deploy the controller's software on the board, you
may want to test that its logic and remapping work as expected. To
this end, this directory includes plain C++ stubs for the Arduino
libraries used by the controller, as well as a testing loop that
allows you to do some checks that there are no obvious crashes or
inconsistent usage of the data.

Compile and run the testing program as a standard C++ program:

```sh
make test  # equivalent to: g++ -o test test.cpp
./test
```

The testing program first executes the setup code once (in Arduino, 
function `setup()`). Before doing this, it prompts the user for up to
four *control bits*. These are the four bits read on the 4-bit switch
that determine which remapping is used. Type up to four `0`/`1` values
and then `Enter`; any values not provided on the command line (or
unrecognized) will be set to `0`.

```console
SETUP: reading control bits (up to 4 0/1 values)
0 0 1 foo [Enter]

[...]

Configuration number is: 2 (0 0 1 0)
```

Then, the testing program executes the main control loop body (in
Arduino, function `loop()`) repeatedly until it is terminated with
`Ctrl + C`. Before each iteration, it prompts the user for any number
of button presses, each identified by an integer. Any value that is
not recognized as an integer in the given range is ignored; repeating
the same integer several times is allowed (and equivalent to just
typing it once). After reading this input, the testing program acts as
if those buttons where pressed simultaneously, and shows the
corresponding presses that the controller would issue.

```console
CONTROL LOOP ITERATION #1: reading presses (integers in [0..14])
0 10 6 10 bar [Enter]

[...]

[Gamepad] Press button 16

[...]

[Gamepad] Press button 13

[...]

[Gamepad] Sets D-pad to direction 6
```

Each button press corresponds is first translated into (up to 3) key presses
according to the remapping in the current configuration.
Each key corresponds to a directional input or to a controller button.

   - In the first case, all directional inputs are recorded in the
     loop iteration, and at the end they are translated into a single
     8-way direction (up, up right, and so on). Contradicting
     direction results in a neutral directional inputs; for example,
     keys left and right cancel each other out.
	 
   - In the second case, the corresponding controller button is
     pressed.
	 
All controller inputs in one iteration are sent to the gamepad at the
end. All buttons that were not pressed are released on the gamepad.
