"""
This module defines various GUI components (panes) for the Nez-Oba GUI.

The components are built using the JustPy framework and include headers, controllers button layouts,
and key presses associated with each button.
"""

# JustPy components are defined dynamically, in a way that trips up the static analyzer
# pylint: disable=not-callable, no-member, inherit-non-class
# Allow passing protected state to create a derived component from the current one
# pylint: disable=protected-access

from __future__ import annotations
from typing import Optional
import logging
import justpy

from ..remapper.buttons import Buttons
from ..remapper.namings import NameScheme
from .utils import (
    parse_html_file_robust,
    NodeSpec,
    wrap,
    click_target,
    upload_file_content
)
from .model import State
from .widgets import (
    InOutButton,
    OnOffComponent,
    HideShowComponent,
    LabelContent,
    IconButton,
    HoverHighlight,
    SelectOptions,
    ButtonRange,
    NamedLink
)
from .views import (
    ControllerButtonView,
    ConfigurationBitView,
    InEditView,
    PressView,
    KeyNameView,
    KeyDescriptionView,
    KeyIsTurboView,
    KeyTurboView,
    KeyIsHoldView,
    KeyHoldView,
    TitleView,
    DescriptionView,
    PlatformView,
    CurrentHasChangedView,
    AnyHasChangedView,
    FilenameView,
    AlwaysView,
    ExistsCurrentView,
    SwapFromView,
    SwapToView,
    MaySwapView,
    ConfigurationsView,
    MessageView,
    UploadPickedView
)

ID = "svg:id"


# pylint: disable=too-few-public-methods # The constructor does all the work
class Header(justpy.H1):
    """A header banner for the GUI, formatted consistently with the rest of the GUI."""

    header_classes: str = "text-3xl font-sans font-bold m-1 p-3 w-full"

    def __init__(self, **kwargs):
        self.set_color_scheme(kwargs)
        self.header_classes += " " + f"text-white bg-{self.get_color()}-700"
        super().__init__(classes=self.header_classes,
                         **kwargs)


class Controller(justpy.Div):
    """A controller picture, taken from an SVG file, with clickable buttons 
    and a configuration number expressed in binary."""

    buttons: dict[Buttons, justpy.Svg]  # type: ignore

    def __init__(self, **kwargs):
        self.buttons = {}
        super().__init__(**kwargs)

    def add_controller(self, buttons: Buttons, filename: str):
        """
        Add a controller with a given set of buttons from a given SVG file.
        
        For each of the given buttons, this method scans the SVG
        filename for an element whose identifier is the same as the
        button's identifier. It then sets up the element so that it's
        clickable and wraps it in an InOutButton component. It also
        looks for configuration bits in the SVG file (elements with
        identifiers following the pattern 'cfg[0-9]+-(low|high)'), and
        wraps them in OnOffComponent components.
        """
        svg = parse_html_file_robust(
            filename, reset_size=True, renames={"id": ID})
        for button in buttons:
            components = svg.by_layer_spec(NodeSpec(attribute=ID,
                                                    value=str(button.identifier)))
            if not components:
                logging.error(
                    "Controller picture %s has no button %s", filename, button)
                continue
            if len(components) > 1:
                logging.warning(
                    "Controller picture %s has more than one of %s", filename, button)
            io_button = components[0]
            # Extend io_button with the same interface as InOutButton, and add a model to it
            wrap(io_button, InOutButton,
                 model=ControllerButtonView(self.model._state, button=button))
            io_button.on("click", lambda component, msg, target=self, button=button:
                         target.set_model(button))
            # Look for any configuration bits components
            bit_number, more = -1, True
            while more:
                bit_number += 1
                for position in ("low", "high"):
                    bit_components = svg.by_layer_spec(
                        NodeSpec(attribute=ID,
                                 value=f"cfg{bit_number}-{position}")
                    )
                    # Stop at highest found bit number
                    if not bit_components:
                        more = False
                        logging.info(
                            "Found %d bit components in %s", bit_number, filename)
                        if position == "high":
                            logging.warning(
                                "Bit %d has low but no high component", bit_number)
                        break
                    bit_component = bit_components[0]
                    # Extend bit_component with the same interface as OnOffComponent
                    # and add a model to it
                    wrap(bit_component, OnOffComponent,
                         model=ConfigurationBitView(self.model._state,
                                                    bit_number=bit_number,
                                                    high=position == "high"))
        self.buttons[buttons] = svg
        svg.show = False
        self.add(svg)

    def model_update(self):
        current_buttons = self.get_model()
        for buttons, svg in self.buttons.items():
            if current_buttons is not None and buttons == current_buttons:
                svg.show = True
            else:
                svg.show = False


