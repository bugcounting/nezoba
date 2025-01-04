# Package `nezoba.gui`

Package `nezoba.gui` offers an implementation of a web-based GUI,
which supports visual inspection and editing of button-to-key-presses
mappings (defined in package `nezoba.remapper`).

The implementation uses the JustPy web framework. In the end, I had to
extend several components and features of the framework to fit my
needs. Most important, I modified the `justpy.Svg` component to be
able to use parts of an SVG image as clickable and dynamically
editable GUI buttons. Since I didn't want to distribute my own fork of
JustPy, I ended up doing some fairly heavy monkey patching, mostly in
module `utils` described below.


## Module `gui`

This module sets up the GUI as `justpy.WebPage`. The GUI's layout
includes several panes, each either a regular `Div` or a specialized
component defined in module `panes`.

The main wepage uses a [favicon](imgs/nez-oba-favicon.ico), which can
be generated from [this SVG](imgs/nez-oba-favicon.svg) using an
[online converter](https://favicon.io/favicon-converter/).


## Module `panes`

This module includes several specialized HTML components used by the
GUI:

- `Header` is the page's header banner, with the name and number of
  the current mapping.
  
- `Controller` is the page's left main pane, which displays a stylized
  image of the Nez-Oba controller board, whose buttons can be clicked
  to associate a key press with each of them.
  
- `PressList` is used in the page's right main pane, which displays
  all the presses associated with the currently selected button. Each
  press is displayed as an instance of `PressBox`, which shows all the
  information about the press (e.g., if it's turboed) and allows the
  user to edit it.
  
- `Info` is the page's left bottom pane, which shows a description and
  the platform used by the currently displayed mapping.
  
- `Menu` is the page's right bottom pane, with buttons to load/save
  the mappings, create a new mapping, switch between mappings, and so
  on. 

As noted elsewhere, sometimes this module's documentation refers to a
mapping (e.g., the currently selected mapping) as a *configuration*
(e.g., the current configuration). A configuration is often associated
with its index (*configuration number*) in the list of mappings in the
menu.


## Module `widgets`

This module includes other HTML components, which are used as building
blocks by some of the `panes`.

- `OnOffComponent` and `HideShowComponent` are SVG components that can
  be displayed or hidden dynamically.
  
- `InOutButton` is an SVG component that can display text on it (this
  is the *out* part), can be activated by clicking on it and
  deactivated by clicking again (this is the *in* part).
  
- `HoverHighlight` is a way of explicitly highlighting an SVG
  component's background when the mouse hover over it.
  
- `LabelContent` is a `div` component organized as vertically stacked
  subcomponents, each consisting of a label and some content.
  
- `ButtonRange` is a `div` component that displays a range of buttons.

- `SelectOptions` is a `select` component that reacts to changes in the
  model.
  
- `NamedLink` is an `a` link component that displays the URL in the
  model.
  
- `IconButton` is an HTML button component that displays text and/or
  icons on its face.
  

## Modules `model` and `views`

One of the main overhauls of JustPy is its support for model-based
dynamic components. In JustPy, a component's model is a way of
associating the component's state to the dynamic value of an attribute
(called the *model* of the component). In JustPy, the model[^1] is usually
of type string or integer. In the Nez-Oba GUI, this capability is
substantially extended to accommodate complex model types.

Class `State` encapsulates all the information that characterizes the
GUI's overall state: all mappings, the currently selected mapping, any
save files, and so on.

A component does not directly access the whole state. Instead, a
different `View` encapsulates the whole state and only leaks
information that is needed for a particular purpose. Precisely, `View`
has a single public member `value`, implemented as a property, which
can be read and, possibly, written (depending on whether the component
accessing that view is allowed to change the state).

JustPy's components are equipped with methods `get_model` and
`set_model` to respectively read and write the current model value
linked to that component. Module `model` redefines these methods in a
way that they work on views by default. 

Module `views` includes the actual subclasses of `View` that are used
by GUI components.


## Module `utils`

This module is where most of the dirty work of adapting JustPy's
functionality to our needs is done. Here, I will just describe the
main functions.

- `instrument_component_class` equips an existing JustPy component
  class with all of the extra functionality implemented in this
  project. In particular, it replaces the original `get_model` and
  `set_model` with their extensions defined in `model`.
  
- `filter_by_attribute` provides a way of searching through the
  subcomponents of an HTML component (usually, an SVG) for elements
  with certain attribute values. This is mainly used to display and
  dynamically modify the SVG of the Nez-Oba game controller board as a
  collection of clickable GUI buttons.
  
- Similarly, `by_layer_spec` navigates an SVG not by attribute values
  but according to its hierarchical tree structure. Other functions
  used this in combinatino with `replace`, which supports
  modifications of some parts of a tree structure.
  
- `add_styles` provides a more flexible way of adding CSS styles or
  Tailwind classes to an HTML component in JustPy. This function is
  needed because the version of JustPy that was available when I
  developed Nez-Oba only had support for older versions of Tailwind;
  hence, I had to manually implement some style changes that would
  have been possible with more recent version of Tailwind.
  
- `pack_text` resizes multiple lines of text so that they can be
  displayed to fit (more or less) nicely a bounding box.

- `wrap` provides another kind of monkey patching, one that is used
  directly in the definition of some panes. Precisely, it can turn an
  SVG component into an instance of `InOutButton` or `OnOffComponent`.


[^1]: Pet peeve: JustPy documentation's and terminology occasionally
    uses "model" to refer indifferently to the model *value* (the
    current value of the component's state) and to the *model type*
    (the range of values that the component's state spans). I tried to
    be more rigorous with the terminology, but no takesies-backsies
    :-).
