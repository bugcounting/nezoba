"""
This module defines the state model for the remapper GUI and
provides functions to read and modify it.

The module includes the `State` class, which models the complete state
of the remapper GUI. GUI components do not access the state directly
but through JustPy's `get_model` and `set_model` functions, which are
redefined in this module to fit the remapper's state
features. Components access views of the state, which are instances of
the `View` class, also defined in this module, and exchange values
that are instances of suitable subclasses of `ModelValue`.

Classes:
    Options: A class to store the main options of the remapper GUI.
    State: A class to represent the current state of the remapper GUI.
    View: A class to represent a view of the state.
    ModelValue: A base type for values of state components.

Functions:
    get_model: JustPy's get_model function, revised to work with State components.
    set_model: JustPy's set_model function, revised to work with State components.
"""

from __future__ import annotations
from typing import IO, Any, Optional, List, Set, Generic, TypeVar
import logging
import os
from pathlib import Path
import tempfile
import justpy

from ..remapper.buttons import Button, Buttons, ButtonsInfo
from ..remapper.mappings import Mapping, Mappings
from ..remapper.namings import NamedKeys, NamedMapping, KeysInfo
from ..remapper.serialization import from_yaml, to_yaml


class Options:
    """A class to store the main options of the remapper GUI."""

    _save_dir: Path
    _image_dir: Path
    _max_messages: int

    _messages: List[str]

    # Available button sets, each an instance of `buttons.Buttons`.
    # The dictionary keys are filenames of the images of each button set; the
    # dictionary values are a pair of button set object (an instance of
    # `buttons.Buttons`) and the full path to the image file.
    _buttons: ButtonsInfo = ButtonsInfo()

    # Available key sets, each an instance of `namings.NamedKeys`.
    # The dictionary keys are filenames of the images of each key set (that is,
    # a device with those keys); the dictionary values are a pair of key set
    # object (an instance of `namings.NamedKeys`) and the full path to the image
    # file.
    _keys: KeysInfo = KeysInfo()

    def __init__(self, save_dir: str, image_dir: str, max_messages: int):
        """Constructs an instance of `Options`.

        Arguments:
            save_dir: The directory where mappings are saved.
            image_dir: The directory where images of controllers and buttons are
              saved.
            max_messages: The maximum number of messages kept in the message log.
        """
        self._messages = []
        self._validate_options(save_dir, image_dir, max_messages)

    def _validate_options(self, save_dir: str, image_dir: str, max_messages: int):
        self._save_dir = Path(save_dir)
        # Create save directory if it doesn't already exist
        self._save_dir.mkdir(parents=True, exist_ok=True)
        self._image_dir = Path(image_dir)
        if not self._image_dir.is_dir():
            raise ValueError(
                f"Image directory {self._image_dir} doesn't exist."
                )
        self._max_messages = max_messages
        if self._max_messages < 0:
            raise ValueError(
                f"Invalid maximum number of messages: {self._max_messages}."
                )

    def image_path(self, filename: str) -> str:
        """Path to the image file `filename`."""
        return str(Path(self._image_dir, filename))

    def message(self, *args: str):
        """Join all arguments and add them as a new message in the message log."""
        new_message = " ".join(args)
        logging.info(new_message)
        self._messages.append(new_message)
        # Keep only the N_MESSAGES most recent messages
        self._messages = self._messages[-self._max_messages:]

    @property
    def save_dir(self) -> str:
        """The directory where mappings are saved."""
        return self._save_dir

    @property
    def messages(self) -> List[str]:
        """The list of messages in the message log."""
        return self._messages

    def add_buttons(self, buttons: Buttons, image_filename: str):
        """Add button set `buttons`, and display it using image `image_filename`
        in the image path."""
        self._buttons[buttons] = self.image_path(image_filename)

    def add_keys(self, keys: NamedKeys, image_filename: str):
        """Add key set `keys`, and display it using image `image_filename`
        in the image path."""
        self._keys[keys] = self.image_path(image_filename)

    @property
    def buttons(self) -> ButtonsInfo:
        """Information about the available button sets."""
        return self._buttons

    @property
    def keys(self) -> KeysInfo:
        """Information about the available key sets."""
        return self._keys

