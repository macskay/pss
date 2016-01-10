# -*- encoding: utf-8 -*-

from datetime import datetime
from logging import getLogger
from os.path import dirname, abspath, join
from sys import setrecursionlimit

from pss.settings import Settings
from pss.svg import SvgHandler

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

    # SvgHandler(join(FILE_LOCATION, "..", "resources", "grouped_VAT_09671_Rs_SJakob.svg"))
    SvgHandler(join(FILE_LOCATION, "..", "resources", "test_query.svg"))

if __name__ == "__main__":
    main()
