# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,too-few-public-methods
# pylint: disable=no-name-in-module # PyLint cannot resolve the imports
import os
import tempfile

from .context import buttons, keys, combos, namings, mappings, serialization


to_yaml = serialization.to_yaml
from_yaml = serialization.from_yaml

class TestSerialization:

    temp_dir = None

    @classmethod
    def setup_class(cls):
        if cls.temp_dir is None:
            cls.temp_dir = tempfile.mkdtemp(dir=os.getcwd(),
                                            prefix=("tmp_"
                                                    + os.path.splitext(
                                                        os.path.basename(__file__)
                                                    )[0] + "_"))

    @classmethod
    def temp_path(cls, fname: str):
        if cls.temp_dir is not None:
            return os.path.join(cls.temp_dir, fname)
        return fname

    def test_serialize_button(self):
        old = buttons.B00
        yml = to_yaml(old)
        new = from_yaml(yml)
        assert new == old

    def test_serialize_buttons(self):
        old = buttons.NEZOBA_BUTTONS
        yml = to_yaml(old, self.temp_path("buttons.yaml"))
        new = from_yaml(yml)
        assert new == old

    def test_serialize_key(self):
        old = keys.K_A
        yml = to_yaml(old)
        new = from_yaml(yml)
        assert new == old

    def test_serialize_keys(self):
        old = keys.STANDARD_KEYS
        yml = to_yaml(old, self.temp_path("keys.yaml"))
        new = from_yaml(yml)
        assert new == old

    def test_serialize_press(self):
        old = combos.Press(keys.K_B, 0.3, True)
        yml = to_yaml(old)
        new = from_yaml(yml)
        assert new == old

    def test_serialize_combos(self):
        old = combos.And([combos.Press(keys.K_A),
                          combos.Press(keys.K_B, 0.3, True),
                          combos.Press(keys.K_X, 0.111, False)])
        yml = to_yaml(old, self.temp_path("combos.yaml"))
        new = from_yaml(yml)
        assert new == old

    def test_serialize_named_key(self):
        old = namings.NS_KEYS["K_A"]
        yml = to_yaml(old)
        new = from_yaml(yml)
        assert new == old
        assert new.unnamed() == old.unnamed()

    def test_serialize_named_keys(self):
        old = namings.NS_KEYS
        yml = to_yaml(old, self.temp_path("nskeys.yaml"))
        new = from_yaml(yml)
        assert new == old
        assert new.unnamed() == old.unnamed()

    def test_serialize_mappings(self):
        m1 = mappings.Mapping(buttons.NEZOBA_BUTTONS,
                              keys.STANDARD_KEYS,
                              1, "m1", "This is mapping #1")
        m1[buttons.B01] = combos.Press(keys.K_A)
        m1[buttons.B02] = combos.And([combos.Press(keys.K_B), combos.Press(keys.K_X)])
        yml1 = to_yaml(m1)
        new1 = from_yaml(yml1)
        assert new1 == m1
        m2 = mappings.Mapping(buttons.NEZOBA_BUTTONS,
                               keys.STANDARD_KEYS,
                               2, "m2", "This is mapping #2")
        m2[buttons.B04] = combos.Press(keys.K_Y)
        m2[buttons.B07] = combos.Press(keys.K_X)
        yml2 = to_yaml(m2)
        new2 = from_yaml(yml2)
        assert new2 == m2
        old = mappings.Mappings([m1, m2])
        yml = to_yaml(old, self.temp_path("mappings.yaml"), version=True)
        new = from_yaml(yml)
        assert new == old

    def test_serialize_named_mappings(self):
        K_A, K_B, K_X = namings.NS_KEYS["K_A"], namings.NS_KEYS["K_B"], namings.NS_KEYS["K_X"]
        m1 = namings.NamedMapping(buttons.NEZOBA_BUTTONS,
                                  namings.NS_KEYS)
        m1[buttons.B01] = combos.Press(K_A)
        m1[buttons.B02] = combos.And([combos.Press(K_B), combos.Press(K_X)])
        yml1 = to_yaml(m1)
        new1 = from_yaml(yml1)
        assert new1 == m1
        m2 = mappings.Mapping(buttons.NEZOBA_BUTTONS,
                               keys.STANDARD_KEYS,
                               2, "m2", "This is mapping #2")
        m2[buttons.B04] = combos.Press(keys.K_Y)
        m2[buttons.B07] = combos.Press(keys.K_X)
        old = mappings.Mappings([m1, m2])
        yml = to_yaml(old, self.temp_path("named_mappings.yaml"), version=True)
        new = from_yaml(yml)
        assert new == old
