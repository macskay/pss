# -*- encoding: utf-8 -*-
from logging import getLogger

from matplotlib.pyplot import subplots, cm

gui_logger = getLogger("SymbolGroupDisplay")


class ImagePlot(object):  # pragma: no cover
    def __init__(self, image):
        ax1, ax2, fig = self.setup_figure(image.name)
        self.setup_subplot(ax1, image.original_array, "original")
        self.setup_subplot(ax2, image.skeleton_array, "skeleton")

    def setup_figure(self, name):
        fig, (ax1, ax2) = subplots(1, 2, figsize=(3.5, 5), sharex=True, sharey=True,
                                   subplot_kw={'adjustable': 'box-forced'})
        fig.canvas.set_window_title("name: [{}]".format(name))
        fig.subplots_adjust(wspace=0.02, hspace=0.02, top=0.98,
                            bottom=0.02, left=0.02, right=0.98)
        return ax1, ax2, fig

    def setup_subplot(self, ax, array, title):
        ax.imshow(array, cmap=cm.gray)
        ax.axis('off')
        ax.set_title(title, fontsize=20)


