"""
This module provides functionality for encoding and decoding mappings
for the Nez-Oba board.

Classes:
    Encoder: Translates back and forth between mappings and their
      encoded form.
    Exporter: Manages the encoding and decoding of mappings for the
      board software, handling file operations.
"""
import os
import re

from typing import Optional, Union
from dataclasses import dataclass
import textwrap
import logging

from .mappings import Mapping, Mappings
from .combos import Press
from .namings import NameScheme, default_from_scheme
from .serialization import from_yaml, to_yaml



@dataclass(frozen=True)
class BoardInfo:
    """
    Information about the buttons and keys supported by a physical controller board.

    Attributes:
      n_buttons: The number of physical buttons on the board.
      n_mappings: The number of supported button-to-key mappings.
      n_keys_per_button: The maximum number of key presses associated with a button.
      keys: A list of all key names supported by the board.
      noop: The name of the key associated with no mapping.
    """
    n_buttons: int
    n_mappings: int
    n_keys_per_button: int
    keys: list[str]

    @property
    def noop(self) -> str:
        """The name of the key associated with no mapping (the first key name)."""
        return self.keys[0]

    def check_n_buttons(self, n_buttons: int) -> bool:
        """Does the board support `n_buttons` buttons?"""
        return n_buttons <= self.n_buttons

    def check_n_mappings(self, n_mappings: int) -> bool:
        """Does the board support `n_mappings` mappings?"""
        return n_mappings <= self.n_mappings

    def check_n_keys_per_button(self, n_keys_per_button: int) -> bool:
        """Does the board support `n_keys_per_button` keys per button?"""
        return n_keys_per_button <= self.n_keys_per_button

    def check_keys(self, keys: list[str]) -> bool:
        """Does the board support all the keys in `keys`?"""
        return set(keys) <= set(self.keys)


