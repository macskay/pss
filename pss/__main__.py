# -*- encoding: utf-8 -*-

from datetime import datetime
from logging import getLogger
from os.path import dirname, abspath, join

from pss.gui import GUIHandler
from pss.model import DistanceTransform, Query, Target
from pss.png import TargetPNG
from pss.settings import Settings
from pss.svg import QuerySVG

logger = getLogger('Main')
FILE_LOCATION = dirname(abspath(__file__))


def main():
    """
    Main entry point for the application to start the program from.
    """
    settings = Settings()
    scale = settings.options.scale

    starting_time = str(datetime.now())
    logger.info("PartStructuredSpotting started at %s", starting_time)

    """ Example SVG Usage """
    svg_query = QuerySVG(join(FILE_LOCATION, "..", "resources", "test_query.svg"))
    # svg_target = TargetSVG(join(FILE_LOCATION, "..", "resources", "VAT_09671_Rs_SJakob.svg"))
    query = Query(svg_query, scale=scale)
    # target = Target(svg_target.renderer, scale=scale)

    """ Example png Usage"""
    # png_query = QueryPNG(join(FILE_LOCATION, "..", "resources", "test_query.png"), scale=scale)
    png_target = TargetPNG(join(FILE_LOCATION, "..", "resources", "VAT_09671_Rs_SJakob.png"), scale=scale)
    # query = Query(png_query, png=True, scale=scale)
    target = Target(png_target, png=True, scale=scale)

    distance_transform = DistanceTransform(query, target)

    gui_handler = GUIHandler()
    gui_handler.display_query(query)
    gui_handler.display_target(target)
    gui_handler.display_distance_transform(distance_transform)
    gui_handler.show()

if __name__ == "__main__":
    main()
