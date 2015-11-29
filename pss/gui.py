# -*- encoding: utf-8 -*-

from logging import getLogger

from matplotlib.pyplot import subplots, cm

gui_logger = getLogger("SymbolGroupDisplay")

SPACE = .02
POSITION = .98
FIG_POS = (3.5, 5.)
ROWS = 1
COLUMNS = 2
FONTSIZE = 20
NODESIZE = 15


class ImagePlot(object):  # pragma: no cover
    def __init__(self, symbol_group):
        ax1, ax2 = self.setup_figure(symbol_group.name)
        self.setup_subplot(ax1, symbol_group.original_array, "original")
        self.setup_subplot(ax2, symbol_group.skeleton_array, "skeleton", symbol_group.nodes)

    @staticmethod
    def setup_figure(name):
        fig, (ax1, ax2) = subplots(ROWS, COLUMNS, figsize=FIG_POS, sharex=True, sharey=True,
                                   subplot_kw={'adjustable': 'box-forced'})
        fig.canvas.set_window_title("name: [{}]".format(name))
        fig.subplots_adjust(wspace=SPACE, hspace=SPACE, top=POSITION,
                            bottom=SPACE, left=SPACE, right=POSITION)
        return ax1, ax2

    def setup_subplot(self, ax, array, title, nodes=None):
        ax.imshow(array, cmap=cm.gray)
        self.plot_nodes(ax, nodes)
        ax.axis('off')
        ax.set_title(title, fontsize=FONTSIZE)

    @staticmethod
    def plot_nodes(ax, nodes):
        if nodes is not None and len(nodes) > 0:
            for node in nodes:
                ax.plot(node.position.item(1), node.position.item(0), "yo", markersize=NODESIZE)


pn_logger = getLogger("PrintNodes")


class PrintNodes(object):   # pragma: no cover
    def __init__(self, symbol_group):
        self.symbol_group = symbol_group
        self.print_positions()

    def print_positions(self):
        for node in self.symbol_group.nodes:
            pn_logger.info(node)
        
    

