"""
Named variants of Key, Keys, and Mapping.

Variables:

   NS_KEYS: The collection of named keys available on a Nintendo
      Switch system.
   PC_KEYS: The collection of named keys available on a PC (or
      compatible systems such as a Raspberry Pi/Xbox).
   SCHEME_TO_KEYS: A dictionary mapping each name scheme to the
      corresponding instance of NamedKeys.
"""
from __future__ import annotations
from collections import UserDict
from typing import NamedTuple, Union, Optional, List
from dataclasses import dataclass
from enum import Enum, unique

from .buttons import NEZOBA_BUTTONS
from .keys import Key, Keys
from .mappings import Mapping, RawMapping
# from .combos import Press, And


@unique
class NameScheme(Enum):
    """
    A name scheme.

    A name scheme (also: naming scheme) denotes a platform and its
    nomenclature for controller inputs.
    """

    NS = "Nintendo Switch"
    PC = "PC/Raspberry Pi"


@dataclass(frozen=True, init=False)
class NamedKey(Key):
    """
    A named key.

    A named key is a key with a name scheme. In other words, the key
    denotes the controller output, which can be named differently
    under different name scheme.

    Attributes:
       name: The key's name.
       scheme: The name scheme.
       named_description: A description of the key specific to the
          name scheme.
    """

    name: str
    scheme: NameScheme
    named_description: str

    def __init__(self, key: Union[Key, str], *args, **kwargs):
        """Creates an instance of NamedKey given either a Key or all
        attributes of the Key class, plus a name and name scheme.

        There are two ways to call this constructor. In all examples,
        name and scheme are the instance's name and name scheme.

           1. NamedKey(key: Key, name, scheme), where key is an instance of
              Key, which will be extended with a name and scheme.

           2. NamedKey(key: str, identifier, group, description, name,
              scheme), where key is a generic key name (and identifier, group,
              and description are as in Key's constructor).

        Args:
           key: A Key to be named or a generic key name.
           name: A name in this name scheme.
           scheme: A name scheme.
           named_description: A name-specific description. If omitted,
              set to the key's generic description.

        Raises:
           ValueError: If some required arguments are missing.
        """
        def get_arg(arg_name: str, counter: int, strict=True) -> tuple[object, int]:
            """Try to find an argument arg_name in **kwargs, or at
            index counter in *args.

            Args:
               arg_name: The name of the argument to be retrieved (if
                  available as named argument in **kwargs).
               counter: The current index in *args.
               strict: If True, raise an exception if no suitable
                  argument is found.

            Returns:
               A tuple (obj, new_counter), where obj is the argument
               and new_counter is the updated counter in *args. If
               strict is False and no suitable argument is found, obj
               is None.

            Raises:
               ValueError if strict is True and no suitable argument
               was found.
            """
            try:
                obj = kwargs[arg_name]
            except KeyError:
                try:
                    obj = args[counter]
                    counter += 1
                except IndexError as exc:
                    if strict:
                        raise ValueError(f"Missing argument: {arg_name}") from exc
                    obj = None
            return (obj, counter)
        a_i = 0
        if isinstance(key, Key):
            _key = key.key
            _identifier = key.identifier
            _group = key.group
            _description = key.description
        else:
            _key = key
            _identifier, a_i = get_arg("identifier", a_i)
            _group, a_i = get_arg("group", a_i)
            _description, a_i = get_arg("description", a_i)
        _name, a_i = get_arg("name", a_i)
        _scheme, a_i = get_arg("scheme", a_i)
        _named_description, a_i = get_arg("named_description", a_i, strict=False)
        super().__init__(_key, _identifier, _group, _description)
        if _named_description is None:
            _named_description = _description
        object.__setattr__(self, "name", _name)
        object.__setattr__(self, "scheme", _scheme)
        object.__setattr__(self, "named_description", _named_description)

    def unnamed(self) -> Key:
        as_key = Key(key=self.key,
                     identifier=self.identifier,
                     group=self.group,
                     description=self.description)
        return as_key

    # def change_scheme(self, new_keys: NamedKeys) -> Optional[NamedKey]:
    #     try:
    #         return new_keys[self.key]
    #     except IndexError:
    #         return None


