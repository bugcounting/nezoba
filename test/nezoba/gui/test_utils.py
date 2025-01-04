# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,too-few-public-methods,not-callable,too-many-locals
from typing import Union
from collections import Counter
from xml.dom import minidom
import justpy

from .context import gui_utils as utils



XML_FNAME = "gui/pic.svg"

def svg(as_list: bool=False) -> Union[justpy.HTMLBaseComponent,
                                      list[justpy.HTMLBaseComponent]]:
    """Returns HTML (SVG) component corresponding to the tree
    structure:

       Svg(lab='root', 0)
          |
        ----------------------------
        |                          |
     G(lab='group', 1)           Text(lab='root-text', 2)
        |
     -------------------------------------------------
     |                         |                     |
    Text(lab='in-group', 3)   Rect(lab='rect', 4)   Text(lab='in-group', 5)

    If `as_list` is True, returns a list of all nodes in a
    breadth-first visit.

    """
    svg_obj = justpy.Svg(lab="root", id=0)
    g = justpy.G(a=svg_obj, lab="group", id=1)
    justpy.Text(a=svg_obj, lab="root-text", id=2)
    justpy.Text(a=g, lab="in-group", id=3)
    justpy.Rect(a=g, lab="rect", id=4)
    justpy.Text(a=g, lab="in-group", id=5)
    if not as_list:
        return svg_obj
    flat = [svg_obj, *svg_obj.components, *svg_obj.components[0].components]
    return flat


def test_parse_html_file_robust():
    html = utils.parse_html_file_robust(XML_FNAME)
    assert len(html) == 2
    assert len(html.components[1][1]) == 3

def test_parse_html_file_robust_renames():
    old_a, new_a = "id", "foo"
    html = utils.parse_html_file_robust(XML_FNAME,
                                        renames={old_a:new_a})
    component = html.components[1].components[1]
    # Attribute old_a no longer exists
    assert getattr(component, old_a, None) is None
    # Attribute old_a has been renamed to new_a
    assert getattr(component, new_a)

def test_xml_rename_attribute():
    with open(XML_FNAME, "r", encoding='utf-8') as fp:
        xml = minidom.parseString(fp.read())
    component = xml.childNodes[1].childNodes[5]
    old_a, new_a = "id", "foo"
    value = component.getAttribute(old_a)
    assert value
    utils.xml_rename_attribute(xml, old_a, new_a)
    # Attribute old_a no longer exists
    assert component.getAttribute(old_a) == ""
    # Attribute old_a has been renamed to new_a
    assert component.getAttribute(new_a) == value


def test_filter_by_attribute():
    components = svg(as_list=True)
    assert components
    assert len(utils.filter_by_attribute(components, "foo", "rect", value_is_re=False)) == 0
    assert len(utils.filter_by_attribute(components, "lab", "foo", value_is_re=False)) == 0
    assert len(utils.filter_by_attribute(components, "lab", "rect", value_is_re=False)) == 1
    assert len(utils.filter_by_attribute(components, "lab", "in-group", value_is_re=False)) == 2
    assert len(utils.filter_by_attribute(components, "lab", r"root.*", value_is_re=True)) == 2
    assert len(utils.filter_by_attribute(components, "lab", r"r.{3}$", value_is_re=True)) == 2
    assert len(utils.filter_by_attribute(components, "foo", r"root[.]", value_is_re=True)) == 0
    assert len(utils.filter_by_attribute(components, "lab", r"X+", value_is_re=True)) == 0

def test_visited():
    component = svg()
    components = svg(as_list=True)
    visited = utils.visited(component)
    # Note that visited lists nodes in DFS, whereas components in BFS
    # Besides, they are different objects since we called svg() twice.
    assert len(visited) == len(components)
    # Every visited node is in the components list
    for node in visited:
        found = [comp for comp in components if comp.id == node.id]
        assert len(found) == 1
    # Every node in the components list is in visited
    for node in components:
        found = [comp for comp in visited if comp.id == node.id]
        assert len(found) == 1
    with_depths = utils.visited(component, depths=True)
    # Visit order is the same regardless of whether depths=True or False
    for k, visited_element in enumerate(visited):
        assert with_depths[k][1] == visited_element
    depths = [depth for depth, _component in with_depths]
    # Depths of svg's nodes, in depth-first order
    assert depths == [0, 1, 2, 2, 2, 1]

