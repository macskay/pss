from numpy import where, argsort
from scipy.ndimage import minimum_filter

LIMIT = 20


class Evaluation(object):
    def __init__(self, query, target, dt):
        self.query = query
        self.target = target
        self.dt = dt

        self.minimum = self.find_local_minima()
        self.found_symbols = self.extract_found_symbols()

    def find_local_minima(self):
        res = minimum_filter(self.dt.sum_dt, size=10)
        x, y = where(res == self.dt.sum_dt)
        order = argsort(self.dt.sum_dt[x, y])
        x, y = x[order], y[order]
        return x[0:LIMIT], y[0:LIMIT]

    def extract_found_symbols(self):
        found_symbols = list()

        height, width = self.query.original_array.shape

        for (i, j) in zip(*self.minimum):
            box = self.target.original_array[i - height // 2:i + height // 2, j - width // 2:j + width // 2]
            found_symbols.append(box)

        return found_symbols