# pylint: disable=too-many-instance-attributes  # Touché, but the state is complex and I won't be refactoring in the foreseeable future.
class State:
    """The remapper GUI's complete state.

    The state comprises numerous attributes, capturing all details of the
    remapper GUI's state. The attributes should be considered private (that's
    why they are not documented here), and accessed only through the methods of
    this class. Roughly, every attribute has a getter method and, if it is
    mutable, a setter method.

    The design of the class may look verbose, with many attributes and fairly
    simple methods. Indeed, the abstraction of the state takes place with the
    views; thus, the state interface is as straightforward ("dumb"?) as possible, 
    so that it is decoupled as much as possible from the specific views.

    A clarification about the terminology. A "mapping" is an instance of class
    `mappings.Mapping`, whereas a "configuration" is an integer index, denoting
    a mapping in a list of type `mappings.Mappings`. Thus, the "current mapping"
    is the mapping with the "current configuration" as index.
    """

    _options: Options

    # File with currently saved mappings.
    saved_file: IO
    # Content of `saved_file`.
    serialized_file: str = ""

    # Remapper's mappings.
    mappings: Optional[Mappings]
    # Currently displayed configuration (index of current mapping), or None if
    # no mapping is selected.
    _configuration: Optional[int]
    # Currently selected button in current mapping, or None if no button is
    # selected.
    button: Optional[Button]
    # Index of the button press being edited, or None if no button press is
    # being edited.
    in_edit: Optional[int]

    # Filename of saved mappings.
    _filename: str = ""

    # Configurations with unsaved changes.
    unsaved: Set[int] = set()

    # Is a file selected for upload?
    upload_selected: bool = False

    # Configurations currently selected for swapping.
    swap_from: Optional[int]
    swap_to: Optional[int]

    def __init__(self, options: Options):
        self._options = options
        self.message = self._options.message
        self.mappings = Mappings()
        # Save empty mapping, and keep a version as string
        self.serialized_file = to_yaml(self.mappings)
        self._configuration = None
        self.button = None
        self.in_edit = None
        self.swap_from, self.swap_to = None, None
        self.message("Welcome to the Nez-Oba configuration app!")
        if not self.mappings:
            self.message(
                "Please upload a configurations file, or create a new configuration.")

    @property
    def options(self) -> Options:
        """The main options of the remapper GUI."""
        return self._options

    @property
    def filename(self) -> str:
        """The current filename."""
        return self._filename

    @filename.setter
    def filename(self, new_filename: str):
        """Set the current filename to `new_filename`."""
        self._filename = new_filename
        if new_filename == "":
            self.message("Empty filename set.")
        else:
            self.message(f"New filename set: {new_filename}.")

    def load(self) -> bool:
        """Load mappings from the current file. Return False if the file format is invalid."""
        if not self._filename:
            return False
        self.mappings = None
        try:
            filename = os.path.abspath(self._filename)
            with open(filename, "r", encoding="utf-8") as file_handle:
                self.mappings = from_yaml(file_handle.read())
        except FileNotFoundError:
            self.message(f"File {self._filename} doesn't exist.")
        if not isinstance(self.mappings, Mappings):
            # Deserialization error
            self.message(
                f"File {self._filename} is invalid. Please select a new one.")
            return False
        logging.info(
            "Loaded file %s has %d mappings.",
            os.path.abspath(self._filename),
            len(self.mappings)
        )
        return True

    def save(self, current: bool = True):
        """Save the current mapping to file. If `current` is False, save all mappings."""
        if not current:
            if not self.unsaved:
                return
            to_save = self.mappings
            self.unsaved = set()
            self.message("All mappings saved to file.")
        else:
            old_mappings = from_yaml(self.serialized_file)
            if not isinstance(old_mappings, Mappings):
                logging.error(
                    "Deserialization of mappings failed (file %s)", self.saved_file.name)
                return
            l_old, l_cur = len(old_mappings), len(self.mappings)
            cfg = self._configuration
            assert 0 <= cfg < l_cur, f"Invalid current configuration for save: {cfg}"
            if cfg not in self.unsaved:
                return
            if cfg < l_old:
                old_mappings[cfg] = self.mappings[cfg]
            elif l_old <= cfg < l_cur:
                old_mappings.append(self.mappings[cfg])
            else:
                logging.error(
                    "Cannot save mapping to cfg %d: old %d, cur %d", cfg, l_old, l_cur)
                return
            to_save = old_mappings
            self.unsaved.remove(cfg)
            self.message(f"Mapping #{cfg} saved to file.")
        # Create new temporary file
        with tempfile.NamedTemporaryFile(mode="w+",
                                         suffix=".yml", prefix="nezoba_save_",
                                         dir=self._options.save_dir,
                                         delete=False) as file:
            self.saved_file = file
            # Convert mapping to be saved to yaml, and save it to file and as attribute `serialized`
            self.serialized_file = to_yaml(to_save, self.saved_file)
            # with will close the file

    def undo(self, current: bool = True):
        """Undo the last unsaved changes to the current mapping. 
        If `current` is False, undo unsaved changes to all mappings."""
        old_mappings = from_yaml(self.serialized_file)
        if not isinstance(old_mappings, Mappings):
            logging.error(
                "Deserialization of mappings failed (file %s)", self.saved_file.name)
            return
        if not current:
            if not self.unsaved:
                return
            self.mappings = old_mappings
            self.unsaved = set()
            self.message("Undo of changes to all mappings.")
        else:
            l_old, l_cur = len(old_mappings), len(self.mappings)
            cfg = self._configuration
            assert 0 <= cfg < l_cur, f"Invalid current configuration for undo: {cfg}"
            if cfg not in self.unsaved:
                return
            if cfg < l_old:
                self.mappings[cfg] = old_mappings[cfg]
                self.unsaved.remove(cfg)
            elif l_old <= cfg < l_cur:
                self.delete_current_configuration()
            else:
                logging.error(
                    "Cannot undo mapping to cfg %d: old %d, cur %d", cfg, l_old, l_cur)
                return
            self.message(f"Undo of changes to mapping #{cfg}.")
        # Reset partial state
        self.button = None
        if len(self.mappings) <= cfg:
            self._configuration = None

    @property
    def mapping(self) -> Optional[Mapping]:
        """The current mapping if one is selected, None otherwise."""
        if self._configuration is not None and self.mappings is not None:
            return self.mappings[self._configuration]
        return None

    @mapping.setter
    def mapping(self, new_mapping: Mapping):
        """Set the current mapping to `new_mapping`. 
        Do nothing if no mapping is currently selected."""
        if self._configuration is not None and self.mappings is not None:
            self.mappings[self._configuration] = new_mapping
            self.modified()

    def modified(self):
        """Mark the current configuration as modified."""
        self.unsaved.add(self._configuration)

    @property
    def configuration(self) -> Optional[int]:
        """The current configuration if one is selected, None otherwise."""
        return self._configuration

    @configuration.setter
    def configuration(self, new_configuration: Optional[int]):
        """Set the current configuration to `new_configuration`."""
        if new_configuration == self._configuration:
            return
        self.in_edit = None
        self._configuration = new_configuration
        self.button = None
        if new_configuration is not None:
            self.message(f"Current mapping: #{self._configuration}."
                         " Click any button to remap.")

    def new_configuration(self):
        """Create a new configuration with an empty mapping."""
        identifier = len(self.mappings)
        title, description = "Empty mapping", "This is an empty mapping."
        mapping = self.mapping
        empty = None
        # Use buttons and keys of current mapping, if one exists
        if mapping:
            empty = NamedMapping(mapping.buttons, mapping.keys, identifier,
                                 title, description)
        # Otherwise, try to pick the first sets of buttons and keys
        else:
            buttons = self.options.buttons.first()
            keys = self.options.keys.first()
            if buttons is None or keys is None:
                logging.error(
                    "Missing buttons and/or keys to create new mappings.")
                return
            empty = NamedMapping(buttons, keys, identifier, title, description)
        self.mappings.append(empty)
        self.message(f"New empty mapping #{identifier} created.")
        self.configuration = identifier
        self.modified()

    def delete_current_configuration(self):
        """Delete the current configuration."""
        cfg = self._configuration
        # No current configuration: do nothing
        if cfg is None:
            return
        self.mappings.pop(cfg)
        self.unsaved.remove(cfg)
        # Rescale indexes of unsaved cfgs
        self.unsaved = {(c if c < cfg else c - 1) for c in self.unsaved}
        self.message(f"Mapping #{cfg} deleted.")
        self.configuration = None

    def copy_current_configuration(self):
        """Create a new configuration with a copy of the current one."""
        cfg = self._configuration
        # No current configuration: do nothing
        if cfg is None:
            return
        mapping = self.mapping
        new_mapping = NamedMapping(mapping)
        new_cfg = len(self.mappings)
        self.mappings.append(new_mapping)
        self.message(
            f"The new mapping #{new_cfg} is a copy of mapping #{cfg}.")
        self.configuration = new_cfg
        self.unsaved.add(new_cfg)

    def swap(self):
        """Swap the two configurations currently selected for swapping."""
        if self.swap_from is None or self.swap_to is None or self.swap_from == self.swap_to:
            return
        self.mappings[self.swap_from], self.mappings[self.swap_to] = (
            self.mappings[self.swap_to], self.mappings[self.swap_from]
        )
        # swap self.swap_from and self.swap_to also in unsaved
        def swp(var, sw_from, sw_to):
            return sw_to if var == sw_from else (sw_from if var == sw_to else var)
        self.unsaved = {swp(c, self.swap_from, self.swap_to) for c in self.unsaved}
        self.message(
            f"Mappings #{self.swap_from} and #{self.swap_to} swapped.")
        # swap self.swap_from and self.swap_to
        self.swap_from, self.swap_to = self.swap_to, self.swap_from

    def toggle_edit(self, idx: int):
        """Toggle the currently editing component."""
        if idx == self.in_edit:
            self.in_edit = None
        # Any other component stops editing
        else:
            self.in_edit = idx

    def get_download(self) -> str:
        """Return the content of the saved file as a string."""
        return self.serialized_file

    def pick_upload(self, picked=True):
        """Show if a file is selected for upload."""
        self.upload_selected = picked
        if picked:
            self.message("File selected for upload. CLICK the upload button.")

    def set_upload(self, upload: str):
        """Set the content of the uploaded file as the new mappings."""
        new_mappings = from_yaml(upload)
        # Deserialization error
        if not isinstance(new_mappings, Mappings):
            if not self.upload_selected:
                self.message("Please select a valid file to upload.")
            else:
                self.message(
                    "Uploaded file is invalid. Current mappings not changed."
                    )
                self.pick_upload(False)
        else:
            self.mappings = new_mappings
            self.unsaved = set(range(len(self.mappings)))
            self._configuration = None
            self.message("File uploaded. New mappings not saved!")


