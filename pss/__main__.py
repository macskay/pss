# -*- encoding: utf-8 -*-

from datetime import datetime
from logging import getLogger
from os.path import dirname, abspath, join

from pss.binimg import TargetBin, QueryBin
from pss.eval import Evaluation, PR
from pss.gui import GUIHandler
from pss.model import DistanceTransform, Query, Target
from pss.settings import Settings
from pss.svg import QuerySvg, TargetSvg

logger = getLogger('Main')
FILE_LOCATION = dirname(abspath(__file__))




def main():
    """
    Main entry point for the application to start the program from.
    """
    settings = Settings()
    scale = settings.options.scale
    limit = settings.options.limit
    index = settings.options.index

    starting_time = str(datetime.now())
    logger.info("PartStructuredSpotting started at %s", starting_time)

    """ Example SVG Usage """
    # svg_query = QuerySvg(join(FILE_LOCATION, "..", "resources", "grouped_VAT_10321_Vs_SJakob.svg"))
    # svg_target = TargetSvg(join(FILE_LOCATION, "..", "resources", "VAT_10321_Vs_SJakob.svg"))
    # query = Query(svg_query, index=index, scale=scale)
    # target = Target(svg_target, scale=scale)

    """ Example png Usage"""
    png_query = QueryBin(join(FILE_LOCATION, "..", "resources", "fox.png"), scale=scale)
    png_target = TargetBin(join(FILE_LOCATION, "..", "resources", "pangrams_dot.png"), scale=scale)
    query = Query(png_query, bin=True, scale=scale)
    target = Target(png_target, bin=True, scale=scale)

    distance_transform = DistanceTransform(query, target)

    evaluation = Evaluation(query, target, distance_transform, limit, scale=scale)

    gui_handler = GUIHandler()
    # gui_handler.display_query(query, index)
    gui_handler.display_target(target, index)
    # gui_handler.display_distance_transform(distance_transform, index)
    gui_handler.display_evaluation(evaluation, index)

    gui_handler.show()

    # precision_recall = PR(join(FILE_LOCATION, "..", "resources"))


if __name__ == "__main__":
    main()