def test_by_layer_spec():
    component = svg()
    # Layer specifications of type utils.Layer
    layer_this = utils.by_layer_spec(component, utils.Layer.THIS)
    assert layer_this == [component]
    layer_all = utils.by_layer_spec(component, utils.Layer.ALL)
    assert set(layer_all) == set(utils.visited(component))
    layer_leaves = utils.by_layer_spec(component, utils.Layer.LEAVES)
    assert set(layer_leaves) == set(component.components[0])
    layer_background = utils.by_layer_spec(component, utils.Layer.BACKGROUND)
    assert set(layer_background) == set([component.components[0].components[0]])
    layer_foreground = utils.by_layer_spec(component, utils.Layer.FOREGROUND)
    assert set(layer_foreground) == set([component.components[0].components[2]])
    # Layer specifications of type utils.NodeIndex
    layer_middleground = utils.by_layer_spec(component, utils.NodeIndex(depth=-1, index=1))
    assert set(layer_middleground) == set([component.components[0].components[1]])
    layer_first = utils.by_layer_spec(component, utils.NodeIndex(depth=None, index=0))
    assert set(layer_first) == set([component])
    layer_right = utils.by_layer_spec(component, utils.NodeIndex(depth=1, index=1))
    assert set(layer_right) == set([component.components[1]])
    layer_middle = utils.by_layer_spec(component, utils.NodeIndex(depth=1, index=None))
    assert set(layer_middle) == set(component.components)
    # Layer specifications of type utils.NodeSpec
    lab_in_group = utils.by_layer_spec(component, utils.NodeSpec(attribute="lab",
                                                                 value="in-group",
                                                                 regex=False))
    assert set(lab_in_group) == set([component.components[0].components[0],
                                     component.components[0].components[2]])
    id_2 = utils.by_layer_spec(component, utils.NodeSpec(attribute="id", value="2", regex=False))
    assert set(id_2) == set([component.components[1]])
    id_digit = utils.by_layer_spec(component, utils.NodeSpec(attribute="id",
                                                             value=r"[0-9]",
                                                             regex=True))
    assert set(id_digit) == set(utils.visited(component))


def test_recycle():
    values, target = [1, 2, 3], range(3)
    assert utils.recycle(values, target) == values
    values, target = [1], range(3)
    assert utils.recycle(values, target) == [1, 1, 1]
    values, target = [1, 2], range(3)
    assert utils.recycle(values, target) == [1, 2, 1]
    values, target = [1, 2, 3, 4, 5], range(3)
    assert utils.recycle(values, target) == [1, 2, 3]


def test_add_classes():
    # Only testing with Layer.THIS, since `visited` handles layer specifications
    base_classes = "w-1/2 bg-red-700 hover:text-blue-700"
    component = justpy.Div(classes=base_classes)
    # Plain addition
    old_classes = utils.add_classes(component, "w-full")
    assert base_classes == old_classes[0]
    assert "w-full" in component.classes.split()
    assert "w-1/2" not in component.classes.split()
    # Undo
    utils.add_classes(component, old_classes, replacement=utils.Replace.RESET)
    assert set(component.classes.split()) == set(base_classes.split())
    # Unsupported class, no state modifier: no change, no error
    component = justpy.Div(classes=base_classes)
    fake = "fake-class"
    utils.add_classes(component, fake)
    assert set(component.classes.split()) == set(base_classes.split())
    # Unsupported class with state modifier: change most similar one
    mod = "hover:text-green-700"
    utils.add_classes(component, mod)
    assert mod in component.classes.split()
    assert "hover:text-blue-700" not in component.classes.split()
    # Removal of class after adding it
    component = justpy.Div(classes=base_classes)
    new = "mt-10"
    assert new not in component.classes.split()
    utils.add_classes(component, new)
    assert new in component.classes.split()
    utils.add_classes(component, new, replacement=utils.Replace.REMOVE)
    assert new not in component.classes.split()
    # Removal of a class that doesn't exist
    utils.add_classes(component, new, replacement=utils.Replace.REMOVE)
    assert new not in component.classes.split()
    # Add existing class
    repeated = "w-1/2"
    component = justpy.Div(classes=base_classes)
    old_classes = Counter(component.classes.split())
    # Normally: nothing happens
    utils.add_classes(component, repeated)
    assert Counter(component.classes.split()) == old_classes
    # With option EXTEND: the added class appears twice
    utils.add_classes(component, repeated, replacement=utils.Replace.EXTEND)
    for key, count in Counter(component.classes.split()).items():
        if key == repeated:
            assert count == old_classes[key] + 1
        else:
            assert count == old_classes[key]


