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
# This is needed when running the tests in this directory directly (not from the upper directory)
from src.nezoba.gui import utils as gui_utils
