# -*- encoding: utf-8 -*-

import logging
from argparse import ArgumentParser

configLogger = logging.getLogger('Configuration')


class Configuration(object):
    def __init__(self):
        self.arg_parser = self.setup_arg_parser()
        self.setup_arg_options()

    @staticmethod
    def setup_arg_parser():
        return ArgumentParser(
            prog='WordSpot',
            add_help=True
        )

    def setup_arg_options(self):
        self.add_arguments()
        ArgumentListener(self.arg_parser)

    def add_arguments(self):
        self.arg_parser.add_argument("-v", "--verbose",
                                     help="Activates verbose mode (DEBUG-logging)", action="store_true")


class ArgumentListener(object):
    def __init__(self, arg_parser):
        self.arg_parser = arg_parser
        self.options = self.arg_parser.parse_args()
        self.setup_option_handler()

    def setup_option_handler(self):
        self.setup_verbose_mode()

    def setup_verbose_mode(self):
        debuglevel = logging.INFO
        level_msg = "INACTIVE"
        if self.options.verbose:
            debuglevel = logging.DEBUG
            level_msg = "ACTIVE"

        logging.basicConfig(level=debuglevel)
        configLogger.info("Verbose-Mode {}".format(level_msg))
