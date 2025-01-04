# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,too-few-public-methods
import pytest

# pylint: disable=no-name-in-module # PyLint cannot resolve the imports
from .context import namings, keys, buttons, combos, mappings


class TestNameScheme:

    def test_scheme(self):
        s1 = namings.NameScheme.NS
        s2 = namings.NameScheme.PC
        assert s1 != s2


class TestNamedKey:

    def test_init_from_key(self):
        k = keys.Key("K", 1, keys.KeyGroup.REGULAR, ";")
        name, scheme, named_description = "Name1", namings.NameScheme.PC, "Desc1"
        nk = namings.NamedKey(k, name, scheme, named_description)
        assert nk.key == k.key
        assert nk.identifier == k.identifier
        assert nk.group == k.group
        assert nk.name == name
        assert nk.scheme == scheme
        assert nk.named_description == named_description
        nk2 = namings.NamedKey(k, name, scheme)
        assert nk2.named_description == k.description

    def test_init_from_args(self):
        key, identifier, group, description = "K", 1, keys.KeyGroup.REGULAR, "BaseDesc1"
        name, scheme, _named_description = "Name1", namings.NameScheme.PC, "Desc1"
        nk = namings.NamedKey(key, identifier, group, description,
                              name, scheme)
        assert nk.key == key
        assert nk.identifier == identifier
        assert nk.group == group
        assert nk.name == name
        assert nk.scheme == scheme
        assert nk.description == description
        # Insufficient number of arguments
        with pytest.raises(ValueError):
            _nk2 = namings.NamedKey(key, identifier, group, description, name)

    def test_init_from_kwargs(self):
        key, identifier, group, description = "K", 1, keys.KeyGroup.REGULAR, "BaseDesc1"
        name, scheme, named_description = "Name1", namings.NameScheme.PC, "Desc1"
        nk = namings.NamedKey(group=group,
                              description=description,
                              key=key,
                              name=name,
                              identifier=identifier,
                              scheme=scheme,
                              named_description=named_description)
        assert nk.key == key
        assert nk.identifier == identifier
        assert nk.group == group
        assert nk.description == description
        assert nk.name == name
        assert nk.scheme == scheme
        assert nk.named_description == named_description

    def test_unnamed_key(self):
        ns_a = namings.NS_KEYS["K_A"]
        pc_a = namings.PC_KEYS["K_A"]
        assert ns_a.unnamed() == pc_a.unnamed()


class TestNamedKeys:

    def test_init(self):
        nk1 = namings.NamedKey("K1", 0, keys.KeyGroup.NOOP, "desc1",
                               "key3", namings.NameScheme.NS)
        nk2 = namings.NamedKey("K2", 2, keys.KeyGroup.REGULAR, "desc2",
                               "key2", namings.NameScheme.NS)
        nk3 = namings.NamedKey("K3", 3, keys.KeyGroup.REGULAR, "desc3",
                               "key3", namings.NameScheme.PC)
        nks1 = namings.NamedKeys([nk1, nk2])
        assert len(nks1) == 2
        nks2 = namings.NamedKeys([nk3])
        assert len(nks2) == 1
        nks3 = namings.NamedKeys([])
        assert len(nks3) == 0
        # Different naming schemes cannot be mixed
        with pytest.raises(AssertionError):
            _nks4 = namings.NamedKeys([nk2, nk3])
        # The same constraints of Keys still apply
        with pytest.raises(AssertionError):
            _nks5 = namings.NamedKeys([nk2, nk2])
        ks4 = keys.Key(nk1.name, nk1.identifier, nk1.group, nk1.description)
        # Cannot add unnamed Key to NamedKeys
        with pytest.raises(AssertionError):
            namings.NamedKeys([ks4, nk2])

    def test_NS_KEYS(self):
        assert len(namings.NS_KEYS) == len(keys.STANDARD_KEYS)
        assert namings.NS_KEYS["K_A"].name == "A"
        assert namings.NS_KEYS["K_PLUS"].named_description == "Menu +"

    def test_PC_KEYS(self):
        assert len(namings.PC_KEYS) == len(keys.STANDARD_KEYS)
        assert namings.PC_KEYS["K_A"].name == "B"
        assert namings.PC_KEYS["K_B"].name == "A"
        assert namings.PC_KEYS["K_X"].name == "Y"
        assert namings.PC_KEYS["K_Y"].name == "X"
        assert namings.PC_KEYS["K_L"].name == "LB"
        assert namings.PC_KEYS["K_R"].name == "RB"
        assert namings.PC_KEYS["K_L"].named_description == "Button left bumper"
        assert namings.PC_KEYS["K_R"].named_description == "Button right bumper"
        assert namings.PC_KEYS["K_ZL"].name == "LT"
        assert namings.PC_KEYS["K_ZR"].name == "RT"
        assert namings.PC_KEYS["K_MINUS"].name == "select"
        assert namings.PC_KEYS["K_PLUS"].name == "start"

    def test_unnamed_keys(self):
        ns_unnamed = namings.NS_KEYS.unnamed()
        pc_unnamed = namings.PC_KEYS.unnamed()
        assert ns_unnamed == pc_unnamed


class TestNamedMapping:

    def test_init(self):
        nk1 = namings.NamedKey("K1", 0, keys.KeyGroup.NOOP, "desc1",
                               "key3", namings.NameScheme.NS)
        nk2 = namings.NamedKey("K2", 2, keys.KeyGroup.REGULAR, "desc2",
                               "key2", namings.NameScheme.NS)
        nks1 = namings.NamedKeys([nk1, nk2])
        nks2 = namings.NamedKeys([])
        ks3 = keys.Keys([nk1, nk2])
        # plain usage of constructor
        nms1 = namings.NamedMapping(buttons.NEZOBA_BUTTONS, nks1)
        assert nms1.scheme == namings.NameScheme.NS
        # constructing NamedMapping instance from Mapping instance
        ms2 = mappings.Mapping(buttons.NEZOBA_BUTTONS, namings.NS_KEYS)
        ms2[buttons.B02] = combos.Press(namings.NS_KEYS["K_A"])
        nms2 = namings.NamedMapping(ms2)
        assert nms2.scheme == namings.NameScheme.NS
        assert nms2[buttons.B02] == combos.Press(namings.NS_KEYS["K_A"])
        # empty set of keys
        with pytest.raises(ValueError):
            _nms3 = namings.NamedMapping(buttons.NEZOBA_BUTTONS, nks2)
        # Keys without naming scheme
        with pytest.raises(TypeError):
            _nms4 = namings.NamedMapping(buttons.NEZOBA_BUTTONS, ks3)
