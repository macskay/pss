# -*- encoding: utf-8 -*-

from logging import getLogger
from os.path import isfile

from PyQt4.QtSvg import QSvgRenderer

from external.elka_svg import parse

svg_logger = getLogger("SvgHandler")


def handle_file_not_existing(path):
    """
    Checks whether the given file is existing
    :param path: Path of file to check for existence
    :raises: FileNotFoundError if path not found
    """
    if not isfile(path):
        svg_logger.error("Path to SVG-File invalid! Make sure the file is placed in the resources-folder")
        raise FileNotFoundError  # noqa


class TargetSvg(object):
    """
    This class opens and manages a given svg file as the target image.
    """
    def __init__(self, path):
        """
        :param path: Path to the SVG-file (required)
        :raise FileNotFoundError: This is raised, when an invalid svg file is passed.
        """
        svg_logger.info("Target SVG-Handler started")
        handle_file_not_existing(path)
        self.renderer = QSvgRenderer(path)


class QuerySvg(object):
    """
    This class opens and manages as the query image.
    """
    def __init__(self, path, infix=''):
        """
        :param path: Path to the SVG-file (required)
        :param infix: Infix to look for in svg-file (default: "")
        :raise FileNotFoundError: This is raised, when an invalid svg file is passed.
        """
        svg_logger.info("Query SVG-Handler started")
        handle_file_not_existing(path)
        self.names, self.svg_symbol_groups = self.load_svg(infix, path)

    @staticmethod
    def load_svg(infix, path):
        """
        Opens an SVG-file
        :param infix: This infix is used by the external library elka_svg.py
        to check for specific groups within the svg.
        :param path: Path, where the SVG file is located
        :return: names and lists of QPainterPaths of the SymbolGroups read from the SVG
        """
        svg_logger.info("Opening SVG-File at [%s]", path)
        names, symbol_groups = zip(*parse(infix, path))
        svg_logger.info("SVG-File successfully loaded. (%d names, %d symbol-groups)\n",
                        len(names), len(symbol_groups))
        return names, symbol_groups

    @staticmethod
    def get_symbol_group_size(symbol_group):
        """
        Returns the number of QPainterPaths within a given SymbolGroup
        :param symbol_group: The SymbolGroup to find the size of
        :return: The number of Paths within that SymbolGroup
        """
        return len(symbol_group)

