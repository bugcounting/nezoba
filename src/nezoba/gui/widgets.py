"""
This module defines various GUI widgets used by the Nez-Oba GUI.

The widgets defined in this module should be more abstract than the
panes defined in module `panes`, and are usually monkey-patched onto
JustPy components to extend their functionality.

The widgets include components that can be displayed/hidden, SVG
elements used as buttons with a dynamically changing face, and buttons
with SVG icons on their face.
"""


# Classes in this module are monkey-patched onto JustPy components,
# which trips up the static analyzer
# pylint: disable=no-member, attribute-defined-outside-init, unused-argument

from typing import Union
import logging
import justpy

from .utils import parse_html_file_robust, NodeSpec, Layer, Replace, pack_text
from .model import View


class OnOffComponent:
    """A component that reacts to model changes by toggling between being visible and invisible.
    An invisible component remains in the rendered page but it is not visible."""

    model: View

    def model_update(self): # pylint: disable=missing-function-docstring # See JustPy's documentation
        if self.get_model():
            self.add_classes("invisible")
        else:
            self.add_classes("visible")

    def react(self, data): # pylint: disable=missing-function-docstring # See JustPy's documentation
        self.model_update()


class HideShowComponent:
    """A component that reacts to model changes by toggling between showing and hiding.
    A hidden component (show == False) is removed from the page, and not rendered at all."""

    model: View

    def model_update(self): # pylint: disable=missing-function-docstring # See JustPy's documentation
        if self.get_model():
            self.show = True
        else:
            self.show = False

    def react(self, data): # pylint: disable=missing-function-docstring # See JustPy's documentation
        self.model_update()


class InOutButton:
    """
    An SVG element that acts as an input/output button.

    The component reacts to changes in the `input` and `output`
    component of its model view.

    - If `input` is True, fill the component as "active"; otherwise,
      fill it as "inactive" (as defined by colors `FILL_ACTIVE` and
      `FILL_INACTIVE`).
    - Display all text elements in the `output` list, redered by
      function `utils.pack_text`, on the element's face.

    The output only covers the bounding box part of the element. This
    is determined by looking for a sub-component with attribute
    'svg:id' starting with 'bb'. If none is found, the whole component
    is used as bounding box.
    """

    model: View

    FILL_ACTIVE: str = "fill:#4ADE80"    # text-green-400
    FILL_INACTIVE: str = "fill:#FFF6D5"

    def _init_(self):
        setattr(self, "output", [])
        setattr(self, "bounding_box", None)
        # Show clicking finger
        self.add_classes("cursor-pointer", layers=Layer.ALL)
        # Base background
        background = self.get_background()
        background.add_styles(self.FILL_INACTIVE)
        # Look for a bounding box subcomponent
        bbs = self.by_layer_spec(
            NodeSpec(attribute="svg:id", value=r"^bb", regex=True))
        if not bbs:
            logging.warning("No bounding box for: %s", str(self))
            bounding_box = background
        else:
            bounding_box = bbs[0]
        # Set bounding box component to invisible, provided it's not the component itself
        bounding_box.add_classes("invisible")
        # Save bounding box as attribute
        self.bounding_box = bounding_box

    def model_update(self): # pylint: disable=missing-function-docstring # See JustPy's documentation
        # Update input
        background = self.get_background()
        model_value = self.get_model()
        if background is not None:
            if model_value.input:
                background.add_styles(self.FILL_ACTIVE)
            else:
                background.add_styles(self.FILL_INACTIVE)
        # Update output
        for old_output in self.output:  # pylint: disable=access-member-before-definition # output is defined in the JustPy component
            # Remove previous output subcomponents
            self.remove_component(old_output)
        # Add new output subcomponent to this
        output = model_value.output
        self.output = pack_text(self.bounding_box, *output)
        self.add(*self.output)

    def react(self, data): # pylint: disable=missing-function-docstring # See JustPy's documentation
        self.model_update()


# pylint: disable=too-few-public-methods # The constructor does all the work
class HoverHighlight:
    """A component that is highlighted in color when the mouse hovers over it.
    This component is needed because the version of JustPy used in this project
    does not properly support the ':hover' CSS pseudo-class for SVG components."""

    def _init_(self):
        self.add_classes("text-green-400", layers=Layer.BACKGROUND)
        # Adding 'and None' makes the whole lambda evaluate to None.
        # This is necessary because JustPy updates a page after an event handler
        # only if the event handler returns None. Since 'add_styles' does not return
        # None, the change in style would not be visible until the next page refresh
        # triggered by any other event.
        self.on("mouseenter",
                lambda component, msg:
                component.get_background().add_styles("fill:currentColor") and None)
        self.on("mouseleave",
                lambda component, msg:
                component.get_background().add_styles(
                    "fill:currentColor", replacement=Replace.REMOVE)
                and None)

    def model_update(self): # pylint: disable=missing-function-docstring # See JustPy's documentation
        pass


