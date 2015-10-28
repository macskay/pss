# -*- encoding: utf-8 -*-
from logging import getLogger

from PyQt4 import QtGui

gui_logger = getLogger("GUI")


class SymbolGroupWidget(QtGui.QWidget):
    def __init__(self, symbol_group):
        gui_logger.info("Creating SymbolGroup-Widget")
        super(SymbolGroupWidget, self).__init__()
        self.show_as_image(symbol_group)
        self.setWindowTitle("SymbolGroup")

    def show_as_image(self, symbol_group):
        gui_logger.info("Opening symbol group image")
        self.show()

