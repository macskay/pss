from itertools import chain

from math import isnan
from numpy import argsort, nonzero, genfromtxt
from scipy.ndimage import minimum_filter
from sklearn.metrics import precision_recall_curve
from matplotlib import pyplot as plt


class Evaluation(object):
    """
    This class calculates the minima and extracts the symbols from the target tablet.
    """
    def __init__(self, query, target, dt, limit, scale=1):
        self.query = query
        self.target = target
        self.dt = dt
        self.limit = limit

        self.minimum = self.find_local_minima()
        self.found_symbols = self.extract_found_symbols()

    def find_local_minima(self):
        """
        This method returns the top n minima in two lists for x and y respectively.
        n is set by self.limit
        :return: x, y lists
        """
        size = min(self.dt.sum_dt.shape[1], self.dt.sum_dt.shape[0]) // 10

        res = minimum_filter(self.dt.sum_dt, size=size, mode="nearest")
        x, y = nonzero(res == self.dt.sum_dt)
        order = argsort(self.dt.sum_dt[x, y])
        x, y = x[order], y[order]
        return x[0:self.limit], y[0:self.limit]

    def extract_found_symbols(self):
        """
        Extracts the symbols at the local minima of the target tablet
        :return: List of symbols represented as boolean arrays and their respective energies
        """
        found_symbols = list()

        height, width = self.query.original_array.shape

        for (y, x) in zip(*self.minimum):
            begin_bbox_y = y - self.query.root_node.position[0]
            begin_bbox_x = x - self.query.root_node.position[1]
            box = self.target.original_array[begin_bbox_y:begin_bbox_y + height, begin_bbox_x:begin_bbox_x + width]
            found_symbols.append((box, self.dt.sum_dt[y, x]))

        return found_symbols