class NamedKeys(Keys):
    """
    A collection of named keys.

    All keys in the collection must use the same name scheme.
    """

    scheme: NameScheme

    def __new__(cls, keys: list[NamedKey]):
        return super().__new__(cls, keys)

    def __init__(self, keys: list[NamedKey]):
        """Creates an instance of NamedKeys given a list of NamedKey instances.

        The NamedKey instances in keys must be unique (constraints
        inherited from Keys) and must all use the same name scheme.

        Args:
           keys: A list of NameKey instances with the same name scheme.

        Raises:
           AssertionError: If two elements of keys use different name
              schemes.
        """
        # perform the same consistenty check of superclass
        super().__init__(keys)
        nks = [isinstance(nk, NamedKey) for nk in keys]
        assert all(nks), "Named keys may only include instances of NamedKey"
        schemes = {k.scheme for k in self}
        assert len(schemes) <= 1, \
            f"Different naming schemes cannot be mixed: {schemes}"
        for scheme in schemes:
            self.scheme = scheme

    def unnamed(self) -> Keys:
        as_keys = Keys([n.unnamed() for n in self])
        return as_keys

    # def change_scheme(self, new_keys: NamedKeys) -> NamedKeys:
    #     result = [new for new in [key.change_scheme(new_keys) for key in self] if new is not None]
    #     return NamedKeys(result)


class NamedMapping(Mapping):
    """
    A named mapping.

    A named mapping is a buttons-to-keys mapping whose keys have the same name scheme.

    Attributes:
       scheme: The name scheme of all keys in the mapping's codomain.
    """

    scheme: NameScheme

    def __init__(self, *args, **kwargs):
        """Creates an instance of NamedMapping.

        There are two ways to call this constructor.

           1. NamedMapping(mapping: Mapping), where mapping is an
              instance of Mapping whose codomain is an instance of
              NamedKeys. The constructed instance will have the same
              button-to-combo associations as mapping. In other words,
              this acts as a copy constructor.

           2. NamedMapping(buttons: Buttons, keys: NamedKeys,
              identifier, title, description), where keys is an
              instance of NamedKey (and the other arguments are as in
              Mapping's constructor). The constructed instance will
              represent an empty mapping.

        Raises:
           TypeError: If some of the mapping does not use NamedKeys as codomain.
           ValueError: If the codomain is empty.

        """
        # pylint: disable=invalid-name  # m and b are acceptable variable names
        m = None
        if len(args) + len(kwargs) == 1:
            try:
                m = args[0]
            except IndexError:
                try:
                    m = kwargs["mapping"]
                except KeyError:
                    pass
        if m is None:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(m.buttons, m.keys,
                             m.identifier, m.title, m.description)
            for b, k in m.items():
                self[b] = k
        if not self.keys:
            raise ValueError("Named mappings must include at least one key")
        if not isinstance(self.keys, NamedKeys):
            raise TypeError("Named mappings can only use NamedKeys")
        self.scheme = self.keys[0].scheme

    def raw(self) -> RawMapping:
        """Encode a single mapping into a string that can be written to a header file."""
        raw_mapping = super().raw()
        raw_mapping.scheme = self.scheme.name
        return raw_mapping

    # def change_scheme(self, new_keys: NamedKeys) -> NamedMapping:
    #     old_keys = self.keys
    #     new_keys = old_keys.change_scheme(new_keys)
    #     result = NamedMapping(self.buttons, new_keys,
    #                           self.identifier, self.title, self.description)
    #     for button, combo in self.items():
    #         new_keys = [(press.key.change_scheme(new_keys), press) for press in combo.flat()]
    #         new_combo = [Press(key, press.turbo, press.hold) \
    #                      for key, press in new_keys if key is not None]
    #         result[button] = And(new_combo)
    #     return result



