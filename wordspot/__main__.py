# -*- encoding: utf-8 -*-

import logging
from wordspot.settings import Settings

logger = logging.getLogger('Main')


def main():
    Settings()
    logger.info("WordSpot started")

if __name__ == "__main__":
    main()
