# -*- encoding: utf-8 -*-

from logging import getLogger
from os.path import dirname, abspath, join

from wordspot.settings import Settings
from wordspot.svg import SvgHandler

logger = getLogger('Main')
FILE_LOCATION = dirname(abspath(__file__))


def main():
    Settings()
    logger.info("WordSpot started")

    SvgHandler(join(FILE_LOCATION, "..", "resources", "grouped_VAT_09671_Rs_SJakob.svg"))

if __name__ == "__main__":
    main()
