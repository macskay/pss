# -*- encoding: utf-8 -*-
from logging import getLogger
from os.path import isfile
from sys import argv

from PyQt4 import QtGui

from external.elka_svg import parse
from pss.gui import SymbolGroupWidget

svg_logger = getLogger("SvgHandler")


class SvgHandler(object):
    def __init__(self, path, infix=""):
        """
        :param path: Path to the SVG-file (required)
        :param infix: Infix to look for in svg-file (default: "")
        :raise FileNotFoundError: This is raised, when an invalid svg file is passed.
        """
        svg_logger.info("SVG-Handler started")
        if not isfile(path):
            svg_logger.error("Path to SVG-File invalid!")
            raise FileNotFoundError  # noqa

        svg_logger.info("Opening SVG-File at [%s]", path)
        self.names, self.symbol_groups = zip(*parse(infix, path))
        svg_logger.info("SVG-File successfully loaded. (%d names, %d symbol-groups)",
                        len(self.names), len(self.symbol_groups))

        self.show_symbol_group_as_image(5)


    def show_symbol_group_as_image(self, index):  # pragma: no cover
        if index < len(self.names) and index < len(self.symbol_groups):
            svg_logger.info("Showing symbol group [%d] with name [%s]", index, self.names[index])
            app = QtGui.QApplication(argv)
            svg_gui = SymbolGroupWidget(self.symbol_groups[index])  # noqa
            app.exec_()
        else:
            svg_logger.warning("Can't show symbol group [%d], IndexOutOfBounds: %d", index, len(self.symbol_groups))

    def get_symbol_group_path_count(self, symbol_group):
        return len(symbol_group)

    # TODO: add thinner (from skimage.morphology import medial_axis)
    # TODO: add GUI class to show image (reference this class, calls pathhs to create image on QtApplicaiton)
