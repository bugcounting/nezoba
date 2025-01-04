"""
This module provides various utility functions for the Nez-Oba remapper.

The utilities include functions for parsing SVG files, wrapping JustPy component interactions,
and navigating nested JustPy elements.
"""

# pylint: disable=too-many-lines # This module is just a collection of several utility functions

from __future__ import annotations
from typing import Optional, Union, Any, Callable
from types import FunctionType, MethodType
from dataclasses import dataclass
from enum import Enum, unique
import logging
import re
import base64
from xml.dom import minidom
import xml.dom
import justpy

from .model import get_model, set_model, View

# pylint: disable=too-many-locals
def parse_html_file_robust(filename: str,
                           reset_size: bool = False,
                           renames: Optional[dict[str, str]] = None) -> justpy.HTMLBaseComponent:
    """
    Parses HTML file with given `filename` and returns the
    corresponding JustPy component instance.

    If the parser encounters any unknown tag, it will remove it and
    try to parse again.

    The parser can also reset the size (width and height attributes),
    which is convenient to scale them dynamically when displaying
    them.

    The parser can also rename attributes. One situation where this is
    useful is when combining the parsed component into a larger HTML
    document. In this case, each node's attribute 'id' should be
    unique within the whole HTML document
    (https://www.w3schools.com/html/html_id.asp). Therefore, it is
    advisable to rename 'id' to something else in the parsed
    component, and then assigning fresh 'id' values to its nodes that
    are unique globally.

    Args:
       filename: The name of the file to be parsed.

       reset_size: If True, sets the width and height attributes of
          the parsed component to 100%, making them relative size. If
          the parsed component doesn't have width or height
          attributes, this argument is ignored.

       renames: For every key, value in this dictionary, renames all
          attributes with name key to name value. For example {"id":
          "myid"} renames all attributes "id" to "myid", without
          changing their value.

    Returns:
       An instance of HTMLBaseComponent corresponding to the parsed
       file.
    """
    with open(filename, "r", encoding="utf-8") as file_handle:
        html_str = file_handle.read()
    xml_obj = minidom.parseString(html_str)
    # Set `renames` to an empty dictionary if it is None
    if renames is None:
        renames = {}
    # Rename attributes
    for rename, into in renames.items():
        xml_rename_attribute(xml_obj, rename, into)
    while True:
        html_str = xml_obj.toxml()
        try:
            html = justpy.parse_html(html_str)
            # Reset size
            if reset_size and hasattr(html, "width") and hasattr(html, "height"):
                html.width = "100%"
                html.height = "100%"
            return html
        except ValueError as exc:
            # Parsing error
            msg = str(exc)
            match = re.match(r"Tag not defined: (\S+)", msg)
            if match:
                # Remove all nodes with the undefined tag
                tag = match.group(1)
                to_be_deleted = xml_obj.getElementsByTagName(tag)
                for node in to_be_deleted:
                    parent = node.parentNode
                    parent.removeChild(node)
            else:
                # Propagate any other exception
                raise


def xml_rename_attribute(node: xml.dom.Node, rename: str, into: str):
    """
    Changes all attributes with name `rename` to name `into`.

    The renaming goes through the whole XML tree rooted in `node` and
    is in place (that is, it modifies the nodes directly). Thus, after
    renaming, the tree rooted in node has no more instances of
    attribute `rename`; and all nodes that previously had an attribute
    `rename` now have an attribute `into` with the same value.

    Args:
       node: The root node of the XML tree.

       rename: The attribute name to be renamed.

       into: The new attribute name, replacing the renamed
          attribute.
    """
    try:
        # Value of attribute `rename`
        id_value = node.attributes[rename].value
        if id_value:
            # Add attribute `into` with value `id_value`
            node.setAttribute(into, id_value)
            # Remove attribute `rename`
            node.removeAttribute(rename)
    except (TypeError, KeyError, NameError, xml.dom.NotFoundErr):
        # Skip nodes without attribute `rename` or of different kinds
        pass
    # Recursively rename children
    if node.hasChildNodes():
        for child in node.childNodes:
            xml_rename_attribute(child, rename, into)


def instrument_component_class(cls: type = justpy.HTMLBaseComponent):
    """
    Add several service methods to a given class `cls`.

    In Python, a method bound to `cls` (a class object) becomes
    available in all instances of cls, as if it had been defined
    statically in `cls`'s definition.

    Args:
       cls: The class (type) object to be instrumented.
    """
    # Tree navigation
    cls.filter_by_attribute = filter_by_attribute
    cls.by_layer_spec = by_layer_spec
    cls.replace = replace
    cls.get_background = get_background
    # Class and style change
    cls.add_classes = add_classes
    cls.add_styles = add_styles
    # Model management
    cls.get_model = get_model
    cls.set_model = set_model
    # Color scheme (to be replaced by a Theme class)
    cls.set_color_scheme = set_color_scheme
    cls.get_color = get_color


