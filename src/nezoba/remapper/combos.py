"""
Combinations of key presses on a controller.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Set

from .keys import Key, Keys


# pylint: disable=too-few-public-methods  # One method is all I need!
class Combo:
    """The interface shared by all kinds of key presses."""

    def keys(self) -> set[Key]:
        """Set of all Key instances used in self."""

    def flat(self) -> list[Press]:
        """List of all presses in combo"""

    def __and__(self, other: Combo) -> Combo:
        """Combine `self` and `other` into a simultaneous combo."""

    def as_text(self) -> str:
        """Return a human-readable string representation of the combo."""

    @classmethod
    def from_text(cls, text: str, keys: Keys) -> Optional[Combo]:
        """Parse a human-readable string representation of the combo."""
        ands = [press.strip() for press in text.split(And.AND_MARK)]
        combos = []
        for full_press in ands:
            no_turbo_press = full_press.strip(Press.TURBO_MARK)
            turboed = no_turbo_press != full_press
            no_hold_press = no_turbo_press.strip(Press.HOLD_MARK)
            held = no_hold_press != no_turbo_press
            press_str = no_hold_press.strip()
            try:
                key = keys[press_str]
            except IndexError:
                try:
                    named_keys = [key for key in keys if key.name == press_str]
                    key = named_keys[0]
                except (IndexError, AttributeError):
                    return None
            # if key is K_NOOP we ignore it
            if key == keys[0] and key.key == "K_NOOP":
                continue
            press = Press(key,
                          turbo=Press.TURBO_DEFAULT if turboed else None,
                          hold=Press.HOLD_DEFAULT if held else None)
            combos.append(press)
        if len(combos) == 1:
            return combos[0]
        print(combos)
        return And(combos)


@dataclass
class Press(Combo):
    """
    The press of a single key.

    A press can be turboed: the key is pressed and released repeatedly
    with a given frequency. A press can be held: every press
    alternates between keeping the key pressed and keeping it released
    until the next press.

    Attributes:
       key: The Key that is pressed.
       turbo: An integer denoting the turbo frequency in Hertz (the
          number of time the key is pressed in one second); or None if
          no turbo is applied.
       hold: A positive integer denoting the amount in milliseconds
          the key is held for; or a non-positive integer if the key is
          held until the next press; or None if the duration of the
          key press is the same as the duration of the button press
          (normal behavior of pressing a button).
    """

    TURBO_MARK = "'"
    HOLD_MARK = "_"

    TURBO_DEFAULT = 75
    HOLD_DEFAULT = 0

    key: Key
    turbo: Optional[int] = None
    hold: Optional[int] = None

    def is_turbo(self) -> bool:
        """Is the press turboed?"""
        return isinstance(self.turbo, int) and self.turbo > 0

    def is_hold(self) -> bool:
        """Is the press held for a certain amount of time (or until
        the next press)?"""
        return self.hold is not None

    def is_timed(self) -> bool:
        """Is the press held for a certain, finite amount of time?"""
        return self.is_hold() and self.hold > 0

    def keys(self) -> Set[Key]:
        return set([self.key])

    def flat(self) -> List[Press]:
        return [self]

    def __and__(self, other: Combo) -> Combo:
        if isinstance(other, type(self)):
            return And([self, other])
        return other & self

    def as_text(self) -> str:
        # Use key name if available
        try:
            key = self.key.name
        except AttributeError:
            key = self.key.key
        turbo = self.TURBO_MARK if self.is_turbo() else ""
        hold = self.HOLD_MARK if self.is_hold() else ""
        return hold + key + turbo


class And(Combo, tuple):
    """
    A combination of simultaneous presses of different keys.

    Instances of this class are immutable sequences of Combo
    instances.
    """

    AND_MARK = "&"

    def __new__(cls, cmbs: list[Combo]):
        return super().__new__(cls, tuple(cmbs))

    def __init__(self, cmbs: list[Combo]):
        """Creates an instance of And given a list of Combo instances."""
        # pylint: disable=invalid-name  # c is an acceptable variable name
        for c in cmbs:
            assert isinstance(c, Combo), f"{c} is not of type Combo"

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.__class__.__name__ + super().__repr__()

    def keys(self):
        return set([]).union(*[k.keys() for k in self])

    def flat(self):
        return [item for sublist in [k.flat() for k in self] for item in sublist]

    def __and__(self, other: Combo):
        if isinstance(other, type(self)):
            return And(self + other)
        return And(self + (other,))

    def as_text(self) -> str:
        return f" {self.AND_MARK} ".join(k.as_text() for k in self)




## Tags for serialization
# pylint: disable=invalid-name  # Using the same capitalization as the classnames
TAG_Combo = "!Combo"
TAG_Press = "!Press"
TAG_And = "!AndPress"
