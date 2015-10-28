# -*- encoding: utf-8 -*-

from unittest import TestCase

from numpy import matrix

from pss.model import Node, RestConfiguration


def assertEqualMatrix(a, b):  # noqa
    return (a == b).all()


class NodeTestCase(TestCase):
    def setUp(self):
        self.node = Node()

    def test_has_position(self):
        self.assertEqual(self.node.position, [0, 0])

    def test_has_parent_none_as_default(self):
        self.assertIsNone(self.node.parent)

    def test_has_offset_zero_as_default(self):
        self.assertTrue(self.node.offset, [0, 0])

    def test_has_children_empty_list_as_default(self):
        self.assertEqual(0, len(self.node.children))

    def test_adding_children_increases_list_size(self):
        self.node.add_child(Node())
        self.assertEqual(1, len(self.node.children))


class RestConfigurationTestCase(TestCase):
    def setUp(self):
        self.rest_config = RestConfiguration()

    def add_nodes_to_positions_matrix(self):
        self.rest_config.add_node(Node(position=[1, 1]))
        self.rest_config.add_node(Node(position=[2, 2]))

    def add_nodes_to_offset_matrix(self):
        self.rest_config.add_node(Node(offset=[5, 5]))
        self.rest_config.add_node(Node(offset=[6, 6]))

    def test_has_node_matrix(self):
        self.assertEqual(0, len(self.rest_config.nodes))

    def test_adding_node_increases_node_list_size(self):
        self.rest_config.add_node(Node())
        self.assertEqual(1, len(self.rest_config.nodes))

    def test_can_get_matrix_of_node_positions(self):
        self.add_nodes_to_positions_matrix()
        pos_matrix = self.rest_config.get_position_matrix()
        self.assertTrue(assertEqualMatrix(pos_matrix, matrix("1 2; 1 2")))

    def test_can_get_elements_of_node_positions_matrix(self):
        self.add_nodes_to_positions_matrix()
        first_position = self.rest_config.get_position_matrix_at(0)
        self.assertTrue(assertEqualMatrix(first_position, matrix("1; 1")))

    def test_can_get_matrix_of_default_offsets(self):
        self.add_nodes_to_offset_matrix()
        offset_matrix = self.rest_config.get_offset_matrix()
        self.assertTrue(assertEqualMatrix(offset_matrix, matrix("5 6; 5 6")))

    def test_can_get_elements_of_node_offsets_matrix(self):
        self.add_nodes_to_offset_matrix()
        first_position = self.rest_config.get_offset_matrix_at(0)
        self.assertTrue(assertEqualMatrix(first_position, matrix("5; 5")))