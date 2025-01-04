# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,too-few-public-methods
import pytest

# pylint: disable=no-name-in-module # PyLint cannot resolve the imports
from .context import mappings, combos, keys, buttons


class TestMapping:

    @classmethod
    def setup_class(cls):
        cls.b1 = buttons.Button(0, "B0")
        cls.b2 = buttons.Button(1, "B1")
        cls.bs = buttons.Buttons([cls.b1, cls.b2])
        cls.k1 = keys.Key("K0", 1, keys.KeyGroup.REGULAR, "")
        cls.k2 = keys.Key("K1", 2, keys.KeyGroup.REGULAR, "")
        cls.ks = keys.Keys([cls.k1, cls.k2])

    def test_init(self):
        bs, ks = self.bs, self.ks
        _m = mappings.Mapping(bs, ks)

    def test_empty(self):
        m = mappings.Mapping()
        # no iteration items in an empty mapping
        for _button, _combo in m.items():
            assert False

    def test_identifier(self):
        bs, ks = self.bs, self.ks
        identifier, title, description = 3, "title", "Desc"
        m = mappings.Mapping(bs, ks, identifier, title, description)
        assert m.identifier == identifier
        assert m.title == title
        assert m.description == description

    def test_iteration(self):
        b1, b2 = self.b1, self.b2
        k1, k2 = self.k1, self.k2
        bs, ks = self.bs, self.ks
        m = mappings.Mapping(bs, ks)
        m[b1] = combos.Press(k1)
        m[b2] = combos.Press(k2) & combos.Press(k1)
        for button, _combo in m.items():
            assert button in bs

    def test_setitem(self):
        b1, b2 = self.b1, self.b2
        k1, _k2 = self.k1, self.k2
        bs, ks = self.bs, self.ks
        m = mappings.Mapping(bs, ks)
        c1 = combos.Press(k1)
        m[b1] = c1
        assert m[b1] == c1
        assert not m.istotal()
        m[b2] = c1
        assert m[b2] == c1
        assert m.istotal()
        # Unknown button
        b0 = buttons.Button(2, "B0")
        with pytest.raises(AssertionError):
            m[b0] = c1
        # Unknown key
        c0 = combos.Press(keys.Key("K0", 3, keys.KeyGroup.REGULAR, ""))
        with pytest.raises(AssertionError):
            m[b2] = c0

    def test_nezoba(self):
        m = mappings.Mapping(buttons.NEZOBA_BUTTONS, keys.STANDARD_KEYS)
        b0, b1 = buttons.NEZOBA_BUTTONS[0], buttons.NEZOBA_BUTTONS[1]
        b3 = buttons.NEZOBA_BUTTONS[5]
        c1 = combos.Press(keys.K_A)
        c2 = combos.Press(keys.K_A, turbo=0.3)
        c3 = combos.And([combos.Press(keys.K_A), combos.Press(keys.K_B)])
        m[b0] = c1
        m[b1] = c2
        m[b3] = c3


class TestMappings:

    def test_init(self):
        bs, ks = TestMapping.bs, TestMapping.ks
        m1 = mappings.Mapping(bs, ks)
        m2 = mappings.Mapping(bs, ks)
        ms1 = mappings.Mappings()
        assert len(ms1) == 0
        assert ms1.buttons is None and ms1.keys is None
        ms2 = mappings.Mappings([m1, m2])
        assert len(ms2) == 2
        assert ms2.buttons is not None and ms2.keys is not None
        ms3 = mappings.Mappings([m1])
        assert len(ms3) == 1
        assert ms3.buttons is not None and ms3.keys is not None

    def test_init_validation(self):
        bs, ks = TestMapping.bs, TestMapping.ks
        m = mappings.Mapping(bs, ks)
        # Must pass a list to the constructor
        with pytest.raises(TypeError):
            mappings.Mappings(m)
        # Can only add instances of Mapping
        with pytest.raises(ValueError):
            mappings.Mappings([24, 12])
        m_ob = mappings.Mapping(buttons.Buttons([TestMapping.b1]), ks)
        # Cannot mix mappings with different button sets
        with pytest.raises(ValueError):
            mappings.Mappings([m, m_ob])
        m_ok = mappings.Mapping(bs, keys.Keys([TestMapping.k1]))
        # Cannot mix mappings with different key sets
        with pytest.raises(ValueError):
            mappings.Mappings([m, m_ok])

    def test_modify(self):
        bs, ks = TestMapping.bs, TestMapping.ks
        m1 = mappings.Mapping(bs, ks)
        m2 = mappings.Mapping(bs, ks)
        ms = mappings.Mappings([m1, m2])
        assert ms.buttons is not None and ms.keys is not None
        ms[0] = m2
        assert ms[0] == m2
        assert ms.buttons is not None and ms.keys is not None
        ms.insert(4, m2)
        assert len(ms) == 3 and ms[2] == m2
        assert ms.buttons is not None and ms.keys is not None
        ms.append(m1)
        assert len(ms) == 4 and ms[3] == m2
        assert ms.buttons is not None and ms.keys is not None
        ms.extend([m1, m2])
        assert len(ms) == 6
        assert ms.buttons is not None and ms.keys is not None

    def test_modify_validation(self):
        bs, ks = TestMapping.bs, TestMapping.ks
        m1 = mappings.Mapping(bs, ks)
        m2 = mappings.Mapping(bs, ks)
        ms = mappings.Mappings([m1, m2])
        # Can only add instances of Mapping
        with pytest.raises(ValueError):
            ms[0] = 7
        m_ob = mappings.Mapping(buttons.Buttons([TestMapping.b1]), ks)
        # Cannot mix mappings with different button sets
        with pytest.raises(ValueError):
            ms[0] = m_ob
        m_ok = mappings.Mapping(bs, keys.Keys([TestMapping.k1]))
        # Cannot mix mappings with different key sets
        with pytest.raises(ValueError):
            ms[0] = m_ok

    def test_from_identifier(self):
        bs, ks = TestMapping.bs, TestMapping.ks
        m1 = mappings.Mapping(bs, ks, identifier=1)
        m2 = mappings.Mapping(bs, ks, identifier=2)
        ms = mappings.Mappings()
        ms += [m1, m2]
        assert ms[0] == m1
        assert ms[1] == m2
        assert ms.from_identifier(1) == m1
        assert ms.from_identifier(2) == m2
        # Identifier not found
        with pytest.raises(IndexError):
            ms.from_identifier(7)