# pylint: disable=too-few-public-methods # View is a base, abstract class.
S = TypeVar("S")


class View(Generic[S]):
    """
    A wrapper around a state object, used to constrain access of a component to the object state. 

    A view's interface always includes a property `value`, which provides access
    to some, possibly compound, information about the wrapped object state.
    The interface may also include other methods, which are normally used
    as callback by the component that is built on the view.

    In some cases, a View subclass may also store additional information
    passed to the constructor. This information is used to determine the
    view on the object state specifically for the component that is built
    on the view.

    In most cases, a View subclass is a wrapper around a State object. 
    Some View subclasses are wrappers around 'local' state objects,
    such as individual button presses.
    """

    _state: S

    def __init__(self, state: S, **kwargs):
        """Construct a view on `state`. If `state` is already a View,
        the new view is a wrapper around `state.value`.

        If `state` has a method `message`, the new view has a method
        with the same name that calls `state.message`.

        The constructor also accepts additional keyword arguments, 
        which are stored as attributes with the same name as 
        the keyword arguments' names.
        """
        if isinstance(state, View):
            self._state = state.value
        else:
            self._state = state
        if hasattr(state, "message") and callable(state.message):
            self.message = state.message
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)

    @property
    def value(self) -> Any:
        """The value of the state components exported by this view."""
        return None

    @value.setter
    def value(self, new_value: Any):
        """Set the value of the state components exported by this view."""
        raise NotImplementedError("Cannot change the value of "
                                  + self.__class__.__name__ + " instances.")


