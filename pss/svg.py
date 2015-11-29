# -*- encoding: utf-8 -*-

from logging import getLogger
from os.path import isfile

from matplotlib.pyplot import show

from external.elka_svg import parse
from pss.gui import ImagePlot, PrintNodes
from pss.model import SymbolGroup

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
        self.names, self.svg_symbol_groups = self.load_svg(infix, path)
        self.symbol_groups = self.create_symbol_groups()

        # These need to be commented when pushing, to make the tests pass
        # self.display_symbol_groups()
        # self.display_single_symbol_group(0)
        # self.print_single_symbol_group_nodes(6)
        # self.symbol_groups = self.create_single_symbol_group(0)
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
        for symbol_group in self.symbol_groups:
            ImagePlot(symbol_group)
        show()

    def display_single_symbol_group(self, i):  # pragma: no cover
        ImagePlot(self.symbol_groups[i])
        show()

    def print_single_symbol_group_nodes(self, i):  # pragma: no cover
        PrintNodes(self.symbol_groups[i])

    def create_symbol_groups(self):  # pragma: no cover
        symbol_groups = list()
        for i, item in enumerate(self.svg_symbol_groups):
            symbol_groups.append(SymbolGroup(item, self.names[i]))
        return symbol_groups

    def create_single_symbol_group(self, i):  # pragma: no cover
        symbol_group = list()
        symbol_group.append(SymbolGroup(self.svg_symbol_groups[i], self.names[i]))
        return symbol_group

    @staticmethod
    def get_symbol_group_size(symbol_group):
        return len(symbol_group)

