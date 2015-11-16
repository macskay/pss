# -*- encoding: utf-8 -*-
from logging import getLogger

from matplotlib.pyplot import subplots, cm

gui_logger = getLogger("SymbolGroupDisplay")


class ImagePlot(object):  # pragma: no cover
    def __init__(self, image):
        ax1, ax2 = self.setup_figure(image.name)
        self.setup_subplot(ax1, image.original_array, "original", image.original_corners)
        self.setup_subplot(ax2, image.skeleton_array, "skeleton", image.skeleton_corners)

    # TODO: get rid off magic numbers
    @staticmethod
    def setup_figure(name):
        fig, (ax1, ax2) = subplots(1, 2, figsize=(3.5, 5), sharex=True, sharey=True,
                                   subplot_kw={'adjustable': 'box-forced'})
        fig.canvas.set_window_title("name: [{}]".format(name))
        fig.subplots_adjust(wspace=0.02, hspace=0.02, top=0.98,
                            bottom=0.02, left=0.02, right=0.98)
        return ax1, ax2

    # TODO: get rid off magic numbers
    @staticmethod
    def setup_subplot(ax, array, title, corners=None):
        ax.imshow(array, cmap=cm.gray)
        if corners is not None:
            ax.plot(corners[:, 1], corners[:, 0], "r+", markersize=15)
        ax.axis('off')
        ax.set_title(title, fontsize=20)


