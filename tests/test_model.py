# -*- encoding: utf-8 -*-
from os.path import join, dirname, abspath
from unittest import TestCase

from numpy import array

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

    def test_when_building_tree_make_sure_parents_are_not_added_as_children(self):
        nodes = self.build_nodes()
        edge_list = self.build_edge_list(nodes)
        self.sgi.nodes = nodes
        self.sgi.edge_list = edge_list
        self.sgi.root_node = nodes[2]

        self.sgi.build_up_tree()
        self.assertEqual(len(self.sgi.nodes[0].children), 1)  # Node [1, 1] should have one children ([2, 0])
        self.assertEqual(len(self.sgi.nodes[1].children), 0)  # Node [2, 0] should not have any children
        self.assertEqual(len(self.sgi.nodes[2].children), 2)  # Node [4, 5] should have two children ([1, 1] & [5, 3])
        self.assertEqual(len(self.sgi.nodes[3].children), 0)  # Node [5, 3] should not have any children
        self.assertEqual(self.sgi.nodes[0].parent, self.sgi.nodes[2])  # Parent of [1, 1] should be [4, 5]
        self.assertEqual(self.sgi.nodes[1].parent, self.sgi.nodes[0])  # Parent of [2, 0] should be [1, 1]
        self.assertIsNone(self.sgi.nodes[2].parent)  # Node [4, 5] is root and therefore has no parent
        self.assertEqual(self.sgi.nodes[3].parent, self.sgi.nodes[2])  # Parent of [5, 3] should be [4, 5]

    def build_nodes(self):
        node_list = list()
        node_list.append(Node(position=array([1, 1], dtype=int)))
        node_list.append(Node(position=array([2, 0], dtype=int)))
        node_list.append(Node(position=array([4, 5], dtype=int)))
        node_list.append(Node(position=array([5, 3], dtype=int)))
        return node_list

    def build_edge_list(self, nodes):
        edge_list = list()
        edge_list.append([nodes[0], nodes[1]])
        edge_list.append([nodes[1], nodes[0]])

        edge_list.append([nodes[0], nodes[2]])
        edge_list.append([nodes[2], nodes[0]])

        edge_list.append([nodes[2], nodes[3]])
        edge_list.append([nodes[3], nodes[2]])

        return edge_list


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
