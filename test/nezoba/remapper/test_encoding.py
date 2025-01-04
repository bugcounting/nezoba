# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,too-few-public-methods
import filecmp
import re
import os
import tempfile
import pytest

# pylint: disable=no-name-in-module # PyLint cannot resolve the imports
from .context import encoding, buttons, keys, mappings, combos, namings


class TestEncoder:

    def test_init(self):
        board_info = encoding.BoardInfo(
            n_buttons=5, n_mappings=2, n_keys_per_button=1, keys=["K_NOOP", "K_A", "K_B"]
        )
        encoder = encoding.Encoder(board_info)
        assert encoder.board_info.noop == "K_NOOP"

    @classmethod
    def setup_class(cls):
        cls.buttons = buttons.Buttons([
            buttons.Button(0, "Button #0"),
            buttons.Button(1, "Button #1"),
            buttons.Button(2, "Button #2")
        ])
        cls.keys = keys.Keys([
            keys.Key("K_NOOP", 0, keys.KeyGroup.NOOP, ""),
            keys.Key("K_A", 1, keys.KeyGroup.REGULAR, ""),
            keys.Key("K_DP_UP", 2, keys.KeyGroup.DPAD, "")
        ])
        cls.named_keys = namings.NamedKeys([
            namings.NamedKey(cls.keys[0], "", namings.NameScheme.NS),
            namings.NamedKey(cls.keys[1], "A", namings.NameScheme.NS),
            namings.NamedKey(cls.keys[2], "⇑", namings.NameScheme.NS)
        ])
        cls.mapping = mappings.Mapping(buttons=cls.buttons, keys=cls.keys)
        cls.mapping[cls.buttons[0]] = combos.Press(cls.keys[1])
        cls.mapping[cls.buttons[1]] = combos.Press(cls.keys[2])

    def test_is_compatible(self):
        mapping = self.mapping
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=5, n_mappings=2, n_keys_per_button=1,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ))
        encoder.set_mapping(mapping)
        assert encoder.is_compatible()

    def test_is_compatible_minimal(self):
        mapping = self.mapping
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=2, n_mappings=1, n_keys_per_button=1,
            keys=["K_A", "K_DP_UP"]
            ))
        encoder.set_mapping(mapping)
        assert encoder.is_compatible()

    def test_is_compatible_key_presses(self):
        mapping = self.mapping
        mapping[self.buttons[1]] = combos.Press(self.keys[1]) & combos.Press(self.keys[2])
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=5, n_mappings=2, n_keys_per_button=3,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ))
        encoder.set_mapping(mapping)
        assert encoder.is_compatible()

    def test_is_compatible_too_many_buttons(self):
        mapping = self.mapping
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=1, n_mappings=2, n_keys_per_button=1,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ))
        encoder.set_mapping(mapping)
        with pytest.raises(ValueError):
            assert encoder.is_compatible()

    def test_is_compatible_unsupported_keys(self):
        mapping = self.mapping
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=5, n_mappings=2, n_keys_per_button=1,
            keys=["K_NOOP", "K_A"]
            ))
        encoder.set_mapping(mapping)
        with pytest.raises(ValueError):
            assert encoder.is_compatible()

    def test_is_compatible_too_many_key_presses(self):
        mapping = self.mapping
        mapping[self.buttons[1]] = combos.Press(self.keys[1]) & combos.Press(self.keys[2])
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=5, n_mappings=2, n_keys_per_button=1,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ))
        encoder.set_mapping(mapping)
        with pytest.raises(ValueError):
            encoder.is_compatible()

    def test_encode(self):
        mapping = self.mapping
        n_buttons, n_keys_per_button = 5, 3
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=n_buttons, n_mappings=2, n_keys_per_button=n_keys_per_button,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ))
        encoder.set_mapping(mapping)
        as_text = encoder.encode()
        print(as_text)
        assert as_text.count(",") == n_keys_per_button * n_buttons - 1

    def test_encode_named(self):
        mapping = namings.NamedMapping(buttons=self.buttons, keys=self.named_keys)
        mapping[self.buttons[0]] = combos.Press(self.named_keys[1])
        mapping[self.buttons[1]] = (combos.Press(self.named_keys[2])
                                    & combos.Press(self.named_keys[1]))
        n_buttons, n_keys_per_button = 5, 3
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=n_buttons, n_mappings=2, n_keys_per_button=n_keys_per_button,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ))
        encoder.set_mapping(mapping)
        as_text = encoder.encode()
        print(as_text)
        assert as_text.count(",") == n_keys_per_button * n_buttons - 1

    def test_encode_empty(self):
        n_buttons, n_keys_per_button = 5, 3
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=n_buttons, n_mappings=2, n_keys_per_button=n_keys_per_button,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ))
        as_text = encoder.encode()
        print(as_text)
        assert as_text.count("K_NOOP") == n_keys_per_button * n_buttons

    def test_iteration(self):
        mapping = self.mapping
        mappings_obj = mappings.Mappings([mapping, mapping])
        n_buttons, n_mappings, n_keys_per_button = 2, 2, 2
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=n_buttons, n_mappings=n_mappings, n_keys_per_button=n_keys_per_button,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ), iterate_over=mappings_obj)
        k = -1
        for k, as_text in enumerate(encoder):
            assert as_text.count(",") == n_keys_per_button * n_buttons - 1
        assert k == max(len(mappings_obj), n_mappings) - 1

    def test_iteration_padded(self):
        mapping = self.mapping
        mappings_obj = mappings.Mappings([mapping, mapping])
        n_buttons, n_mappings, n_keys_per_button = 2, 5, 2
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=n_buttons, n_mappings=n_mappings, n_keys_per_button=n_keys_per_button,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ), iterate_over=mappings_obj)
        k = -1
        for k, as_text in enumerate(encoder):
            assert as_text.count(",") == n_keys_per_button * n_buttons - 1
        assert k == max(len(mappings_obj), n_mappings) - 1

    def test_show(self):
        title, description = "Title", """Let's try how this handles a long description,
        one that spans multiple lines and columns, and hence it requires wrapping"""
        mapping = namings.NamedMapping(buttons=self.buttons, keys=self.named_keys,
                                       identifier=0, title=title, description=description)
        mapping[self.buttons[0]] = combos.Press(self.named_keys[1])
        mapping[self.buttons[1]] = (combos.Press(self.named_keys[2])
                                    & combos.Press(self.named_keys[1]))
        encoder = encoding.Encoder(None)
        encoder.set_mapping(mapping)
        print(encoder.show())

    def test_iteration_show(self):
        mapping = self.mapping
        mappings_obj = mappings.Mappings([mapping, mapping])
        encoder = encoding.Encoder(None,
                                   iterate_over=mappings_obj, encode=False)
        k = -1
        for k, _ in enumerate(encoder):
            pass
        assert k == len(mappings_obj) - 1

    def test_decode(self):
        mapping = self.mapping
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=len(self.buttons), n_mappings=2, n_keys_per_button=3,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ))
        encoder.set_mapping(mapping)
        as_text = encoder.encode()
        encoder.decode(as_text)
        decoded = encoder.mapping
        assert decoded.title == ""
        assert decoded.description == ""
        assert len(decoded) == len(mapping)
        assert len(decoded[self.buttons[1]].flat()) == len(mapping[self.buttons[1]].flat())

    def test_decode_titled(self):
        title, description = "Title", "Description"
        mapping = namings.NamedMapping(buttons=self.buttons, keys=self.named_keys,
                                       identifier=0, title=title, description=description)
        mapping[self.buttons[0]] = combos.Press(self.named_keys[1])
        mapping[self.buttons[1]] = (combos.Press(self.named_keys[2])
                                    & combos.Press(self.named_keys[1]))
        encoder = encoding.Encoder(encoding.BoardInfo(
            n_buttons=len(self.buttons), n_mappings=2, n_keys_per_button=3,
            keys=["K_NOOP", "K_A", "K_DP_UP"]
            ))
        encoder.set_mapping(mapping)
        as_text = encoder.encode()
        encoder.decode(as_text)
        decoded = encoder.mapping
        assert decoded.title == title
        assert decoded.description == description
        assert len(decoded) == len(mapping)
        assert len(decoded[self.buttons[0]].flat()) == len(mapping[self.buttons[0]].flat())


