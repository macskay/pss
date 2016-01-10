# -*- encoding: utf-8 -*-
from os.path import join, dirname, abspath
from unittest import TestCase

from numpy import array

from pss.model import Node, Query, HEIGHT, WIDTH
from pss.svg import SvgHandler

FILE_LOCATION = dirname(abspath(__file__))


def assert_equal_matrix(a, b):
    """
    Checks if two matrices are the same. For that all vectors must be equal.
    :param a: Matrix A
    :param b: Matrix B
    :return: True if equal, False otherwise
    """
    return (a == b).all()


class SymbolGroupImageTestCase(TestCase):
    def setUp(self):
        valid_path = join(FILE_LOCATION, "..", "resources", "test_query.svg")
        self.svg_handler = SvgHandler(valid_path)
        self.sgi = Query(self.svg_handler.svg_symbol_groups[0], "Name")

    def test_when_creating_symbol_group_image_bounding_box_is_not_none(self):
        self.assertIsNotNone(self.sgi.bounding_box)

    def test_get_width_returns_width_of_image(self):
        self.assertEqual(self.sgi.get_image_width(), self.sgi.bounding_box.width() * WIDTH)

    def test_get_height_returns_height_of_image(self):
        self.assertEqual(self.sgi.get_image_height(), self.sgi.bounding_box.height() * HEIGHT)

    def test_when_building_tree_make_sure_parents_are_not_added_as_children(self):
        nodes = self.build_nodes()
        self.sgi.nodes = nodes
        self.sgi.root_node = nodes[5]

        self.sgi.build_up_tree()

        # Children Assertion
        self.assertEqual(len(self.sgi.nodes[0].children), 0)
        self.assertEqual(len(self.sgi.nodes[1].children), 2)
        self.assertEqual(len(self.sgi.nodes[2].children), 1)
        self.assertEqual(len(self.sgi.nodes[3].children), 0)
        self.assertEqual(len(self.sgi.nodes[4].children), 1)
        self.assertEqual(len(self.sgi.nodes[5].children), 2)
        self.assertEqual(len(self.sgi.nodes[6].children), 2)
        self.assertEqual(len(self.sgi.nodes[7].children), 0)
        self.assertEqual(len(self.sgi.nodes[8].children), 1)
        self.assertEqual(len(self.sgi.nodes[9].children), 0)

        # Parent Assertion
        self.assertEqual(self.sgi.nodes[0].parent, nodes[1])
        self.assertEqual(self.sgi.nodes[1].parent, nodes[4])
        self.assertEqual(self.sgi.nodes[2].parent, nodes[1])
        self.assertEqual(self.sgi.nodes[3].parent, nodes[2])
        self.assertEqual(self.sgi.nodes[4].parent, nodes[5])
        self.assertIsNone(self.sgi.nodes[5].parent)
        self.assertEqual(self.sgi.nodes[6].parent, nodes[5])
        self.assertEqual(self.sgi.nodes[7].parent, nodes[6])
        self.assertEqual(self.sgi.nodes[8].parent, nodes[6])
        self.assertEqual(self.sgi.nodes[9].parent, nodes[8])

    def build_nodes(self):
        node_list = list()
        node_list.append(Node(position=array([1, 2], dtype=int)))  # 4
        node_list.append(Node(position=array([2, 2], dtype=int)))  # 3
        node_list.append(Node(position=array([2, 4], dtype=int)))  # 5
        node_list.append(Node(position=array([3, 5], dtype=int)))  # 6
        node_list.append(Node(position=array([3, 1], dtype=int)))  # 2
        node_list.append(Node(position=array([4, 2], dtype=int)))  # R
        node_list.append(Node(position=array([5, 3], dtype=int)))  # 1
        node_list.append(Node(position=array([6, 2], dtype=int)))  # 8
        node_list.append(Node(position=array([7, 4], dtype=int)))  # 7
        node_list.append(Node(position=array([6, 5], dtype=int)))  # 9

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
        self.node = Node(position=[3, 10])

    def test_has_position(self):
        self.assertEqual(self.node.position, [3, 10])

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
        self.assertEqual("Node-Position: [3, 10]", self.node.__str__())

    def test_when_calculating_offset_to_parent_set_offset(self):
        self.node.set_parent(Node(position=[5, 7]))
        self.node.calculate_offset()
        self.assertEqual(self.node.offset, [-2, 3])
