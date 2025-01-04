"""
Functions to serialize and deserialize instances of the classes in
this package in YAML format.

The serialization function can optionally save information about the
system version used to serialize, so as to ensure that the
serialization and deserialization functions operate on a consistent
data representation.

Functions:
   to_yaml: serializes an object to YAML
   from_yaml: deserializes a string to an object
"""
from typing import Optional, Union, IO
import dataclasses
import enum
from collections import UserDict

# Documentation of PyYAML:
#    https://pyyaml.org/wiki/PyYAMLDocumentation
#    https://pyyaml.docsforge.com/master/api/yaml/
import yaml

from .buttons import Button, ButtonLayout, Buttons, TAG_Button, TAG_ButtonLayout, TAG_Buttons
from .keys import KeyGroup, Key, Keys, TAG_KeyGroup, TAG_Key, TAG_Keys
from .combos import Press, And, TAG_Press, TAG_And
from .mappings import Mapping, Mappings, TAG_Mapping, TAG_Mappings
from .namings import (NameScheme, NamedKey, NamedKeys, NamedMapping,
                      TAG_NameScheme, TAG_NamedKey, TAG_NamedKeys, TAG_NamedMapping)


class VersionedObject:
    """
    A versioned object.

    This class wraps an object content and adds a version tag. It also
    includes a tag for the de/serialization of instances of this
    class, as well as a current version tag.

    Attributes:
       TAG_VersionedObject: A class attribute with the tag used for
          serialization.
       VERSION: A class attribute with the system's current version
          tag.
       version: The instance's version tag.
       content: The instance's wrapped object.
    """
    # pylint: disable=too-few-public-methods  # This is a wrapper class

    TAG_VersionedObject = "!VersionedObject"
    VERSION = 1.0

    version: str
    content: object

    def __init__(self, obj: object, version: str):
        """Creates a VersionedObject that wraps a given object obj
           with a version tag version.

        Arguments:
           obj: The object to be wrapped.
           version: A string representing the used version tag.

        """
        self.version = version
        self.content = obj


class NoEnumAliasDumper(yaml.Dumper):
    """Subclass of yaml.Dumper that does not add references for
    identical instances of Enum, Button, and Key."""
    # pylint: disable=too-many-ancestors  # This follows from yaml's design.
    def ignore_aliases(self, data):
        if isinstance(data, (enum.Enum, Button, Key)):
            return True
        return super().ignore_aliases(data)


def versioned_representer(dumper: yaml.Dumper, data: VersionedObject) -> yaml.Node:
    """Serializes a VersionedObject."""
    # Dictionary data.__dict__ will only include instance attributes version and content
    return dumper.represent_mapping(VersionedObject.TAG_VersionedObject,
                                    data.__dict__)

def versioned_constructor(loader: yaml.Loader, node: yaml.Node, ignore_version: bool) -> object:
    """Deserializes a VersionedObject."""
    vobj = loader.construct_mapping(node)
    if not ignore_version:
        assert vobj["version"] == VersionedObject.VERSION, \
            "Cannot deserialize from different version"
    # If the versions match, discard the wrapper and return the content
    return vobj["content"]


def dataclass_representer(dumper: yaml.Dumper, data: object, tag: str) -> yaml.Node:
    """Serializes a dataclass object."""
    assert dataclasses.is_dataclass(data)
    # we do NOT use dataclasses.asdict, since that is recursive, whereas we want to
    # apply represeters based on the actual nested types of dataclasses
    datadict = data.__dict__
    return dumper.represent_mapping(tag, datadict)

def dataclass_constructor(loader: yaml.Loader, node: yaml.Node, cls: type) -> object:
    """Deserializes a dataclass object."""
    datadict = loader.construct_mapping(node)
    obj = cls(**datadict)
    return obj


def tuple_representer(dumper: yaml.Dumper, data: tuple, tag: str) -> yaml.Node:
    """Serializes a tuple object."""
    return dumper.represent_sequence(tag, data)

def tuple_constructor(loader: yaml.Loader, node: yaml.Node, cls: type) -> tuple:
    """Deserializes a tuple object."""
    # cls should be a subtype of tuple
    seq = loader.construct_sequence(node)
    obj = cls(seq)
    return obj