def get_model(component: justpy.HTMLBaseComponent) -> Any:
    """
    Return the current model value of `component`. If `component`
    has no attribute `model`, returns None.

    Usually, the model is an object of class View, and its value is given
    by its property `value`. However, on JustPy's standard components, 
    the model value can be of any type (usually, str, int, or bool).

    Returns:
       The current model value of `component`, or None if `component`
       has no attribute `model`.
    """
    if not hasattr(component, "model"):
        return None
    if isinstance(component.model, View):
        return component.model.value
    # In JustPy, get_model is first defined in JustpyBaseComponent,
    # which is a superclass of HTMLBaseComponent. Hence, the following
    # calls the overridden get_model implementation as a fallback, for
    # compatibility with JustPy's standard components.
    return super(type(component), component).get_model()


def set_model(component: justpy.HTMLBaseComponent, value: Any):
    """
    Set the model value of `component` to `value`. If `component`
    has no attribute 'model', does nothing.

    Usually, the model is an object of class View, and its value is given
    by its property `value`. However, on JustPy's standard components, 
    the model value can be of any type (usually, str, int, or bool).

    Args:
       value: The new model value of `component`.
    """
    if not hasattr(component, "model"):
        return
    if isinstance(component.model, View):
        component.model.value = value
    else:
        # In JustPy, set_model is first defined in JustpyBaseComponent,
        # which is a superclass of HTMLBaseComponent. Hence, the following
        # calls the overridden set_model implementation as a fallback, for
        # compatibility with JustPy's standard components.
        super(type(component), component).set_model(value)
