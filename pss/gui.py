# -*- encoding: utf-8 -*-
from functools import reduce  # pylint:disable=redefined-builtin
from logging import getLogger

from PyQt4 import QtGui

gui_logger = getLogger("GUI")


class SymbolGroupWidget(QtGui.QLabel):  # pragma: no cover pylint:disable=super-on-old-class
    def __init__(self, symbol_group):
        gui_logger.info("Creating SymbolGroup-Widget")
        super(SymbolGroupWidget, self).__init__()
        self.setWindowTitle("SymbolGroup")

        self.show_as_image(symbol_group)

    def show_as_image(self, symbol_group):
        gui_logger.info("Opening symbol group image")
        image = self.rasterize_symbol_group(symbol_group)
        self.setPixmap(QtGui.QPixmap(image))
        self.show()

    def rasterize_symbol_group(self, symbol_group):
        gui_logger.info("Rasterizing symbol group")
        bounding_box = self.create_bounding_box(symbol_group)
        image = self.create_empty_image(bounding_box)
        self.try_to_fill_image_with_paths(symbol_group, image, bounding_box)
        return image

    def create_bounding_box(self, symbol_group):
        gui_logger.info("Creating bounding box")
        return reduce(lambda xs, x: xs | x.boundingRect(),
                      symbol_group[1:],
                      symbol_group[0].boundingRect())

    def create_empty_image(self, bounding_box):
        image = QtGui.QImage(bounding_box.width()*5, bounding_box.height()*5,
                             QtGui.QImage.Format_RGB32)
        image.fill(QtGui.QColor("White"))
        return image

    def try_to_fill_image_with_paths(self, symbol_group, image, bounding_box):
        qpainter = QtGui.QPainter(image)
        try:
            self.fill_image_with_paths(symbol_group, qpainter, bounding_box)
        finally:
            qpainter.end()

    def fill_image_with_paths(self, symbol_group, qpainter, bounding_box):
        gui_logger.info("Filling image with paths")
        qpainter.setBrush(QtGui.QColor("Black"))
        qpainter.setPen(QtGui.QColor("Black"))
        qpainter.scale(5, 5)
        qpainter.translate(-bounding_box.topLeft())
        for path in symbol_group:
            qpainter.drawPath(path)
