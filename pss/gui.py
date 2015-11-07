# -*- encoding: utf-8 -*-
from logging import getLogger

from PyQt4 import QtGui

gui_logger = getLogger("SymbolGroupDisplay")


class ImageDisplay(QtGui.QLabel):  # pragma: no cover
    def __init__(self, image):  # pylint:disable=super-on-old-class
        gui_logger.info("Displaying SymbolGroup on screen")
        super(ImageDisplay, self).__init__()
        self.setWindowTitle("SymbolGroup")
        self.show_on_screen(image)

    def show_on_screen(self, image):
        self.setPixmap(QtGui.QPixmap(image))
        self.show()
