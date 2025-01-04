# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name
import pytest

# pylint: disable=no-name-in-module # PyLint cannot resolve the imports
from .context import buttons


class TestButton:

    def test_init(self):
        identifier1, name1 = 12, "Button 12"
        identifier2, name2 = 0, "Button 0"
        b1 = buttons.Button(identifier1, name1)
        b2 = buttons.Button(name=name2, identifier=identifier2)
        b3 = buttons.Button(name=name1, identifier=identifier1)
        assert b1.identifier == identifier1 and b1.name == name1
        assert b2.identifier == identifier2 and b2.name == name2
        assert b3.identifier == identifier1 and b3.name == name1
        assert b1 != b2
        assert b1 == b3

    def test_Bs(self):
        assert buttons.B00.identifier == 0
        assert buttons.B07.identifier == 7
        assert buttons.B14.identifier == 14


class TestButtons:

    def test_init(self):
        b1 = buttons.Button(0, "B0")
        b2 = buttons.Button(1, "B1")
        b3 = buttons.Button(1, "B2")
        bs1 = buttons.Buttons([b1, b2])
        assert len(bs1) == 2
        assert bs1.layout is None
        bs2 = buttons.Buttons([b1, b2], buttons.ButtonLayout.NEZ_OBA)
        assert len(bs2) == 2
        assert bs2.layout == buttons.ButtonLayout.NEZ_OBA
        assert bs1 != bs2
        bs3 = buttons.Buttons((b2, b1))
        assert len(bs3) == 2
        assert bs3.layout is None
        bs4 = buttons.Buttons({b1, b2})
        assert len(bs4) == 2
        with pytest.raises(AssertionError):
            _bs4 = buttons.Buttons([b1, b1])
        with pytest.raises(AssertionError):
            _bs4 = buttons.Buttons([b3, b2])

    def test_NEZOBA_BUTTONS(self):
        bs = buttons.NEZOBA_BUTTONS
        for k, b in enumerate(bs):
            assert b.identifier == k