class KeysDisplay(NamedTuple):
    """A named key set and a tagged picture file showing a gamepad with the keys."""
    keys: NamedKeys
    picture_filename: str

class KeysInfo(UserDict):
    """A collection of KeysDisplay instances, indexed by NameScheme."""

    def __setitem__(self, key: NamedKeys, value: str):
        """Add a new KeysDisplay instance with `key` and `value` fields,
        indexed by `key.scheme`."""
        scheme = key.scheme
        # if scheme in self and self[scheme] != value:
        #     logging.warning("Overwriting key set for %s", scheme)
        display = KeysDisplay(key, value)
        super().__setitem__(scheme, display)

    def schemes(self) -> List[NameScheme]:
        """The available naming schemes."""
        return list(self.keys())

    def first(self) -> Optional[NamedKeys]:
        """The first named keys set stored in the dictionary, or None
        if the dictionary is empty."""
        try:
            return self[self.schemes()[0]].keys
        except IndexError:
            return None



# pylint: disable=wrong-import-position  # Placing a long import right where it's used
from .keys import (K_NOOP, K_DP_UP, K_DP_UP_RIGHT, K_DP_RIGHT,
                   K_DP_DOWN_RIGHT, K_DP_DOWN, K_DP_DOWN_LEFT, K_DP_LEFT, K_DP_UP_LEFT,
                   K_DP_CENTER, K_A, K_B, K_X, K_Y, K_L, K_R, K_ZL, K_ZR, K_HOME, K_PLUS,
                   K_MINUS, K_LS_PRESS, K_RS_PRESS, K_CAPTURE, K_LS_UP, K_LS_UP_RIGHT,
                   K_LS_RIGHT, K_LS_DOWN_RIGHT, K_LS_DOWN, K_LS_DOWN_LEFT, K_LS_LEFT,
                   K_LS_UP_LEFT, K_LS_CENTER, K_RS_UP, K_RS_UP_RIGHT, K_RS_RIGHT,
                   K_RS_DOWN_RIGHT, K_RS_DOWN, K_RS_DOWN_LEFT, K_RS_LEFT, K_RS_UP_LEFT,
                   K_RS_CENTER)


