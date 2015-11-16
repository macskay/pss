# -*- encoding: utf-8 -*-
from functools import reduce  # pylint:disable=redefined-builtin
from logging import getLogger
from os.path import isfile

from PyQt4 import QtGui
from matplotlib.pyplot import show
from numpy import zeros
from skimage.feature import corner_harris
from skimage.feature import corner_peaks
from skimage.morphology import skeletonize

from external.elka_svg import parse
from pss.gui import ImagePlot

svg_logger = getLogger("SvgHandler")


class SvgHandler(object):
    def __init__(self, path, infix=""):
        """
        :param path: Path to the SVG-file (required)
        :param infix: Infix to look for in svg-file (default: "")
        :raise FileNotFoundError: This is raised, when an invalid svg file is passed.
        """
        svg_logger.info("SVG-Handler started")
        self.handle_file_not_existing(path)
        self.names, self.symbol_groups = self.load_svg(infix, path)
        self.images = self.create_symbol_group_images()

        # self.display_symbol_groups()
        # self.display_single_symbol_group(0)

    @staticmethod
    def handle_file_not_existing(path):
        if not isfile(path):
            svg_logger.error("Path to SVG-File invalid!")
            raise FileNotFoundError  # noqa

    @staticmethod
    def load_svg(infix, path):
        svg_logger.info("Opening SVG-File at [%s]", path)
        names, symbol_groups = zip(*parse(infix, path))
        svg_logger.info("SVG-File successfully loaded. (%d names, %d symbol-groups)\n",
                        len(names), len(symbol_groups))
        return names, symbol_groups

    def display_symbol_groups(self):  # pragma: no cover
        for image in self.images:
            ImagePlot(image)
        show()

    def display_single_symbol_group(self, i):  # pragma: no cover
        ImagePlot(self.images[i])
        show()

    @staticmethod
    def get_symbol_group_size(symbol_group):
        return len(symbol_group)

    def create_symbol_group_images(self):
        images = list()
        for i, item in enumerate(self.symbol_groups):
            images.append(SymbolGroupImage(item, self.names[i]))
        return images


sgi_logger = getLogger("SymbolGroupImage")


class SymbolGroupImage(QtGui.QImage):
    def __init__(self, symbol_group, name):  # pylint:disable=super-on-old-class
        """
        :param symbol_group: The group of symbols to represent as QImage
        :param name: This is the name of the symbol group as set in the svg
        """
        sgi_logger.info("Setup SymbolGroupImage with name [%s]", name)
        self.symbol_group = symbol_group
        self.name = name
        self.bounding_box = self.create_bounding_box()

        super(SymbolGroupImage, self).__init__(self.get_width(), self.get_height(), QtGui.QImage.Format_RGB32)

        self.set_background("Black")
        self.try_to_fill_image_with_paths()

        self.original_array = self.convert_qimage_to_ndarray()

        sgi_logger.info("Skeletonizing QImage with name [%s]\n", name)
        self.skeleton_array = skeletonize(self.original_array)

        self.original_corners = corner_peaks(corner_harris(self.original_array), min_distance=1)
        self.skeleton_corners = corner_peaks(corner_harris(self.skeleton_array), min_distance=1)

    def create_bounding_box(self):
        sgi_logger.info("Setting up Bounding Box")
        return reduce(lambda xs, x: xs | x.boundingRect(),
                      self.symbol_group[1:],
                      self.symbol_group[0].boundingRect())

    # TODO: get rid off magic numbers
    def get_width(self):
        return self.bounding_box.width()*5

    # TODO: get rid off magic numbers
    def get_height(self):
        return self.bounding_box.height()*5

    def set_background(self, color):
        sgi_logger.info("Setting Background to [%s]", color)
        self.fill(QtGui.QColor(color))

    def try_to_fill_image_with_paths(self):
        qpainter = QtGui.QPainter(self)
        try:
            self.fill_image_with_paths(qpainter)
        finally:
            qpainter.end()

    # TODO: get rid off magic numbers
    def fill_image_with_paths(self, qpainter):
        sgi_logger.info("Brushing Paths onto QImage")
        qpainter.setBrush(QtGui.QColor("White"))
        qpainter.setPen(QtGui.QColor("White"))
        qpainter.scale(5, 5)
        qpainter.translate(-self.bounding_box.topLeft())
        for path in self.symbol_group:
            qpainter.drawPath(path)

    # TODO: get rid off magic numbers
    def convert_qimage_to_ndarray(self):  # pragma: no cover
        m, n = self.height(), self.width()
        array = zeros((m, n))
        for y in range(m):
            for x in range(n):
                c = QtGui.qGray(self.pixel(x, y))
                array[y, x] = 0 if c < 127 else 1
        return array
