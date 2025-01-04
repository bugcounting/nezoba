"""
This module provides the graphical user interface (GUI) for the Nez-Oba remapper.

The GUI is built using the JustPy framework, which was fairly heavily monkey-patched 
to work with GUI elements defined on an SVG image.

Functions:
    nezoba_gui(): Create the main page of the GUI.
    download_cfgs(): Set the route to the download link.
    keys(): Set the route to the keys/gamepad page.

Constants:
    app_options: An instance of the Options class containing configuration options for the app.
    app_state: An instance of the State class representing the current state of the app.
    keys_div: A JustPy Div component containing all keys.
"""

from typing import Optional
from importlib import resources as impresources
import justpy

from ..remapper.buttons import NEZOBA_BUTTONS
from ..remapper.namings import NS_KEYS, PC_KEYS
from .utils import instrument_component_class, override_event_handler
from .views import HeaderView, ControllersView, ComboView
from .model import Options, State
from .panes import Header, Controller, PressList, Info, Menu

from . import imgs
_image_dir = impresources.files(imgs) / ""
_favicon_path = impresources.files(imgs) /  "nez-oba-favicon.ico"

# GUI state object
app_options = Options(save_dir="nezoba-saves/",
                      image_dir=_image_dir,
                      max_messages=3)
app_state = State(app_options)

# Div with all keys
keys_div = justpy.Div(classes="w-full")


def nezoba_gui(mapping_fname: Optional[str] = None) -> justpy.WebPage:
    """Create the main page of the GUI. If a mapping file is provided, load it."""
    # Add utility methods to justpy components
    instrument_component_class()
    override_event_handler()
    state = app_state
    state.options.add_keys(NS_KEYS, "ns.inkscape.svg")
    state.options.add_keys(PC_KEYS, "pc.inkscape.svg")
    state.options.add_buttons(NEZOBA_BUTTONS, "nez-oba.inkscape.svg")
    if mapping_fname is not None:
        state.filename = mapping_fname
        state.load()
    # Web page
    # pylint: disable=invalid-name  # Using the same name as in JustPy's examples
    wp = justpy.WebPage(title="Nez-Oba Configuration App",
                        # display_url="NezOba-GUI",
                        favicon=str(_favicon_path)  # explicit conversion to string is needed
                        )
    # Keep a reference to main web page in state
    state.main_wp = wp
    # Header
    _header = Header(a=wp, model=HeaderView(state))
    # Content pane: everything except the header
    content = justpy.Div(a=wp,
                         classes="w-11/12 flex flex-col ml-7 mt-5 gap-y-7")
    ## Main pane: controller on the left, current key mapping on the right
    main = justpy.Div(a=content,
                      classes="w-full h-2/3 grid grid-cols-2 gap-x-10")
    ## Bottom pane
    bottom = justpy.Div(a=content,
                        classes="w-full h-1/3 grid grid-cols-2 gap-x-10")
    ### Left pane: controller
    left = justpy.Div(a=main,
                      classes="w-full h-full")
    ### Right pane: current key mapping
    right = justpy.Div(a=main,
                       classes="w-full")
    ### Controller component
    controller = Controller(a=left,
                            model=ControllersView(state))
    for buttons, image in state.options.buttons:
        controller.add_controller(buttons, image)
    ### Combo of current button
    press_pane = PressList(a=right, classes="w-full", cols=3,
                           model=ComboView(state), keys_div=keys_div)
    # keys_div.add_page(wp)
    press_pane.add_keys(state, here=True)
    ### Info pane: bottom left
    _info = Info(a=bottom, state=state)
    ### Menu pane: bottom right
    _menu = Menu(a=bottom, state=state)
    return wp


@justpy.SetRoute('/download_cfgs')
def download_cfgs():
    """Set the route to the download link."""
    # pylint: disable=invalid-name  # Using the same name as in JustPy's examples
    wp = justpy.WebPage()
    # Setting the `html` attribute makes the whole page simply text
    wp.html = app_state.get_download()
    return wp


@justpy.SetRoute('/keys')
def keys():
    """Set the route to the keys/gamepad page."""
    # pylint: disable=invalid-name  # Using the same name as in JustPy's examples
    wp = justpy.WebPage()
    wp += keys_div
    return wp
