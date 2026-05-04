"""Logger configuration for Google SecOps connector."""

import logging
import sys

from . import consts

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

applogger = logging.getLogger(consts.LOG_PREFIX)
log_level = LOG_LEVELS.get(consts.LOG_LEVEL.upper(), logging.INFO)
applogger.setLevel(log_level)

handler = logging.StreamHandler(stream=sys.stdout)
applogger.addHandler(handler)
