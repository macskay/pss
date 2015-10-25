# -*- encoding: utf-8 -*-

from logging import getLogger

from wordspot.settings import Settings

logger = getLogger('Main')


def main():
    Settings()
    logger.info("WordSpot started")

if __name__ == "__main__":
    main()
