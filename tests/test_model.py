# -*- encoding: utf-8 -*-
from os.path import join, dirname, abspath
from unittest import TestCase

from pss.model import Node, SymbolGroup, HEIGHT, WIDTH
from pss.svg import SvgHandler

FILE_LOCATION = dirname(abspath(__file__))


def assertEqualMatrix(a, b):  # noqa
    return (a == b).all()


class SymbolGroupImageTestCase(TestCase):
    def setUp(self):
        valid_path = join(FILE_LOCATION, "..", "resources", "test_query.svg")
        self.svg_handler = SvgHandler(valid_path)
        self.sgi = SymbolGroup(self.svg_handler.svg_symbol_groups[0], "Name")

    def test_when_creating_symbol_group_image_bounding_box_is_not_none(self):
        self.assertIsNotNone(self.sgi.bounding_box)

    def test_get_width_returns_width_of_image(self):
        self.assertEqual(self.sgi.get_image_width(), self.sgi.bounding_box.width() * WIDTH)

    def test_get_height_returns_height_of_image(self):
        self.assertEqual(self.sgi.get_image_height(), self.sgi.bounding_box.height() * HEIGHT)


class NodeTestCase(TestCase):
    def setUp(self):
        self.node = Node(position=[0, 10])

    def test_has_position(self):
        self.assertEqual(self.node.position, [0, 10])

    def test_has_parent_none_as_default(self):
        self.assertIsNone(self.node.parent)

    def test_has_offset_zero_as_default(self):
        self.assertTrue(self.node.offset, [0, 0])

    def test_has_children_empty_list_as_default(self):
        self.assertEqual(0, len(self.node.children))

    def test_adding_children_increases_list_size(self):
        self.node.add_child(Node())
        self.assertEqual(1, len(self.node.children))

    def test_when_printing_node_return_position_string(self):
        self.assertEqual("Node-Position: [0, 10]", self.node.__str__())