class TestExporter:

    temp_dir = None
    
    BOARD_DIR = "../../src/board/"
    MAPPING_YAML = "../../src/data/platformers-2d.yaml"

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

    def test_init_load(self):
        exporter = encoding.Exporter(self.BOARD_DIR, "")
        assert exporter.project_dir == self.BOARD_DIR
        assert exporter.board_info.n_buttons == 15
        assert exporter.board_info.n_mappings == 16
        assert exporter.board_info.n_keys_per_button == 3
        assert len(exporter.board_info.keys) == 42
        assert exporter.board_info.noop == "K_NOOP"

    def test_show(self):
        exporter = encoding.Exporter("",
                                     self.MAPPING_YAML)
        showed = exporter.show()
        # cfg numbers
        pattern = r'\[[0-1]+\]'
        # find all non-overlapping matches of the pattern
        matches = re.findall(pattern, showed)
        # number of mappings
        assert len(matches) == 11

    def test_encode_decode(self):
        # the project_dir is only used to read the board info
        exporter = encoding.Exporter(self.BOARD_DIR,
                                     self.MAPPING_YAML)
        # change the project_dir to the temp_dir
        exporter.project_dir = self.temp_dir
        # write the encoded mappings into the temp_dir
        mappings_obj = exporter.encode(bak = False)
        # actual number of non-empty mappings
        n_mappings = len(mappings_obj)
        # change the mapping_yaml file to one in the temp dir
        exporter.mapping_yaml = self.temp_path("mappings.yaml")
        # decode the previously written mappings in the temp_dir
        exporter.decode()
        # now, encode the decoded mappings again, creating bak files
        exporter.encode(bak = True)
        # finally, we can check that the exported mappings have not changed
        for n_mapping in range(exporter.board_info.n_mappings):
            fname = os.path.join(exporter.project_dir, exporter.mapping_fname % n_mapping)
            fname_bak = fname + exporter.BAK_EXT
            # non-empty mappings should be identical
            if n_mapping < n_mappings:
                assert filecmp.cmp(fname, fname_bak, shallow=False)
            # all other mappings (including empty ones) should be identical except for the scheme
            else:
                with open(fname, "r", encoding="utf-8") as f:
                    as_lines = [line for line in f.readlines() if not re.match(r'^//.*$', line)]
                with open(fname_bak, "r", encoding="utf-8") as f:
                    as_lines_bak = [line for line in f.readlines() if not re.match(r'^//.*$', line)]
                assert as_lines == as_lines_bak
