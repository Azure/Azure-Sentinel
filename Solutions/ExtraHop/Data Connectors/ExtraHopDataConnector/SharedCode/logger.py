"""Handle the logger."""
import logging
import sys
from .consts import DEFAULT_LOG_LEVEL, LOG_LEVEL

default_log_level = DEFAULT_LOG_LEVEL
log_level = LOG_LEVEL
applogger = None
applogger = logging.getLogger("azure")
log_level = log_level.upper()
numeric_level = getattr(logging, log_level, default_log_level)
applogger.setLevel(level=numeric_level)
handler = logging.StreamHandler(stream=sys.stdout)
applogger.addHandler(handler)
