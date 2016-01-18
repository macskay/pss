from logging import getLogger
from os.path import isfile

from PyQt4.QtGui import QImage

svg_logger = getLogger("PngHandler")


def handle_file_not_existing(path):
    """
    Checks whether the given file is existing
    :param path: Path of file to check for existence
    :raises: FileNotFoundError if path not found
    """
    if not isfile(path):
        svg_logger.error("Path to SVG-File invalid!")
        raise FileNotFoundError  # noqa


class QueryPNG(object):
    def __init__(self, path, scale=1):
        handle_file_not_existing(path)
        im = QImage(path, "0xAARRGGBB")
        self.image = im.scaled(im.size() * scale)


class TargetPNG(object):
    def __init__(self, path, scale=1):
        handle_file_not_existing(path)
        im = QImage(path, "0xAARRGGBB")
        self.image = im.scaled(im.size() * scale)
