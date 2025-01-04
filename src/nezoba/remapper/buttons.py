"""
Buttons representing all possible physical inputs on a controller.

Variables:
   NEZOBA_BUTTONS: An instance of Buttons with all buttons available on
      the Nez-Oba controller.
"""
from __future__ import annotations
from collections import UserList
from typing import NamedTuple, Optional
from dataclasses import dataclass
from enum import Enum, unique


@dataclass(frozen=True, init=True)
class Button:
    """
    A pressable button.

    Instances of this class represent a button that can be pressed or
    released at any time. Analog inputs are not supported: a button is
    either pressed or released.

    Attributes:
       identifier: An integer uniquely identifying the button.
       name: A string describing the button.
    """

    identifier: int
    name: str


@unique
class ButtonLayout(Enum):
    """
    A button layout.

    A button layout denotes a controller and its available inputs
    (buttons and directional sticks).
    """

    NEZ_OBA = "Nez-Oba controller"


class Buttons(tuple):
    """
    A collection of buttons.

    Instances of this class are immutable sequences of Button
    instances.

    Attributes:
       layout: The buttons' layout.
    """

    layout: Optional[ButtonLayout]

    # pylint: disable=unused-argument # __new__ and __init__ should have the same signature
    def __new__(cls, buttons: list[Button], layout: Optional[ButtonLayout] = None):
        return super().__new__(cls, tuple(buttons))

    def __init__(self, buttons: list[Button], layout: ButtonLayout = None):
        """Creates an instance of Buttons given a list of Button instances.

        The identifiers of the Button instances in buttons must be unique.

        Args:
           buttons: A list of Button instances with unique identifiers.

        Raises:
           AssertionError: If two elements of buttons have the same identifier.
        """
        self.layout = layout
        ids = [b.identifier for b in buttons]
        assert len(ids) == len(set(ids)), "Button identifiers must be unique."

    def __hash__(self) -> int:
        return hash(self + (self.layout,))

    def __eq__(self, other: Buttons) -> bool:
        return super().__eq__(other) and self.layout == other.layout

    def __ne__(self, other: Buttons) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return super().__repr__() + "@" + str(self.layout)



class ButtonsDisplay(NamedTuple):
    """A button set and a tagged picture file showing a controller with the buttons."""
    buttons: Buttons
    picture_filename: str

class ButtonsInfo(UserList):
    """A collection of ButtonsDisplay instances."""

    def __setitem__(self, key: Buttons, value: str):
        """Append a new ButtonsDisplay instance with `key` and `value` fields
        at the end of the list."""
        display = ButtonsDisplay(key, value)
        super().append(display)

    def first(self) -> Optional[Buttons]:
        """The first button set stored in the list, or None
        if the list is empty."""
        try:
            return self[0].buttons
        except (AttributeError, IndexError):
            return None



# Remappable buttons on NezOba.
#
# The identifier of each button should match the name of the
# corresponding object in the SVG, as well as the index in
# `globals.h` (`BUTTONS2MCP`).
B00 = Button(0, "Button #0")
B01 = Button(1, "Button #1")
B02 = Button(2, "Button #2")
B03 = Button(3, "Button #3")
B04 = Button(4, "Button #4")
B05 = Button(5, "Button #5")
B06 = Button(6, "Button #6")
B07 = Button(7, "Button #7")
B08 = Button(8, "Button #8")
B09 = Button(9, "Button #9")
B10 = Button(10, "Button #10")
B11 = Button(11, "Button #11")
B12 = Button(12, "Button #12")
B13 = Button(13, "Button #13")
B14 = Button(14, "Button #14")

NEZOBA_BUTTONS = Buttons([
    B00, B01, B02, B03, B04, B05, B06, B07, B08, B09, B10, B11, B12, B13, B14
], ButtonLayout.NEZ_OBA)


# Tags for serialization
# pylint: disable=invalid-name  # Using the same capitalization as the classnames
TAG_Button = "!Button"
TAG_ButtonLayout = "!ButtonLayout"
TAG_Buttons = "!Buttons"
