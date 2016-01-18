# -*- encoding: utf-8 -*-

from datetime import datetime
from logging import getLogger
from os.path import dirname, abspath, join
from sys import setrecursionlimit

from pss.gui import GUIHandler
from pss.model import DistanceTransform, Query, Target
from pss.settings import Settings
from pss.svg import QuerySVG, TargetSVG, QueryPNG

logger = getLogger('Main')
FILE_LOCATION = dirname(abspath(__file__))


def main():
    """
    Main entry point for the application to start the program from.
    """
    Settings()
    starting_time = str(datetime.now())
    logger.info("PartStructuredSpotting started at %s", starting_time)
    setrecursionlimit(1000000)

    # svg_target = TargetSVG(join(FILE_LOCATION, "..", "resources", "test_target.svg"))
    # svg_query = QuerySVG(join(FILE_LOCATION, "..", "resources", "test_query.svg"))
    png_query = QueryPNG(join(FILE_LOCATION, "..", "resources", "test_query.png"))

    # query = Query(svg_query)
    query = Query(png_query, png=True)
    # target = Target(svg_target.renderer)
    # distance_transform = DistanceTransform(query, target)

    gui_handler = GUIHandler()

    # gui_handler.display_query(query)
    # gui_handler.display_target(target)
    # gui_handler.display_distance_transform(distance_transform)
    # gui_handler.show()

if __name__ == "__main__":
    main()
