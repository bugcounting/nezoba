# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,too-few-public-methods
import pytest

# pylint: disable=no-name-in-module # PyLint cannot resolve the imports
from .context import keys


class TestKeyGroup:

    def test_group(self):
        g1 = keys.KeyGroup.NOOP
        g2 = keys.KeyGroup.REGULAR
        g3 = keys.KeyGroup.NOOP
        assert g1 != g2
        assert g2 != g3
        assert g3 == g1


class TestKey:

    def test_init(self):
        key1, identifier1, group1, description1 = "K", 2, keys.KeyGroup.NOOP, "//"
        key2, identifier2, group2, description2 = "K", 1, keys.KeyGroup.REGULAR, ";"
        k1 = keys.Key(key1, identifier1, group1, description1)
        k2 = keys.Key(description=description2,
                      key=key2,
                      identifier=identifier2,
                      group=group2)
        assert k1.identifier == identifier1
        assert k2.group == group2
        assert k1 != k2


class TestKeys:

    # pylint: disable=too-many-locals
    def test_init(self):
        k1 = keys.Key("K1", 0, keys.KeyGroup.NOOP, "")
        k2 = keys.Key("K2", 1, keys.KeyGroup.NOOP, "")
        k3 = keys.Key("K3", -2, keys.KeyGroup.REGULAR, "")
        k4 = keys.Key("K4", 0, keys.KeyGroup.REGULAR, "")
        k5 = keys.Key("K5", 3, keys.KeyGroup.REGULAR, "")
        k6 = keys.Key("K6", 3, "REGULAR", "")
        k7 = keys.Key("K7", 3, keys.KeyGroup.REGULAR, "A.k.a. K5")
        k8 = keys.Key("K2", 2, keys.KeyGroup.REGULAR, "Repeated key")
        ks1 = keys.Keys([k1, k2])
        assert len(ks1) == 2
        assert ks1[0] == k1
        assert ks1[1] == k2
        with pytest.raises(IndexError):
            _tmp = ks1[2]
        assert ks1["K1"] == k1
        assert ks1["K2"] == k2
        with pytest.raises(IndexError):
            _tmp = ks1["K0"]
        ks2 = keys.Keys([k1])
        assert len(ks2) == 1
        ks3 = keys.Keys([])
        assert len(ks3) == 0
        ks4 = keys.Keys((k2, k5))
        assert len(ks4) == 2
        # Repeated keys are not allowed
        with pytest.raises(AssertionError):
            _ks = keys.Keys([k2, k8])
        # Negative identifiers are invalid
        with pytest.raises(AssertionError):
            _ks5 = keys.Keys([k1, k3])
        # Only NOOP can use identifier 0
        with pytest.raises(AssertionError):
            _ks6 = keys.Keys([k4])
        # Group of invalid type
        with pytest.raises(AssertionError):
            _ks6 = keys.Keys([k6])
        # Identifiers must be unique
        with pytest.raises(AssertionError):
            _ks7 = keys.Keys([k7, k5])
        # Identifiers must be unique
        with pytest.raises(AssertionError):
            _ks7 = keys.Keys([k1, k1])

    def test_group_ranges(self):
        ks1 = keys.Keys([
            keys.Key("K1", 0, keys.KeyGroup.NOOP, ""),
            keys.Key("K2", 1, keys.KeyGroup.NOOP, ""),
            keys.Key("K3", 2, keys.KeyGroup.NOOP, ""),
            ])
        assert len(ks1.group_ranges(keys.KeyGroup.NOOP)) == 1
        assert len(ks1.group_ranges(keys.KeyGroup.NOOP)[0]) == 2
        assert len(ks1.group_ranges(keys.KeyGroup.REGULAR)) == 0
        ks2 = keys.Keys([
            keys.Key("K1", 1, keys.KeyGroup.REGULAR, ""),
            keys.Key("K2", 4, keys.KeyGroup.REGULAR, ""),
            keys.Key("K3", 7, keys.KeyGroup.REGULAR, ""),
            ])
        assert len(ks2.group_ranges(keys.KeyGroup.REGULAR)) == 3
        ks3 = keys.Keys([
            keys.Key("K2", 4, keys.KeyGroup.REGULAR, ""),
            keys.Key("K1", 1, keys.KeyGroup.REGULAR, ""),
            keys.Key("K3", 5, keys.KeyGroup.REGULAR, ""),
            ])
        assert len(ks3.group_ranges(keys.KeyGroup.REGULAR)) == 2
        ks4 = keys.Keys([
            keys.Key("K1", 1, keys.KeyGroup.REGULAR, ""),
            keys.Key("K2", 2, keys.KeyGroup.REGULAR, ""),
            keys.Key("K3", 5, keys.KeyGroup.REGULAR, ""),
            ])
        assert len(ks4.group_ranges(keys.KeyGroup.REGULAR)) == 2

    def test_STANDARD_KEYS(self):
        ks = keys.STANDARD_KEYS
        assert len(ks.group_ranges(keys.KeyGroup.NOOP)) == 1
        assert len(ks.group_ranges(keys.KeyGroup.DPAD)) == 1
        assert len(ks.group_ranges(keys.KeyGroup.REGULAR)) == 1
        assert ks[keys.K_HOME.key] == keys.K_HOME
