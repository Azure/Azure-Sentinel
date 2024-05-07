import logging

from fnc.logger import FncClientLogger
from fnc.global_variables import LOGGER_NAME_PREFIX

class Logger(FncClientLogger):
    NAME = LOGGER_NAME_PREFIX
    
    def __init__(self, name: str = NAME, level: str = logging.INFO):
        self.name = name
        self.console_handler = None
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        logging.info('Logging Initialized')
        
    def set_level(self, level):
        self.level = level
        self.logger.setLevel(level)
            
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
        
    