# -*- encoding: utf-8 -*-

import logging
import argparse

import log

logger = logging.getLogger('Main')


def main():
    parser = setup_args_parser()
    opts = get_options(parser)
    handle_opts(opts)

    logger.info("WordSpot started")


def setup_args_parser():
    return argparse.ArgumentParser(
        prog="WordSpot",
        add_help=True
    )


def get_options(parser):
    parser.add_argument("-dl", "--debuglevel", nargs=1,
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Sets the level of information shown in the logger")
    return parser.parse_args()


def handle_opts(opts):
    handle_debuglevel(opts)


def handle_debuglevel(opts):
    if opts.debuglevel:
        log.setup_log_level(opts.debuglevel[0])

if __name__ == "__main__":
    main()
