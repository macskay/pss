# -*- encoding: utf-8 -*-
from logging import getLogger

from matplotlib.pyplot import subplots, cm, show
from numpy import nanmax, nanmin

gui_logger = getLogger("SymbolGroupDisplay")

SPACE = .02
POSITION = .98
FIG_POS = (16, 9)
ROWS = 1
COLUMNS = 1
FONTSIZE = 20
NODESIZE = 10
DIVISOR = 12


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


def draw_array(ax, array):
    """
    Fills the AxisSubplot with the array to draw
    :param ax: AxisSubplot to draw on
    :param array: Array to draw onto AxisSubplot
    """
    ax.imshow(array, cmap=cm.gray)


class GUIHandler(object):
    """
    This class starts up all the gui wanted.

    """

    def __init__(self):
        gui_logger.info("GUIHandler started")

    @staticmethod
    def display_query(query):  # pragma: no cover
        """
        Plots the query entered in different forms
        :param query: The query image to plot
        """
        QueryPlot(query)

    @staticmethod
    def display_target(target):
        TargetPlot(target)

    @staticmethod
    def display_distance_transform(target):
        """
        Plots the summed up distance transform for the target image
        :param target: TargetDistanceTransform-object, which holds summed up distance transform
        """
        DistanceTransformPlot(target)

    @staticmethod
    def show():
        show()


class TargetPlot(object):
    def __init__(self, target):
        self.create_target_figure("Target", target.original_array, "Target")

    def create_target_figure(self, name, original_array, title):
        ax = setup_figure(name)
        setup_plot(ax, original_array, title)
        self.draw_target_image(ax, original_array)

    @staticmethod
    def draw_target_image(ax, target):
        draw_array(ax, target)


class DistanceTransformPlot(object):
    def __init__(self, target):
        self.create_distance_transform_figure("DT", target.sum_dt, "Distance Transform")

    def create_distance_transform_figure(self, name, dt, title):
        ax = setup_figure(name)
        setup_plot(ax, dt, title)
        dt_min, dt_max = nanmin(dt), nanmax(dt)
        self.draw_distance_transform(ax, dt, dt_min, (dt_max + dt_min) / DIVISOR)

    @staticmethod
    def draw_distance_transform(ax, dt, vmin, vmax):
        ax.imshow(dt, cmap=cm.jet, vmin=vmin, vmax=vmax)


class QueryPlot(object):  # pragma: no cover
    """
    This class is responsible for plotting the Query.
    """

    def __init__(self, query):
        self.create_original_image_figure(query)
        self.create_skeleton_figure(query)
        self.create_tree_figure(query)

    def create_skeleton_figure(self, query):
        ax = setup_figure(query.name)
        setup_plot(ax, query.original_array, "skeleton")
        self.draw_skeleton_image(ax, query.skeleton)

    def create_original_image_figure(self, query):
        ax = setup_figure(query.name)
        setup_plot(ax, query.original_array, "original")
        draw_array(ax, query.original_array)

    def create_tree_figure(self, query):
        ax = setup_figure(query.name)
        setup_plot(ax, query.original_array, "tree")
        root_node = query.root_node
        center_of_mass = query.center_of_mass
        self.draw_tree_image(ax, root_node, center_of_mass)

    def draw_skeleton_image(self, ax, array):
        """
        Draws skeletonized version of the original array
        :param ax: AxisSubplot to draw on
        :param array: Skeletonized-Array to draw onto AxisSubplot
        """
        draw_array(ax, array)

    def draw_tree_image(self, ax, root_node, center_of_mass):
        """
        Draws tree
        :param ax: AxisSubplot to draw on
        :param root_node: Root-Node (is drawn green)
        :param center_of_mass: Center-Of-Mass Node (is drawn red)
        """
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


pn_logger = getLogger("PrintNodes")


class PrintNodes(object):  # pragma: no cover
    """
    Prints the Nodes locations to the log
    """

    def __init__(self, symbol_group):
        """
        Initialized the PrintNodes-object for a given SymbolGroup
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
