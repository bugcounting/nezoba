"""
Keys representing all possible outputs on a controller.

Variables:
   STANDARD_KEYS: The collection of keys (including stick movements)
      available on a standard gamepad.
"""
# Allow using the defined class in its type annotations
from __future__ import annotations
from typing import Union

from dataclasses import dataclass
from enum import Enum, unique


@unique
class KeyGroup(Enum):
    """
    A key group.

    A key group represents a partition of all possible keys. Mainly,
    we distinguish between regular buttons, Dpad directions, and stick
    directions.
    """

    NOOP = "NOOP"
    DPAD = "DP"
    LEFT_STICK = "LS"
    RIGHT_STICK = "RS"
    REGULAR = "BUTTON"


@dataclass(frozen=True)
class Key:
    """
    A key output.

    Attributes:
       key: A string with a unique key name.
       identifier: An integer uniquely identifying the key.
       group: The KeyGroup this key belongs to.
       description: A string describing the key.
    """

    key: str
    identifier: int
    group: KeyGroup
    description: str

    def unnamed(self) -> Key:
        """This key without platform-specific names."""
        return self


class Keys(tuple):
    """
    A collection of keys.

    Instances of this class are immutable sequences of Key instances.
    """

    def __new__(cls, keys: list[Key]):
        return super().__new__(cls, tuple(keys))

    def __init__(self, keys: list[Key]):
        """Creates an instance of Keys given a list of Key instances.

        The Key instances in keys must be unique (no repeated keys,
        and no repeated identifiers).

        Args:
           keys: A list of unique Key instances.

        Raises:
           AssertionError: If two elements of keys are not unique.
        """
        # pylint: disable=invalid-name  # ks is an acceptable variable name
        ids, ks = [], []
        for k in keys:
            kid = k.identifier
            assert kid > 0 or (kid == 0 and k.group == KeyGroup.NOOP), \
                    f"Invalid key identifier: {k}"
            ids += [kid]
            ks += [k.key]
        assert len(ids) == len(set(ids)), "Key identifiers must be unique"
        assert len(ks) == len(set(ks)), "Keys must be unique"
        for k in keys:
            assert isinstance(k.group, KeyGroup), \
                f"{k} is not of enum type KeyGroup"

    def __getitem__(self, idx: Union[int, str]) -> Key:
        """Returns the key in self identified by idx.

        If idx is an integer, returns the key at index idx. If idx is
        a string, returns the key with key name idx.

        Args:
           idx: An integer index, or a string key name.

        Raises:
           IndexError: If idx does not correspond to any key in self.

        """
        if isinstance(idx, int):
            return super().__getitem__(idx)
        for k in self:
            if k.key == idx:
                return k
        raise IndexError("key not found")

    def group_ranges(self, group: KeyGroup) -> list:
        """Returns a list of endpoints of all keys in group by
        identifier number.

        The method considers only the keys in self that belong to the
        given group. Then, it sorts them by their integer identifiers,
        and represents each sequence of successive integers by their
        endpoints.

        Returns:
           A list `[e1, e2, ...]` such that each `e` is a single Key
           instance or a pair of Key instances. If it's a single
           instance `k`, then `k.identifier` belongs to `group`; if it's a
           pair `[k1, k2]`, then all keys with identifiers between
           `k1.identifier` and `k2.identifier` (included) belong to `group`.
        """
        # filter only keys in `group`
        group_keys = [k for k in self if k.group == group]
        # sort keys by identifier
        group_keys.sort(key=lambda k: k.identifier)
        # compute ranges
        res = []
        for k in group_keys:
            identifier = k.identifier
            # first element: add it as single value
            if not res:
                res.append(k)
                continue
            try:
                # latest range pair
                start, end = res[0]
            except TypeError:
                # the range pair is actually a single value
                start, end = res[0], res[0]
            if identifier <= end.identifier + 1:
                # extend latest range pair
                res[0] = (start, k)
            else:
                # create new (singleton) range pair
                res = [k] + res
        # reverse ranges, so that they are in the same order as the identifiers
        res.reverse()
        return res

    def unnamed(self) -> Keys:
        """These keys without platform-specific names."""
        return self


## Standard keys available as individual variables
K_NOOP          = Key("K_NOOP",
                      0, KeyGroup.NOOP, "Do nothing")
K_DP_UP         = Key("K_DP_UP",
                      1, KeyGroup.DPAD, "D-pad up")
K_DP_UP_RIGHT   = Key("K_DP_UP_RIGHT",
                      2, KeyGroup.DPAD, "D-pad up right")
K_DP_RIGHT      = Key("K_DP_RIGHT",
                      3, KeyGroup.DPAD, "D-pad right")
K_DP_DOWN_RIGHT = Key("K_DP_DOWN_RIGHT",
                      4, KeyGroup.DPAD, "D-pad down right")
K_DP_DOWN       = Key("K_DP_DOWN",
                      5, KeyGroup.DPAD, "D-pad down")
K_DP_DOWN_LEFT  = Key("K_DP_DOWN_LEFT",
                      6, KeyGroup.DPAD, "D-pad down left")
K_DP_LEFT       = Key("K_DP_LEFT",
                      7, KeyGroup.DPAD, "D-pad left")
K_DP_UP_LEFT    = Key("K_DP_UP_LEFT",
                      8, KeyGroup.DPAD, "D-pad up left")
K_DP_CENTER     = Key("K_DP_CENTER",
                      9, KeyGroup.DPAD, "D-pad centered")
K_A             = Key("K_A",
                      10, KeyGroup.REGULAR, "Button A")