def attrtuple_representer(dumper: yaml.Dumper, data: tuple, tag: str) -> yaml.Node:
    """Serializes a tuple with attributes object."""
    # Any attributes of a tuple object are stored in __dict__
    try:
        attrs = data.__dict__
    except AttributeError:
        # Tuple has no attributes
        attrs = {}
    # Store the actual tuple under 'data'
    attrs["data"] = tuple(data)
    return dumper.represent_mapping(tag, attrs)

def attrtuple_constructor(loader: yaml.Loader, node: yaml.Node, cls: type) -> tuple:
    """Deserializes a tuple with attributes object."""
    # cls should be a subtype of tuple
    attrs = loader.construct_mapping(node)
    try:
        data = attrs["data"]
        del attrs["data"]
    except KeyError:
        pass
    obj = cls(data, **attrs)
    return obj


def enum_representer(dumper: yaml.Dumper, data: enum.Enum, tag: str) -> yaml.Node:
    """Serializes and Enum value."""
    name = data.name
    return dumper.represent_scalar(tag, name)

def enum_constructor(loader: yaml.Loader, node: yaml.Node, cls: type) -> enum.Enum:
    """Deserializes and Enum value."""
    # cls should be a subtype of Enum
    name = loader.construct_scalar(node)
    # Iterate though the Enum values to find the one that matches the deserialized name
    for val in cls:
        if val.name == name:
            return val
    raise ValueError(f"{name} is not a value of {cls}")


def userdict_representer(dumper: yaml.Dumper, data: UserDict, tag: str) -> yaml.Node:
    """Serializes a UserDict object."""
    node = dumper.represent_object(data)
    node.tag = tag
    return node

def mapping_constructor(loader: yaml.Loader, node: yaml.Node) -> Mapping:
    """Deserializes a Mapping object."""
    # pylint: disable=invalid-name  # m, b, and c are acceptable variable names
    m = loader.construct_mapping(node, deep=True)
    # Construct an empty mapping
    obj = Mapping(buttons=m["buttons"], keys=m["keys"],
                  identifier=m["identifier"], title=m["title"], description=m["description"])
    # Add all mapping pairs
    for b, c in m["data"].items():
        obj[b] = c
    return obj

def namedmapping_constructor(loader: yaml.Loader, node: yaml.Node) -> NamedMapping:
    """Deserializes a NamedMapping object."""
    # pylint: disable=invalid-name  # m is an acceptable variable name
    m = mapping_constructor(loader, node)
    # Use NamedMapping's copy constructor
    obj = NamedMapping(mapping=m)
    return obj


def mappinglist_representer(dumper: yaml.Dumper, data: Mappings, tag: str) -> yaml.Node:
    """Serializes a Mappings object."""
    return dumper.represent_mapping(tag,
                                    # by putting buttons and keys first, all Mapping instances
                                    # in data will use references to them, thus becoming much
                                    # more concise in serialized form
                                    {"buttons": data.buttons,
                                     "keys": data.keys,
                                     "data": data.data})

def mappinglist_constructor(loader: yaml.Loader, node: yaml.Node) -> Mappings:
    """Deserializes a Mappings object."""
    # pylint: disable=invalid-name  # m is an acceptable variable name
    m = loader.construct_mapping(node, deep=True)
    obj = Mappings(m["data"])
    return obj



