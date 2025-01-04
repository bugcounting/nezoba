"""This module provides views for all components of the GUI."""

from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass
import logging

from ..remapper.buttons import Button, Buttons
from ..remapper.keys import Key
from ..remapper.namings import NameScheme
from ..remapper.combos import Press, And
from .model import State, View


# pylint: disable=too-few-public-methods
# Views are usually classes with a very small interface.


class ComboView(View[State]):
    """The currently selected key press combo."""

    @dataclass(frozen=True, init=True)
    class Value:
        """The value of the view.
        
        Attributes:
            presses: The list of presses of the currently selected button,
              or None if no button is selected.
            scheme: The name scheme of the currently selected mapping,
              or None if no mapping is selected.
            in_edit: The index of the press currently being edited,
              or None if no press is being edited.
        """
        presses: Optional[List[Press]] = None
        scheme: Optional[NameScheme] = None
        in_edit: Optional[int] = None

    @property
    def value(self) -> ComboView.Value:
        mapping = self._state.mapping
        button = self._state.button
        try:
            combo = mapping[button]
            presses = combo.flat()
        except (KeyError, TypeError):
            if mapping is None or button is None:
                presses = None
            else:
                presses = []
        if mapping is None:
            scheme = None
        else:
            scheme = mapping.scheme
        in_edit = self._state.in_edit
        return ComboView.Value(presses=presses, scheme=scheme, in_edit=in_edit)

    @value.setter
    def value(self, new_value: Optional[list[Press]]):
        """Set the currently selected button to the combo corresponding to
        the simultaneous pressing of keys `new_value`. If `new_value` is None,
        reset the currently's selected button's combo. If no button is currently
        selected, do nothing."""
        if new_value is None:
            combo = None
        else:
            combo = And(new_value)
        mapping = self._state.mapping
        button = self._state.button
        if mapping is None or button is None:
            return
        mapping[button] = combo
        self._state.modified()

    def remove(self, idx: int):
        """Delete the press at index `idx` from the currently selected button's combo."""
        presses = self.value.presses
        removed = None
        if 0 <= idx < len(presses):
            removed = presses[idx]
        new_presses = presses[:idx] + presses[idx + 1:]
        self.value = new_presses
        self.message(f"Key press removed at index {idx} "
                     f"({removed.key.name if removed else removed}).")

    def add_empty(self, idx: int):
        """Add an empty press at index `idx` to the currently selected button's combo."""
        presses = self.value.presses
        try:
            noop = self._state.mapping.keys[0]
        except (IndexError, AttributeError):
            logging.warning("Cannot find NOOP key.")
            return
        empty_press = Press(noop)
        new_presses = presses[:idx+1] + [empty_press] + presses[idx+1:]
        self.message(f"Empty key press added at index {idx}.")
        self.value = new_presses

    def set_key(self, idx: int, key: Key):
        """Set to `key` the key of the press at index `idx` 
        in the currently selected button's combo."""
        presses = self.value.presses
        if presses is None:
            return
        if 0 <= idx < len(presses):
            old = presses[idx]
            new = Press(key, turbo=old.turbo, hold=old.hold)
            new_presses = presses[:idx] + [new] + presses[idx + 1:]
            self.value = new_presses
            self.message(f"Key press at index {idx} changed to {key.name}.")


class PressView(ComboView):
    """The key press at index `press_idx` in the currently selected button's combo.
    
    Attributes:
        press_idx: The index of the press monitored by this view
         (passed as an extra named argument to the constructor).
    """

    press_idx: int

    @property
    def value(self) -> Optional[Press]:
        presses = super().value.presses
        try:
            press = presses[self.press_idx]
        except IndexError:
            return None
        return press


class KeyNameView(View[Press]):
    """Name of the key in this press."""

    @property
    def value(self) -> str:
        return self._state.key.name


class KeyDescriptionView(View[Press]):
    """Description of the key in this press."""

    @property
    def value(self) -> str:
        return self._state.key.named_description


class KeyIsTurboView(View[Press]):
    """Is the key in this press turboed?"""

    @property
    def value(self) -> bool:
        return self._state.is_turbo()

    @value.setter
    def value(self, new_value: bool):
        if not new_value and self._state.is_turbo():
            self._state.turbo = None
            self.message("Turbo of current key removed.")
        elif new_value and not self._state.is_turbo():
            self._state.turbo = Press.TURBO_DEFAULT
            self.message("Turbo of current key added.")


class KeyTurboView(View[Press]):
    """Turbo value of the key in this press, 
    or the empty string if the key is not turboed."""

    @property
    def value(self) -> str:
        turbo = self._state.turbo
        if turbo is None:
            return ""
        return str(turbo)

    @value.setter
    def value(self, new_value: str):
        try:
            new_value = int(float(new_value))
            self.message(f"Turbo of current key set to {new_value}.")
        except ValueError:
            new_value = None
            self.message("Turbo of current removed.")
        self._state.turbo = new_value


