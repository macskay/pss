# -*- encoding: utf-8 -*-
from logging import getLogger

from matplotlib.pyplot import subplots, cm
from numpy import empty, nanmax, nanmin

gui_logger = getLogger("SymbolGroupDisplay")

SPACE = .02
POSITION = .98
FIG_POS = (3.5, 5.)
ROWS = 1
COLUMNS = 1
FONTSIZE = 20
NODESIZE = 15


class ImagePlot(object):  # pragma: no cover
    """
    This class is responsible for plotting the QImage.
    """

    def __init__(self, symbol_group):
        self.create_original_image_figure(symbol_group)
        self.create_skeleton_figure(symbol_group)
        self.create_distance_transform_figure(symbol_group)
        self.create_tree_figure(symbol_group)

    def create_distance_transform_figure(self, symbol_group):
        ax = self.setup_figure(symbol_group.name)
        self.setup_plot(ax, symbol_group.original_array, "distance transform (single node)")
        dt_min, dt_max = nanmin(symbol_group.distance_transform), nanmax(symbol_group.distance_transform)
        self.draw_distance_transform(ax, symbol_group.distance_transform, dt_min, dt_max)

    def create_skeleton_figure(self, symbol_group):
        ax = self.setup_figure(symbol_group.name)
        self.setup_plot(ax, symbol_group.original_array, "skeleton")
        self.draw_skeleton_image(ax, symbol_group.skeleton_array, symbol_group)

    def create_original_image_figure(self, symbol_group):
        ax = self.setup_figure(symbol_group.name)
        self.setup_plot(ax, symbol_group.original_array, "original")
        self.draw_array(ax, symbol_group.original_array)

    def create_tree_figure(self, symbol_group):
        ax = self.setup_figure(symbol_group.name)
        self.setup_plot(ax, symbol_group.original_array, "original")
        root_node = symbol_group.root_node
        center_of_mass = symbol_group.center_of_mass
        self.draw_tree_image(ax, symbol_group.original_array, root_node, center_of_mass)

    @staticmethod
    def setup_figure(name):
        """
        This sets up the plot-figures, respectively the window.
        :param name: The name to set the windows title
        :return: The two empty subplots for the original image and the skeletonized one
        """
        fig, ax = subplots(ROWS, COLUMNS, figsize=FIG_POS, sharex=True, sharey=True,
                                        subplot_kw={'adjustable': 'box-forced'})
        fig.canvas.set_window_title("name: [{}]".format(name))
        fig.subplots_adjust(wspace=SPACE, hspace=SPACE, top=POSITION,
                            bottom=SPACE, left=SPACE, right=POSITION)
        return ax

    @staticmethod
    def setup_plot(ax, array, title):
        """
        :param ax: Empty subplot for the original image or the skeletonized image
        :param array: The array to fill up the subplot
        :param title: Title of the subplot

        This fills up the subplots
        """
        ax.axis('on')
        ax.set_xlim([0, array.shape[1]])
        ax.set_ylim([array.shape[0], 0])
        ax.set_title(title, fontsize=FONTSIZE)

    @staticmethod
    def draw_array(ax, array):
        """
        Fills the AxisSubplot with the array to draw
        :param ax: AxisSubplot to draw on
        :param array: Array to draw onto AxisSubplot
        """
        ax.imshow(array, cmap=cm.gray)

    def draw_skeleton_image(self, ax, array, symbol_group):
        """
        Draws skeletonized version of the original array
        :param ax: AxisSubplot to draw on
        :param array: Skeletonized-Array to draw onto AxisSubplot
        :param symbol_group: SymbolGroup which holds all the nodes to draw
        """
        self.draw_array(ax, array)
        self.plot_nodes(ax, symbol_group.nodes)

    def draw_tree_image(self, ax, emptied_array, root_node, center_of_mass):
        """
        Draws tree
        :param ax: AxisSubplot to draw on
        :param emptied_array: Background for Tree-Image
        :param root_node: Root-Node (is drawn green)
        :param center_of_mass: Center-Of-Mass NOde (is drawn red)
        """
        self.draw_array(ax, emptied_array)
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
        :param ax: Subplot to draw the root node into
        :param root_node: Root-Node to highlight
        """
        if root_node is not None:
            ax.plot(root_node.position.item(1), root_node.position.item(0), "go", markersize=NODESIZE)

    @staticmethod
    def plot_edge(ax, parent, child):
        """
        This plots edge between parent-child relation
        :param ax: Subplot to draw the edge into
        :param parent: Parent of the relation
        :param child: Child of the Relation
        """
        ax.plot([parent.position[1], child.position[1]], [parent.position[0], child.position[0]], "b-")
        ax.plot(child.position.item(1), child.position.item(0), "y.", markersize=NODESIZE)

    def draw_distance_transform(self, ax1, distance_transform, vmin, vmax):
        ax1.imshow(distance_transform, cmap=cm.jet, vmin=vmin, vmax=vmax)


pn_logger = getLogger("PrintNodes")


class PrintNodes(object):  # pragma: no cover
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
