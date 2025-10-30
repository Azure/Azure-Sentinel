import logging

from pythonjsonlogger import jsonlogger
from shared_code import configurations
from shared_code.trace_utils.trace import trace_manager


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        log_record['logger_name'] = log_record['name']
        log_record['func_name'] = log_record['funcName']
        log_record['level'] = log_record['levelname']

        del log_record['name']
        del log_record['funcName']
        del log_record['levelname']


def init_id_and_version():
    current_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = current_factory(*args, **kwargs)

        record.trace_id = trace_manager.trace_id
        record.task_id = trace_manager.task_id
        record.version = configurations.get_user_agent()

        return record

    logging.setLogRecordFactory(record_factory)


def get_customized_json_logger(logger_name=None):
    '''
    The caller can bring any logger name if needed.
    '''
    init_id_and_version()

    logging.basicConfig()
    root = logging.getLogger()
    log_handler = root.handlers[0]

    log_format = '%(asctime) %(levelname) %(name) %(funcName) %(message)'
    formatter = CustomJsonFormatter(fmt=log_format)
    log_handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.handlers = [log_handler]

    # avoid duplicated logger print
    logger.propagate = False
    return logger
