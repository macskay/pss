from numpy import argsort, nonzero
from scipy.ndimage import minimum_filter


class Evaluation(object):
    def __init__(self, query, target, dt, limit):
        self.query = query
        self.target = target
        self.dt = dt
        self.limit = limit

        self.minimum = self.find_local_minima()
        self.found_symbols = self.extract_found_symbols()

    def find_local_minima(self):
        size = min(self.dt.sum_dt.shape[0], self.dt.sum_dt.shape[1]) / 10

        res = minimum_filter(self.dt.sum_dt, size=size, mode="nearest")
        x, y = nonzero(res == self.dt.sum_dt)
        order = argsort(self.dt.sum_dt[x, y])
        x, y = x[order], y[order]
        return x[0:self.limit], y[0:self.limit]

    def extract_found_symbols(self):
        found_symbols = list()

        width, height = self.query.original_array.shape

        for (i, j) in zip(*self.minimum):
            begin_bbox_x = i - self.query.root_node.position[0]
            begin_bbox_y = j - self.query.root_node.position[1]
            box = self.target.original_array[begin_bbox_x:begin_bbox_x + height * 1.1,
                  begin_bbox_y:begin_bbox_y + height * 1.1]
            found_symbols.append(box)

        return found_symbols
