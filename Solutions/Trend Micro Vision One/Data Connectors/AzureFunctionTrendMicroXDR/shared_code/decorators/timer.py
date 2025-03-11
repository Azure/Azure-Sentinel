import time
from functools import wraps

from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)

logger = get_customized_json_logger()


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        elapsed = end - start

        logger.info(
            f'[timer] [{func.__name__}] took {elapsed} seconds to finish. start time:{start}, end time:{end}',
        )

        return result

    return wrapper
