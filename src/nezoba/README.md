# Package `nezoba`

Package `nezoba` includes an implementation of the NezOba command-line
app.


## Main module: `nezoba`

Function `main` in module `nezoba` is the main entry point of the
command-line app.

It sets up a command-line interface with `argparse`, configures
logging in all modules, and instantiates and runs other components of
`nezoba`.

If you're debugging or simply want to follow how the implementation
works, it's recommended to run this module with the `--debug` global
option enabled (duh).


## Module `shell`

This module implements a purely textual CLI shell, which is available
as a simpler alternative to the web-based GUI to browse the available
mappings and edit them.


## Module `deployer`

This module implements a series of scripts useful to setup and
configure an Arduino compiler, and to use it to compile and upload the
Nez-Oba game board's software.
