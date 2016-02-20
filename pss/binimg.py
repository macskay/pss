from logging import getLogger
from os.path import isfile

from PyQt4.QtGui import QImage

svg_logger = getLogger("BinImageHandler")


def handle_file_not_existing(path):
    """
    Checks whether the given file is existing
    :param path: Path of file to check for existence
    :raises: FileNotFoundError if path not found
    """
    if not isfile(path):
        svg_logger.error("Path to PNG-File invalid!")
        raise FileNotFoundError  # noqa


class QueryBin(object):
    """
    This class opens and manages a given png file.
    """
    def __init__(self, path, scale=1):
        """
        :param path: Path to the PNG-file (required)
        :param scale: Multiplier for the scale
        :raise FileNotFoundError: This is raised, when an invalid svg file is passed.
        """
        svg_logger.info("Query Bin-Handler started")
        handle_file_not_existing(path)
        im = QImage(path, "0xAARRGGBB")
        self.image = im.scaled(im.size() * scale)


class TargetBin(object):
    def __init__(self, path, scale=1):
        """
        :param path: Path to the PNG-file (required)
        :param scale: Multiplier for the scale
        :raise FileNotFoundError: This is raised, when an invalid svg file is passed.
        """
        svg_logger.info("Target Bin-Handler started")
        handle_file_not_existing(path)
        im = QImage(path, "0xAARRGGBB")
        self.image = im.scaled(im.size() * scale)

        """
        app = QApplication(sys.argv)
        pm = QPixmap(self.image)
        lbl = QLabel()
        lbl.setPixmap(pm)
        lbl.show()

        sys.exit(app.exec_())
        """