class PressBox(LabelContent):
    """A box displaying information about a single key press."""

    in_edit: bool
    combo: PressList

    label_classes: str = "w-5 italic text-base mr-3 text-right ml-3.5 inline-block text-green-700"
    row_classes: str = "w-full flex flex-row mb-2 items-center"

    self_classes: str = "border-4 border-opacity-50 rounded-lg border-green-700"
    button_classes: str = "bg-white rounded-full inline-flex items-center ml-3 \
    text-green-700 hover:text-green-400"
    checkbox_classes: str = "appearence-none border-2 checked:border-transparent \
    mr-2 ml-2 checked:bg-green-100"
    content_classes: str = "w-full text-center"
    value_classes: str = "w-16 border-2 rounded font-mono text-gray-700 bg-gray-100 \
    text-right mr-0.5 focus:bg-green-100"

    title_not_in_edit: str = "Change this key press"
    title_in_edit: str = "Stop editing this key press"

    def __init__(self, **kwargs):
        self.set_color_scheme(kwargs)
        self.in_edit = False
        super().__init__(label_classes=self.label_classes,
                         row_classes=self.row_classes,
                         **kwargs)
        self.add_classes(self.self_classes)
        self._build()

    def _build(self):
        _press = self.get_model()
        # Pressed key
        key = justpy.Span(model=KeyNameView(self.model),
                          classes=self.content_classes + " " + "text-3xl -mb-2")
        self.add_row("Key", key)
        # Key description
        description = justpy.Span(model=KeyDescriptionView(self.model),
                                  classes=self.content_classes + " " + "text-sm mb-2")
        self.add_row("", description)
        # Turbo
        turbo = justpy.Span(classes=self.content_classes)
        _turbo_checkbox = justpy.Input(a=turbo, type="checkbox",
                                       model=KeyIsTurboView(self.model),
                                       classes=self.checkbox_classes,
                                       disabled=not self.in_edit)
        _turbo_value = justpy.InputChangeOnly(a=turbo,
                                              model=KeyTurboView(self.model),
                                              classes=self.value_classes,
                                              readonly=not self.in_edit)
        justpy.Span(a=turbo, text="Hz", classes="text-sm")
        self.add_row("Turbo", turbo)
        # Hold
        hold = justpy.Span(classes=self.content_classes)
        _hold_checkbox = justpy.Input(a=hold, type="checkbox",
                                      model=KeyIsHoldView(self.model),
                                      classes=self.checkbox_classes,
                                      disabled=not self.in_edit)
        _hold_value = justpy.InputChangeOnly(a=hold,
                                             model=KeyHoldView(self.model),
                                             classes=self.value_classes,
                                             readonly=not self.in_edit)
        justpy.Span(a=hold, text="ms", classes="text-sm")
        self.add_row("Hold", hold)
        # Button row
        icon_buttons = justpy.Span(classes=self.content_classes)
        self.add_row("Edit", icon_buttons)
        # Edit button
        edit = IconButton(a=icon_buttons, classes=self.button_classes,
                          content=[self.model._state.options.image_path("edit.svg")],
                          combo=self.combo,
                          click=lambda component, msg: self.model._state.toggle_edit(
                              self.model.press_idx
                          ), title=self.title_not_in_edit)
        if self.in_edit:
            self.add_classes("border-red-700")
            edit.add_classes("text-red-600")
            edit.add_classes("hover:text-red-400")
            edit.title = self.title_in_edit
        # Remove press button
        IconButton(a=icon_buttons, classes=self.button_classes,
                   content=[self.model._state.options.image_path(
                       "minus-circle.svg")],
                   combo=self.combo,
                   click=lambda component, msg: component.combo.model.remove(
                       self.model.press_idx),
                   title="Remove this key press")
        # Add press button
        IconButton(a=icon_buttons, classes=self.button_classes,
                   content=[self.model._state.options.image_path(
                       "plus-circle.svg")],
                   combo=self.combo,
                   click=lambda component, msg: component.combo.model.add_empty(
                       self.model.press_idx
                   ), title="Add a key press")

