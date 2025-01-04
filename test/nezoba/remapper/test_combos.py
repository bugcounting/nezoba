# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,too-few-public-methods
import pytest

# pylint: disable=no-name-in-module # PyLint cannot resolve the imports
from .context import combos, keys, namings

class TestCombo:

    def test_from_text(self):
        k1, k2, k3 = keys.K_A, keys.K_B, keys.K_X
        keys_ = keys.Keys([k1, k2, k3])
        c1 = combos.Press(k2, turbo=combos.Press.TURBO_DEFAULT)
        c2 = combos.And([combos.Press(k1), combos.Press(k3)])
        assert c1 == combos.Combo.from_text(f"K_B {combos.Press.TURBO_MARK}", keys_)
        assert c2 == combos.Combo.from_text("K_A & K_X", keys_)
        assert combos.Combo.from_text("K_K", keys_) is None
        # Inverse of as_text
        assert c1 == combos.Combo.from_text(c1.as_text(), keys_)
        assert c2 == combos.Combo.from_text(c2.as_text(), keys_)

    def test_from_text_named(self):
        k1, k2, k3 = keys.K_A, keys.K_B, keys.K_X
        keys_ = keys.Keys([k1, k2, k3])
        named_keys = namings.NamedKeys([namings.NS_KEYS[k.key] for k in keys_])
        n1, n2, n3 = named_keys
        c1 = combos.Press(n2, turbo=combos.Press.TURBO_DEFAULT)
        c2 = combos.And([combos.Press(n1), combos.Press(n3)])
        assert c1 == combos.Combo.from_text(f"B{combos.Press.TURBO_MARK}", named_keys)
        assert c2 == combos.Combo.from_text("A & X", named_keys)
        assert combos.Combo.from_text("K", named_keys) is None
        # Inverse of as_text
        assert c1 == combos.Combo.from_text(c1.as_text(), named_keys)
        assert c2 == combos.Combo.from_text(c2.as_text(), named_keys)


class TestPress:

    def test_init(self):
        k1, t1, h1 = keys.K_A, 75, None
        p1 = combos.Press(k1, t1, h1)
        assert p1.key == k1 and p1.turbo == t1 and p1.hold == h1
        assert p1.is_turbo()
        k2, t2, h2 = keys.K_DP_UP, None, True
        p2 = combos.Press(turbo=t2, hold=h2, key=k2)
        assert p2.key == k2 and p2.turbo == t2 and p2.hold == h2


class TestAnd:

    def test_init(self):
        p1 = combos.Press(keys.K_A)
        p2 = combos.Press(keys.K_B)
        _c1 = combos.And([p1, p2])
        _c2 = combos.And([p2, p1])
        # must pass sequence of values
        with pytest.raises(TypeError):
            combos.And(p1, p2)  # pylint: disable=too-many-function-args # That's what this call is testing :)
        # can only pass list of Combos
        with pytest.raises(AssertionError):
            combos.And([p1, keys.K_B])

    def test_and(self):
        p1 = combos.Press(keys.K_A)
        p2 = combos.Press(keys.K_B)
        p3 = combos.Press(keys.K_X)
        c1 = combos.And([p1, p2])
        c2 = combos.And([p2, p3])
        # & is an alternative way of building And instances
        assert c1 == p1 & p2
        assert p3 & c1 == combos.And([p1, p2, p3])
        assert c1 & p3 == combos.And([p1, p2, p3])
        assert c1 & c2 == combos.And([p1, p2, p2, p3])