class Encoder:
    """
    Translate back and forth between mappings and their encoded form.

    The Encoder class is responsible for encoding and decoding mappings
    for a specific board. Each instance needs information about the board
    where the mappings will be deployed: the number of buttons, the number
    of mappings, the maximum number of keys per button, and the names of
    the keys supported by the board (see class BoardInfo). Then, Encoder
    supports three main features:
    
    - Encoding (method `encode`): Given a mapping (an instance of
        Mapping), it translates it into a string that can be written
        to a C header file for the board's software.
    - Decoding (method `decode`): Given an encoded mapping (a string
        represending a C header file), it translates it back to an
        instance of the Mapping class.
    - Showing (method `show`): Given a mapping, it formats it as a
        human-readable string, roughly resembling the layout of the
        physical Nez-Oba board.
        
    While methods `encode` and `show` work on instances of the Mapping
    class, the Encoder class can also be used as an iterator to encode
    or show a series of mappings. In this case, instantiate the
    Encoder with the board information and a list of mappings to
    iterate over, and then use the instance as an iterator, where each
    iteration produces an encoded or formatted mapping.

    Attributes:
        board_info: Information about the board (not needed for `show`).
        mapping: The current mapping to be exported.
        text_width: Width in characters of the human-readable output
          produced by `show`.
        TURBO_MARKER: Marker of a turboed key in the C header
          encoding.

    Methods:
        __init__: Initializes the Encoder with the given board
          information and optional mappings.
        set_mapping: Sets the mapping to be encoded or formatted.
        is_compatible: Checks if the current mapping is compatible
          with the board's capabilities.
        encode: Encodes the current mapping into a string that can be
          written to a header file.
        decode: Decodes a named mapping from an encoded string and
          sets it as the current mapping.
        show: Formats the current mapping as a human-readable string
          with width `self.text_width`.
    """

    # information about the board
    board_info: Optional[BoardInfo]

    # current mapping to be exported
    mapping: Optional[Mapping] = None

    # width in characters of the human-readable output produced by `show`
    text_width: int

    # mappings, index, and action to be performed by iterator
    _mappings: Optional[Mappings] = None
    _index: int
    _encode: bool

    # marker of a turboed key in the encoding
    TURBO_MARKER: str = "-"

    # compiled regular expression to match an encoded mapping
    _enc_re_obj: Optional[re.Pattern] = None

    def __init__(self, board_info: Optional[BoardInfo],
                 iterate_over: Optional[Mappings] = None, encode: bool = True,
                 width: int = 75):
        """Create an encoder for a board with the given information.
        
        If `iterate_over` is provided, the created object works as an
        iterator over the mappings `iterate_over`. If `encode` is True, 
        each iteration calls method `encode`; if it is False, each
        iteration calls method `show`.
        
        If `encode` is True and `iterate_over` includes fewer mappings
        than the board supports, the remaining mappings will be empty,
        so that the iteration will always return
        `board_info.n_mappings` encoded mappings.
        
        Args:
            board_info: Information about the board (not needed for `show`)
            iterate_over: Optional mappings to iterate over.
            encoder: If True, each iteration encodes; if False, 
              each iteration shows.
            width: Width in characters of the human-readable output 
              produced by `show`.
        """
        self.board_info = board_info
        self.text_width = width
        if not board_info:
            logging.warning("No board info given: only show is available.")
        if iterate_over is not None:
            self._encode = encode
            self._mappings = iterate_over
            n_mappings = len(iterate_over)
            if encode and not self.board_info.check_n_mappings(n_mappings):
                logging.warning("Too many mappings: %s (board supports %s, others will be ignored)",
                                n_mappings, self.board_info.n_mappings)
                # Padding `self_mappings` with empty mappings does not work,
                # because all mappings must have the same button set. Instead,
                # we will add empty mappings on the fly during iteration.

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self) -> str:
        if self._mappings is None:
            raise StopIteration
        if self._index >= len(self._mappings) and (
            not self._encode or
            self._index >= self.board_info.n_mappings
            ):
            raise StopIteration
        if self._index >= len(self._mappings):
            # add empty mappings as needed
            mapping = Mapping()
        else:
            mapping = self._mappings[self._index]
        self._index += 1
        self.set_mapping(mapping)
        if not self._encode:
            return self.show(self._index)
        # Only check compatibility if we are encoding
        assert self.is_compatible()
        return self.encode()

    def set_mapping(self, mapping: Mapping):
        """Set the mapping to be encoded or formatted."""
        self.mapping = mapping

    def is_compatible(self) -> bool:
        """Check if the current mapping is compatible with the board's capabilities. 
        If it is, return True; otherwise, raise an error with the reason."""
        n_buttons = len(list(self.mapping))
        if not self.board_info.check_n_buttons(n_buttons):
            raise ValueError(f"Too many buttons: {n_buttons} "
                                f"(board supports {self.board_info.n_buttons})")
        # the board has enough buttons
        keys = [key.key for combo in self.mapping.values() for key in combo.keys()]
        if not self.board_info.check_keys(keys):
            raise ValueError(f"Unsupported key(s): {set(keys) - set(self.board_info.keys)}")
        # all used keys are available on the board
        n_keys_per_button = max(
            (len(combo.flat()) for combo in self.mapping.values()),
            default=0) # an empty mapping uses zero keys
        if not self.board_info.check_n_keys_per_button(n_keys_per_button):
            raise ValueError(f"Too many key presses per button: {n_keys_per_button} "
                                f"(board supports {self.board_info.n_keys_per_button})")
        # all combos press at most n_keys_per_button keys simultaneously
        # warning if there's any turboed press
        if any(press.is_turbo() for combo in self.mapping.values() for press in combo.flat()):
            logging.warning("Turbo frequencies are ignored")
        if any(press.is_hold() for combo in self.mapping.values() for press in combo.flat()):
            logging.warning("Hold modifiers are ignored")
        return True

    def encode(self) -> str:
        """Encode the current mapping into a string that can be written to a header file. 
        If the current mapping is None, create and encode an empty mapping."""
        if self.mapping is None:
            self.mapping = Mapping()
        raw_mapping = self.mapping.raw()
        # title and description of the mapping
        description = (
            "/*\n"
            + textwrap.fill(raw_mapping.title +
                            (": " if raw_mapping.description else "") +
                            raw_mapping.description,
                            initial_indent='  ',
                            subsequent_indent='  ')
            + "\n*/\n\n"
        )
        scheme = raw_mapping.scheme
        rows = []
        extra_buttons = [None for _b in range(len(self.mapping), self.board_info.n_buttons)]
        # for each mapped button, plus any extra buttons that are not explicitly mapped
        for n_button, combo in enumerate(raw_mapping.presses + extra_buttons):
            if combo is None:
                combo_text = ""
                combo_list = []
            else:
                combo_text = combo
                # only non-empty combo_text get a comment
                combo_text = "/* " + combo_text + " */" if combo_text else ""
                # turboed keys get a - in front
                combo_list = [(self.TURBO_MARKER if raw_mapping.turboes[n_button][n_key] else "")
                              + press for n_key, press in enumerate(raw_mapping.keys[n_button])]
            # pad list of keys with noop
            combo_pad = ([self.board_info.noop] *
                         (self.board_info.n_keys_per_button - len(combo_list)))
            # current row
            cur_row = [combo_text] + combo_list + combo_pad
            # add current row
            rows += [cur_row]
        num_cols = [len(row) for row in rows]
        assert len(set(num_cols)) == 1, "Inconsistent number of columns"
        num_cols = num_cols[0]
        # maximum character width of each column
        col_widths = [max(len(rows[r][c]) for r in range(len(rows))) for c in range(num_cols)]
        # format specifiers to align columns
        fmt = " ".join([
            # column 0 is left aligned, all others are right aligned
            # all are padded according to `widths`
            ("{" + f"{w}:" + ("<" if w == 0 else ">") + f"{2 + col_widths[w]}" + "}"
             # all internal columns are separated by commas
             + ("," if 0 < w < len(col_widths) - 1 else ""))
            for w in range(num_cols)
        ])
        return (
            description
            + "// " + scheme + "\n"
            + "{\n"
            + ",\n".join("   " + fmt.format(*row) for row in rows)
            + "\n}"
        )

    # pylint: disable=too-many-locals  # This is not the prettiest code, but I doubt it's worth breaking it down into smaller functions.
    def show(self, cfg: Union[str, int]="CFG", button_numbers: bool=False) -> str:
        """Format the current mapping as a human-readable string with width `self.text_width`."""
        # Format specifiers with $ delimit the boundary
        # between the left and right parts of each button row
        # The numbers refer to the button order, consistent
        # with the one in `keys_file` in `project_dir`
        rows = [
            "[{12}] [{13}]  [{14}]$",
            "$",
            "[{0}] [{1}] [{2}]$[{4}] [{5}] [{6}] [{7}]",
            "$[{8}] [{9}] [{10}] [{11}]",
            "[{3}]$"
        ]
        n_buttons =  len(re.findall(r'\{[^}]*\}', "".join(rows)))
        raw_mapping = self.mapping.raw()
        if len(raw_mapping.presses) > n_buttons:
            raise ValueError(f"'format' only works for mappings with at most {n_buttons} buttons")
        presses = (raw_mapping.presses +
                   (n_buttons - len(raw_mapping.presses)) * [""])
        if button_numbers:
            presses = [f"{p} {k}" for k, p in enumerate(presses)]
        # fill in format specifiers with `buttons`
        filled = "#".join(rows).format(*presses).split("#")
        # split filled rows into left and right parts
        rows = [fr.split("$") for fr in filled]
        # add configuration number to top row
        if isinstance(cfg, int):
            configuration = f"{cfg:04b}"
        else:
            configuration = cfg
        rows[0][1] = f"[{configuration}]"
        # maximum length of left and right parts
        max_len = (max(len(row[0]) for row in rows), max(len(row[1]) for row in rows))
        def pad_left(r, p):    # pylint: disable=invalid-name # r is for row, p is for part
            return (max_len[p]-len(rows[r][p])) * " " + rows[r][p]
        def pad_right(r, p):   # pylint: disable=invalid-name # r is for row, p is for part
            return rows[r][p] + (max_len[p]-len(rows[r][p])) * " "
        new_rows = [
            (pad_right(0, 0), pad_left(0, 1)),
            (pad_right(1, 0), pad_left(1, 1)),
            (pad_right(2, 0), pad_right(2, 1)),
            (pad_right(3, 0), pad_right(3, 1)),
            (pad_left(4, 0), pad_left(4, 1))
        ]
        joined_rows = [left + "    " + right for left, right in new_rows]
        # all rows have the same length now
        ruler = "+-" + (len(joined_rows[0]) * "-") + "-+"
        joined_rows = [ruler] + ["| " + row + " |" for row in joined_rows] + [ruler]
        scheme_fmt = "{0:^" + str(len(joined_rows[0]))+ "}"
        scheme = scheme_fmt.format("( " + raw_mapping.scheme + " )")
        joined_rows = [scheme] + joined_rows
        left_pad = (max(0, (self.text_width - len(joined_rows[0]))) // 2) * " "
        centered_rows = [left_pad + row for row in joined_rows]
        board_str = "\n".join(centered_rows)
        header = (raw_mapping.title
                  + (": " if raw_mapping.description else "") + raw_mapping.description)
        if header:
            header = textwrap.fill(header, width=self.text_width)
            return header + "\n\n" + board_str
        return board_str

    def decode(self, encoded: str):
        """Decodes a named mapping from an encoded string, and sets it as the current mapping."""
        parsed = self._enc_re().match(encoded)
        if not parsed:
            raise ValueError("Parsing of mapping failed")
        scheme_str = parsed.group("scheme")
        # By default, use the first name scheme
        naming_scheme = next(iter(NameScheme))
        for scheme in NameScheme:
            if scheme.name == scheme_str:
                naming_scheme = scheme
                break
        mapping = default_from_scheme(naming_scheme)
        # Try to break down header into title and description
        header_str = parsed.group("header")
        title, description = "", ""
        if header_str:
            at_colon = header_str.split(":", maxsplit=1)
            at_space = header_str.split(" ", maxsplit=1)
            if len(at_colon) == 2:
                title, description = at_colon
            elif len(at_space) == 2:
                title, description = at_space
            # split at whitespaces, replace multiple whitespaces with a single one
            title = " ".join(title.split())
            description = " ".join(description.split())
        mapping.title = title
        mapping.description = description
        for button_num in range(self.board_info.n_buttons):
            try:
                button = mapping.buttons[button_num]
            except IndexError:
                logging.warning("Button #%s is unavailable: skipping", button_num)
                continue
            key_names = [parsed.group(f"B{button_num}K{k}")
                         for k in range(self.board_info.n_keys_per_button)]
            turboeds = [parsed.group(f"B{button_num}T{k}")
                        for k in range(self.board_info.n_keys_per_button)]
            combo = None
            for key_name, turboed in zip(key_names, turboeds):
                if key_name == self.board_info.noop:
                    continue
                try:
                    key = mapping.keys[key_name]
                except IndexError:
                    logging.warning("Key %s is unavailable: skipping", key_name)
                    continue
                press = Press(key, turbo=Press.TURBO_DEFAULT if turboed else None)
                combo = press if combo is None else combo & press
            if combo is not None:
                mapping[button] = combo
        self.mapping = mapping

    def _enc_re(self) -> re.Pattern:
        """Compiled regular expression object to match an encoded mapping.
        This is used by `decode`."""
        if self._enc_re_obj is not None:
            return self._enc_re_obj
        enc_re_ = (
            r"\s*"
            # optional header, with title and description
            + r"([/][*](?P<header>(.(?![*][/]))*(.(?=[*][/]))*)[*][/])?"
            + r"\s*"
            # optional naming scheme, matched with re.MULTILINE and without re.DOTALL
            + r"(?m-s:^\s*[/][/]\s*(?P<scheme>\w*).*$)"
            + r"\s*"
            # open curly brace
            + r"{"
            + r"\s*"
            # as many lines as buttons
            + r"\s*[,]\s*".join([
                # comments at the beginning of each row (ignored/discarded)
                r"([/][*](?P<B" + str(button)
                + r"desc>(.(?![*][/]))*(.(?=[*][/]))*)[*][/])?"
                + r"\s*"
                # n_keys_per_button key identifiers in each row
                + r"\s*[,]\s*".join([
                    # optional leading TURBO_MARKER denoting a turboed key
                    (r"(?P<B" + str(button)
                     + r"T" + str(key) + r">" + re.escape(self.TURBO_MARKER)
                     + r")?")
                    # mandatory key press identifier
                    + r"(?P<B" + str(button) + r"K" + str(key) + r">\s*?\w+)"
                    for key in range(self.board_info.n_keys_per_button)
                ])
                for button in range(self.board_info.n_buttons)
            ])
            + r"\s*"
            # closed curly brace
            + r"}"
            # anything following is ignored/discarded
        )
        self._enc_re_obj = re.compile(enc_re_, re.DOTALL)
        return self._enc_re_obj


class Exporter:
    """
    Export encoded and decoded mappings to and from file.

    The Exporter class applies the functionality of the Encoder class
    to a project directory files, where the Nez-Oba board's software
    is stored. Upon initialization, the class takes the name of a
    serialized mappings file `mapping_yaml`, and reads information
    about the board from a given `keys_file` in a given
    `project_dir`. Then, Exporter supports three main features:

    - Encoding (method `encode`): Encodes all mappings in the given
      `mapping_yaml` and writes them to files into the project
      directory.
    - Decoding (method `decode`): Decodes all mappings in the project
      directory and writes them into the given `mapping_yaml` file.
    - Showing (method `show`): Formats all mappings in the given
      `mapping_yaml` and returns them as a string.

    Attributes:
        project_dir: Directory where the board software is stored.
        mapping_yaml: Filename of the mappings file.
        keys_file: Name of file, in project_dir, with list of key
          names and other information about the board.
        mapping_fname: Filename pattern of the encoded files in
          project_dir.
        board_info: Information about the board (read upon
          initialization).
        BAK_EXT: Extension used for backup files.

    Methods:
        __init__: Initializes the Exporter with the given project
          directory, mapping file, and keys file.
        encode: Encodes the mappings in mapping_yaml and writes them
          into project_dir.
        decode: Decodes the encoded mappings in project_dir and writes
          them in mapping_yaml.
        show: Formats the mappings in mapping_yaml as a human-readable
          string.
    """
    # directory where the board software is stored
    project_dir: str

    # filename of the mapping file
    mapping_yaml: str

    # file with list of key names and other information about the board
    keys_file: str

    # filename pattern of the mapping files
    mapping_fname: str

    # information about the board
    board_info: Optional[BoardInfo]

    # extension used for backup files
    BAK_EXT: str = ".bak"

    def __init__(self, project_dir: str, mapping_yaml: str,
                 keys_file: str="keys.h",
                 mapping_fname: str="remap%02d.h"):
        """Create an exporter for a board with software in `project_dir` 
        for mapping file `mapping_yaml`."""
        self.project_dir = project_dir
        self.mapping_yaml = mapping_yaml
        self.keys_file = keys_file
        self.mapping_fname = mapping_fname
        self._load_info()

    def show(self, width: int = 75) -> str:
        """Read the mapping file and return its content as a human-readable string."""
        with open(self.mapping_yaml, "r", encoding="utf-8") as file_handle:
            mappings = from_yaml(file_handle.read())
        encoder = Encoder(self.board_info, mappings, encode=False, width=width)
        showed = ("\n\n" + width * "-" + "\n\n").join(as_text for as_text in encoder)
        return showed

    def encode(self, bak: bool = True) -> Mappings:
        """Read the mapping file and write its encoded content to a series of files 
        in the `project_dir`.
        
        If `bak`, make a backup of the existing files before overwriting them.
        
        Return the mappings read from the file.
        """
        with open(self.mapping_yaml, "r", encoding="utf-8") as file_handle:
            mappings = from_yaml(file_handle.read())
        encoder = Encoder(self.board_info, mappings, encode=True)
        for n_mapping, encoded in enumerate(encoder):
            fname = os.path.join(self.project_dir, self.mapping_fname % n_mapping)
            if os.path.exists(fname) and bak:
                os.rename(fname, fname + self.BAK_EXT)
            with open(fname, "w", encoding="utf-8") as file_handle:
                file_handle.write(encoded)
        return mappings

    def decode(self, bak: bool = True) -> Mappings:
        """Decodes the encoded mapping files in the `project_dir` and exports
        them to the mapping file `mapping_yaml`.
        
        If `bak`, make a backup of the existing mapping file before overwriting it.
        
        Return the mappings decoded from the files.
        """
        encoder = Encoder(self.board_info)
        mappings = []
        for n_mapping in range(self.board_info.n_mappings):
            fname = os.path.join(self.project_dir, self.mapping_fname % n_mapping)
            if not os.path.exists(fname):
                logging.warning("Mapping file %s does not exist: skipping", fname)
                continue
            with open(fname, "r", encoding="utf-8") as file_handle:
                encoded = file_handle.read()
            encoder.decode(encoded)
            mappings.append(encoder.mapping)
        mappings = Mappings(mappings)
        if os.path.exists(self.mapping_yaml) and bak:
            os.rename(self.mapping_yaml, self.mapping_yaml + self.BAK_EXT)
        with open(self.mapping_yaml, "w", encoding="utf-8") as file_handle:
            file_handle.write(to_yaml(mappings))
        return mappings

    def _load_info(self):
        """Load names and information about the board from `keys_file` in `project_dir`."""
        if not self.project_dir:
            self.board_info = None
            logging.warning("No project directory given: only show is available.")
            return
        keys_path = os.path.join(self.project_dir, self.keys_file)
        if not os.path.isfile(keys_path):
            raise FileNotFoundError(f"Cannot open keys file: {keys_path}")
        with open(keys_path, 'r', encoding='utf-8') as file_handle:
            lines = file_handle.readlines()
        n_buttons, n_mappings, n_keys_per_button, keys = None, None, None, []
        is_key = False
        for line in lines:
            # look for the definition of N_BUTTONS
            n_buttons_match = re.match(
                r"\s*[#]define\s+N_BUTTONS\s+(\d+)", line)
            if n_buttons_match:
                n_buttons = int(n_buttons_match.group(1))
                continue
            # look for the definition of N_KEYS_PER_BUTTON
            n_keys_per_button_match = re.match(
                r"\s*[#]define\s+N_KEYS_PER_BUTTON\s+(\d+)", line)
            if n_keys_per_button_match:
                n_keys_per_button = int(n_keys_per_button_match.group(1))
                continue
            # look for the definition of N_REMAPPINGS
            n_mappings_match = re.match(
                r"\s*[#]define\s+N_REMAPPINGS\s+(\d+)", line)
            if n_mappings_match:
                n_mappings = int(n_mappings_match.group(1))
                continue
            # end of enum type `key`
            if is_key and re.match(r"\s*};", line):
                is_key = False
                continue
            # collect values of enum type `key`
            if is_key:
                keys += [line.strip().split("=")[0]]
                continue
            # beginning of enum type `key`
            if not is_key and re.match(r"\s*enum\s+key", line):
                is_key = True
                continue
            info = BoardInfo(n_buttons, n_mappings, n_keys_per_button, keys)
            self.board_info = info