def override_event_handler(cls: type = justpy.Input):
    """Replace event handler method in the given class `cls`."""
    cls.before_event_handler = before_event_handler


def filter_by_attribute(components: list[justpy.HTMLBaseComponent], attribute: str, value: str,
                        value_is_re: bool = False) -> list[justpy.HTMLBaseComponent]:
    """
    Return a list with all elements of `components` whose
    attribute with name `attribute` matches `value`.

    Args:
       components: The list of components whose elements filtered.

       attribute: The attribute name whose value has to match key.

       value: The attribute value that is searched for.

       value_is_re: If False, matches elements where `attribute`'s
          value exactly equals `value`. If True, matches elements
          where `attribute`'s value matches regular expression `value`
          (using the syntax of Python's re library).

    Returns:
       A sublist of `components` with only those elements whose
       attribute `attribute` matches `value`.

    """
    def match(component: justpy.HTMLBaseComponent) -> bool:
        """Returns True iff components's attribute `attribute` matches `value`."""
        current_value = getattr(component, attribute, None)
        if current_value is None:
            return False
        try:
            current_value = str(current_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Cannot convert value of attribute {attribute} to string"
                ) from exc
        if value_is_re:
            matched = re.match(value, current_value) is not None
        else:
            matched = current_value == value
        return matched

    result = [component for component in components if match(component)]
    return result


@dataclass(frozen=True, init=True)
class NodeIndex:
    """
    A specification of nodes in a tree based on their depth and
    order.

    Attributes:
       depth: If it's a positive integer, it denotes the depth of
          nodes in a tree: the root is depth 0, its children are depth
          1, and so on. If it's a negative integer, it denotes an
          index in the list of all depths in a tree: -1 is the
          deepest. If it's None, it denotes nodes at any depth.

       index: If it's an integer, it denotes the index of all nodes
          among those whose depth matches `depth`. If it's None, it
          denotes all nodes at the given depth.


    Examples:
       - NodeIndex(depth=None, index=None) specifies all nodes in a
            tree: any depth, any index.

       - NodeIndex(depth=3, index=None) specifies all nodes at depth
         3.

       - NodeIndex(depth=-1, index=None) specifies all leaf nodes in a
            balanced tree. If the tree is not balanced, it denotes all
            leaf nodes in the deepest subtree of the tree.

       - NodeIndex(depth=1, index=0) specifies the first leaf node
         under the root.
    """
    depth: Optional[int] = None
    index: Optional[int] = None


@dataclass
class Layer:
    """
    Shorthands for specifying nodes in a tree based on their depth
    and order.

    Attributes:
       THIS: Specifies the root node in a tree.

       ALL: Specifies all nodes in the tree.

       LEAVES: Specifies all leaf nodes in a balanced tree. If the
          tree is not balanced, specifies all leaf nodes in the deepest
          part of the tree.

       BACKGROUND: Specifies the first leaf node in each in a balanced
          tree. If the tree is not balanced, specifies the leaf nodes
          in all deepest parts of the tree.

       FOREGROUND: Specifies the last leaf node in a balanced tree. If
          the tree is not balanced, specifies the leaf nodes in all
          deepest parts of the tree.
    """
    THIS = NodeIndex(depth=0)
    ALL = NodeIndex()
    LEAVES = NodeIndex(depth=-1)
    BACKGROUND = NodeIndex(depth=-1, index=0)
    FOREGROUND = NodeIndex(depth=-1, index=-1)


@dataclass(frozen=True, init=True)
class NodeSpec:
    """
    A specification of nodes in a tree based on their attributes.

    Attributes:
       attribute: The name of the attribute used as node
          specification.

       value: The value of the attribute used as node specification.

       regex: If False, specifies all nodes with `attribute` equal to
          `value`. If True, specifices all nodes with `attribute`
          matching regular expression `value` (using the syntax of
          Python's re library).
    """
    attribute: str
    value: str
    regex: bool = False


# pylint: disable=too-few-public-methods # This type is to have meaningful type annotations
class Layers:
    """A specification of nodes in a tree. This consists of the union
    of types NodeSpec, NodeIndex, and Layer."""


Layers = Union[NodeIndex, Layer, NodeSpec]


def visited(component: justpy.HTMLBaseComponent,
            depths=False, _current_depth=0) -> Union[list[justpy.HTMLBaseComponent],
                                                     list[tuple[int, justpy.HTMLBaseComponent]]]:
    """
    List all subcomponents of `component` (including `component`
    itself) in depth-first order.

    Args:
       component: The HTML component that is the root of the visited
          tree.

       depths: If True, includes the depth of each visited
          subcomponent`.

    Returns:
       If `depths` is False, a list of all subcomponents in
       depth-first order. If `depths` is True, a list of pairs (depth,
       subcomponent) of all subcomponents in depth-first order, with
       `depth` denoting each subcomponent's depth (starting with depth
       0 for `component` itself).
    """
    result = [(_current_depth, component) if depths else component]
    for k in range(len(component)):
        subcomponent = component.components[k]
        result += visited(subcomponent,
                          _current_depth=_current_depth + 1, depths=depths)
    return result


