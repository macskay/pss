# -*- encoding: utf-8 -*-

from logging import getLogger
from os.path import dirname, abspath, join

from pss.settings import Settings
from pss.svg import SvgHandler

logger = getLogger('Main')
FILE_LOCATION = dirname(abspath(__file__))


def main():
    Settings()
    logger.info("PartStructuredSpotting started")

    SvgHandler(join(FILE_LOCATION, "..", "resources", "grouped_VAT_09671_Rs_SJakob.svg"))

if __name__ == "__main__":
    main()
