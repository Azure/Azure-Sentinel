"""Handle the logger."""

import logging
import sys
from . import consts

log_level = consts.LOG_LEVEL

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

try:
    applogger = logging.getLogger("azure")
    applogger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
except Exception:
    applogger.setLevel(logging.INFO)
finally:
    handler = logging.StreamHandler(stream=sys.stdout)
    applogger.addHandler(handler)