def by_layer_spec(component: justpy.HTMLBaseComponent,
                  layers: Layers) -> list[justpy.HTMLBaseComponent]:
    """
    List all subcomponents of `component` (including `component`
    itself) that match layer specification `layers`.

    Args:
       component: The root component (Layer.THIS).

       layers: A layer specification (an instance of Layers).

    Returns:
       The subset of all subcomponents, starting from `component`,
       that match `layer`.
    """
    # Small optimization: avoid recursive visit when layers is THIS
    if layers == Layer.THIS:
        return [component]
    if isinstance(layers, NodeIndex):
        # Visit all subcomponents recursively
        components = visited(component, depths=True)
        # All depths of nodes in components, removing duplicates
        all_depths = sorted(
            list(dict.fromkeys([depth for depth, _component in components])))
        # Filter depths of nodes that match layers.depth
        try:
            depths = [all_depths[layers.depth]]
            assert len(depths) == 1
            assert layers.depth < 0 or depths[0] == layers.depth
        except IndexError:
            # layers.depth is an integer, but out of range: no depths match
            depths = []
        except TypeError:
            if layers.depth is None:
                # layers.depth is None: all depths match
                depths = all_depths
            else:
                # Another kind of TypeError: propagate exception
                raise
        # All nodes at the given depths
        nodes = [node for depth, node in components if depth in depths]
        try:
            result = [nodes[layers.index]]
        except IndexError:
            # layers.index is an integer, but out of range: no nodes match
            result = []
        except TypeError:
            if layers.index is None:
                # layers.index is None: all nodes at the given depth match
                result = nodes
            else:
                # Another kind of TypeError: propagate exception
                raise
        return result
    if isinstance(layers, NodeSpec):
        # Visit all subcomponents recursively
        components = visited(component)
        # Filter those that match specification `layers`
        return filter_by_attribute(components,
                                   attribute=layers.attribute,
                                   value=layers.value,
                                   value_is_re=layers.regex)
    raise TypeError(f"Invalid layer specification: {layers}")


def replace(component: justpy.HTMLBaseComponent, to_be_replaced: justpy.HTMLBaseComponent,
            replacement: justpy.HTMLBaseComponent) -> bool:
    """
    Replace with `replacement the first subcomponent of
    `component` (at any depth) that is equal to `to_be_replaced`.

    Visits the subcomponent tree breadth first.

    Args:
       component: The root component.

       to_be_replaced: The subcomponent to be replaced.

       replacement: The replacement subcomponent.

    Returns:
       True if `to_be_replaced` was found and is not `component`
       itself. Otherwise, False.
    """
    # Cannot replace the root itself
    if component == to_be_replaced:
        return False
    for k in range(len(component)):
        subcomponent = component.components[k]
        if subcomponent == to_be_replaced:
            component.components[k] = replacement
            return True
    # Element to be replaced not found
    return False


def get_background(component: justpy.HTMLBaseComponent,
                   recheck=False) -> Optional[justpy.HTMLBaseComponent]:
    """
    If `component` has an attribute 'background' return
    it. Otherwise, if `recheck` is True or there is no such attribute,
    search for it among its attributes, and saves the result as
    attribute 'background'.

    Usually, `component` is an instance of justpy.Svg; its background
    is either a label attribute with value 'background', or the node
    identified by layer specification Layer.BACKGROUND.

    Args:
       component: The component where to look for a background.

       recheck: If True, ignore any attribute 'background' and
          searches for it anew.

    Returns:
       A background component, or None if no background component was
       found.
    """
    if not recheck:
        try:
            return component.background
        except AttributeError:
            pass
    backgrounds = component.by_layer_spec(
        NodeSpec(attribute="inkscape:label", value="background"))
    if not backgrounds:
        backgrounds = component.by_layer_spec(Layer.BACKGROUND)
    if len(backgrounds) == 0:
        logging.error("No background layer in: %s", str(component))
        backgrounds = [None]
    elif len(backgrounds) > 1:
        logging.warning("Multiple background layers in: %s", str(component))
    # Save it to attribute 'background'
    setattr(component, "background", backgrounds[0])
    return get_background(component)


@unique
class Replace(Enum):
    """Kind of replacement of classes in Tailwind components. See `add_classes` and `add_styles`
    for what each enum value represents."""

    REPLACE = 0
    EXTEND = 1
    RESET = 2
    REMOVE = 3


