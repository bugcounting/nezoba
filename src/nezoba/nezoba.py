"""Main entry point for the Nez-Oba controller board software."""

import argparse
import logging
from enum import Enum
from typing import Optional
from importlib import resources as impresources
import os
import tempfile

import board as nezoba_board
import data as nezoba_data
from .shell import cli_shell
from .remapper.encoding import Exporter
from .deployer import Installer, Deployer

_default_yaml = impresources.files(nezoba_data) / "platformers-2d.yaml"
_default_project_dir = impresources.files(nezoba_board) / ""

class Command(Enum):
    """Available commands."""
    SHOW = "show"
    GUI = "gui"
    CLI = "cli"
    SETUP = "setup"
    DEPLOY = "deploy"
    IMPORT = "import"


_DESCRIPTION = """
This script is the entry point to configuring the Nez-Oba controller
board for use. It provides a simple command-line interface to:

- show: show the content of a button-to-key-presses YAML mapping file.
- gui: edit the content of a button-to-key-presses YAML mapping file
  with a GUI.
- gui: edit the content of a button-to-key-presses YAML mapping file
  with a minimal CLI shell.
- setup: install the Arduino compiler and libraries needed to build
  the Nez-Oba board's software.
- deploy: compile and deploy a chosen series of button-to-key-presses
  mappings to the board.
- import: translate a deployed button-to-key-presses mappings back to
  a YAML mapping file for further editing.
"""


def cmd_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description=_DESCRIPTION,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=35)
    )

    parser.add_argument("--debug", default=False, action="store_true",
                        help="print debugging information")
    parser.add_argument("--log", nargs=None,
                        help="write debugging information to this file")

    subparsers = parser.add_subparsers(dest="command", required=True,
                                       help="command to execute")
    cmd_parsers = {
        Command.SHOW:
        subparsers.add_parser(
            "show",
            help="print the content of a button-to-key-presses YAML mapping file"
        ),
        Command.GUI:
        subparsers.add_parser(
            "gui",
            help="start the GUI to edit a button-to-key-presses YAML mapping file"
        ),
        Command.CLI:
        subparsers.add_parser(
            "cli",
            help="run the CLI shell to edit a button-to-key-presses YAML mapping file"
        ),
        Command.SETUP:
        subparsers.add_parser(
            "setup",
            help="install the Arduino compiler and libraries needed by the Nez-Oba board"
        ),
        Command.DEPLOY:
        subparsers.add_parser(
            "deploy",
            help="compile and deploy to the board a button-to-key-presses YAML mapping file"
        ),
        Command.IMPORT:
        subparsers.add_parser(
            "import",
            help="translate a deployed button-to-key-presses mappings back to a YAML mapping file"
        )
    }

    cmd_parsers[Command.SHOW].add_argument(
        "mappings",
        help="path to the YAML mappings file (default: %(default)s)",
        default=_default_yaml,
        nargs="?"
        )

    cmd_parsers[Command.GUI].add_argument(
        "mappings",
        help="path to the YAML mappings file (default: empty mappings)",
        nargs="?"
        )

    cmd_parsers[Command.CLI].add_argument(
        "mappings",
        help="path to the YAML mappings file to create or modify"
        )

    cmd_parsers[Command.SETUP].add_argument(
        "system_dir",
        help="path where to install the Arduino compiler and libraries"
        )
    cmd_parsers[Command.SETUP].add_argument(
        "--overwrite", default=False, action="store_true",
        help="if the project directory already exists, delete it first"
        )
    cmd_parsers[Command.SETUP].add_argument(
        "--batch", default=False, action="store_true",
        help="do not wait for user confirmation before running each command"
        )

    cmd_parsers[Command.DEPLOY].add_argument(
        "mappings",
        help="path to the YAML mappings file (default: %(default)s)",
        default=_default_yaml,
        nargs="?"
        )
    cmd_parsers[Command.DEPLOY].add_argument(
        "nezoba_sw",
        help="path to the Nez-Oba board's software directory (default: %(default)s)",
        default=_default_project_dir,
        nargs="?"
        )
    cmd_parsers[Command.DEPLOY].add_argument("arduino",
                                             help="path to an installation of the Arduino CLI")
    cmd_parsers[Command.DEPLOY].add_argument(
        "--port", default=None,
        help="use the given serial port to upload to the board (default: try all available ports)"
        )
    cmd_parsers[Command.DEPLOY].add_argument(
        "--batch", default=False, action="store_true",
        help="do not wait for user confirmation before running each command"
        )
    cmd_parsers[Command.DEPLOY].add_argument(
        "--overwrite", default=False, action="store_true",
        help=("if mappings are already present in the project directory, overwrite them "
              "(default: keep the old mappings as backup)")
        )

    cmd_parsers[Command.IMPORT].add_argument(
        "mappings",
        help="path to the YAML mappings file that will be created"
        )
    cmd_parsers[Command.IMPORT].add_argument(
        "nezoba_sw",
        help=("path to the Nez-Oba board's software directory, "
              "where the deployed mappings are stored (default: %(default)s)"),
        default=_default_project_dir,
        nargs="?"
        )
    cmd_parsers[Command.IMPORT].add_argument(
        "--overwrite", default=False, action="store_true",
        help=("if a YAML mappings file at that path is already present, overwrite it "
              "(default: keep the old mappings file as a backup)")
        )

    return parser