_NS_KEYS = [
    NamedKey(K_NOOP, "", NameScheme.NS),
    NamedKey(K_DP_UP, "⇑", NameScheme.NS),
    NamedKey(K_DP_UP_RIGHT, "⇗", NameScheme.NS),
    NamedKey(K_DP_RIGHT, "⇒", NameScheme.NS),
    NamedKey(K_DP_DOWN_RIGHT, "⇘", NameScheme.NS),
    NamedKey(K_DP_DOWN, "⇓", NameScheme.NS),
    NamedKey(K_DP_DOWN_LEFT, "⇙", NameScheme.NS),
    NamedKey(K_DP_LEFT, "⇐", NameScheme.NS),
    NamedKey(K_DP_UP_LEFT, "⇖", NameScheme.NS),
    NamedKey(K_DP_CENTER, "⬤", NameScheme.NS),
    NamedKey(K_A, "A", NameScheme.NS),
    NamedKey(K_B, "B", NameScheme.NS),
    NamedKey(K_X, "X", NameScheme.NS),
    NamedKey(K_Y, "Y", NameScheme.NS),
    NamedKey(K_L, "L", NameScheme.NS),
    NamedKey(K_R, "R", NameScheme.NS),
    NamedKey(K_ZL, "ZL", NameScheme.NS),
    NamedKey(K_ZR, "ZR", NameScheme.NS),
    NamedKey(K_HOME, "⌂", NameScheme.NS),
    NamedKey(K_PLUS, "+", NameScheme.NS, named_description="Menu +"),
    NamedKey(K_MINUS, "-", NameScheme.NS, named_description="Menu -"),
    NamedKey(K_LS_PRESS, "L✓", NameScheme.NS),
    NamedKey(K_RS_PRESS, "R✓", NameScheme.NS),
    NamedKey(K_CAPTURE, "capture", NameScheme.NS),
    NamedKey(K_LS_UP, "L⇑", NameScheme.NS),
    NamedKey(K_LS_UP_RIGHT, "L⇗", NameScheme.NS),
    NamedKey(K_LS_RIGHT, "L⇒", NameScheme.NS),
    NamedKey(K_LS_DOWN_RIGHT, "L⇘", NameScheme.NS),
    NamedKey(K_LS_DOWN, "L⇓", NameScheme.NS),
    NamedKey(K_LS_DOWN_LEFT, "L⇙", NameScheme.NS),
    NamedKey(K_LS_LEFT, "L⇐", NameScheme.NS),
    NamedKey(K_LS_UP_LEFT, "L⇖", NameScheme.NS),
    NamedKey(K_LS_CENTER, "L⬤", NameScheme.NS),
    NamedKey(K_RS_UP, "R⇑", NameScheme.NS),
    NamedKey(K_RS_UP_RIGHT, "R⇗", NameScheme.NS),
    NamedKey(K_RS_RIGHT, "R⇒", NameScheme.NS),
    NamedKey(K_RS_DOWN_RIGHT, "R⇘", NameScheme.NS),
    NamedKey(K_RS_DOWN, "R⇓", NameScheme.NS),
    NamedKey(K_RS_DOWN_LEFT, "R⇙", NameScheme.NS),
    NamedKey(K_RS_LEFT, "R⇐", NameScheme.NS),
    NamedKey(K_RS_UP_LEFT, "R⇖", NameScheme.NS),
    NamedKey(K_RS_CENTER, "R⬤", NameScheme.NS)
]

NS_KEYS = NamedKeys(_NS_KEYS)

_PC_FROM_NS = {
    # A and B are switched
    "K_A": ("B", "Button B"), "K_B": ("A", "Button A"),
    # X and Y are switched
    "K_X": ("Y", "Button Y"), "K_Y": ("X", "Button X"),
    # shoulder buttons are called "bumpers"
    "K_L": ("LB", "Button left bumper"), "K_R": ("RB", "Button right bumper"),
    # triggers are named LT/RT
    "K_ZL": ("LT", "Button left trigger"), "K_ZR": ("RT", "Button right trigger"),
    # - and + are called "select" and "start"
    "K_MINUS": ("select", "Menu select"), "K_PLUS": ("start", "Menu start")
    }

_PC_KEYS = [(NamedKey(n, n.name, NameScheme.PC, n.named_description)
             if n.key not in _PC_FROM_NS
             else NamedKey(n,
                           _PC_FROM_NS[n.key][0],
                           NameScheme.PC,
                           _PC_FROM_NS[n.key][1]))
            for n in _NS_KEYS]

PC_KEYS = NamedKeys(_PC_KEYS)


SCHEME_TO_KEYS = {
    NameScheme.NS: NS_KEYS,
    NameScheme.PC: PC_KEYS
}

def default_from_scheme(scheme: NameScheme = NameScheme.NS) -> NamedMapping:
    """An empty mapping with default Nez-Oba buttons and keys for the given naming scheme."""
    buttons = NEZOBA_BUTTONS
    keys = SCHEME_TO_KEYS[scheme]
    return NamedMapping(buttons, keys)


## Tags for serialization
# pylint: disable=invalid-name  # Using the same capitalization as the classnames
TAG_NameScheme = "!NameScheme"
TAG_NamedKey = "!NamedKey"
TAG_NamedKeys = "!NamedKeys"
TAG_NamedMapping = "!NamedMapping"