class LabelContent(justpy.Div):
    """A Div component organized as vertically stacked rows, 
    each consisting of a content component with a text label."""

    label_classes: str
    row_classes: str

    def __init__(self, **kwargs):
        self.label_classes = ""
        self.row_classes = ""
        super().__init__(**kwargs)

    def add_row(self, label_text: str, content: justpy.HTMLBaseComponent):
        """Add a row with given `content` labeled with text `label_text`."""
        row = justpy.Div(a=self, classes=self.row_classes)
        label = justpy.Label(classes=self.label_classes, text=label_text)
        row += label
        row += content

    # Div's update would use the model value as text, so we override it
    def model_update(self): # pylint: disable=missing-function-docstring # See JustPy's documentation
        pass


class ButtonRange(justpy.Div):
    """A sequence of buttons ranging over the list `configurations` 
    in the component's model value."""

    button_classes: str
    active_classes: str
    inactive_classes: str
    buttons: list[justpy.Button]  # type: ignore

    def __init__(self, **kwargs):
        self.button_classes = ""
        self.active_classes = ""
        self.inactive_classes = ""
        self.buttons = []
        super().__init__(**kwargs)
        self.set_classes("flex flex-row flex-wrap")

    def model_update(self): # pylint: disable=missing-function-docstring # See JustPy's documentation
        model_value = self.get_model()
        for old_button in self.buttons:
            self.remove_component(old_button)
        self.buttons = []
        for cfg in model_value.configurations:
            classes = self.button_classes
            if cfg in model_value.active:
                classes += " " + self.active_classes
            else:
                classes += " " + self.inactive_classes
            # pylint: disable=not-callable  # Deal with dynamically-defined JustPy classes
            button = justpy.Button(a=self, classes=classes, text=f"{cfg}",
                                   num=cfg,
                                   click=lambda component, msg, num=cfg, target=self:
                                   target.set_model(num))
            self.buttons += [button]


class SelectOptions(justpy.Select):
    """A Select component that reacts to changes in the model 
    that redefine the selectable options."""

    option_classes: str

    def __init__(self, **kwargs):
        self.option_classes = ""
        super().__init__(**kwargs)

    def model_update(self): # pylint: disable=missing-function-docstring # See JustPy's documentation
        model_value = self.get_model()
        self.value = model_value.current
        # Remove previous options
        self.delete_components()
        # pylint: disable=not-callable  # Deal with dynamically-defined JustPy classes
        # Create current options
        for option in model_value.choices:
            self.add(justpy.Option(value=option, text=option,
                                   classes=self.option_classes))


class NamedLink(justpy.A):
    """A link whose URL is taken from the model value."""

    def model_update(self):
        model_value = self.get_model()
        self.download = model_value


# pylint: disable=inherit-non-class
class IconButton(justpy.Button):
    """
    A clickable button component displaying an SVG icon on its face.
    
    Attribute `content` expresses the button's content as
    follows. Each element of `content` is an HTMLBaseComponent, a
    single string, or a list of strings.

    - An HTMLBaseComponent is simply added to the button.
    - A single string should be a path to an HTML/SVG file, which is
      parsed and then added to the button.
    - A list of strings are rows of text, which are added to the
      button stacked vertically (if `stack_vertically` is True) or
      horizontally.
    """

    content: list[Union[justpy.HTMLBaseComponent, str, list[str]]]
    stack_vertically: bool
    active_classes: str = ""
    base_classes: str

    def __init__(self, **kwargs):
        self.content = []
        self.stack_vertically = True
        super().__init__(**kwargs)
        self._build()

    def _build(self):
        icons = {}
        classes = "flex " + \
            ("flex-col" if self.stack_vertically else "flex-row")
        for element in self.content:
            try:
                if element in icons:
                    # Repeated element
                    icon = icons[element]
                elif isinstance(element, justpy.HTMLBaseComponent):
                    # SVG/HTML component: use as is
                    icon = element
                else:
                    # Filename: try to parse it
                    icon = parse_html_file_robust(element)
                # Add it to cache
                icons[element] = icon
                # Add it to button
                self.add(icon)
            # `parse_html_file_robust` may also raise exceptions of other types
            except ValueError:
                # Otherwise, element should be either a single text row or a sequence of text rows
                if isinstance(element, str):
                    element = []
                text_div = justpy.Div(classes=classes)
                _rows = [justpy.Div(text=row, a=text_div) for row in element]
                self.add(text_div)

    def model_update(self): # pylint: disable=missing-function-docstring # See JustPy's documentation
        model_value = self.get_model()
        if model_value is None:
            return
        if model_value:
            self.add_classes(self.active_classes)
        else:
            self.add_classes(self.active_classes, replacement=Replace.REMOVE)

    def react(self, data): # pylint: disable=missing-function-docstring # See JustPy's documentation
        self.model_update()
