# -*- encoding: utf-8 -*-
from copy import deepcopy
from datetime import datetime
from functools import reduce  # pylint:disable=redefined-builtin
from logging import getLogger
from math import sqrt

from PyQt4 import QtGui
from numpy import zeros, array, delete, insert, c_, mean, inf, invert, ndarray, add
from skimage.feature import corner_harris
from skimage.feature import corner_peaks
from skimage.morphology import skeletonize, medial_axis

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

        # Query
        self.query_bounding_box = self.create_bounding_box()
        self.query_image = self.create_original_image()
        self.query_original_array = self.convert_qimage_to_ndarray()
        self.query_skeleton = self.create_skeleton(name)
        self.query_enlarged_skeleton = self.enlarge_skeleton()
        self.query_corner_nodes = self.find_corners_and_junctions()
        self.query_true_list = self.create_true_list()
        self.query_center_of_mass = self.calculate_center_of_mass()

        # Tree
        self.query_root_node = None
        self.query_nodes = list()

        self.open_list = list()
        self.closed_list = list()

        self.query_nodes = self.add_remaining_nodes()
        self.query_nodes_backup = deepcopy(self.query_nodes)  # needed for dt height and width
        self.query_root_node = self.find_root_node()
        self.build_up_tree()

        # Distance Transform
        # In here plugin any svg or png or jpg or whatever as ndarray
        # distanztransformierte des target bilds um node offsets wandern lassen und aufaddieren
        # self.target_image = None
        # self.target_original_array = self.query_original_array

        self.height, self.width, self.abs_start = self.calculate_height_and_width_of_distance_transform()
        self.sum_dt = None
        self.calculate_distance_transform(self.query_root_node)

    def calculate_distance_transform(self, node):
        sg_logger.info("Starting to build up Distance Transform")
        start_time = datetime.now()
        self.recursively_add_up_all_distance_transforms(node)
        end_time = datetime.now()
        sg_logger.info("Finished building up Distance Transform.\n")
        self.print_time(end_time, start_time)

    def recursively_add_up_all_distance_transforms(self, node):
        new_sum_dt = self.build_distance_transform_to_parent(node)
        self.sum_dt = add(self.sum_dt, new_sum_dt) if self.sum_dt is not None else new_sum_dt

        for child in node.children:
            self.recursively_add_up_all_distance_transforms(child)

    def build_distance_transform_to_parent(self, child):
        abs_location = child.position.item(0) - self.abs_start[0], child.position.item(1) - self.abs_start[1]

        new_array = zeros((self.height, self.width), dtype=int)
        new_array[abs_location[0]:abs_location[0] + self.query_original_array.shape[0],
        abs_location[1]:abs_location[1] + self.query_original_array.shape[1]] = self.query_original_array

        ia = invert(ndarray.astype(new_array, dtype=bool))
        new_distance_transform = medial_axis(ia, return_distance=True)[1]
        return new_distance_transform

    def calculate_height_and_width_of_distance_transform(self):
        sorted_x = sorted(self.query_nodes_backup, key=lambda x: x.position.item(0))
        sorted_y = sorted(self.query_nodes_backup, key=lambda x: x.position.item(1))
        smallest_x = sorted_x[0].position.item(0)
        smallest_y = sorted_y[0].position.item(1)
        highest_x = sorted_x[-1].position.item(0)
        highest_y = sorted_y[-1].position.item(1)

        height = highest_x - smallest_x + len(self.query_original_array)
        width = highest_y - smallest_y + len(self.query_original_array[0])

        return height, width, (smallest_x, smallest_y)

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
        return self.query_bounding_box.width() * WIDTH

    def get_image_height(self):
        """
        Getter for the QImage height
        :return: Height of the Bounding-Box
        """
        return self.query_bounding_box.height() * HEIGHT

    @staticmethod
    def set_background(color, image):
        """
        Sets the background color of the QImage
        :param image: QImage which background should be changed
        :param color: Color to change background to
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
        qpainter.translate(-self.query_bounding_box.topLeft())
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
                c = QtGui.qGray(self.query_image.pixel(x, y))
                array[y, x] = True if c >= COLORED else False
        return array

    def create_skeleton(self, name):
        """
        Skeletonizes a given Numpy-Array to a 1px width. See skimage-documentation for skeletonize
        :param name: Name of the QImage (For Logging purposes)
        :return: Skeletonized Numpy-Array
        """
        sg_logger.info("Skeletonizing QImage with name [%s]", name)
        return skeletonize(self.query_original_array)

    def enlarge_skeleton(self):
        """
        Adds two columns and two rows at the top, bottom, left and right to ensure the neighbor-search doesn't hit
        a border.
        :return: Numpy-Array, which is a column and row larger on each side.
        """
        rows = len(self.query_skeleton)
        cols = len(self.query_skeleton[0])
        enlarged_array = self.query_skeleton
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
        skeleton_corners = corner_peaks(corner_harris(self.query_enlarged_skeleton), min_distance=2)
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
        for i, x in enumerate(self.query_enlarged_skeleton):
            for j, y in enumerate(x):
                if y and Node(position=array([i, j])) not in self.query_corner_nodes:
                    true_list.append(array([i, j]))
        return true_list

    def add_remaining_nodes(self):
        """
        This calls sub-functions to add the remaining nodes between junctions and corners.
        :return: The list of all nodes representing the QImage
        """
        nodes = list()
        nodes.extend(self.add_nodes_greedily())
        nodes.extend(self.query_corner_nodes)
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

        for corner in self.query_corner_nodes:
            self.open_list.append(corner)
            rest_list = list()

            while self.still_neighbors_to_check(rest_list):
                if self.has_node_more_than_one_neighbor():
                    rest_list = self.create_copy_of_open_list_and_clear()
                    continue

                node = self.open_list.pop(0) if len(self.open_list) > 0 else rest_list.pop(0)
                self.closed_list.append(node)

                good_neighbors, bad_neighbors = self.decide_good_or_bad_neighbor(node)
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
        for i, true_position in enumerate(self.query_true_list):
            if self.is_neighbor_too_close(node, true_position):
                bad_neighbors.append(i)
            elif self.is_neighbor_the_right_distance_away(node, true_position):
                new_node = Node(position=true_position)
                if self.is_node_completely_unknown(new_node):  # pragma: no cover
                    self.open_list.append(new_node)
                    good_neighbors.append(new_node)
        return good_neighbors, bad_neighbors

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
        return (node.position[0] + DISTANCE == true_position[0] and node.position[1] + DISTANCE >= true_position[1] >=
                node.position[1] - DISTANCE) \
               or (
                   node.position[0] - DISTANCE == true_position[0] and node.position[1] + DISTANCE >= true_position[
                       1] >=
                   node.position[1] - DISTANCE) \
               or (
                   node.position[1] + DISTANCE == true_position[1] and node.position[0] + DISTANCE >= true_position[
                       0] >=
                   node.position[0] - DISTANCE) \
               or (
                   node.position[1] - DISTANCE == true_position[1] and node.position[0] + DISTANCE >= true_position[
                       0] >=
                   node.position[0] - DISTANCE)

    def is_node_completely_unknown(self, new_node):
        """
        Checks if a given node is completely unknown, meaning it is neither in the closed_list nor in the corner_nodes
        :param new_node: Node to be checked
        :return: True if completely unknown (not in self.closed_list and not in self.corner_nodes)
        """
        return new_node not in self.closed_list and new_node not in self.query_corner_nodes

    def delete_bad_neighbors_from_true_list(self, bad_neighbors):
        """
        Deletes bad neighbors from the true_list, so they don't get checked ever again. They can't get "Good neighbors"
        any longer.
        :param bad_neighbors: List of "Bad neighbors", which should get deleted out of the true_list
        """
        for item in reversed(bad_neighbors):
            self.query_true_list = delete(self.query_true_list, item, 0)

    def calculate_center_of_mass(self):
        """
        Calculates the center of mass by using the arithmetic mean of all node positions
        :return: The arithmetic mean of all node positions
        """
        return Node(position=mean(self.query_true_list, axis=0, dtype=int))

    def find_root_node(self):
        """
        Finds the closes node to the center of mass
        :return: The node closed to the center od mass. This becomes the root node for the upcoming parent-child tree
        """
        closest_node = None
        closest_distance = float("inf")
        for node in self.query_nodes:
            current_distance = self.get_euclidean_distance(node, self.query_center_of_mass)
            if current_distance < closest_distance:
                closest_node = node
                closest_distance = current_distance
        return closest_node

    def get_euclidean_distance(self, a, b):
        """
        Finds the euclidean distance between two given nodes
        :param a: first node
        :param b: second node
        :return: euclidean distance between node a and node b
        """
        return sqrt(self.get_euclidean_addend(a, b, 0) + self.get_euclidean_addend(a, b, 1))

    @staticmethod
    def get_euclidean_addend(a, b, i):
        """
        Calculates one addend of the euclidean distance
        :param a: first node
        :param b: second node
        :param i: Index of the axis/dimension
        :return: One calculated addend of form (a.pos.item(i) - b.pos.item(i))^2
        """
        return pow((a.position.item(i) - b.position.item(i)), 2)

    def build_up_tree(self):
        """
        Builds up the tree structure starting from the root node.
        """
        sg_logger.info("Starting to build up tree...")
        start_time = datetime.now()
        self.creating_all_relations_for_tree()
        end_time = datetime.now()
        self.print_time(end_time, start_time)
        sg_logger.info("Finished building up tree...\n")

    def creating_all_relations_for_tree(self):
        current_tree = list()
        current_tree.append(self.query_root_node)
        self.query_nodes.remove(self.query_root_node)

        while self.query_nodes:
            real_child, real_parent = self.find_closest_node(current_tree)
            if real_parent is None:  # pragma: no cover
                break

            self.add_relation(real_child, real_parent)
            self.update_tree(current_tree, real_child)

    @staticmethod
    def update_tree(current_tree, real_child):
        """
        Adds new child to the current tree and removes it from the nodes list
        :param current_tree: Already created tree
        :param real_child: Child to add to tree and remove from nodes list
        """
        current_tree.append(real_child)

    def add_relation(self, real_child, real_parent):
        """
        Adding the child to the parent and vice versa
        :param real_child: Child-Node to add
        :param real_parent: Parent-Node where Child-Node should be added
        """
        real_parent.add_child(real_child)
        real_child.set_parent(real_parent)
        real_child.calculate_offset()
        self.query_nodes.remove(real_child)

    def find_closest_node(self, current_tree):
        """
        Finds node with closest distance to the already created tree with a greedy approach
        :param current_tree: Already created tree
        :return: Child-Node to add to the tree and Parent-Node, where child should get added
        """
        closest_distance = float(inf)
        real_parent = None
        real_child = None

        for potential_child in self.query_nodes:
            for potential_source in current_tree:
                if potential_child != potential_source:  # pragma: no cover
                    if abs(potential_child.position.item(0) - potential_source.position.item(0)) <= closest_distance \
                            or abs(potential_child.position.item(1) - potential_source.position.item(
                                    1)) <= closest_distance:
                        current_distance = self.get_euclidean_distance(potential_child, potential_source)
                        if current_distance < closest_distance:  # pragma: no cover
                            closest_distance = current_distance
                            real_child = potential_child
                            real_parent = potential_source
        return real_child, real_parent

    @staticmethod
    def print_time(end_time, start_time):
        """
        This method just prints how long a certain function took
        :param end_time: Timestamp taken after finished building the tree
        :param start_time: Timestamp taken before started building the tree
        """
        delta_time = end_time - start_time
        tuple_divmod = divmod(delta_time.total_seconds(), 60)
        delta_seconds = tuple_divmod[0] * 60 + int(tuple_divmod[1])
        sg_logger.info("Finishing took %d seconds", delta_seconds)


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
        self.position = array([0, 0], dtype=int) if position is None else position
        self.offset = array([0, 0], dtype=int) if offset is None else offset
        self.index = None

    def add_child(self, child):
        """
        Adds a child to the children list. Added to avoid a breach of the law of demeter.
        :param child: The child to add.
        """
        self.children.append(child)

    def set_parent(self, parent):
        """
        Setter for the Parent-Node
        :param parent: A Node, which should be the parent of the current node
        """
        self.parent = parent

    def calculate_offset(self):
        offset = list()
        for i, axis in enumerate(self.position):
            offset.append(axis - self.parent.position[i])
        self.offset = array(offset, dtype=int)

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
        if other is None:
            return False
        return (self.position == other.position).all()
