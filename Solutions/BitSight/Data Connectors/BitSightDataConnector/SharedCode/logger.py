"""Handle the logger."""
import logging
import sys
import os

log_level = os.environ.get('LogLevel')
if log_level is None:
    log_level = "INFO"

try:
    applogger = logging.getLogger('azure')
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
    applogger.setLevel(logging.INFO)
finally:
    handler = logging.StreamHandler(stream=sys.stdout)
    applogger.addHandler(handler)
