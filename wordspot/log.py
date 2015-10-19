# -*- encoding: utf-8 -*-

import logging

logger = logging.getLogger("Log")


def setup_log_level(debuglevel):  # pragma: no cover
    level_msg = "Debug-Level set to {}"
    if debuglevel == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
        logger.info(level_msg.format(debuglevel))
    elif debuglevel == "INFO":
        logging.basicConfig(level=logging.INFO)
        logger.info(level_msg.format(debuglevel))
    elif debuglevel == "WARNING":
        logging.basicConfig(level=logging.WARNING)
        logger.warning(level_msg.format(debuglevel))
    elif debuglevel == "ERROR":
        logging.basicConfig(level=logging.ERROR)
        logger.error(level_msg.format(debuglevel))
    elif debuglevel == "CRITICAL":
        logging.basicConfig(level=logging.CRITICAL)
        logger.critical(level_msg.format(debuglevel))
    else:
        pass
