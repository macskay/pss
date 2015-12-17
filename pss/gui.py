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
    """
    This class is responsible for plotting the QImage.
    """
    def __init__(self, symbol_group):
        ax1, ax2 = self.setup_figure(symbol_group.name)
        self.setup_subplot(ax1, symbol_group.original_array, "original")
        self.setup_subplot(ax2, symbol_group.skeleton_array, "skeleton", symbol_group.nodes)

    @staticmethod
    def setup_figure(name):
        """
        This sets up the plot-figures, respectively the window.
        :param name: The name to set the windows title
        :return: The two empty subplots for the original image and the skeletonized one
        """
        fig, (ax1, ax2) = subplots(ROWS, COLUMNS, figsize=FIG_POS, sharex=True, sharey=True,
                                   subplot_kw={'adjustable': 'box-forced'})
        fig.canvas.set_window_title("name: [{}]".format(name))
        fig.subplots_adjust(wspace=SPACE, hspace=SPACE, top=POSITION,
                            bottom=SPACE, left=SPACE, right=POSITION)
        return ax1, ax2

    def setup_subplot(self, ax, array, title, nodes=None):
        """
        This fills up the subplots
        :param ax: Empty subplot for the original image or the skeletonized image
        :param array: The array to fill up the subplot
        :param title: Title of the subplot
        :param nodes: Parameter to show given Nodes onto the subplot (optional)
        """
        ax.imshow(array, cmap=cm.gray)
        self.plot_nodes(ax, nodes)
        ax.axis('off')
        ax.set_title(title, fontsize=FONTSIZE)

    @staticmethod
    def plot_nodes(ax, nodes):
        """
        Plots the Nodes onto a subplot
        :param ax: Subplot to plot onto
        :param nodes: Nodes-Array to draw the nodes for
        """
        if nodes is not None and len(nodes) > 0:
            for node in nodes:
                ax.plot(node.position.item(1), node.position.item(0), "yo", markersize=NODESIZE)


pn_logger = getLogger("PrintNodes")


class PrintNodes(object):   # pragma: no cover
    """
    Prints the Nodes locations to the log
    """
    def __init__(self, symbol_group):
        """
        Inititialized the PrintNodes-object for a given SymbolGroup
        :param symbol_group: SymbolGroup, which contains the Nodes to print into the log
        """
        self.symbol_group = symbol_group
        self.print_positions()

    def print_positions(self):
        """
        Prints the Nodes
        """
        for node in self.symbol_group.nodes:
            pn_logger.info(node)
        
    