def setup_logging(enable: bool = True, log_file: Optional[str] = None):
    """Enable/disable displaying logging information."""
    # handle warnings with the logging module
    logging.captureWarnings(True)
    # Create JustPy environment file
    justpy_env_dir = tempfile.mkdtemp(prefix="justpy_config")
    justpy_env_path = os.path.join(justpy_env_dir, "justpy.env")
    justpy_env_file = open(justpy_env_path, "w", encoding="utf-8")
    os.environ["JUSTPY_ENV_FILE"] = justpy_env_file.name
    logger = logging.getLogger()
    justpy_logger = logging.getLogger("justpy")
    if enable:
        logger.setLevel(logging.INFO)
        justpy_logger.setLevel(logging.INFO)
        justpy_env_file.write("DEBUG=True\nVERBOSE=True\n")
    else:
        logger.setLevel(logging.CRITICAL)
        justpy_logger.setLevel(logging.CRITICAL)
        justpy_env_file.write("DEBUG=False\nVERBOSE=False\n")
    logging.info("JustPy configuration file: %s", justpy_env_path)
    justpy_env_file.close()
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    while justpy_logger.hasHandlers():
        justpy_logger.removeHandler(justpy_logger.handlers[0])
    if log_file:
        # log to file
        handler = logging.FileHandler(log_file, mode="w")
    else:
        # log to console
        handler = logging.StreamHandler()
    formatter = logging.Formatter("%(pathname)s - line %(lineno)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    justpy_logger.addHandler(handler)

def show(mapping_yaml: str):
    """Show the content of a button-to-key-presses mapping file."""
    exporter = Exporter("", mapping_yaml)
    print(exporter.show())

def gui(mapping_yaml: Optional[str]):
    """Launch the GUI (opening the given button-to-key-presses mapping file if given)."""
    # pylint: disable=import-outside-toplevel # To properly configure justpy's output, I need to import here
    import justpy
    from .gui.gui import nezoba_gui
    justpy.justpy(lambda: nezoba_gui(mapping_yaml))

def encode(mapping_yaml: str, project_dir: str, bak: bool):
    """Encode a button-to-key-presses mapping file to C header files in `project_dir`."""
    exporter = Exporter(project_dir, mapping_yaml)
    exporter.encode(bak=bak)

def decode(mapping_yaml: str, project_dir: str, bak: bool):
    """Decode a button-to-key-presses mapping file from C header files in `project_dir`."""
    importer = Exporter(project_dir, mapping_yaml)
    importer.decode(bak=bak)


def main(args: argparse.Namespace=None):
    """Parse and process commands."""
    if args is None:
        parser = cmd_parser()
        args = parser.parse_args()
    setup_logging(args.debug, args.log)
    if args.command == Command.SHOW.value:
        show(args.mappings)
    elif args.command == Command.GUI.value:
        gui(args.mappings)
    elif args.command == Command.CLI.value:
        cli_shell(args.mappings)
    elif args.command == Command.SETUP.value:
        installer = Installer(args.system_dir, args.overwrite, not args.batch)
        installer.setup()
    elif args.command == Command.DEPLOY.value:
        encode(args.mappings, args.nezoba_sw, not args.overwrite)
        deployer = Deployer(args.arduino, args.nezoba_sw,
                            args.port, not args.batch)
        deployer.deploy()
    elif args.command == Command.IMPORT.value:
        decode(args.mappings, args.nezoba_sw, not args.overwrite)


if __name__ == "__main__":
    main()
