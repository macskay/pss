# -*- encoding: utf-8 -*-
from functools import reduce  # pylint:disable=redefined-builtin
from logging import getLogger
from os.path import isfile
from sys import argv

from PyQt4 import QtGui

from external.elka_svg import parse
from pss.gui import ImageDisplay

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

        self.image = SymbolGroupImage(self.symbol_groups[0])
        #self.show_symbol_group_as_image()

    def handle_file_not_existing(self, path):
        if not isfile(path):
            svg_logger.error("Path to SVG-File invalid!")
            raise FileNotFoundError  # noqa

    def show_symbol_group_as_image(self):  # pragma: no cover
        app = QtGui.QApplication(argv)
        svg_gui = ImageDisplay(QtGui.QImage(self.image))  # noqa
        app.exec_()

    def get_symbol_group_path_count(self, symbol_group):
        return len(symbol_group)

    def load_svg(self, infix, path):
        svg_logger.info("Opening SVG-File at [%s]", path)
        names, symbol_groups = zip(*parse(infix, path))
        svg_logger.info("SVG-File successfully loaded. (%d names, %d symbol-groups)",
                        len(names), len(symbol_groups))
        return names, symbol_groups

    # TODO: add thinner (from skimage.morphology import medial_axis)
    # TODO: add GUI class to show image (reference this class, calls pathhs to create image on QtApplicaiton)


sg_logger = getLogger("SymbolGroupImage")


class SymbolGroupImage(QtGui.QImage):
    def __init__(self, symbol_group):
        self.symbol_group = symbol_group
        self.bounding_box = self.create_bounding_box()
        super(SymbolGroupImage, self).__init__(self.get_width(), self.get_height(), QtGui.QImage.Format_RGB32)
        self.set_background("White")
        self.try_to_fill_image_with_paths()

    def create_bounding_box(self):
        sg_logger.info("Setting up Bounding Box")
        return reduce(lambda xs, x: xs | x.boundingRect(),
                      self.symbol_group[1:],
                      self.symbol_group[0].boundingRect())

    def get_width(self):
        return self.bounding_box.width()*5

    def get_height(self):
        return self.bounding_box.height()*5

    def set_background(self, color):
        sg_logger.info("Setting Background to [{}]".format(color))
        self.fill(QtGui.QColor(color))

    def try_to_fill_image_with_paths(self):
        qpainter = QtGui.QPainter(self)
        try:
            self.fill_image_with_paths(qpainter)
        finally:
            qpainter.end()

    def fill_image_with_paths(self, qpainter):
        sg_logger.info("Brushing Paths onto QImage")
        qpainter.setBrush(QtGui.QColor("Black"))
        qpainter.setPen(QtGui.QColor("Black"))
        qpainter.scale(5, 5)
        qpainter.translate(-self.bounding_box.topLeft())
        for path in self.symbol_group:
            qpainter.drawPath(path)