# pylint: disable=too-many-instance-attributes # You can't expect these HTML components to have a very elegant interface
class PressList(justpy.Div):
    """A wrappable list of key presses, each displayed in a PressBox component."""

    MAX_COLS: int = 4
    MAX_PRESSES: int = 3
    LIST_CLASSES: str = "content-center gap-x-3 gap-y-4"

    button_classes: str = "bg-white rounded-full"
    # in_edit: Optional[int]

    presses: list[justpy.HTMLBaseComponent]
    controllers: dict[NameScheme, justpy.HTMLBaseComponent]

    keys_div: justpy.Div

    def __init__(self, **kwargs):
        self.button_classes += " " + "text-green-700 hover:text-green-400"
        # self.in_edit = None
        self.presses = []
        self.controllers = {}
        self.top = None
        super().__init__(**kwargs)
        self.cols = min(type(self).MAX_COLS, self.cols)
        self.top = justpy.Div(a=self,
                              classes="w-full h-1/2 block flex flex-row flex-wrap" +
                              " " + type(self).LIST_CLASSES)
        self.bottom = justpy.Div(a=self, classes="h-1/2 mt-3")
        self.pressboxes = None

    def add_keys(self, state: State, here: bool = True):
        """
        Link all gamepad keys in state.options.keys to `self`, so
        that they can be clicked to modify any presses.
        
        If `here` is True, the keys are added to the bottom of the
        page, otherwise they are added to a separate div, which is
        kept hidden until a press is being edited.
        """
        for scheme, (keys, filename) in state.options.keys.items():
            assert keys is not None, f"Missing keys for scheme {scheme}"
            svg = parse_html_file_robust(
                filename, reset_size=True, renames={"id": ID})
            svg.add_classes("w-7/12 block")
            for key in keys.unnamed():
                components = svg.by_layer_spec(
                    NodeSpec(attribute=ID, value=str(key.key)))
                if not components:
                    logging.warning(
                        "Controller picture %s has no key %s", filename, key)
                    continue
                if len(components) > 1:
                    logging.warning(
                        "Controller picture %s has more than one of %s", filename, key)
                i_key = components[0]
                wrap(i_key, HoverHighlight)
                # Event handler `keypress` needs to be async because
                # it should call async method update() on the main
                # webpage after updating the model to reflect the new
                # press.  Here's why this is needed:
                #
                #   1. Normally, "when a JustPy event handler finishes
                #      running and returns None, JustPy calls the
                #      update method of the WebPage instance in which
                #      the event occurred."
                #
                #   2. Handler `self.press` does return None. However,
                #      the webpage where the click occurs may not be
                #      the app's main web page, where the key press is
                #      shown in a PressBox instance.
                #
                #   3. Thus, we save a reference to the main web page
                #      in the state, and explicitly call `update()` on
                #      it after the "regular" event handler.  Since
                #      `update()` is async, the wrapper handler must
                #      also be async.
                #
                #   As usual, we use default arguments to ensure that
                #   we have the values of `key.key` in each loop
                #   iteration.
                # pylint: disable=unused-argument,invalid-name # This callback needs a specific signature
                async def keypress(component, msg, key=key.key, wp=self.model._state.main_wp):
                    self.press(key)
                    await wp.update()
                # pylint: enable=unused-argument,invalid-name
                i_key.on("click", keypress)
            wrap(svg, HideShowComponent,
                 model=InEditView(self.model._state,
                                  scheme=scheme))
            self.controllers[scheme] = svg
            if here:
                self.bottom += svg
            try:
                self.keys_div += svg
            except AttributeError:
                logging.warning("Keys div not found")

    def model_update(self):
        # Remove previous pressess
        self.top.delete_components()
        model_value = self.get_model()
        # Presses
        presses = model_value.presses
        if presses is None:
            return
        if len(presses) == 0:
            pressboxes = [IconButton(classes=self.button_classes,
                                     content=[self.model._state.options.image_path(
                                         "plus-circle.svg"
                                     )],
                                     combo=self,
                                     click=lambda component, msg:
                                     component.combo.model.add_empty(0),
                                     title="Add a key press")]
        else:
            pressboxes = [PressBox(model=PressView(self.model._state, press_idx=idx),
                                   combo=self,
                                   classes="w-1/4 basis-1/4 flex-none",
                                   in_edit=idx == model_value.in_edit)
                          for idx in range(len(presses))]
        self.presses = pressboxes
        for box in pressboxes:
            self.top += box
            # box.add_page(self.model._state.wp)
        self.pressboxes = pressboxes
        # Only show controllers when a press is being edited
        if model_value.in_edit is None:
            self.bottom.set_class("invisible")
            return
        self.bottom.set_class("visible")

    def press(self, key: str):
        """React to a pressed key on a gamepad by editing the currently selected button press."""
        model_value = self.get_model()
        # Ignore presses if not in edit
        if model_value.in_edit is None:
            return
        scheme = model_value.scheme
        keys = self.model._state.options.keys[scheme].keys
        assert keys is not None, f"Missing keys for scheme {scheme}"
        self.model.set_key(idx=model_value.in_edit, key=keys[key])


