# -*- encoding: utf-8 -*-

from unittest import TestCase
from model import Node, RestConfiguration


class NodeTestCase(TestCase):
    def setUp(self):
        self.node = Node()

    def test_has_position(self):
        self.assertEqual(self.node.position, (0, 0))

    def test_has_parent_none_as_default(self):
        self.assertIsNone(self.node.parent)

    def test_has_offset_zero_as_default(self):
        self.assertEqual(0, self.node.offset)

    def test_has_children_empty_list_as_default(self):
        self.assertEqual(0, len(self.node.children))

    def test_adding_children_increases_list_size(self):
        self.node.add_child(Node())
        self.assertEqual(1, len(self.node.children))


class RestConfigurationTestCase(TestCase):
    def setUp(self):
        self.rest_config = RestConfiguration()

    def test_has_node_matrix(self):
        self.assertEqual(0, len(self.rest_config.nodes))

    def test_can_get_matrix_of_node_positions(self):
        pass






