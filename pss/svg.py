# -*- encoding: utf-8 -*-

from logging import getLogger
from os.path import isfile

from matplotlib.pyplot import show

from external.elka_svg import parse
from pss.gui import ImagePlot, PrintNodes
from pss.model import SymbolGroup

svg_logger = getLogger("SvgHandler")


class SvgHandler(object):
    """
    This class opens and manages a given svg file. Make sure the display-methods are commented out for Nosetests.
    """
    def __init__(self, path, infix=""):
        """
        :param path: Path to the SVG-file (required)
        :param infix: Infix to look for in svg-file (default: "")
        :raise FileNotFoundError: This is raised, when an invalid svg file is passed.
        """
        svg_logger.info("SVG-Handler started")
        self.handle_file_not_existing(path)
        self.names, self.svg_symbol_groups = self.load_svg(infix, path)

        # self.symbol_groups = self.create_symbol_groups()
        # self.display_symbol_groups()

        self.symbol_groups = self.create_single_symbol_group(0)
        # self.display_single_symbol_group()

    @staticmethod
    def handle_file_not_existing(path):
        """
        Checks whether the given file is existing
        :param path: Path of file to check for existence
        :raises: FileNotFoundError if path not found
        """
        if not isfile(path):
            svg_logger.error("Path to SVG-File invalid!")
            raise FileNotFoundError  # noqa

    @staticmethod
    def load_svg(infix, path):
        """
        Opens an SVG-file
        :param infix: This infix is used by the external library elka_svg.py to check for specific groups within the svg.
        :param path: Path, where the SVG file is located
        :return: names and lists of QPainterPaths of the SymbolGroups read from the SVG
        """
        svg_logger.info("Opening SVG-File at [%s]", path)
        names, symbol_groups = zip(*parse(infix, path))
        svg_logger.info("SVG-File successfully loaded. (%d names, %d symbol-groups)\n",
                        len(names), len(symbol_groups))
        return names, symbol_groups

    def display_symbol_groups(self):  # pragma: no cover
        """
        Plots all SymbolGroups found by the program
        """
        for symbol_group in self.symbol_groups:
            ImagePlot(symbol_group)
        show()

    def display_single_symbol_group(self):  # pragma: no cover
        """
        Plots a single given SymbolGroup of all the SymbolGroups found by the program
        """
        ImagePlot(self.symbol_groups[0])
        show()

    def print_single_symbol_group_nodes(self, i):  # pragma: no cover
        """
        Prints all nodes found within a given SymbolGroup
        :param i: Index of the SymbolGroup within the SymbolGroup-list
        """
        PrintNodes(self.symbol_groups[i])

    def create_symbol_groups(self):  # pragma: no cover
        """
        Creates SymbolGroups from the QPainterPaths lists created before.
        :return: A list of created SymbolGroups for all QPainterPath-lists found by load_svg
        """
        symbol_groups = list()
        for i, item in enumerate(self.svg_symbol_groups):
            symbol_groups.append(SymbolGroup(item, self.names[i]))
        return symbol_groups

    def create_single_symbol_group(self, i):  # pragma: no cover
        """
        Creates a single SymbolGroup from the QPainterPaths lists created before.
        :param i: Index of the QPainterPath-list within the QPainterPaths lists found by load_svg
        :return: A single SymbolGroup for a given the given index within QPainterPath-lists found by load_svg

        """
        symbol_group = list()
        symbol_group.append(SymbolGroup(self.svg_symbol_groups[i], self.names[i]))
        return symbol_group

    @staticmethod
    def get_symbol_group_size(symbol_group):
        """
        Returns the number of QPainterPaths within a given SymbolGroup
        :param symbol_group: The SymbolGroup to find the size of
        :return: The number of Paths within that SymbolGroup
        """
        return len(symbol_group)

