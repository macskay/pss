# -*- encoding: utf-8 -*-

import logging
from wordspot.configuration import Configuration

logger = logging.getLogger('Main')


def main():
    Configuration()
    logger.info("WordSpot started")


if __name__ == "__main__":
    main()
