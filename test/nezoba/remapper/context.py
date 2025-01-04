# Context file, to allow importing project modules from test directory,
# without including test directory in project's packages
# https://docs.python-guide.org/writing/structure/

# pylint: disable=missing-module-docstring, unused-import, import-error
import os
import sys
sys.path.insert(0,
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..", "..", "..")))

# pylint: disable=wrong-import-position # `sys.path` must be properly set before importing project modules
from src.nezoba.remapper import (
    buttons,
    keys,
    combos,
    mappings,
    namings,
    serialization,
    encoding
    )