K_B             = Key("K_B",
                      11, KeyGroup.REGULAR, "Button B")
K_X             = Key("K_X",
                      12, KeyGroup.REGULAR, "Button X")
K_Y             = Key("K_Y",
                      13, KeyGroup.REGULAR, "Button Y")
K_L             = Key("K_L",
                      14, KeyGroup.REGULAR, "Button left shoulder")
K_R             = Key("K_R",
                      15, KeyGroup.REGULAR, "Button right shoulder")
K_ZL            = Key("K_ZL",
                      16, KeyGroup.REGULAR, "Button left trigger")
K_ZR            = Key("K_ZR",
                      17, KeyGroup.REGULAR, "Button right trigger")
K_HOME          = Key("K_HOME",
                      18, KeyGroup.REGULAR, "Menu home")
K_PLUS          = Key("K_PLUS",
                      19, KeyGroup.REGULAR, "Menu right")
K_MINUS         = Key("K_MINUS",
                      20, KeyGroup.REGULAR, "Menu left")
K_LS_PRESS      = Key("K_LS_PRESS",
                      21, KeyGroup.REGULAR, "Left stick press")
K_RS_PRESS      = Key("K_RS_PRESS",
                      22, KeyGroup.REGULAR, "Right stick press")
K_CAPTURE       = Key("K_CAPTURE",
                      23, KeyGroup.REGULAR, "Menu capture")
K_LS_UP         = Key("K_LS_UP",
                      24, KeyGroup.LEFT_STICK, "Left stick up")
K_LS_UP_RIGHT   = Key("K_LS_UP_RIGHT",
                      25, KeyGroup.LEFT_STICK, "Left stick up right")
K_LS_RIGHT      = Key("K_LS_RIGHT",
                      26, KeyGroup.LEFT_STICK, "Left stick right")
K_LS_DOWN_RIGHT = Key("K_LS_DOWN_RIGHT",
                      27, KeyGroup.LEFT_STICK, "Left stick down right")
K_LS_DOWN       = Key("K_LS_DOWN",
                      28, KeyGroup.LEFT_STICK, "Left stick down")
K_LS_DOWN_LEFT  = Key("K_LS_DOWN_LEFT",
                      29, KeyGroup.LEFT_STICK, "Left stick down left")
K_LS_LEFT       = Key("K_LS_LEFT",
                      30, KeyGroup.LEFT_STICK, "Left stick left")
K_LS_UP_LEFT    = Key("K_LS_UP_LEFT",
                      31, KeyGroup.LEFT_STICK, "Left stick up left")
K_LS_CENTER     = Key("K_LS_CENTER",
                      32, KeyGroup.LEFT_STICK, "Left stick center")
K_RS_UP         = Key("K_RS_UP",
                      33, KeyGroup.RIGHT_STICK, "Right stick up")
K_RS_UP_RIGHT   = Key("K_RS_UP_RIGHT",
                      34, KeyGroup.RIGHT_STICK, "Right stick up right")
K_RS_RIGHT      = Key("K_RS_RIGHT",
                      35, KeyGroup.RIGHT_STICK, "Right stick right")
K_RS_DOWN_RIGHT = Key("K_RS_DOWN_RIGHT",
                      36, KeyGroup.RIGHT_STICK, "Right stick down right")
K_RS_DOWN       = Key("K_RS_DOWN",
                      37, KeyGroup.RIGHT_STICK, "Right stick down")
K_RS_DOWN_LEFT  = Key("K_RS_DOWN_LEFT",
                      38, KeyGroup.RIGHT_STICK, "Right stick down left")
K_RS_LEFT       = Key("K_RS_LEFT",
                      39, KeyGroup.RIGHT_STICK, "Right stick left")
K_RS_UP_LEFT    = Key("K_RS_UP_LEFT",
                      40, KeyGroup.RIGHT_STICK, "Right stick up left")
K_RS_CENTER     = Key("K_RS_CENTER",
                      41, KeyGroup.RIGHT_STICK, "Right stick center")

STANDARD_KEYS = Keys([
    K_NOOP,
    K_DP_UP,
    K_DP_UP_RIGHT,
    K_DP_RIGHT,
    K_DP_DOWN_RIGHT,
    K_DP_DOWN,
    K_DP_DOWN_LEFT,
    K_DP_LEFT,
    K_DP_UP_LEFT,
    K_DP_CENTER,
    K_A,
    K_B,
    K_X,
    K_Y,
    K_L,
    K_R,
    K_ZL,
    K_ZR,
    K_HOME,
    K_PLUS,
    K_MINUS,
    K_LS_PRESS,
    K_RS_PRESS,
    K_CAPTURE,
    K_LS_UP,
    K_LS_UP_RIGHT,
    K_LS_RIGHT,
    K_LS_DOWN_RIGHT,
    K_LS_DOWN,
    K_LS_DOWN_LEFT,
    K_LS_LEFT,
    K_LS_UP_LEFT,
    K_LS_CENTER,
    K_RS_UP,
    K_RS_UP_RIGHT,
    K_RS_RIGHT,
    K_RS_DOWN_RIGHT,
    K_RS_DOWN,
    K_RS_DOWN_LEFT,
    K_RS_LEFT,
    K_RS_UP_LEFT,
    K_RS_CENTER
])



## Tags for serialization
# pylint: disable=invalid-name  # Using the same capitalization as the classnames
TAG_KeyGroup = "!KeyGroup"
TAG_Key = "!Key"
TAG_Keys = "!Keys"
