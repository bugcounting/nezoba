# Python code testing

This directory contains several unit tests for the modules in
[src/nezoba/](/src/nezoba/). To run the tests, install
`pytest` and run:

```console
$ pytest
```

in the current directory.

This will run all tests; for selective testing, try these `pytest` options:

   - `pytest gui` only runs the tests for package `gui`.
	 
   - `pytest -k "parse"` only runs test methods whose name includes
     the string `parse`.
	 
   - `pytest -s` dumps standard output to terminal while the tests
     run. This is useful for debugging, to detect the effect of any
     `print` statement. Try it with tests `test_encoding`.

Due to some relative imports of auxiliary files, calling `pytest` from
a subdirectory of this directory may introduce spurious import
errors. Just call all the tests from this directory to avoid this
issue.


## Testing the interactive shell

File `test_shell.sh` sends a series of commands to the interactive
shell to test that it works correctly. Simply run the script from this
directory:

```
./test_shell.sh
```

This testing script creates and then deletes a temporary file.