def test_add_styles():
    # Only testing with Layer.THIS, since `visited` handles layer specifications
    base_styles = "width: 50%; background-color: #b91c1c; color: #1d4ed8"
    component = justpy.Div(style=base_styles)
    # Plain addition
    old_styles = utils.add_styles(component, "width: 100%")
    assert base_styles == old_styles[0]
    assert "width: 100%" in component.style.split(";")
    assert "width: 50%" not in component.style.split(";")
    # Undo
    utils.add_styles(component, old_styles, replacement=utils.Replace.RESET)
    assert set(component.style.split(";")) == set(base_styles.split(";"))
    # Removal of style after adding it
    component = justpy.Div(style=base_styles)
    new = "margin-top: 2.5rem"
    assert new not in component.style.split(";")
    utils.add_styles(component, new)
    assert new in component.style.split(";")
    utils.add_styles(component, new, replacement=utils.Replace.REMOVE)
    assert new not in component.style.split(";")
    # Removal of a style that doesn't exist
    utils.add_styles(component, new, replacement=utils.Replace.REMOVE)
    assert new not in component.style.split(";")
    # Add existing style
    repeated = "width: 50%"
    component = justpy.Div(style=base_styles)
    old_styles = Counter([_s.strip() for _s in component.style.split(";")])
    # Normally: nothing happens
    utils.add_styles(component, repeated)
    assert Counter(component.style.split(";")) == old_styles
    # With option EXTEND: the added style appears twice
    utils.add_styles(component, repeated, replacement=utils.Replace.EXTEND)
    for key, count in Counter(component.style.split(";")).items():
        if key == repeated:
            assert count == old_styles[key] + 1
        else:
            assert count == old_styles[key]


def test_pack_text():
    # Very wide rectangle, to test vertical stacking
    wide = justpy.Rect(x=0, y=0, width=100, height=20)
    tx_A = utils.pack_text(wide, "A", vertical=True)
    assert len(tx_A) == 1 and tx_A[0].font_size < 20
    tx_AB = utils.pack_text(wide, "A", "B", vertical=True)
    # The more elements, the smaller the font size
    assert len(tx_AB) == 2 and tx_AB[0].font_size == tx_AB[1].font_size < tx_A[0].font_size
    # Very tall rectangle, to test horizontal stacking
    tall = justpy.Rect(x=0, y=0, width=20, height=100)
    tx_A = utils.pack_text(tall, "A", vertical=False)
    assert len(tx_A) == 1 and tx_A[0].font_size < 100
    tx_AB = utils.pack_text(tall, "A", "B", vertical=False)
    # The more elements, the smaller the font size
    assert len(tx_AB) == 2 and tx_AB[0].font_size == tx_AB[1].font_size < tx_A[0].font_size
    # With wide rectangles, horizontal stacking is better (larger font)
    tx_wide_v = utils.pack_text(wide, "text", "more", vertical=True)
    tx_wide_h = utils.pack_text(wide, "text", "more", vertical=False)
    tx_wide = utils.pack_text(wide, "text", "more", vertical=None)
    assert tx_wide_v[0].font_size <= tx_wide_h[0].font_size == tx_wide[0].font_size
    # With tall rectangles, vertical stacking is better (larger font)
    tx_tall_v = utils.pack_text(tall, "text", "more", vertical=True)
    tx_tall_h = utils.pack_text(tall, "text", "more", vertical=False)
    tx_tall = utils.pack_text(tall, "text", "more", vertical=None)
    assert tx_tall_h[0].font_size <= tx_tall_v[0].font_size == tx_tall[0].font_size
    # A rectangle, and the same shape expressed with path specifications
    rect = justpy.Rect(x=0, y=0, width=200, height=100)
    path_1 = justpy.Path(d="m 0, 0 v 100 h 200 z")
    path_2 = justpy.Path(d="m 0, 0 h 200 v 100 z")
    tx_rect = utils.pack_text(rect, "txt1", "txt2")
    tx_p1 = utils.pack_text(path_1, "txt1", "txt2")
    tx_p2 = utils.pack_text(path_2, "txt1", "txt2")
    assert len(tx_rect) == len(tx_p1) == len(tx_p2)
    assert tx_rect[0].font_size == tx_p1[0].font_size == tx_p2[0].font_size
    assert tx_rect[1].font_size == tx_p1[1].font_size == tx_p2[1].font_size
    assert tx_rect[0].x == tx_p1[0].x == tx_p2[0].x
    assert tx_rect[0].y == tx_p1[0].y == tx_p2[0].y
    assert tx_rect[1].x == tx_p1[1].x == tx_p2[1].x
    assert tx_rect[1].y == tx_p1[1].y == tx_p2[1].y
