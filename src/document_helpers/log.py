import logging
import logging.handlers
import os

import coloredlogs


def get_logger(name, level, logfile="scripts.log"):

    # coloredlogs.install(
    #   fmt="%(asctime)s %(levelname)s %(name)s %(filename)s:%(funcName)s %(message)s",
    #   level=level,
    # )
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fmt = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s : %(message)s")

    # fh = logging.handlers.RotatingFileHandler(os.path.join(os.path.dirname(__file__), logfile), maxBytes=1025*500)
    # fh.setLevel(level)
    # fh.setFormatter(fmt)
    # logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger
