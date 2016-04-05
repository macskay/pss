# -*- encoding: utf-8 -*-

from datetime import datetime
from logging import getLogger
from os.path import dirname, abspath, join
from sys import exit

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
    query_path = settings.options.query
    target_path = settings.options.target

    starting_time = str(datetime.now())
    logger.info("PartStructuredSpotting started at %s", starting_time)

    query = read_query_file(index, query_path, scale)
    target = read_target_file(scale, target_path)

    distance_transform = DistanceTransform(query, target)

    evaluation = Evaluation(query, target, distance_transform, limit, scale=scale)

    gui_handler = GUIHandler()
    gui_handler.display_query(query, index)
    gui_handler.display_target(target, index)
    gui_handler.display_distance_transform(distance_transform, index)
    gui_handler.display_evaluation(evaluation, index)

    gui_handler.show()


def read_target_file(scale, target_path):
    """
    This method is responsible for reading in the target file and returning a Target-object
    :param scale: Scale of the query
    :param target_path: Path to the target-file starting from the resources-folder
    :return: Target Object
    """
    if target_path.endswith(".svg"):
        svg_target = TargetSvg(join(FILE_LOCATION, "..", "resources", target_path))
        return Target(svg_target, scale=scale)
    elif target_path.endswith(".png"):
        png_target = TargetBin(join(FILE_LOCATION, "..", "resources", target_path), scale=scale)
        return Target(png_target, bin=True, scale=scale)
    else:
        logger.critical("Target can only be of PNG or SVG format!")
        exit(0)


def read_query_file(index, query_path, scale):
    """
    This method is responsible for reading in the query file and returning a Query-object
    :param index: Index for the query in the SVG file
    :param scale: Scale of the query
    :param query_path: Path to the query-file starting from the resources-folder
    :return: Query Object
    """
    if query_path.endswith(".svg"):
        svg_query = QuerySvg(join(FILE_LOCATION, "..", "resources", query_path))
        return Query(svg_query, index=index, scale=scale)
    elif query_path.endswith(".png"):
        png_query = QueryBin(join(FILE_LOCATION, "..", "resources", query_path), scale=scale)
        return Query(png_query, bin=True, scale=scale)
    else:
        logger.critical("Query can only be of PNG or SVG format!")
        exit(0)

if __name__ == "__main__":
    main()