class Info(LabelContent):
    """Information about the currently displayed mapping: title, description, and platform."""

    wp: Optional[justpy.WebPage]

    label_classes: str = "w-28 block font-bold text-xl mr-2 text-green-700"
    row_classes: str = "flex flex-row mb-2"
    title_classes: str = ("w-1/4 border-2 rounded font-semibold "
                          "text-gray-700 focus:bg-green-100 bg-gray-100")
    description_classes: str = ("w-4/5 border-2 rounded font-serif "
                                "text-gray-700 focus:bg-green-100 bg-gray-100")
    description_rows: int = 5
    select_classes: str = "w-1/5 text-gray-700 focus:bg-green-100 bg-gray-100"
    option_classes: str = "rounded border-2 bg-white"

    def __init__(self, **kwargs):
        super().__init__(label_classes=self.label_classes,
                         row_classes=self.row_classes,
                         classes="m-0 w-full",
                         **kwargs)
        self._build()

    def _build(self):
        self.add_row("Title",
                     justpy.InputChangeOnly(classes=self.title_classes,
                                            model=TitleView(self.state)))
        self.add_row("Description",
                     justpy.Textarea(rows=self.description_rows,
                                     classes=self.description_classes,
                                     model=DescriptionView(self.state)))
        self.add_row("Platform",
                     SelectOptions(classes=self.select_classes,
                                   model=PlatformView(self.state)))


