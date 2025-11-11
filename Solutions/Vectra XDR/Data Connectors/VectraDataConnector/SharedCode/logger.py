"""Handle the logger."""
import logging
import sys
from . import consts

default_log_level = consts.DEFAULT_LOG_LEVEL
log_level = consts.LOG_LEVEL
applogger = None
applogger = logging.getLogger("azure")
log_level = log_level.upper()
numeric_level = getattr(logging, log_level, default_log_level)
applogger.setLevel(level=numeric_level)
handler = logging.StreamHandler(stream=sys.stdout)
applogger.addHandler(handler)
