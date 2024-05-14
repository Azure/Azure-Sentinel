import logging
import sys
from logging.handlers import RotatingFileHandler

from .global_variables import LOGGER_FORMAT, LOGGER_MAX_FILE_SIZE, LOGGER_NAME_PREFIX


class FncClientLogger:
    def set_level(self, level):
        raise NotImplementedError()

    def set_console_logging(self, enable: bool = False):
        pass

    def set_log_to_file(self, enable: bool = False):
        pass

    def critical(self, log: str):
        raise NotImplementedError()

    def error(self, log: str):
        raise NotImplementedError()

    def warning(self, log: str):
        raise NotImplementedError()

    def info(self, log: str):
        raise NotImplementedError()

    def debug(self, log: str):
        raise NotImplementedError()


class BasicLogger(FncClientLogger):
    FORMATTER = logging.Formatter(LOGGER_FORMAT)
    NAME = LOGGER_NAME_PREFIX
    MAX_FILE_SIZE = LOGGER_MAX_FILE_SIZE

    def __init__(self, name: str = NAME, level: str = logging.INFO):
        self.name = name
        self.file_handler = None
        self.console_handler = None
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        logging.info('Logging Initialized')

    def set_level(self, level):
        if self.level != level:
            self.level = level
            self.logger.setLevel(level)

    def set_log_to_file(self, enable: bool = False):
        if not self.logger:
            return

        if not enable and self.file_handler:
            self.logger.removeHandler(hdlr=self.file_handler)
            self.file_handler = None

        if enable and not self.file_handler:
            self.file_handler = self._get_file_handler()
            self.logger.addHandler(self.file_handler)

    def set_console_logging(self, enable: bool = False):
        if not self.logger:
            return

        if enable and not self.console_handler:
            self.console_handler = logging.StreamHandler(sys.stdout)
            self.console_handler.setFormatter(self.FORMATTER)
            self.logger.addHandler(self.console_handler)

        if not enable and self.console_handler:
            self.logger.removeHandler(self.console_handler)
            self.console_handler = None

    def _get_file_handler(self):
        file_name: str = f"./{self.name.lower()}.log"
        file_handler = RotatingFileHandler(file_name, maxBytes=self.MAX_FILE_SIZE, backupCount=10)
        file_handler.setFormatter(self.FORMATTER)
        return file_handler

    def critical(self, log: str):
        self.logger.critical(log)

    def error(self, log: str):
        self.logger.error(log)

    def warning(self, log: str):
        self.logger.warning(log)

    def info(self, log: str):
        self.logger.info(log)

    def debug(self, log: str):
        self.logger.debug(log)
