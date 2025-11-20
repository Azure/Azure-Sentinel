"""This __init__ file will be called by Orchastrator function to ingest data in Log Analytics Workspace."""

import inspect
import time

from SharedCode.logger import applogger
from SharedCode.consts import LOGS_STARTS_WITH
from .extrahop import ExtraHop
from SharedCode.extrahop_exceptions import ExtraHopException


def main(name: str) -> str:
    """Start Execution of Activity Function.

    Args:
        name (dict): data received via Dataminr RTAP.

    Returns:
        str: status message of activity function.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        applogger.debug("{}(method={}) Activity function called.".format(LOGS_STARTS_WITH, __method_name))
        start = time.time()
        extrahop_obj = ExtraHop()
        status = extrahop_obj.parse_data_and_send_to_sentinel(name)
        end = time.time()
        applogger.info(
            "{}(method={}) :time taken for data ingestion is {} sec".format(
                LOGS_STARTS_WITH, __method_name, int(end - start)
            )
        )
    except ExtraHopException as err:
        return err
    return status