class KeyIsHoldView(View[Press]):
    """Is the key in this press held?"""

    @property
    def value(self) -> bool:
        return self._state.is_hold()

    @value.setter
    def value(self, new_value: bool):
        if not new_value and self._state.is_hold():
            self._state.hold = None
            self.message("Hold of current key removed.")
        elif new_value and not self._state.is_hold():
            self._state.hold = Press.HOLD_DEFAULT
            self.message("Hold of current key added.")


class KeyHoldView(View[Press]):
    """Hold value of the key in this press, 
    or the empty string if the key is not held."""

    @property
    def value(self) -> str:
        hold = self._state.hold
        if hold is None:
            return ""
        return str(hold)

    @value.setter
    def value(self, new_value: str):
        try:
            new_value = int(float(new_value))
            self.message(f"Hold of current key set to {new_value}.")
        except ValueError:
            new_value = None
            self.message("Hold of current key removed.")
        self._state.hold = new_value


class HeaderView(View[State]):
    """The header string, including the configuration number and the mapping's title"""

    @property
    def value(self) -> str:
        mapping = self._state.mapping
        configuration = self._state.configuration
        header = ""
        if configuration is not None:
            header += f"Configuration #{configuration}"
            if mapping is not None and mapping.title is not None:
                header += f": {mapping.title}"
        return header


class ControllerButtonView(View[State]):
    """The keys mapped to `button`, and whether `button` is currently selected.
    
    Attributes:
        button: The button monitored by this view.
    """

    button: Button

    @dataclass(frozen=True, init=True)
    class Value:
        """The value of the view.

        Attributes:
            input: Whether the current mapping's selected button is 
              the same as `button`.
            output: A list of the names of keys that are mapped to `button`.
        """
        input: bool = False
        output: List[str] = None

    @property
    def value(self) -> ControllerButtonView.Value:
        button_input = self._state.button == self.button
        try:
            mapping = self._state.mapping
            combo = mapping[self.button].flat()
            button_output = [press.as_text() for press in combo]
        except (KeyError, AttributeError, TypeError):
            button_output = []
        return ControllerButtonView.Value(input=button_input, output=button_output)


class ControllersView(View[State]):
    """The buttons of the currently selected mapping, 
    or None if no mapping is selected."""

    @property
    def value(self) -> Optional[Buttons]:
        mapping = self._state.mapping
        if mapping is None:
            buttons = None
        else:
            buttons = mapping.buttons
        return buttons

    @value.setter
    def value(self, new_value: Optional[Button]):
        """Set the currently selected button in the current mapping
        to `new_value`. If `new_value` is different from the previously
         selected button, also exit the edit state."""
        button = self._state.button
        if button == new_value:
            return
        self._state.in_edit = None
        self._state.button = new_value


class ConfigurationBitView(View[State]):
    """Whether the current configuration's `bit_number` is on or off.

    For each `bit_number`, there are two instances of the current class:
    one where `high` is True, and one where `high` is False. An instance
    has value True iff exactly one of the following conditions holds:
     
      1. The current configuration's `bit_number`th binary digit is 1, 
         and `high` is True.

      2. The current configuration's `bit_number`th binary digit is 0,
         and `high` is False.

    Attributes:
        bit_number: The bit number monitored by this view
          (passed as an extra named argument to the constructor).
        high: Whether this view monitors when the bit is high (i.e., 1)
          (passed as an extra named argument to the constructor).
    """

    bit_number: int
    high: bool

    # The view is False iff the bit is off
    @property
    def value(self) -> bool:
        cfg = self._state.configuration
        off = True
        if cfg is not None:
            # cfg as a binary number, big-endian
            bits = [bool(int(digit)) for digit in reversed(f"{cfg:b}")]
            # set to on the corresponding digit (low or high)
            if 0 <= self.bit_number < len(bits) and (bits[self.bit_number] == self.high):
                off = False
            # all other bits are set iff they are low bits
            if self.bit_number >= len(bits) and not self.high:
                off = False
        return off


class InEditView(View[State]):
    """Whether the current mapping's scheme is the same as `scheme`,
    and a key press is currently being edited.

    Attributes:
        scheme: The scheme monitored by this view 
          (passed as an extra named argument to the constructor).
    """

    scheme: Optional[NameScheme]

    @property
    def value(self) -> bool:
        if self.scheme is None:
            scheme_is_current = True
        else:
            mapping = self._state.mapping
            if mapping is None:
                scheme = None
            else:
                scheme = mapping.scheme
            scheme_is_current = self.scheme == scheme
        # The current scheme is the same as `self.scheme`,
        # and the state's `in_edit`` is not None.
        show = scheme_is_current and self._state.in_edit is not None
        return show


@dataclass(frozen=True, init=True)
class Option:
    """The `current` value of an option, among a number of possible `choices`."""
    current: str
    choices: List[str]


