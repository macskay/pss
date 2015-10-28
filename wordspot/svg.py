# -*- encoding: utf-8 -*-
from logging import getLogger
from os.path import isfile
from sys import argv

from external.elka_svg import parse

from PyQt4 import QtGui, QtCore
from wordspot.gui import SymbolGroupWidget

svg_logger = getLogger("SvgHandler")


class SvgHandler(object):
    def __init__(self, path, infix=""):
        svg_logger.info("SVG-Handler started")
        """
        :param path: Path to the SVG-file (required)
        :param infix: Infix to look for in svg-file (default: "")
        :raise FileNotFoundError: This is raised, when an invalid svg file is passed.
        """
        if not isfile(path):
            svg_logger.error("Path to SVG-File invalid!")
            raise FileNotFoundError

        svg_logger.info("Opening SVG-File at [%s]", path)
        self.names, self.symbol_groups = zip(*parse(infix, path))
        svg_logger.info("SVG-File successfully loaded. (%d names, %d symbol-groups)",
                        len(self.names), len(self.symbol_groups))

    def show_symbol_group_as_image(self, symbol_group):  # pragma: no cover
        app = QtGui.QApplication(argv)
        svg_gui = SymbolGroupWidget(symbol_group)
        app.exec_()

    # TODO: add thinner (from skimage.morphology import medial_axis)
    # TODO: add GUI class to show image (reference this class, calls pathhs to create image on QtApplicaiton)
