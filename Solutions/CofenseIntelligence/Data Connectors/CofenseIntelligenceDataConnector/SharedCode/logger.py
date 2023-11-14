"""Handle the logger."""
import logging
import sys
from ..SharedCode import consts

log_level = consts.LOG_LEVEL
try:
    applogger = logging.getLogger("azure")
    log_level = log_level.upper()
    if log_level == "DEBUG":
        applogger.setLevel(logging.DEBUG)

    elif log_level == "INFO":
        applogger.setLevel(logging.INFO)

    elif log_level == "WARNING":
        applogger.setLevel(logging.WARNING)

    elif log_level == "ERROR":
        applogger.setLevel(logging.ERROR)
except Exception:
    applogger.info(
        "{} : no log level selected hance setting log level as info.".format(
            consts.LOGS_STARTS_WITH
        )
    )
    applogger.setLevel(logging.INFO)
finally:
    handler = logging.StreamHandler(stream=sys.stdout)
    applogger.addHandler(handler)