def to_yaml(obj: object,
            fname: Optional[Union[str, IO]]=None, overwrite=True, version=False) -> str:
    """
    Converts obj to a YAML representation.

    Attributes:
       obj: The object to be serialized into YAML. It should be an
          instance of the classes in this package.
       fname: If it's a string or file object, the method writes the
          serialized string into the corresponding file. If it's None,
          the method does not write to file.
       overwrite: If fname is None or a file object, this argument is
          ignored. Otherwise, if True the method overwrites any
          existing file with name fname; if False it appends to any
          existing file.
       version: If True, wraps obj into an instance of VersionedObject
          with version = VersionedObject.VERSION and serializes that.
    """
    # Add representers for all supported classes
    yaml.add_representer(VersionedObject, versioned_representer)
    yaml.add_representer(Button,
                         lambda dumper, data: dataclass_representer(dumper, data, TAG_Button))
    yaml.add_representer(ButtonLayout,
                         lambda dumper, data: enum_representer(dumper, data, TAG_ButtonLayout))
    yaml.add_representer(Buttons,
                         lambda dumper, data: attrtuple_representer(dumper, data, TAG_Buttons))
    yaml.add_representer(KeyGroup,
                         lambda dumper, data: enum_representer(dumper, data, TAG_KeyGroup))
    yaml.add_representer(Key,
                         lambda dumper, data: dataclass_representer(dumper, data, TAG_Key))
    yaml.add_representer(Keys,
                         lambda dumper, data: tuple_representer(dumper, data, TAG_Keys))
    yaml.add_representer(Press,
                         lambda dumper, data: dataclass_representer(dumper, data, TAG_Press))
    yaml.add_representer(And,
                         lambda dumper, data: tuple_representer(dumper, data, TAG_And))
    yaml.add_representer(NameScheme,
                         lambda dumper, data: enum_representer(dumper, data, TAG_NameScheme))
    yaml.add_representer(NamedKey,
                         lambda dumper, data: dataclass_representer(dumper, data, TAG_NamedKey))
    yaml.add_representer(NamedKeys,
                         lambda dumper, data: tuple_representer(dumper, data, TAG_NamedKeys))
    yaml.add_representer(Mapping,
                         lambda dumper, data: userdict_representer(dumper, data, TAG_Mapping))
    yaml.add_representer(NamedMapping,
                         lambda dumper, data: userdict_representer(dumper, data, TAG_NamedMapping))
    yaml.add_representer(Mappings,
                         lambda dumper, data: mappinglist_representer(dumper, data, TAG_Mappings))
    if version:
        to_dump = VersionedObject(obj, VersionedObject.VERSION)
    else:
        to_dump = obj
    serialized = yaml.dump(to_dump,
                           sort_keys=False,
                           # ignore aliases of Enum classes, since these
                           # are treated as unique instances anyways
                           Dumper=NoEnumAliasDumper)
    if fname is not None:
        if isinstance(fname, str):
            # pylint: disable=invalid-name  # fp is an acceptable variable name
            with open(fname, "w" if overwrite else "a", encoding="utf-8") as fp:
                fp.write(serialized)
        else:
            fname.write(serialized)
    return serialized


def from_yaml(yml: str, version=False) -> object:
    """
    Deserializes yml from a YAML representation.

    Attributes:
       yml: A string encoding a YAML-serialized object of the classes
          in this package.
       version: If True, the method expects to deserialize an instance
          of VersionedObject; after deserializing, it checks that the
          deserialized object's attribute version equals
          VersionedObject.VERSION, and then returns the deserialized
          object's attribute content. If False, the method returns the
          deserialized object as is.

    Raises:
       AssertionError: If version is True and the deserialized
          object's version check fails.
    """
    yaml.add_constructor(VersionedObject.TAG_VersionedObject,
                         lambda loader, node: versioned_constructor(loader, node, version))
    yaml.add_constructor(TAG_Button,
                         lambda loader, node: dataclass_constructor(loader, node, Button))
    yaml.add_constructor(TAG_ButtonLayout,
                         lambda loader, node: enum_constructor(loader, node, ButtonLayout))
    yaml.add_constructor(TAG_Buttons,
                         lambda loader, node: attrtuple_constructor(loader, node, Buttons))
    yaml.add_constructor(TAG_KeyGroup,
                         lambda loader, node: enum_constructor(loader, node, KeyGroup))
    yaml.add_constructor(TAG_Key,
                         lambda loader, node: dataclass_constructor(loader, node, Key))
    yaml.add_constructor(TAG_Keys,
                         lambda loader, node: tuple_constructor(loader, node, Keys))
    yaml.add_constructor(TAG_Press,
                         lambda loader, node: dataclass_constructor(loader, node, Press))
    yaml.add_constructor(TAG_And,
                         lambda loader, node: tuple_constructor(loader, node, And))
    yaml.add_constructor(TAG_NameScheme,
                         lambda loader, node: enum_constructor(loader, node, NameScheme))
    yaml.add_constructor(TAG_NamedKey,
                         lambda loader, node: dataclass_constructor(loader, node, NamedKey))
    yaml.add_constructor(TAG_NamedKeys,
                         lambda loader, node: tuple_constructor(loader, node, NamedKeys))
    yaml.add_constructor(TAG_Mapping, mapping_constructor)
    yaml.add_constructor(TAG_Mappings, mappinglist_constructor)
    yaml.add_constructor(TAG_NamedMapping, namedmapping_constructor)
    try:
        return yaml.full_load(yml)
    except yaml.YAMLError:
        return None
