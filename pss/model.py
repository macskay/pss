# -*- encoding: utf-8 -*-
from copy import deepcopy
from functools import reduce  # pylint:disable=redefined-builtin
from PyQt4 import QtGui
from numpy import zeros, array, delete, insert, c_, mean
from skimage.feature import corner_harris
from skimage.feature import corner_peaks
from skimage.morphology import skeletonize
from math import sqrt

from logging import getLogger

sg_logger = getLogger("SymbolGroup")

WIDTH = 15
HEIGHT = 15
COLORED = 127
COLOR_BG = "Black"
COLOR_FG = "White"
DISTANCE = 4


class SymbolGroup(object):
    """
    This class represents one symbol group as defined in the given svg.
    It uses these svg-paths to create a QImage using QPainterPaths.
    This "original_image" is converted to a Numpy-array to get skeletonized
    by skimage. The array holding the skeltonized version of the QImage
    is then used to find joints and corners, also using skimage.
    These vectors are used to create the first nodes representing
    the initial symbol group paths given by ther svg.
    """

    def __init__(self, paths, name):  # pylint:disable=super-on-old-class
        """
        :param paths: The group of symbols to represent as QImage
        :param name: This is the name of the symbol group as set in the svg
        """
        sg_logger.info("Setup SymbolGroupImage with name [%s]", name)
        self.paths = paths
        self.name = name

        self.bounding_box = self.create_bounding_box()

        self.original_image = self.create_original_image()
        self.original_array = self.convert_qimage_to_ndarray()

        self.skeleton_array = self.create_skeleton(name)
        self.enlarged_skeleton = self.enlarge_skeleton()
        self.corner_nodes = self.find_corners_and_junctions()
        self.true_list = self.create_true_list()
        self.center_of_mass = self.calculate_center_of_mass()

        self.open_list = list()
        self.closed_list = list()

        self.edge_list = list()

        self.nodes = self.add_remaining_nodes()
        self.root_node = self.find_root_node()

        self.build_up_tree()

    def create_bounding_box(self):
        """
        Creates the Bounding Box given all the paths given to the constructor
        :return: Bounding Box that surrounds all paths of this symbol group
        """
        sg_logger.info("Setting up Bounding Box")
        return reduce(lambda xs, x: xs | x.boundingRect(),
                      self.paths[1:],
                      self.paths[0].boundingRect())

    def create_original_image(self):
        """
        Creates a QImage and sets its background to COLOR_BG. After that the QImage is tried to get filled with the paths
        :return: QImage created out of QPainterPaths, which were given to the constructor
        """
        image = QtGui.QImage(self.get_image_width(), self.get_image_height(), QtGui.QImage.Format_RGB32)
        self.set_background(COLOR_BG, image)
        image = self.try_to_fill_image_with_paths(image)
        return image

    def get_image_width(self):
        """
        Getter for the QImage width
        :return: Width of the Bounding-Box
        """
        return self.bounding_box.width()*WIDTH

    def get_image_height(self):
        """
        Getter for the QImage height
        :return: Height of the Bounding-Box
        """
        return self.bounding_box.height()*HEIGHT

    @staticmethod
    def set_background(color, image):
        """
        Sets the background color of the QImage
        """
        sg_logger.info("Setting Background to [%s]", color)
        image.fill(QtGui.QColor(color))

    def try_to_fill_image_with_paths(self, image):
        """
        Tries filling up the QImage with QPainterPaths
        :param image: The empty QImage
        :return: The QImage, filled with QPainterPaths in a binary representation
        """
        qpainter = QtGui.QPainter(image)
        try:
            return self.fill_image_with_paths(qpainter, image)
        finally:
            qpainter.end()

    def fill_image_with_paths(self, qpainter, image):
        """
        Fills the QImage with the QPainterPaths
        :param qpainter: QPainter to let Qt draw into the QImage
        :param image: The empty QImage
        :return: The QImage, filled with QPainterPaths in a binary representation

        """
        sg_logger.info("Brushing Paths onto QImage")
        qpainter.setBrush(QtGui.QColor(COLOR_FG))
        qpainter.setPen(QtGui.QColor(COLOR_FG))
        qpainter.scale(HEIGHT, WIDTH)
        qpainter.translate(-self.bounding_box.topLeft())
        for path in self.paths:
            qpainter.drawPath(path)
        return image

    def convert_qimage_to_ndarray(self):  # pragma: no cover
        """
        Converts a given QImage into a Numpy-Array
        :return: Boolean Numpy-Array representing the QImage. "True" = Foreground, "False" = Background
        """
        sg_logger.info("Converting QImage to NumPy-Array")
        m, n = self.get_image_height(), self.get_image_width()
        array = zeros((m, n))
        for y in range(int(m)):
            for x in range(int(n)):
                c = QtGui.qGray(self.original_image.pixel(x, y))
                array[y, x] = True if c >= COLORED else False
        return array

    def create_skeleton(self, name):
        """
        Skeletonzes a given Numpy-Array to a 1px width. See skimage-documentation for skeletonize
        :param name: Name of the QImage (For Logging purposes)
        :return: Skeletonized Numpy-Array
        """
        sg_logger.info("Skeletonizing QImage with name [%s]", name)
        return skeletonize(self.original_array)

    def enlarge_skeleton(self):
        """
        Adds two columns and two rows at the top, bottom, left and right to ensure the neighbor-search doesn't hit
        a border.
        :return: Numpy-Array, which is a column and row larger on each side.
        """
        rows = len(self.skeleton_array)
        cols = len(self.skeleton_array[0])
        enlarged_array = self.skeleton_array
        enlarged_array = c_[zeros(rows, dtype=bool), enlarged_array, zeros(rows, dtype=bool)]
        enlarged_array = insert(enlarged_array, 0, zeros(cols + 2, dtype=bool), 0)
        enlarged_array = insert(enlarged_array, rows, zeros(cols + 2, dtype=bool), 0)
        return enlarged_array

    def find_corners_and_junctions(self):
        """
        Finds all junctions and corners of the enlarged_skeleton, which represents a QImage
        :return: List of all junctions and corners found within the enlarged_skeleton Numpy-Array
        """
        sg_logger.info("Detecting Nodes of skeletonized QImage with name [%s]\n", self.name)
        skeleton_corners = corner_peaks(corner_harris(self.enlarged_skeleton), min_distance=2)
        nodes = list()
        for corner in skeleton_corners:
            nodes.append(Node(position=corner))
        return nodes

    def create_true_list(self):
        """
        Creates a List, which holds all indices of a "True"-appearance within the enlarged_skeleton.
        Only Non-Corner-/Non-Junction-Nodes are added to this list.
        :return: A list of 2D-Numpy-Arrays. The 2D-Numpy-Arrays represent the appearance of a "True" within the enlarged_skeleton.
        """
        true_list = list()
        for i, x in enumerate(self.enlarged_skeleton):
            for j, y in enumerate(x):
                if y and Node(position=array([i, j])) not in self.corner_nodes:
                    true_list.append(array([i, j]))
        return true_list

    def add_remaining_nodes(self):
        """
        This calls sub-functions to add the remaining nodes between junctions and corners.
        :return: The list of all nodes representing the QImage
        """
        nodes = list()
        nodes.extend(self.add_nodes_greedily())
        nodes.extend(self.corner_nodes)
        return nodes

    def add_nodes_greedily(self):
        """
        Adds nodes between junctions and corners greedily.
        All corners and junctions are given as starting points.
        For each of these a neighborhood of DISTANCE is checked. If "True"'s within the enlarged_skeleton
        are found closer than DISTANCE away they get deleted from the true_list. If they are exactly DISTANCE away
        they are added to additional_nodes. This is done for every new "good" neighbor found until a corner_node is hit.
        If there is more than one "good" neighbors for a given node they get saved into a rest_list.
        This leads to a path getting finished before switching to a new path. The node creation therefor first checks
        one path until it hits a corner_node. When this happens the algorithm switches to the next path (starting point
        in rest_list).
        :return: The list of all nodes representing the QImage
        """
        additional_nodes = list()

        for corner in self.corner_nodes:
            self.open_list.append(corner)
            rest_list = list()

            while self.still_neighbors_to_check(rest_list):
                if self.has_node_more_than_one_neighbor():
                    rest_list = self.create_copy_of_open_list_and_clear()
                    continue

                node = self.open_list.pop(0) if len(self.open_list) > 0 else rest_list.pop(0)
                self.closed_list.append(node)

                good_neighbors, bad_neighbors = self.decide_good_or_bad_neighbor(node)
                self.add_neighbor_relation_to_edge_list(good_neighbors, node)
                self.delete_bad_neighbors_from_true_list(bad_neighbors)
                additional_nodes.extend(good_neighbors)

        return additional_nodes

    def still_neighbors_to_check(self, rest_list):
        """
        :param rest_list: List of other Neighbors found when started to populate from corner_node
        :return: True nodes still in open_list or rest_list
        """
        return len(self.open_list) > 0 or len(rest_list) > 0

    def has_node_more_than_one_neighbor(self):
        """
        Checks if a node has more than one neighbor
        :return: True if more than one neighbor
        """
        return len(self.open_list) > 1

    def create_copy_of_open_list_and_clear(self):
        """
        Creates a copy of the open_list and saves it inside a rest_list. After that the open_list is cleared
        :return: A list of all neighbors
        """
        rest_list = deepcopy(self.open_list)
        self.open_list.clear()
        return rest_list

    def decide_good_or_bad_neighbor(self, node):
        """
        Decides if a neighbor is seen as good neighbor, meaning a new node should be build there or as a bad neighbor,
        meaning it should get deleted, since it is too close to existing nodes.
        :param node: Current node which neighbors should get checked
        :return: List of "Good neighbors" and list of "Bad neighbors"
        """
        good_neighbors = list()
        bad_neighbors = list()
        for i, true_position in enumerate(self.true_list):
            if self.is_neighbor_too_close(node, true_position):
                bad_neighbors.append(i)
            elif self.is_neighbor_the_right_distance_away(node, true_position):
                new_node = Node(position=true_position)
                if self.is_node_completely_unknown(new_node):  # pragma: no cover
                    self.open_list.append(new_node)
                    good_neighbors.append(new_node)
        return good_neighbors, bad_neighbors

    def add_neighbor_relation_to_edge_list(self, good_neighbors, node):
        """
        This function creates a new list item consisting of the node currently observed and one of its good
        neighbors. The relation is added in both directions, meaning [node, neighbor] and [neighbor, node]
        :param good_neighbors: Good neighbors for a given node
        :param node: The node tp add the [node, neighbor] relation to the edge_list
        :return:
        """
        for neighbor in good_neighbors:
            self.edge_list.append([node, neighbor])
            self.edge_list.append([neighbor, node])

    @staticmethod
    def is_neighbor_too_close(node, true_position):
        """
        Checks if a neighbor is too close to its node (Too close meaning less than DISTANCE away)
        :param node: Current node
        :param true_position: Position of potential neighbor
        :return: True if distance is too close
        """
        return node.position[0] + DISTANCE > true_position[0] > node.position[0] - DISTANCE \
                            and node.position[1] + DISTANCE > true_position[1] > node.position[1] - DISTANCE

    @staticmethod
    def is_neighbor_the_right_distance_away(node, true_position):
        """
        Checks if a neighbor is the right distance to be seen as a "Good neighbor"
        :param node: Current node
        :param true_position: Position of potential neighbor
        :return: True if distance is just right to be seen as a "Good neighbor"
        """
        return (node.position[0] + DISTANCE == true_position[0] and node.position[1] + DISTANCE >= true_position[1] >= node.position[1] - DISTANCE) \
                      or (node.position[0] - DISTANCE == true_position[0] and node.position[1] + DISTANCE >= true_position[1] >= node.position[1] - DISTANCE) \
                      or (node.position[1] + DISTANCE == true_position[1] and node.position[0] + DISTANCE >= true_position[0] >= node.position[0] - DISTANCE) \
                      or (node.position[1] - DISTANCE == true_position[1] and node.position[0] + DISTANCE >= true_position[0] >= node.position[0] - DISTANCE)

    def is_node_completely_unknown(self, new_node):
        """
        Checks if a given node is completely unknown, meaning it is neither in the closed_list nor in the corner_nodes
        :param new_node: Node to be checked
        :return: True if completely unknown (not in self.closed_list and not in self.corner_nodes)
        """
        return new_node not in self.closed_list and new_node not in self.corner_nodes

    def delete_bad_neighbors_from_true_list(self, bad_neighbors):
        """
        Deletes bad neighbors from the true_list, so they don't get checked ever again. They can't get "Good neighbors"
        any longer.
        :param bad_neighbors: List of "Bad neighbors", which should get deleted out of the true_list
        """
        for item in reversed(bad_neighbors):
            self.true_list = delete(self.true_list, item, 0)

    def calculate_center_of_mass(self):
        """
        Calculates the center of mass by using the arithmetic mean of all node positions
        :return: The arithmetic mean of all node positions
        """
        return Node(position=mean(self.true_list, axis=1, dtype=int))

    def find_root_node(self):
        """
        Finds the closes node to the center of mass
        :return: The node closed to the center od mass. This becomes the root node for the upcoming parent-child tree
        """
        closest_node = None
        closest_distance = float("inf")
        for node in self.nodes:
            current_distance = self.get_euclidean_distance_to_center_of_mass(node)
            if current_distance < closest_distance:
                closest_node = node
                closest_distance = current_distance
        return closest_node

    def get_euclidean_distance_to_center_of_mass(self, node):
        """
        Finds the euclidean distance of a node to the center of mass
        :param node: node to calculate the euclidean distance to center of mass for
        :return: euclidean distance from the given node to the center of mass
        """
        return sqrt(self.get_euclidean_addend(node, 0) + self.get_euclidean_addend(node, 1))

    def get_euclidean_addend(self, node, i):
        """
        Calculates one addend of the euclidean distance
        :param node: node to calculate the euclidean distance to center of mass for
        :param i: Index of the axis/dimension
        :return: One calculated addend of form (node.pos.item(i) - center_of_mass.pos.item(i))^2
        """
        return pow((node.position.item(i) - self.center_of_mass.position.item(i)), 2)

    def build_up_tree(self):
        """
        Builds up the Parent-Child relationship starting from the root-Node. It is build up successively. Every Node
        that is added as a child of a parent node does not get its parent as child.
        ex.: Node1 -> Node2. If this is a valid parent-child relationship the edge [Node1, Node2] is used,
        edge [Node2, Node1] is not valid anymore and therefore added to the closed list. This makes sure Node1 does not
        become a child of Node1 as well. See Unittest for usage.
        """
        closed_edge_list = list()
        open_nodes = list()
        open_nodes.append(self.root_node)

        while len(open_nodes) > 0:
            current_node = open_nodes.pop()
            for edge in self.edge_list:
                if current_node == edge[0] and edge not in closed_edge_list:
                    child = edge[1]
                    current_node.add_child(child)
                    child.set_parent(current_node)
                    closed_edge_list.append(edge)
                    closed_edge_list.append(list(reversed(edge)))

                    open_nodes.append(child)


class Node(object):
    """
    This class represents a node, defined by Howe et. al.
    It contains the reference to a parent-node and a list of its children-nodes, as well as the 2d-representation of that node.
    Additionally an offset is stored within the node. This shows the offset relative to its parent-node
    """

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
        self.index = None

    def add_child(self, child):
        """
        Adds a child to the children list. Added to avoid a breach of the law of demeter.
        :param child: The child to add.
        """
        self.children.append(child)

    def set_parent(self, parent):
        self.parent = parent

    def __str__(self):
        """
        :return: Node-Position
        """
        return "Node-Position: {}".format(self.position)

    def __eq__(self, other):
        """
        Two nodes are equal, if their position is equal
        :param other: Other Node to check for equality
        :return: True, if position is equal - False, else
        """
        return (self.position == other.position).all()
