# -*- encoding: utf-8 -*-

from os.path import isfile

from external.elka_svg import parse


class SvgHandler(object):
    def __init__(self, path, infix=""):
        """
        :param path: Path to the SVG-file (required)
        :param infix: Infix to look for in svg-file (default: "")
        :raise FileNotFoundError: This is raised, when an invalid svg file is passed.
        """
        if not isfile(path):
            raise FileNotFoundError
        self.names, self.symbol_groups = zip(*parse(infix, path))

    # TODO: add thinner (from skimage.morphology import merdial_axis)
    # TODO: add GUI class to show image (reference this class, calls pathhs to create image on QtApplicaiton)
