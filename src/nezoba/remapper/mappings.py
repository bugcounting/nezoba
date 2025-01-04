"""
Mappings associating key presses to buttons, that is controller
outputs to controller inputs.
"""
from dataclasses import dataclass
from typing import Optional
from collections import UserDict, UserList

from .buttons import Buttons, Button
from .keys import Keys
from .combos import Combo


@dataclass
class RawMapping:
    """A textual, human readable representation of a mapping."""
    title: str
    description: str
    scheme: str
    presses: list[str]
    keys: list[list[str]]
    turboes: list[list[bool]]
    holds: list[list[bool]]


class Mapping(UserDict):
    """
    A mapping of Button instances to Combo instances.

    Attributes:
       identifier: An integer uniquely identifying the mapping.
       title: A string concisely describing the mapping.
       description: A string with a longer description of the mapping.

    """

    buttons: Buttons
    keys: Keys
    identifier: int
    title: str
    description: str

    def __init__(self,
                 buttons: Buttons=Buttons([]), keys: Keys=Keys([]),
                 identifier: int=0, title: str="", description: str=""):
        # pylint: disable=too-many-arguments  # This is a dataclass + dictionary
        """Creates an instance of a mapping from buttons to combos.

        A mapping's domain self.buttons is the set of all buttons that
        may be mapped to. A mapping's codomain self.keys is the set of
        all keys that may appear in any combo that is mapped to some
        button. With no arguments to the constructor, the mapping is empty.

        Args:
           buttons: The Buttons denoting the mapping's domain.
           keys: The Keys denoting the mapping's codomain.
           identifier: The mapping's integer identifier.
           title: The mapping's title.
           description: The mapping's description.
        """
        self.buttons = buttons
        self.keys = keys
        self.identifier = identifier
        self.title = title
        self.description = description
        super().__init__()

    def __setitem__(self, button: Button, combo: Combo):
        """Map button to combo in self.

        Args:
           button: Must be an element of self.buttons.
           combo: A Combo such that all elements of combo.keys() are
              also elements of self.keys..

        Raises:
           AssertionError: If button is not in self.buttons, or some
              combo.keys() is not in self.keys.
        """
        assert button in self.buttons, f"Cannot remap unknown button: {button}"
        unknown_keys = {k for k in combo.keys() if k not in self.keys}
        assert not unknown_keys, f"Cannot remap unknown keys: {unknown_keys}"
        super().__setitem__(button, combo)

    def istotal(self):
        """Is every button in self.buttons mapped to something?"""
        return all(b in self for b in self.buttons)

    def raw(self) -> RawMapping:
        """Encode a single mapping into a string that can be written to a header file."""
        title = self.title
        description = " ".join(self.description.split())
        scheme = ""
        # Even though the underlying dictionary is ordered, the order of insertion of the mapping
        # is immaterial. This is not an issue when the mapping is used as a mapping from buttons,
        # but when we extract the raw mapping we want the presses to be in the same order as the
        # buttons.
        ordered_combos = [self[button] for button in self.buttons if button in self]
        presses = [combo.as_text() for combo in ordered_combos]
        keys = [[press.key.key for press in combo.flat()] for combo in ordered_combos]
        turboes = [[press.is_turbo() for press in combo.flat()] for combo in ordered_combos]
        holds = [[press.is_hold() for press in combo.flat()] for combo in ordered_combos]
        return RawMapping(
            title=title,
            description=description,
            scheme=scheme,
            presses=presses,
            keys=keys,
            turboes=turboes,
            holds=holds
            )


class Mappings(UserList):
    """
    A collection of mappings.

    Instances of this class are mutable sequences of Mapping
    instances.

    Attributes:
       buttons: An instance of Buttons that every mapping in self has as
          domain.
       keys: An instance of Keys that every mapping in self has as
          codomain.

    All operations validate the input to enforce the class invariant:
       - All elements e in self are of type Mapping
       - All elements e in self have the same domain e.buttons
       - All elements e in self have the range included in the same
         codomain e.keys.unnamed()
    """

    buttons: Optional[Buttons]
    keys: Optional[Keys]

    def __init__(self, seq: Optional[list[Mapping]]=None):
        """Creates an instance of Mappings given a list seq of Mapping
        instances.

        Args:
           seq: A list of Mapping instances, all with the same domain
              and codomain.

        """
        if seq is None:
            seq = []
        super().__init__(seq)
        self.buttons, self.keys = None, None
        self._validate(seq, only_lists=True)

    def __setitem__(self, index: int, item: Mapping):
        self._validate(item)
        self.data[index] = item

    def insert(self, i: int, item: Mapping):
        self._validate(item)
        self.data.insert(i, item)

    def append(self, item: Mapping):
        self._validate(item)
        self.data.append(item)

    def extend(self, other: list[Mapping]):
        self._validate(other)
        self.data.extend(other)

    def pop(self, i: int=-1) -> Mapping:
        return self.data.pop(i)

    def from_identifier(self, identifier: int) -> Mapping:
        """Returns the Mapping in self with given identifier.

        Args:
           identifier: The integer identifier of a Mapping in self.

        Returns:
           The Mapping in self with given identifier. If there are
           multiple Mapping instances with the identifier, returns the
           first one in list order.

        Raises:
           IndexError: If there is no Mapping in self with identifier.

        """
        lookup = [m for m in self if m.identifier == identifier]
        if not lookup:
            raise IndexError(f"mapping with identifier {identifier} not found")
        return lookup[0]

    def _validate(self, eoit: object, only_lists: bool=False):
        """Validate eoit to check if its element can be added to self
        without breaking the class invariant.

        If validation is successful, the method terminates
        normally. Otherwise, it raises an exception that explains the
        validation failure.

        Args:
           eoit: An object to be validated. It must be a list[Mapping]
              or a single Mapping.
           only_lists: If True, eoit must be a list, otherwise
              validation fails.

        Raises:
           TypeError: If eoit is of the incorrect type.
           ValueError: If the Mapping instances in eoit fail
              validation (and would violate the class invariant).

        """
        # If eoit is not a list, convert it to single-element list
        if not isinstance(eoit, list):
            if only_lists:
                raise TypeError(f"{eoit} should be a list")
            seq = [eoit]
        else:
            seq = eoit
        # pylint: disable=invalid-name  # bs, ks, ... are all acceptable variable names
        bs, ks = set(), set()
        for e in seq:
            if not isinstance(e, Mapping):
                raise ValueError("Mappings can only store Mapping instances")
            bs |= {e.buttons}
            ks |= {e.keys.unnamed()}
        bs |= {m.buttons for m in self}
        ks |= {m.keys.unnamed() for m in self}
        if len(bs) > 1:
            raise ValueError("Cannot mix mappings over different buttons")
        if len(ks) > 1:
            raise ValueError("Cannot mix mappings over different keys")
        # Update buttons and keys of whole Mappings instance
        for b in bs:
            self.buttons = b
            break
        for k in ks:
            self.keys = k.unnamed()
            break



## Tags for serialization
# pylint: disable=invalid-name  # Using the same capitalization as the classnames
TAG_Mapping = "!Mapping"
TAG_Mappings = "!MappingList"
