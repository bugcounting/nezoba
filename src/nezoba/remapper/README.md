# Package `nezoba.remapper`

Package `nezoba.remapper` provides the main abstractions to define
button-to-key-presses mappings. They are deliberately more general
than what is strictly supported by the Nez-Oba controller board's
software at the moment, so that they may be usable also with future
extensions of the hardware and its software.


## Buttons: module `buttons`

A `Button` instance represents a physical button on the game
controller that can be pressed or depressed. Each button is uniquely
identified by an integer `identifier`.

Class `Buttons` models a collection of buttons, with the convention
that the `k`th button in an instance of `Buttons` is a `Button` with
`identifier == k`.

This usage of identifiers is also relied upon to map buttons to
physical buttons on the Nez-Oba PCB: a comment in
[keys.h](/src/board/keys.h) includes a simple diagram that illustrates
how the 15 clickable buttons on the Nez-Oba board are numbered.

Correspondingly, module `buttons` includes constant `NEZOBA_BUTTONS`,
which is an instance of `Buttons` with all buttons available on the
Nez-Oba board.


## Keys: module `keys`

A `Key` instance represents a possible logical output of a controller,
signaling to the game that a certain key has been pressed. Each key is
uniquely identified by an integer `identifier`, as well as by a unique
name `key`. 

Class `Keys` models a collection of keys. The order of keys in an
instance of `Keys` is immaterial since the keys can be indexed by
`identifier` or by name `key`.

Module `keys` also includes constant `STANDARD_KEYS`, which includes
all keys available on a standard gamepad. Currently, the Nez-Oba
board's software does not support left stick and right
joystick/thumbstick events, whereas all other keys should be
available.

Adding support for the joysticks should not be hard, given that the
Arduino gamepad libraries already support them.


## Combos: module `combos`

A `Combo` instance represents a certain combination of keys. At the
moment, there are two kinds of combos:

- A `Press` represents the pressing of a single key. The press may be
  *turboed* (the key is repeatedly pressed and depressed as long as
  the triggering button is pressed) or *held* (the key is held until
  the triggering button is pressed). Currently, the Nez-Oba controller
  board only supports turbo with frequency of 75 Herz, and does not
  support `hold` presses.
  
- An `And` represents several simultaneous `Press`es. Currently, the
  Nez-Oba controller board only supports up to three simultaneous
  presses.
  

## Mappings: module `mappings`

A `Mapping` instance represents a `Button` → `Combo` mapping. It is
built around Python dictionaries.

Class `Mappings` models a collection of mappings, all with the same
domain (an instance of `Buttons`) and with codomains with the same
keys used in `Combo`s (an instance of `Keys`).

Throughout this project, sometimes an instance of `Mappings` is also
referred to as a collection of *configurations*, where each
configuration corresponds to an instance of `Mapping`.


## Namings: module `namings`

Module `namings` provides wrappers around classes `Key`, `Keys`, and
`Mappings` that add associate platform-specific *names* to keys.

For example, the same gamepad key that is called `A` on a Nintendo Pro
Controller is called `B` on a PC/XBox controller.

Module `namings` also includes constant `NS_KEYS` and `PC_KEYS`, which
includes all `keys.STANDARD_KEYS` with their names on a Nintendo
Switch gamepad and on a PC/Raspberry Pi controller, respectively.


## Serialization: module `serialization`

Module `serialization` provides functions to serialize/deserialize an
instance of `Mappings` to/from a YAML file.

Functions `to_yaml` and `from_yaml` are the two main entry points for
using this module.


## Encoding and decoding: module `encoding`

Module `serialization` provides means to convert a `Mapping` to the
format used by the Nez-Oba board's software (that is, a C array
format). This conversion is called *encoding* and is provided by
`Encoder.encode`.

Class `Encoder` also provides the reverse conversion, from a C array
format back to an instance of `Mapping`, called *decoding* and
provided by `Encoder.decode`.

Finally, `Encoder.show` formats a `Mapping` instance as a string that
mimicks the controller board's actual physical layout and is human
readable.

The rest of the software does not use class `Encoder` directly but
through class `Exporter`, which handles encoding and decoding through
files.
