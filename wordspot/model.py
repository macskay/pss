# -*- encoding: utf-8 -*-

class Node(object):
    def __init__(self, parent=None, position=(0, 0), offset=0):
        """
        :param parent: parent-node - None for root (default: None)
        :param position: 2d coordinate vector of the image plane (default: 0, 0)
        :param offset: relative offset to parent-node, which is set by the rest configuration (default: 0)
        """
        self.offset = offset
        self.children = list()
        self.parent = parent
        self.position = position

    def add_child(self, child):
        self.children.append(child)


class RestConfiguration(object):
    def __init__(self):
        self.nodes = list()

    pass
