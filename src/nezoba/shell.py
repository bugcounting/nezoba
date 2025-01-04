"""
A simple command-line interface (CLI) shell for editing Nez-Oba mappings.

Classes:
    EditableAttributes: Enum representing attributes of a mapping that can be edited.
    NezObaCLI: A command-line shell for editing Nez-Oba mappings.
    
Functions:
    cli_shell: Start the Nez-Oba CLI shell with a given mappings file.

"""
from enum import Enum
import os
import sys
import cmd
import textwrap
from typing import Optional

from .remapper.combos import Combo, Press, And
from .remapper.mappings import Mappings
from .remapper.namings import NameScheme, NamedMapping, default_from_scheme
from .remapper.serialization import from_yaml, to_yaml
from .remapper.encoding import Encoder


class EditableAttributes(Enum):
    """Attributes of a mapping that can be edited."""
    TITLE = "title"
    DESCRIPTION = "description"


# pylint: disable=too-many-instance-attributes # I don't think it's worth extracting the shell state.
class NezObaCLI(cmd.Cmd):
    """
    Command-line interface shell for editing Nez-Oba mappings.
    
    Implementation based on Python's `cmd.Cmd` class. Use through the `cli_shell` function.
    """

    # application data
    #-----------------

    # width of text columns
    WIDTH = 75

    # path to the YAML mappings file
    mappings_yaml: str

    # whether to disable printing of messages
    _disable_msg: bool = False

    # current mappings
    mappings: Mappings

    # current mapping index (a.k.a. configuration number)
    _cfg_n: Optional[int]

    @property
    def cfg_n(self) -> Optional[int]:
        """Current configuration number."""
        return self._cfg_n

    @cfg_n.setter
    def cfg_n(self, map_num: Optional[int]):
        """Set current mapping to #`n`."""
        if map_num is None:
            self._message("Unselecting current mapping.")
            self._cfg_n = None
            self._prompt = ""
        else:
            cfg_str = f"{map_num:02d} ({map_num:04b})"
            # switch to configuration and update prompt
            self._message("Selecting mapping: " + cfg_str)
            self._prompt = " map " + cfg_str
            self._cfg_n = map_num

    # configuration numbers whose remapping has been changed and not saved
    changed: set[int]

    # current displayed prompt
    _prompt_str: str

    @property
    def _prompt(self) -> str:
        """Current prompt."""
        return self._prompt_str

    @_prompt.setter
    def _prompt(self, message: str):
        """Set prompt to message."""
        self._prompt_str = "<Nez-Oba CLI" + (f":{message}" if message else "") + "> "

    # setup
    # -----

    # Text printed when the shell starts
    intro = "\n\n".join([
        "Welcome to the Nez-Oba CLI shell.",
        "Type 'help' or '?' to list commands."
    ]) + "\n"

    def emptyline(self):
        """If an empty line is entered to the prompt, do nothing"""

    # executed before starting the REPL loop
    def preloop(self):
        """Shell initialization."""
        # reset prompt
        self._prompt = ""
        # load mappings from file
        if os.path.exists(self.mappings_yaml):
            with open(self.mappings_yaml, "r", encoding="utf-8") as file_handle:
                self.mappings = from_yaml(file_handle.read())
            if self.mappings is None:
                self._message(f"Invalid mappings file {self.mappings_yaml}.")
                sys.exit(1)
        else:
            self.mappings = Mappings()
        self._disable_msg = True
        self.changed = set()
        self.cfg_n = None
        self._disable_msg = False

    # commands and help
    # -----------------

    def do_map(self, cfg: str):
        """
        Switch to mapping #`cfg`.
        
        A valid mapping number is either an integer in `range(len(self.mappings))`, 
        or a space-separated sequence of binary digits that converts to such an integer.
        """
        try:
            # try to convert `cfg` to integer in base 10
            cfg_n = int(cfg)
        except ValueError:
            try:
                # try to convert `cfg`'s digits to integer in base 2
                cfg_n = int("".join(cfg.split()), 2)
            except ValueError:
                cfg_n = -1
        # if `cfg_n` is a valid configuration number
        if cfg_n in range(len(self.mappings)):
            self.cfg_n = cfg_n
            return
        # if `cfn_n` is invalid, report error
        self._message(f"Invalid configuration number: {cfg}")

    def help_map(self):
        """Help for command 'map'."""
        self._message("map N", center=True)
        range_lst = list(range(len(self.mappings)))
        if range_lst:
            range_str = f"[{range_lst[0]}..{range_lst[-1]}]"
        else:
            range_str = "[]"
        msg = f"Switch to mapping #N. N must be an integer in {range_str}."
        self._message(msg)

    def do_show(self, _arg: str):
        """Print the current mapping."""
        if not self._in_cfg():
            return
        encoder = Encoder(None)
        encoder.text_width = self.WIDTH
        encoder.set_mapping(self.mappings[self.cfg_n])
        self._message(encoder.show(cfg=self.cfg_n, button_numbers=True),
                     raw=True, line_before=True)

    def help_show(self):
        """Help for command 'show'."""
        self._message("show", center=True)
        msg = "Print the currently selected mapping."
        self._message(msg)

    def do_new(self, scheme_str: str):
        """Create a new mapping with the given naming scheme."""
        scheme = None
        for name_scheme in NameScheme:
            if name_scheme.name == scheme_str.strip():
                scheme = name_scheme
                break
        if scheme is None:
            self._message(f"Invalid naming scheme: {scheme_str}")
            return
        # create new mapping
        new_mapping = default_from_scheme(scheme)
        self.mappings.append(new_mapping)
        self.changed.add(len(self.mappings) - 1)

    def help_new(self):
        """Help for command 'new'."""
        self._message("new NAME_SCHEME", center=True)
        name_schemes = ", ".join([scheme.name for scheme in NameScheme])
        msg = f"Create a new mapping with NAME_SCHEME. Supported name schemes: {name_schemes}"
        self._message(msg)

    def do_delete(self, _arg: str):
        """Delete the currently selected mapping."""
        if not self._in_cfg():
            return
        self.mappings.pop(self.cfg_n)
        # scale indexes of changed mappings
        self.changed = {n - 1 if n > self.cfg_n else n for n in self.changed}
        self.cfg_n = None

    def help_delete(self):
        """Help for command 'delete'."""
        self._message("delete", center=True)
        msg = "Delete the currently selected mapping."
        self._message(msg)

    def do_copy(self, _arg: str):
        """Create a copy of the currently selected mapping as a new mapping."""
        if not self._in_cfg():
            return
        cur_mapping = self.mappings[self.cfg_n]
        new_mapping = NamedMapping(
            buttons = cur_mapping.buttons,
            keys = cur_mapping.keys,
            identifier = cur_mapping.identifier,
            title = cur_mapping.title,
            description = cur_mapping.description
            )
        self.mappings.append(new_mapping)
        self.changed.add(len(self.mappings) - 1)

    def help_copy(self):
        """Help for command 'copy'."""
        self._message("copy", center=True)
        msg = "Create a copy of the currently selected mapping as a new mapping."
        self._message(msg)

    def do_edit(self, button_or_attribute: str):
        """Edit the currently selected mapping."""
        if not self._in_cfg():
            return
        try:
            button = int(button_or_attribute)
            self._edit_button(button)
        except ValueError:
            self._edit_attribute(button_or_attribute.strip())

    def help_edit(self):
        """Help for command 'edit'."""
        self._message("edit BUTTON", center=True)
        self._message(
            "Edit the key presses associated with BUTTON in the current mapping. "
            "'show' displays the valid button numbers."
            )
        self._message("edit ATTRIBUTE", center=True)
        editable = ", ".join(self._editable())
        self._message(
            "Edit the attribute ATTRIBUTE in the current mapping. "
            f" Editable attributes: {editable}"
            )

    def do_save(self, _arg: str):
        """Save all mappings to file."""
        if not self.changed:
            self._message("No unsaved changes.")
            return
        if os.path.exists(self.mappings_yaml):
            os.rename(self.mappings_yaml, self.mappings_yaml + ".bak")
        with open(self.mappings_yaml, "w", encoding="utf-8") as file_handle:
            file_handle.write(to_yaml(self.mappings))
        self.changed = set()

    def help_save(self):
        """Help for command 'save'."""
        self._message("save", center=True)
        msg = f"Save all mappings to {self.mappings_yaml}."
        self._message(msg)

    def do_undo(self, _arg: str):
        """Undo changes to current mapping."""
        if not self._in_cfg():
            return
        if not self.changed:
            self._message("No unsaved changes to undo.")
            return
        if not os.path.exists(self.mappings_yaml):
            self._message(f"Cannot undo: there are no saved changes at {self.mappings_yaml}.")
            return
        with open(self.mappings_yaml, "r", encoding="utf-8") as file_handle:
            saved_mappings = from_yaml(file_handle.read())
        if saved_mappings is None:
            self._message(f"Cannot undo: invalid mappings file {self.mappings_yaml}.")
            return
        assert 0 <= self.cfg_n < len(self.mappings), "The current mapping is invalid!"
        if self.cfg_n > len(saved_mappings):
            self._message("Cannot undo: the current mapping is not saved. Try 'delete' instead.")
            return
        self.mappings[self.cfg_n] = saved_mappings[self.cfg_n]
        self.changed.remove(self.cfg_n)

    def help_undo(self):
        """Help for command 'undo'."""
        self._message("undo", center=True)
        msg = "Undo unsaved changes to current mapping. To undo all changes, quit the shell."
        self._message(msg)

    def do_quit(self, _arg: str):
        """Exit the CLI shell."""
        if self.changed:
            unsaved = ", ".join([str(m) for m in sorted(list(self.changed))])
            msg = (
                f"The following mappings have unsaved chages: {unsaved}. "
                "Type 'exit' to discard these changes and quit."
            )
            self._message(msg)
            line = input()
            if line.lower() != "exit":
                self._message("Exit cancelled.")
                return
        self._message("Exiting now. Bye!")
        sys.exit(0)

    # helper functions
    # ----------------

    # pylint: disable=too-many-arguments # Just a quick formatting function
    def _message(self, message: str, raw: bool=False,
                center: bool=False, line_after: bool=True, line_before: bool=False):
        """
        Print message with suitable formatting. 
        
        If `center`, `message` should be a single line, which is printed centered; 
        otherwise, `msg` is reflown to a width of `self.WIDTH` characters. 
        
        If `line_after` (resp. `line_before`) is true, an empty line is printed 
        after (resp. before) the message.
        """
        if self._disable_msg:
            return
        if raw:
            text = message
        elif not center:
            text = textwrap.fill(message, width=self.WIDTH)
        else:
            text = f"{message:^{self.WIDTH}}"
        padded = ("\n" if line_before else "") + text + ("\n" if line_after else "")
        print(padded)

    def _quit(self):
        """Help for command 'quit'."""
        self._message("quit", center=True)
        msg = "Exit the CLI shell, warning if there are unsaved changes."
        self._message(msg)

    def _in_cfg(self) -> bool:
        """If a mapping is selected, return True. 
        Otherwise, return False and print an error message."""
        if self.cfg_n is None:
            self._message("Select a mapping first.")
            return False
        return True

    def _editable(self) -> list[str]:
        """Return the editable attributes of a mapping."""
        return [attr.value for attr in EditableAttributes]

    def _edit_button(self, button_num: int):
        """Edit the mapping of `button` in the current mapping."""
        cur_mapping = self.mappings[self.cfg_n]
        button = None
        for button_ in cur_mapping.buttons:
            if button_.identifier == button_num:
                button = button_
                break
        if button is None:
            self._message(f"Invalid button number: {button_num}")
            return
        print(f"Found button {button}")
        keys = ", ".join([f"{key.name}|{key.key}"  for key in cur_mapping.keys])
        self._message(f"Available keys: {keys}", line_before=True)
        self._message(
            f"Mark a key with {Press.TURBO_MARK} for turboing it. "
            f"Use {And.AND_MARK} to combine key presses."
            )
        self._message(
            "The current key press is: " +
            cur_mapping[button].as_text() if button in cur_mapping else "",
            line_after=False
            )
        new_combo = input("Type the new combo: ")
        combo = Combo.from_text(new_combo, keys=cur_mapping.keys)
        if combo is None:
            self._message("Invalid combo.")
            return
        cur_mapping[button] = combo
        self.changed.add(self.cfg_n)

    def _edit_attribute(self, attribute: str):
        """Edit the attribute `attribute` in the current mapping."""
        if attribute not in self._editable():
            self._message(f"Invalid attribute: {attribute}")
            return
        cur_mapping = self.mappings[self.cfg_n]
        if attribute == EditableAttributes.TITLE.value:
            self._message(f"The current mapping's title is: {cur_mapping.title}", line_after=False)
            new_title = input("Type the new title: ")
            cur_mapping.title = new_title.strip()
        if attribute == EditableAttributes.DESCRIPTION.value:
            self._message("The current mapping's description is:")
            self._message(cur_mapping.description)
            self._message(
                "Type the new description, terminating it with one empty line. "
                "To keep the current description, don't type anything and press Enter."
                )
            # read all lines until empty one
            lines = []
            while True:
                line = input()
                if line:
                    lines += [line.strip()]
                else:
                    break
            # if some non-empty lines were read
            if lines:
                # set header
                cur_mapping.description = " ".join(lines)
                self._message("Description changed.")
                self.changed.add(self.cfg_n)
            # if only an empty line was read
            else:
                self._message("Description NOT changed.", line_before=True)


def cli_shell(mappings_yaml: str):
    """
    Start the Nez-Oba CLI shell mappings file `mappings_yaml`.
    If `mappings_yaml` does not exist, create it.
    """
    shell = NezObaCLI()
    shell.mappings_yaml = mappings_yaml
    shell.cmdloop()