class PlatformView(View[State]):
    """The scheme of the currently selected mapping, 
    or the empty string if no mapping is selected."""

    @property
    def value(self) -> Option:
        mapping = self._state.mapping
        if mapping is None or mapping.scheme is None:
            current_option = ""
        else:
            current_option = mapping.scheme.value
        return Option(
            current=current_option,
            choices=[scheme.value \
                               for scheme in self._state.options.keys.schemes()]
            )

    @value.setter
    def value(self, new_value: str):
        new_scheme = [scheme \
                      for scheme in self._state.options.keys.schemes() \
                      if scheme.value == new_value]
        assert len(new_scheme) == 1, f"Invalid name scheme value: {new_value}"
        new_scheme = new_scheme[0]
        mapping = self._state.mapping
        if mapping is None:
            logging.warning("No current mapping: scheme not changed")
            return
        old_scheme = mapping.scheme
        if new_scheme == old_scheme:
            return
        # Change scheme of current mapping
        try:
            new_keys, _ = self._state.options.keys[new_scheme]
        except KeyError:
            logging.error("There is no set of keys for scheme %s", new_scheme)
            return
        new_mapping = mapping.change_scheme(new_keys)
        self._state.mapping = new_mapping
        self.message("Platform changed.")


class SwapFromView(View[State]):
    """The option currently selected for swapping from."""

    def _get_current(self) -> Optional[int]:
        return self._state.swap_from

    def _set_current(self, value: Optional[int]):
        self._state.swap_from = value

    @property
    def value(self) -> Option:
        available_options = list(range(len(self._state.mappings)))
        current_option = self._get_current()
        if current_option not in available_options:
            current_option = ""
        return Option(
            current=str(current_option),
            choices=[str(opt) for opt in available_options]
            )

    @value.setter
    def value(self, new_value: str):
        try:
            new_swap = int(new_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid configuration number: {new_value}") from exc
        self._set_current(new_swap)


class SwapToView(SwapFromView):
    """The option currently selected for swapping to."""

    def _get_current(self) -> Optional[int]:
        return self._state.swap_to

    def _set_current(self, value: Optional[int]):
        self._state.swap_to = value


class TitleView(View[State]):
    """The title of the current mapping, 
    or the empty string if no mapping is currently selected."""

    @property
    def value(self) -> str:
        mapping = self._state.mapping
        if mapping is None or mapping.title is None:
            return ""
        return mapping.title

    @value.setter
    def value(self, new_value: str):
        mapping = self._state.mapping
        if mapping is None or mapping.title == new_value:
            return
        mapping.title = new_value
        self._state.modified()
        self.message("Title changed.")


class DescriptionView(View[State]):
    """The description of the current mapping, 
    or the empty string if no mapping is currently selected."""

    @property
    def value(self) -> str:
        mapping = self._state.mapping
        if mapping is None or mapping.description is None:
            return ""
        return mapping.description

    @value.setter
    def value(self, new_value: str):
        mapping = self._state.mapping
        if mapping is None or mapping.description == new_value:
            return
        mapping.description = new_value
        self._state.modified()
        self.message("Description changed.")


class AlwaysView(View[State]):
    """A view that always returns True."""

    @property
    def value(self) -> bool:
        return True


class MaySwapView(View[State]):
    """Is it possible to swap configurations 
    (that is, are two configurations selected for swapping)?"""

    @property
    def value(self) -> bool:
        may_swap = self._state.swap_from is not None and self._state.swap_to is not None
        return may_swap


class ExistsCurrentView(View[State]):
    """Is a configuration currently selected?"""

    @property
    def value(self) -> bool:
        current_exists = self._state.configuration is not None
        return current_exists


class CurrentHasChangedView(View[State]):
    """Has the current configuration changed (and not been saved yet)?"""

    @property
    def value(self) -> bool:
        has_changed = self._state.configuration in self._state.unsaved
        return has_changed


class AnyHasChangedView(View[State]):
    """Has any configuration changed (and not been saved yet)?"""

    @property
    def value(self) -> bool:
        any_change = len(self._state.unsaved) > 0
        return any_change


class UploadPickedView(View[State]):
    """Whether a file has been selected for upload."""

    @property
    def value(self) -> bool:
        picked = self._state.upload_selected
        return picked


class FilenameView(View[State]):
    """The name of the current file."""

    @property
    def value(self) -> str:
        filename = self._state.filename
        assert filename is not None, "Filename is None."
        return filename

    @value.setter
    def value(self, new_value: str):
        self._state.filename = new_value


class MessageView(View[State]):
    """The text representing the current status messages."""

    @property
    def value(self) -> str:
        messages = "\n".join(self._state.options.messages)
        return messages


class ConfigurationsView(View[State]):
    """The list of available configurations, and the one currently active."""

    @dataclass(frozen=True, init=True)
    class Value:
        """The value of the view.

        Attributes:
            configurations: The list of available configurations.
            active: Either a singleton list with the currently active configuration, 
              or the empty list if no configuration is active.
        """
        configurations: List[int]
        active: List[int]

    @property
    def value(self) -> ConfigurationsView.Value:
        configurations = list(range(len(self._state.mappings)))
        current = self._state.configuration
        if current is None:
            active = []
        else:
            active = [current]
        assert current is None or current in configurations, \
            f"Invalid current configuration: {current}"
        return ConfigurationsView.Value(
            configurations=configurations,
            active=active
            )

    @value.setter
    def value(self, new_value: int):
        """Set the current configuration to `new_value`."""
        self._state.configuration = new_value
