# -*- encoding: utf-8 -*-
from copy import deepcopy
from logging import getLogger

from matplotlib.pyplot import subplots, cm
from numpy import empty

gui_logger = getLogger("SymbolGroupDisplay")

SPACE = .02
POSITION = .98
FIG_POS = (3.5, 5.)
ROWS = 1
COLUMNS = 3
FONTSIZE = 20
NODESIZE = 15


class ImagePlot(object):  # pragma: no cover
    """
    This class is responsible for plotting the QImage.
    """
    def __init__(self, symbol_group):
        ax1, ax2, ax3 = self.setup_figure(symbol_group.name)
        self.setup_subplot(ax1, symbol_group.original_array, "original")
        self.setup_subplot(ax2, symbol_group.skeleton_array, "skeleton", symbol_group=symbol_group)

        root = symbol_group.root_node
        center_of_mass = symbol_group.center_of_mass
        skeleton_empty = empty(shape=symbol_group.skeleton_array.shape, dtype=bool)
        self.setup_subplot(ax3, skeleton_empty, "tree", root_node=root, center_of_mass=center_of_mass)

    @staticmethod
    def setup_figure(name):
        """
        This sets up the plot-figures, respectively the window.
        :param name: The name to set the windows title
        :return: The two empty subplots for the original image and the skeletonized one
        """
        fig, (ax1, ax2, ax3) = subplots(ROWS, COLUMNS, figsize=FIG_POS, sharex=True, sharey=True,
                                    subplot_kw={'adjustable': 'box-forced'})
        fig.canvas.set_window_title("name: [{}]".format(name))
        fig.subplots_adjust(wspace=SPACE, hspace=SPACE, top=POSITION,
                            bottom=SPACE, left=SPACE, right=POSITION)
        return ax1, ax2, ax3

    def setup_subplot(self, ax, array, title, symbol_group=None, root_node=None, center_of_mass=None):
        """
        This fills up the subplots
        :param ax: Empty subplot for the original image or the skeletonized image
        :param array: The array to fill up the subplot
        :param title: Title of the subplot
        :param nodes: Parameter to show given Nodes onto the subplot (optional)
        """
        ax.axis('on')
        ax.set_xlim([0, array.shape[1]])
        ax.set_ylim([array.shape[0], 0])
        ax.set_title(title, fontsize=FONTSIZE)

        if array is not None:
            ax.imshow(array, cmap=cm.gray)
        if symbol_group is not None:
            self.plot_nodes(ax, symbol_group.nodes)
        if root_node is not None:
            self.plot_center_of_mass(ax, center_of_mass)

            open_list = list()
            open_list.append(root_node)
            while len(open_list) > 0:
                current_node = open_list.pop()
                for child in current_node.children:
                    open_list.append(child)
                    self.plot_edge(ax, current_node, child)

            self.plot_root_node(ax, root_node)


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

    @staticmethod
    def plot_center_of_mass(ax, center_of_mass):
        """
        Plots the center of mass into a given subplot
        :param ax: Subplot to draw the center of mass into
        :param center_of_mass: Center of mass to draw to the subplot
        """
        if center_of_mass is not None:
            ax.plot(center_of_mass.position.item(1), center_of_mass.position.item(0), "r.", markersize=NODESIZE)

    @staticmethod
    def plot_root_node(ax, root_node):
        """
        Highlights the root node, which is the node closest to the center of mass
        :param ax: Subplot to draw the center of mass into
        :param root_node: Root-Node to highlight
        """
        if root_node is not None:
            ax.plot(root_node.position.item(1), root_node.position.item(0), "go", markersize=NODESIZE)

    def plot_edge(self, ax, parent, child):
        ax.plot([parent.position[1], child.position[1]], [parent.position[0], child.position[0]], "b-")
        ax.plot(child.position.item(1), child.position.item(0), "y.", markersize=NODESIZE)


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
        
    