class Menu(justpy.Div):
    """A menu with buttons to undo and save changes, create new configurations, 
    and swap between them."""

    row_classes: str = "flex flex-row mb-6"
    section_classes: str = "flex flex-row gap-x-1 items-center"
    label_classes: str = "w-14 block font-bold text-xl ml-1 mr-0.5"
    button_classes: str = ("w-8 text-white text-sm rounded-lg px-1 py-1 mr-1" +
                           " " + "text-center inline-flex items-center")
    active_classes: str = "hover:bg-green-400"
    fname_classes: str = "w-1/4 border-2 rounded text-gray-700 ml-2 mr-1 bg-gray-100 text-right"
    cfg_classes: str = "font-mono text-white rounded-full text-sm px-1 py-1 text-center \
    ml-1 mr-1 w-7"
    select_classes: str = "w-1/4 text-gray-700 font-mono text-sm text-center mr-2"
    message_rows: int = 3

    def __init__(self, **kwargs):
        self.label_classes += " " + "text-green-700"
        self.button_classes += " " + "bg-green-700 hover:bg-green-700"
        self.fname_classes += " " + "focus:bg-green-100"
        self.select_classes += " " + "focus:bg-green-100 bg-gray-100"
        super().__init__(**kwargs)
        self._build()

    def _build(self):
        self._build_save_undo()
        self._build_new_swap()
        self._build_goto()
        self._build_messages()

    def _build_save_undo(self):
        save_undo = justpy.Div(a=self, classes=self.row_classes)
        undo = justpy.Div(a=save_undo, classes="w-1/3" +
                          " " + self.section_classes)
        justpy.Span(a=undo, classes=self.label_classes, text="Undo")
        IconButton(a=undo, classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("undo.svg")],
                   title="Undo changes to current configuration",
                   model=CurrentHasChangedView(self.state),
                   click=lambda this, msg: self.state.undo(current=True))
        IconButton(a=undo, classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("undo-all.svg")],
                   title="Undo changes to all configurations",
                   model=AnyHasChangedView(self.state),
                   click=lambda this, msg: self.state.undo(current=False))
        save = justpy.Div(a=save_undo, classes="w-1/3" +
                          " " + self.section_classes)
        justpy.Span(a=save, classes=self.label_classes, text="Save")
        IconButton(a=save, classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("save.svg")],
                   title="Save changes to current configuration",
                   model=CurrentHasChangedView(self.state),
                   click=lambda this, msg: self.state.save(current=True))
        IconButton(a=save, classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("save-all.svg")],
                   title="Save changes to all configurations",
                   model=AnyHasChangedView(self.state),
                   click=lambda this, msg: self.state.save(current=False))
        filename = justpy.Div(
            a=save_undo, classes="w-2/3" + " " + self.section_classes)
        justpy.Span(a=filename, classes="w-20" + " " +
                    self.label_classes, text="Filename")
        justpy.InputChangeOnly(a=filename, classes=self.fname_classes,
                               model=FilenameView(self.state))
        # Download link, associated to download icon button
        download_link = NamedLink(a=filename, href="/download_cfgs",
                                  model=FilenameView(self.state))
        IconButton(a=download_link,
                   classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("download.svg")],
                   title="Download all saved configurations",
                   model=AlwaysView(self.state))
        # Choose file to upload
        upload_form = justpy.Form(enctype='multipart/form-data',
                                  submit=(lambda component, msg,
                                            # pylint: disable=unnecessary-lambda # JustPy is particular about callback objects
                                            callback=lambda c: self.state.set_upload(c),
                                            n=0:
                                                upload_file_content(msg, callback=callback, num=n)))
        # The input file chooser is hidden, clicked indirectly by the
        # icon button Note that it must use class "hidden"
        # (equivalent to style "display: none"), which includes the
        # element in the page, but does not use any space for it. In
        # contrast `show=False` would not include the element (as if
        # it didn't exist), and class "invisible" would use the space
        # without actually showing anything.
        file_picker = justpy.Input(a=upload_form, type='file', multiple=False, accept='text/yaml',
                                   classes="hidden",
                                   click=(lambda component, msg,
                                          target=self.state: target.pick_upload(True)))
        IconButton(a=filename,
                   classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("folder.svg")],
                   title="Pick a file for upload",
                   # Clicking on this icon button triggers a click on `target`
                   click=click_target,
                   target=file_picker,
                   model=AlwaysView(self.state))
        IconButton(a=upload_form, classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("upload.svg")],
                   title="Upload new configurations (replacing current ones)", type="submit",
                   model=UploadPickedView(self.state))
        # Add upload as last button
        filename += upload_form

    def _build_goto(self):
        goto = justpy.Div(a=self, classes="mt-7" + " " + self.row_classes)
        justpy.Span(a=goto, classes=self.label_classes, text="Go to")
        ButtonRange(a=goto, classes="w-7/8",
                    button_classes=self.cfg_classes,
                    active_classes="bg-green-400",
                    inactive_classes="bg-green-700 hover:bg-green-400",
                    model=ConfigurationsView(self.state))

    def _build_new_swap(self):
        new_swap = justpy.Div(a=self, classes=self.row_classes)
        new = justpy.Div(a=new_swap, classes="w-1/3" +
                         " " + self.section_classes)
        justpy.Span(a=new, classes=self.label_classes, text="New")
        IconButton(a=new, classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("plus.svg")],
                   title="Create a new blank configuration",
                   click=lambda this, msg: self.state.new_configuration(),
                   model=AlwaysView(self.state))
        IconButton(a=new, classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("duplicate.svg")],
                   title="Create a copy of the current configuration",
                   click=lambda this, msg: self.state.copy_current_configuration(),
                   model=ExistsCurrentView(self.state))
        IconButton(a=new, classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("minus.svg")],
                   title="Delete the current configuration",
                   click=lambda this, msg: self.state.delete_current_configuration(),
                   model=ExistsCurrentView(self.state))
        swap = justpy.Div(a=new_swap, classes="w-1/3" +
                          " " + self.section_classes)
        justpy.Span(a=swap, classes=self.label_classes, text="Swap")
        SelectOptions(a=swap, classes=self.select_classes,
                      model=SwapFromView(self.state))
        IconButton(a=swap, classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path("swap.svg")],
                   title="Swap configurations",
                   click=lambda this, msg: self.state.swap(),
                   model=MaySwapView(self.state))
        SelectOptions(a=swap, classes=self.select_classes,
                      model=SwapToView(self.state))
        other_tab = justpy.Div(a=new_swap,
                               classes="w-2/3" + " " + self.section_classes + " " + "pl-8")
        # Link to page with available keys, associated to icon
        keys_link = justpy.Link(a=other_tab, href="/keys", target="_blank")
        IconButton(a=keys_link,
                   classes=self.button_classes, active_classes=self.active_classes,
                   content=[self.state.options.image_path(
                       "arrow-top-right.svg")],
                   title="Open keys page or tab",
                   model=InEditView(self.state, scheme=None))

    def _build_messages(self):
        messages = justpy.Div(a=self, classes=self.row_classes)
        justpy.Span(a=messages, classes=self.label_classes, text="Info")
        justpy.Textarea(a=messages,
                        rows=self.message_rows,
                        classes="border-0 rounded font-serif text-sm text-gray-700 w-full",
                        readonly=True,
                        model=MessageView(self.state))
