# -*- encoding: utf-8 -*-

from numpy import matrix


class Node(object):
    def __init__(self, parent=None, position=None, offset=None):
        """
        :param parent: parent-node - None for root (default: None)
        :param position: 2d coordinate vector of the image plane (default: [0, 0])
        :param offset: relative offset to parent-node, which is set by the rest configuration (default: [0, 0)
        """
        self.children = list()
        self.parent = parent
        self.position = [0, 0] if position is None else position
        self.offset = [0, 0] if offset is None else offset

    def add_child(self, child):
        self.children.append(child)


class RestConfiguration(object):
    def __init__(self):
        self.nodes = list()

    def add_node(self, node):
        self.nodes.append(node)

    def get_position_matrix(self):
        positions = list()
        for node in self.nodes:
            positions.append(node.position)
        return matrix(positions).transpose()

    def get_position_matrix_at(self, index):
        pos_matrix = self.get_position_matrix()
        return pos_matrix[:, [index]]

    def get_offset_matrix(self):
        offsets = list()
        for node in self.nodes:
            offsets.append(node.offset)
        return matrix(offsets).transpose()

    def get_offset_matrix_at(self, index):
        offset_matrix = self.get_offset_matrix()
        return offset_matrix[:, [index]]