def recycle(values: list, target: list) -> list:
    """Returns a list with as many elements as `target` obtained by
    repeating `values` as many times as needed."""
    len_target, len_values = len(target), len(values)
    result = (len_target // len_values) * values + \
        values[:len_target % len_values]
    return result

# pylint: disable=too-many-statements  # This function is structurally complex, but I don't see much benefit from splitting it up
def add_classes(component: justpy.HTMLBaseComponent, *args: Union[str, list[str]],
                replacement: Replace = Replace.REPLACE, layers: Layers = Layer.THIS) -> list[str]:
    """
    Set Tailwind classes `args` in all `layers` of `components`. 

    This method extends HTMLBaseComponent's `set_class`, providing ways of
    adding/changing/removing classes in several subcomponents at once
    (argument `layers`), as well as of undoing a change of classes,
    and of handling classes with state modifiers (such as 'hover:').

    Returns the list of classes of all components before setting
    `args`. Thus, after add_classes(component, add_classes(component,
    tw_class, replacement=Replace.REPLACE), replacement=Replace.RESET)
    `component`'s classes are unchanged, as the list of previous
    classes is returned by the innermost call and restored by the
    outermost call.

    Similarly, add_classes(component, tw_class) followed by
    add_classes(component, tw_class, replacement=Replace.REMOVE) leaves
    `component`'s classes unchanged.

    Args:
       component: The root component (Layer.THIS).

       args: A collection of Tailwind class names, given as individual
          strings (possibly with multiple classes separated by spaces) or
          lists of strings.

       replacement:
          - If Replace.REPLACE (the default), relies on
            `HTMLBaseComponent.set_class` to add `args` to the
            components' classes, replacing any class of the same
            kind. If this fails for classes with a state modifier,
            looks for the most similar classes to the added ones, and
            forcefully replaces them. Most similar means that they are
            classes with the same state modifiers, and have at least 2
            characters in common (not counting the shared state
            modifiers).
          - If Replace.EXTEND, appends `args` to the components'
            classes regardless of the existing classes. This may
            introduce duplicates.
          - If Replace.RESET, removes any existing classes and sets
            the components' classes to `args`. If the number of
            classes in `args` differs from the number of components,
            recycles `args` to cover all cases. In particular, if
            there is only one class string in `args`, all components'
            classes are set to that class string.
          - If Replace.REMOVE, removes any `args` from the components'
            classes that include them. Classes are removed by exact
            matching; to remove a class based on its kind, add a class
            of that kind, and them remove it.

       layers: A layer specification (an instance of Layers).

    Returns:
       A list with as many elements as subcomponents of `component`
       were found in `layers`. Each element of the list is a string
       with all classes of each subcomponent (separated by spaces)
       before adding/removing the given classes.
    """

    def similar_replacement(subcomponent: justpy.HTMLBaseComponent,
                            class_spec: str, before: str):
        """
        Check if `subcomponent`'s classes include `class_spec`. If
        not, replace the most similar class with the same state
        modifier. If `class_spec` has no state modifiers, do
        nothing.

        Args:
           subcomponent: The component whose classes should include
              `class_spec`.

           class_spec: A single Tailwind class specification.

           before: All classes of `subcomponent` before adding
              `class_spec` to them, separated by spaces.
        """

        def longest_prefix(str1: str, str2: str) -> int:
            """Length of the longest prefix shared by `str1` and `str2`."""
            k, size = 0, min(len(str1), len(str2))
            while k < size and str1[k] == str2[k]:
                k += 1
            return k

        before = set(before.split())
        after = set(subcomponent.classes.split())
        # If `class_spec` was already a component class, or it is a component class now
        if class_spec in after:
            # Nothing to do
            return
        # State modifier of `class_spec`
        modifier, *new_specs = class_spec.split(":", maxsplit=1)
        # If `class_spec` has no state modifier
        if not new_specs:
            logging.warning(
                "Option %s: class %s without state modifier", replacement, class_spec)
            # Nothing to do
            return
        assert len(new_specs) == 1
        before = list(before)
        # Length and index of the longest common prefix between
        # `class_spec` and any class in `before`
        len_prefix, idx_prefix = 0, -1
        for k, before_spec in enumerate(before):
            # Current class spec
            # before_spec = before[k]
            # State modifier of `before_spec`
            before_modifier, *before_specs = before_spec.split(":", maxsplit=1)
            # If `before_spec` has no state modifier
            if before_modifier != modifier or not before_specs:
                # Skip
                continue
            # Length of the longest common prefix between `class_spec` and `before_spec`,
            # ignoring the common state modifier
            new_prefix = longest_prefix(new_specs[0], before_specs[0])
            if len_prefix < new_prefix:
                # New maximum
                len_prefix, idx_prefix = new_prefix, k
        # If the longest common prefix is at least 2 characters (after the state modifier)
        if len_prefix > 1 and idx_prefix >= 0:
            # Forcefully replace `before_spec` with `class_spec`
            before[idx_prefix] = class_spec
            # Reset classes in `subcomponent`
            subcomponent.classes = " ".join(before)
        # Otherwise, there is nothing to replace: just add `class_spec` to the class_content
        else:
            add_classes(subcomponent, class_spec, replacement=Replace.EXTEND)

    if not isinstance(replacement, Replace):
        raise ValueError(f"Invalid option replacement={replacement}")
    result = []
    # Turn all arguments into a list of strings
    replacements = [class_spec.split() if isinstance(class_spec, str) else class_spec
                    for class_spec in args]
    # Flatten list of lists
    replacements = [class_spec.strip()
                    for class_list in replacements for class_spec in class_list]
    # Find components
    components = by_layer_spec(component, layers)
    if replacement == Replace.RESET:
        if len(replacements) != len(components):
            logging.warning(
                "Only %d class replacements for %d components",
                len(replacements), len(components)
            )
            replacements = recycle(replacements, components)
        assert len(replacements) == len(components)
    for k_sub, subcomponent in enumerate(components):
        # subcomponent = components[k_sub]
        old_classes = subcomponent.classes
        result.append(old_classes)
        if replacement == Replace.RESET:
            subcomponent.classes = replacements[k_sub]
            continue
        if replacement == Replace.EXTEND:
            subcomponent.classes = subcomponent.classes.strip() + " " + " ".join(replacements)
            continue
        for class_spec in replacements:
            if replacement == Replace.REMOVE:
                subcomponent.remove_class(class_spec)
                continue
            assert replacement == Replace.REPLACE
            before = subcomponent.classes
            try:
                subcomponent.set_class(class_spec)
            # pylint: disable=broad-exception-caught # I don't know which exceptions Tailwind will raise, have to catche 'em all (cit.)
            except Exception as exc:
                # Propagate all exceptions except no Tailwind class exceptions
                if str(exc) != f"No Tailwind class named {class_spec}":
                    raise
                logging.warning("Unrecognized Tailwind class %s", class_spec)
            # Check whether the replacement was successful, and do it by other means if not
            similar_replacement(subcomponent, class_spec, before)
    return result


def add_styles(component: justpy.HTMLBaseComponent, *args: Union[str, list[str]],
               replacement: Replace = Replace.REPLACE, layers: Layers = Layer.THIS) -> list[str]:
    """
    Set CSS styles `args` in all `layers` of `components`. 

    Mirrors the behavior of `add_classes` but for CSS styles instead
    of Tailwind classes..

    Returns the list of styles of all components before setting
    `args`. Thus, after add_styles(component, add_styles(component,
    css_style, replacement=Replace.REPLACE), replacement=Replace.RESET)
    `component`'s styles are unchanged, as the list of previous styles
    is returned by the innermost call and restored by the outermost
    call.

    Similarly, add_styles(component, css_style) followed by
    add_styles(component, css_style, replacement=Replace.REMOVE) leaves
    `component`'s styles unchanged.

    If a style specification has multiple values for the same CSS
    class, only the last one will be used. CSS class names are matched
    after discarding any whitespaces; thus, a component's style string
    may be stripped of some whitespaces after calling this function,
    even if no replacement actually takes place.

    Args:
       component: The root component (Layer.THIS).

       args: A collection of CSS styles, given as individual strings
          (possibly with multiple classes separated by semicolons) or
          lists of strings.

       replacement:
          - If Replace.REPLACE (the default), adds `args` to the
            components' styles, replacing any style of the same
            class. A style's class is whatever comes before the colon,
            such as 'fill:' in the style 'fill:#ff0000'. 
          - If Replace.EXTEND, appends `args` to the components'
            styles regardless of the existing styles. This may
            introduce duplicates.
          - If Replace.RESET, removes any existing styles and sets the
            components' styles to `args`. If the number of styles in
            `args` differs from the number of components, recycles
            `args` to cover all cases. In particular, if there is only
            one style string in `args`, all components' styles are set
            to that style string.
          - If Replace.REMOVE, removes any `args` from the components'
            styles that include them. Styles are removed by exact
            matching; to remove a style based on its class, add any
            style of that class, and them remove it. 

       layers: A layer specification (an instance of Layers).

    Returns:
       A list with as many elements as subcomponents of `component`
       were found in `layers`. Each element of the list is a string
       with all styles of each subcomponent (separated by semicolons)
       before adding/removing the given styles.
    """
    if not isinstance(replacement, Replace):
        raise ValueError(f"Invalid option replacement={replacement}")
    result = []
    # Turn all arguments into a list of strings
    replacements = [style_spec.split(";") if isinstance(style_spec, str) else style_spec
                    for style_spec in args]
    # Flatten list of lists
    replacements = [style_spec.strip()
                    for style_list in replacements for style_spec in style_list]
    # Find components
    components = by_layer_spec(component, layers)
    if replacement == Replace.RESET:
        if len(replacements) != len(components):
            logging.warning(
                "Only %d style replacements for %d components",
                len(replacements), len(components)
            )
            replacements = recycle(replacements, components)
        assert len(replacements) == len(components)
    for k_sub, subcomponent in enumerate(components):
        # subcomponent = components[k_sub]
        old_styles = subcomponent.style
        result.append(old_styles)
        if replacement == Replace.RESET:
            subcomponent.style = replacements[k_sub]
            continue
        if replacement == Replace.EXTEND:
            subcomponent.style = subcomponent.style.strip(
                ";") + ";" + ";".join(replacements)
            continue
        # Turn subcomponent's style into dict: css_class -> style_value
        subcomp_styles = [style_spec.strip()
                          for style_spec in subcomponent.style.split(";")]
        subcomp_styles = [style_spec.split(
            ":", maxsplit=1) for style_spec in subcomp_styles]
        subcomp_styles = {css_class.strip(): values for css_class,
                          *values in subcomp_styles}
        for style_spec in replacements:
            style_class, *style_values = style_spec.split(":", maxsplit=1)
            style_class = style_class.strip()
            if replacement == Replace.REMOVE:
                if style_class in subcomp_styles and subcomp_styles[style_class] == style_values:
                    del subcomp_styles[style_class]
                continue
            assert replacement == Replace.REPLACE
            # If the same `style_class` exists, replace it; otherwise add a new one
            subcomp_styles[style_class] = style_values
        new_styles = [css_class + ("" if not values else (":" + values[0]))
                      for css_class, values in subcomp_styles.items()]
        subcomponent.style = ";".join(new_styles)
    return result


# pylint: disable=too-many-branches, too-many-statements, too-many-locals
# This function is structurally complex, but I don't see much benefit from splitting it up
def pack_text(bounding_rectangle: justpy.Rect, *args: str,          # type: ignore
              vertical: Optional[bool] = None,
              v_to_h_font_ratio: float = 0.5) -> list[justpy.Text]: # type: ignore
    """
    Render each string in `args` as an SVG text component, and
    positions the components so that they all fit
    `bounding_rectangle`.

    Args:
       bounding_rectangle: An SVG rectangle that delimits the area the
          text can occupy. It must be a component with attributes 'x'
          and 'y' (denoting the coordinates of the rectangle's
          top-left corner), as well as 'width' and 'height';
          alternatively, it should have a path specification (SVG
          attribute 'd') that can be used to reconstruct such
          coordinates.

       args: Strings of text to be rendered.

       vertical: If True, positions texts vertically, top-down. If
          False, positions texts horizontally, left-to-right. If None,
          chooses the optimal positioning among the two, preferring
          the one that allows larger text size.

       v_to_h_font_ratio: The average vertical (height) to horizontal
          (width) size ratio of a character in the chosen font. Thus,
          font_size * `v_to_h_font_ratio` is used as an approximation
          of a text character's width. Note that this function does
          not set the font itself, but assumes it has this average
          size characteristic.

    Returns:
       A list of SVG text components that render the strings in `args`. The
       components are already positioned within `bounding_rectangle`,
       and hence only need to be added to an SVG image to be displayed.
    """
    if not args:
        return []
    if vertical is None:
        # Try both positionings
        h_text = pack_text(bounding_rectangle, *args, vertical=False)
        v_text = pack_text(bounding_rectangle, *args, vertical=True)
        h_font, v_font = h_text[0].font_size, v_text[0].font_size
        # pylint: disable=no-else-return # I think it's clearer with an else here
        # Pick the one with a larger font size
        if h_font > v_font:
            return h_text
        else:
            return v_text

    def is_overlap(widths: list[float], padding: float, d_anchors: float) -> bool:
        """
        Check if any two consecutive lines of given `widths` overlap.

        Assuming lines are anchored around their midpoints, a line
        overlaps with the next one iff the sum of their half-widths
        plus some `padding` is greater than the distance between the
        anchor points.

        Note that, if len(`widths`) < 2, lines trivially do not overlap
        since there are no consecutive lines.

        Args:
           widths: An ordered list of line widths.

           padding: The minimum spacing to be added between two
              consecutive lines.

           d_anchors: The distance between two consecutive anchor
              points.

        Returns:
           True iff any two consecutive lines would overlap.
        """
        overlap = False
        for k in range(len(widths) - 1):
            first, second = widths[k], widths[k+1]
            if first/2 + padding + second/2 > d_anchors:
                overlap = True
        return overlap

    lines = args
    try:
        bb_x, bb_y = float(bounding_rectangle.x), float(bounding_rectangle.y)
        bb_width, bb_height = float(bounding_rectangle.width), float(
            bounding_rectangle.height)
    except AttributeError as exc:
        # Try to reconstruct bounding box from path specification
        pat1 = (r"\s*[m]\s+(?P<x>[-]?\d+([.]\d*)?)\s*[,]\s*(?P<y>[-]?\d+([.]\d*)?)" +
                r"\s+[v]\s+(?P<v>[-]?\d+([.]\d*)?)\s+[h]\s+(?P<h>[-]?\d+([.]\d*)?)")
        pat2 = (r"\s*[m]\s+(?P<x>[-]?\d+([.]\d*)?)\s*[,]\s*(?P<y>[-]?\d+([.]\d*)?)" +
                r"\s+[h]\s+(?P<h>[-]?\d+([.]\d*)?)\s+[v]\s+(?P<v>[-]?\d+([.]\d*)?)")
        m_pat = re.match(pat1, bounding_rectangle.d) or re.match(
            pat2, bounding_rectangle.d)
        # pylint: disable=invalid-name # It's just a bunch of coordinates
        if m_pat:
            x, y, v, h = (float(m_pat.group("x")), float(m_pat.group("y")),
                          float(m_pat.group("v")), float(m_pat.group("h")))
            if v < 0:
                y += v
                v = abs(x)
            if h < 0:
                x += h
                h = abs(h)
            bb_x, bb_y = x, y
            bb_width, bb_height = h, v
        else:
            raise ValueError(f"Invalid bounding box: {bounding_rectangle}") from exc
    # pylint: disable=invalid-name # It's just a bunch of coordinates
    # pack lines vertically
    if vertical:
        # x center of all lines: the horizontal middle of bounding_rectangle
        x_mids = len(lines)*[bb_x + bb_width/2]
        # y center of each line: split the vertical range of bounding_rectangle into equal parts
        d = bb_height / (len(lines) + 1)
        y_mids = [bb_y + k*d for k in range(1, len(lines) + 1)]
        # initially, the font size is as large as each vertical range segment
        base_size = d
    # pack lines horizontally
    else:
        # y center of all lines: the vertical middle of bounding_rectangle
        y_mids = len(lines)*[bb_y + bb_height/2]
        # x center of each line: split the horizontal range of bounding_rectangle into equal parts
        d = bb_width / (len(lines) + 1)
        x_mids = [bb_x + k*d for k in range(1, len(lines)+1)]
        # initially, the font size is as large as the whole vertical range (with some padding)
        base_size = 0.99 * bb_height
    # initially, no scaling of base_size
    scale_font = 1.0
    # stop when the font_size becomes nearly zero
    while scale_font > 0.01:
        # scale font size
        font_size = base_size * scale_font
        # rough estimate of a character's width from the font size (its height)
        dx = v_to_h_font_ratio * font_size
        # overall width of each line
        widths = [len(line)*dx for line in lines]
        # vertical packing
        if vertical:
            # vertical packing: the widest line is the overall text width
            width = max(widths)
            # there's no horizontal overlap with vertical packing
            overlap = False
        # horizontal packing
        else:
            # check if two lines overlap horizontally
            overlap = is_overlap(widths, dx, d)
            # there can only be overlapping with two or more lines
            assert not overlap or len(lines) > 1
            old_d, old_x_mids = d, x_mids
            # if they do, try moving the first and last x_mids to the
            # leftmost/rightmost position possible
            if overlap:
                w_first, w_last = widths[0], widths[-1]
                x_first = bb_x + w_first/2
                x_last = bb_x + bb_width - w_last/2
                # rearrange all intermediate x_mids uniformly
                d = (x_last - x_first) / (len(lines) - 1)
                x_mids = [x_first] + [x_first + k *
                                      d for k in range(1, len(lines)-1)] + [x_last]
                overlap = is_overlap(widths, dx, d)
                # if they still overlap, go back to the previous geometry
                if overlap:
                    d, x_mids = old_d, old_x_mids
            # horizontal packing: the sum of widths is the overall text width
            width = widths[0]/2 + (x_mids[-1] - x_mids[0]) + widths[-1]/2
        # if the text overlaps horizontally, or its overall width overflows bounding_rectangle
        if overlap or width > bb_width:
            # use a smaller font size
            scale_font -= 0.01
        else:
            # suitable font size found
            break
    # center horizontally and vertical around center
    style = f"font-size: {font_size}; text-anchor: middle; dominant-baseline: middle;"
    # JustPy components are defined dynamically, in a way that trips up the static analyzer
    # pylint: disable=not-callable
    texts = [justpy.Text(text=line, style=style, x=x_mid, y=y_mid, font_size=font_size)
             for line, x_mid, y_mid in zip(lines, x_mids, y_mids)]
    return texts



def before_event_handler(component, msg):
    """Replacement for JustPy's implementation of before_event_handler in class Input.
    The replacement uses set_model instead of an explicit assignment, which
    makes it possible to use overridden versions of set_model in HTMLBaseComponent.
    The replaced code is left below commented out just before its replacement."""
    # logging.debug(
    #     "%s %s %s %s %s", "before ", component.type, msg.event_type, msg.input_type, msg
    # )
    if msg.event_type not in ["input", "change", "select"]:
        return
    if msg.input_type == "checkbox":
        # The checked field is boolean
        component.checked = msg.checked
        # Replace:
        # if hasattr(component, "model"):
        #     component.model[0].data[component.model[1]] = msg.checked
        # with:
        component.set_model(msg.checked)
    elif msg.input_type == "radio":
        # If a radio field, all other radio buttons with same name need to have value changed
        # If form is specified, the scope is that form. If not, it is the whole page
        component.checked = True
        if component.form:
            justpy.Input.radio_button_set(component, component.form)
        else:
            justpy.Input.radio_button_set(component, msg.page)
        # Replace:
        # if hasattr(self, "model"):
        #     self.model[0].data[self.model[1]] = msg.value
        # with:
        component.set_model(msg.value)
        component.value = msg.value
    else:
        if msg.input_type == "number":
            try:
                msg.value = int(msg.value)
            except (TypeError, ValueError):
                msg.value = float(msg.value)
        # Replace:
        # if hasattr(component, "model"):
        #     # component.model[0].data[component.model[1]] = msg.value
        #     component.set_model(msg.value)
        # with:
        component.set_model(msg.value)
        component.value = msg.value


def set_color_scheme(component, kwargs: dict[str, Any]):
    """Apply color schemes to a component."""
    try:
        color_scheme = kwargs["color_scheme"]
        del kwargs["color_scheme"]
    except KeyError:
        color_scheme = []
    if isinstance(color_scheme, str):
        color_scheme = [color_scheme]
    elif not color_scheme:
        color_scheme = ["gray"]
    component.color_scheme = color_scheme


def get_color(component, num: int = 0):
    """Get a component's color scheme at index `num`."""
    try:
        return component.color_scheme[num]
    except IndexError:
        return component.color_scheme[0]


def wrap(base_object: object, overrides: type, model: View = None, init=True, **kwargs):
    """
    Create a wrapper around `base_object` by adding all members of
    class `overrides` that are not already in `base_object`. Also sets
    `model` attribute, and any other attribute/value pair in `kwargs`.

    The members that are added to `base_object` are:

       - All members of `overrides` that don't exist at all in
         `base_object` and that are not built-in.

       - All members that are redefined in `overrides` compared to
         `base_object` and that are not built-in.

    Here, a built-in method is simply a method whose name begins and
    ends with '__'.

    If `init` is True and `overrides` includes a method '_init_' (note
    the single underscores), calls `base_object._init_()`.

    Class `overrides` is thus a pseudo-subclass of `base_object`'s
    class, and `base_object` will be changed so that it conforms to
    `overrides`'s interface. This is useful to extend objects whose
    creation was not under our control (for example, because they were
    obtained by parsing).

    Args:

       base_object: An object that will be "wrapped" by adding other
          members.

       overrides: A class object whose members will be copied over to
          the wrapped object.

       model: A model object, added as `base_object.model`.

       init: If True, and `overrides` includes a method `_init_`,
          executes it before terminating.
    """
    members = base_object.__class__.__dict__
    wrapper_members = overrides.__dict__
    # New members: all those in the set difference, excluding built-ins
    new_members = {member for member in wrapper_members.keys() - members.keys()
                   if not re.match(r"^__.+__$", member)}
    # Overridden: all those in the set intersection that change, excluding built-ins
    overridden_members = {member for member in wrapper_members.keys() & members.keys()
                          if wrapper_members[member] != members[member]
                          and not re.match(r"^__.+__$", member)}
    for name in new_members | overridden_members:
        member = wrapper_members[name]
        # Callables are set as methods
        if isinstance(member, (MethodType, FunctionType)):
            member = MethodType(member, base_object)
        setattr(base_object, name, member)
    setattr(base_object, "model", model)
    for name, value in kwargs.items():
        setattr(base_object, name, value)
    # Call pseudo-initializer if it exists
    # pylint: disable=protected-access # We're dynamically wrapping objects, you can't worry about visibility...
    if init and "_init_" in base_object.__dict__.keys():
        base_object._init_()


async def click_target(component: justpy.HTMLBaseComponent, msg: dict):
    """
    Trigger a click event on `component.target`.

    It uses `run_javascript` function of the webpage at `msg.page`; it
    first looks up the target by its id, and then executes a click
    action.
    """
    try:
        target_id = component.target.id
    except AttributeError:
        logging.error("No target id in %s", str(component))
        return
    try:
        page = msg.page
    except AttributeError:
        logging.error("No webpage in %s", str(component))
        return
    await page.run_javascript(f'document.getElementById("{target_id}").click();')


def upload_file_content(msg: dict, callback: Callable[[str], None],
                        num: Optional[int] = None, decode: bool = True):
    """Process form upload of file defininig a key mapping."""
    files = None
    # Find element in form data that contains file information
    for files in msg.form_data:
        if files.type == "file":
            break
    if files is None:
        logging.error("No file data in %s", str(msg))
        return
    # pylint: disable=undefined-loop-variable # Checked by the conditional block
    # Enumerate all file content
    content = [blob.file_content for _, blob in enumerate(files.files)]
    # Decode file content
    if decode:
        content = [base64.b64decode(cnt) for cnt in content]
    # Call back on content
    if 0 <= num < len(content):
        callback(content[num])
    else:
        callback("")
