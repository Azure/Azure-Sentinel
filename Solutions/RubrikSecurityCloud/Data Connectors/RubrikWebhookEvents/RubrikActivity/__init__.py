"""This __init__ file will be called by Orchastrator function to ingest data in Sentinel."""
import inspect
import time
from shared_code.logger import applogger
from shared_code.consts import LOGS_STARTS_WITH
from shared_code.rubrik_exception import RubrikException
from .rubrik import Rubrik


def main(name) -> str:
    """Start Execution of Activity Function.

    Args:
        name (dict): data received via Rubrik Webhook.

    Returns:
        str: status message of activity function.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        applogger.info(
            "{}(method={}) Activity function called!".format(
                LOGS_STARTS_WITH, __method_name
            )
        )
        start = time.time()
        rubrik_obj = Rubrik()
        rubrik_obj.post_data_to_sentinel(name)
        end = time.time()
        applogger.info(
            "{}(method={}) time taken for data ingestion is {} sec".format(
                LOGS_STARTS_WITH, __method_name, int(end - start)
            )
        )
        applogger.info(
            "{}(method={}) Activity function Completed!".format(
                LOGS_STARTS_WITH, __method_name
            )
        )
    except RubrikException as err:
        return err
    except Exception as err:
        applogger.error("{}(method={}) {}".format(LOGS_STARTS_WITH, __method_name, err))
        return err
    return "Data Posted successfully to {}".format(name.get("log_type"))
