"""Handle the logger."""
import logging
import os
import sys

log_level = (os.environ.get("LogLevel") or "INFO").upper()

applogger = logging.getLogger("azure")
applogger.setLevel(getattr(logging, log_level, logging.INFO) if log_level in ("DEBUG", "INFO", "WARNING", "ERROR") else logging.INFO)
if not any(isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout for h in applogger.handlers):
    applogger.addHandler(logging.StreamHandler(stream=sys.stdout))
