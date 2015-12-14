# -*- encoding: utf-8 -*-

from functools import reduce  # pylint:disable=redefined-builtin
from PyQt4 import QtGui
from numpy import zeros, array, delete, insert, c_, where
from skimage.feature import corner_harris
from skimage.feature import corner_peaks
from skimage.morphology import skeletonize

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
        self.nodes = self.create_nodes()

    def create_bounding_box(self):
        sg_logger.info("Setting up Bounding Box")
        return reduce(lambda xs, x: xs | x.boundingRect(),
                      self.paths[1:],
                      self.paths[0].boundingRect())

    def create_original_image(self):
        image = QtGui.QImage(self.get_image_width(), self.get_image_height(), QtGui.QImage.Format_RGB32)
        self.set_background(COLOR_BG, image)
        image = self.try_to_fill_image_with_paths(image)
        return image

    def get_image_width(self):
        return self.bounding_box.width()*WIDTH

    def get_image_height(self):
        return self.bounding_box.height()*HEIGHT

    @staticmethod
    def set_background(color, image):
        sg_logger.info("Setting Background to [%s]", color)
        image.fill(QtGui.QColor(color))

    def try_to_fill_image_with_paths(self, image):
        qpainter = QtGui.QPainter(image)
        try:
            return self.fill_image_with_paths(qpainter, image)
        finally:
            qpainter.end()

    def fill_image_with_paths(self, qpainter, image):
        sg_logger.info("Brushing Paths onto QImage")
        qpainter.setBrush(QtGui.QColor(COLOR_FG))
        qpainter.setPen(QtGui.QColor(COLOR_FG))
        qpainter.scale(HEIGHT, WIDTH)
        qpainter.translate(-self.bounding_box.topLeft())
        for path in self.paths:
            qpainter.drawPath(path)
        return image

    def convert_qimage_to_ndarray(self):  # pragma: no cover
        sg_logger.info("Converting QImage to NumPy-Array")
        m, n = self.get_image_height(), self.get_image_width()
        array = zeros((m, n))
        for y in range(int(m)):
            for x in range(int(n)):
                c = QtGui.qGray(self.original_image.pixel(x, y))
                array[y, x] = True if c >= COLORED else False
        return array

    def create_skeleton(self, name):
        sg_logger.info("Skeletonizing QImage with name [%s]", name)
        return skeletonize(self.original_array)

    def create_nodes(self):
        nodes = self.find_corners_and_junctions()
        nodes.extend(self.add_nodes_greedily(nodes))
        return nodes

    def find_corners_and_junctions(self):
        sg_logger.info("Detecting Nodes of skeletonized QImage with name [%s]\n", self.name)
        skeleton_corners = corner_peaks(corner_harris(self.enlarged_skeleton), min_distance=2)
        nodes = list()
        for corner in skeleton_corners:
            nodes.append(Node(position=corner))
        return nodes

    def add_nodes_greedily(self, corner_nodes):
        additional_nodes = list()
        new_nodes = list()
        true_list = list()

        for i, x in enumerate(self.enlarged_skeleton):
            for j, y in enumerate(x):
                if y and Node(position=array([i, j])) not in corner_nodes:
                    true_list.append(array([i, j]))

        new_nodes.extend(corner_nodes)
        to_delete = list()
        open_list = list()
        closed_list = list()
        rest_list = list()

#       corner = corner_nodes[0]
        for corner in corner_nodes:
            open_list.append(corner)
            while len(open_list) > 0 or len(rest_list) > 0:
                to_delete.clear()
                if len(open_list) > 1:
                    rest_list.extend(open_list)
                    open_list.clear()
                    continue

                node = None
                if len(open_list) > 0:
                    node = open_list.pop(0)
                else:
                    node = rest_list.pop(0)

                closed_list.append(node)
                for i, true in enumerate(true_list):
                    if node.position[0] + DISTANCE > true[0] > node.position[0] - DISTANCE \
                            and node.position[1] + DISTANCE > true[1] > node.position[1] - DISTANCE:
                        to_delete.append(i)
                    elif (node.position[0] + DISTANCE == true[0] and node.position[1] + DISTANCE >= true[1] >= node.position[1] - DISTANCE) \
                      or (node.position[0] - DISTANCE == true[0] and node.position[1] + DISTANCE >= true[1] >= node.position[1] - DISTANCE) \
                      or (node.position[1] + DISTANCE == true[1] and node.position[0] + DISTANCE >= true[0] >= node.position[0] - DISTANCE) \
                      or (node.position[1] - DISTANCE == true[1] and node.position[0] + DISTANCE >= true[0] >= node.position[0] - DISTANCE):
                        if Node(position=true) not in closed_list and Node(position=true) not in corner_nodes:
                            new_node = Node(position=true)
                            open_list.append(new_node)
                            additional_nodes.append(new_node)

                for item in reversed(to_delete):
                    true_list = delete(true_list, item, 0)

        return additional_nodes

    def enlarge_skeleton(self):
        rows = len(self.skeleton_array)
        cols = len(self.skeleton_array[0])
        enlarged_array = self.skeleton_array
        enlarged_array = c_[zeros(rows, dtype=bool), enlarged_array, zeros(rows, dtype=bool)]
        enlarged_array = insert(enlarged_array, 0, zeros(cols + 2, dtype=bool), 0)
        enlarged_array = insert(enlarged_array, rows, zeros(cols + 2, dtype=bool), 0)
        return enlarged_array


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
        self.children.append(child)

    def __str__(self):
        return "Node-Position: {}".format(self.position)

    def __eq__(self, other):
        return (self.position == other.position).all()