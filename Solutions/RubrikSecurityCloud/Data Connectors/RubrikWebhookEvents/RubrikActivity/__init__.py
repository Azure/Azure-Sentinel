"""This __init__ file is called by the Orchestrator to ingest data into Sentinel."""
import inspect
import time
from shared_code.logger import applogger
from shared_code.consts import LOGS_STARTS_WITH, LOG_FORMAT
from shared_code.rubrik_exception import RubrikException
from .rubrik import Rubrik

FUNCTION_NAME = "RubrikActivity"


def main(name) -> str:
    """Start execution of the Activity function.

    Args:
        name (dict): payload with keys data, log_type, stream_name, rule_id.

    Returns:
        str: status message of the activity function.
    """
    __method_name = inspect.currentframe().f_code.co_name
    log_type = name.get("log_type")
    applogger.info(
        LOG_FORMAT.format(
            LOGS_STARTS_WITH,
            FUNCTION_NAME,
            __method_name,
            "Activity function started for log_type={}.".format(
                log_type
            ),
        )
    )
    try:
        start = time.time()
        rubrik_obj = Rubrik()
        rubrik_obj.post_data_to_sentinel(name)
        elapsed = int(time.time() - start)
        applogger.info(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "Data ingestion completed for {} in {} sec.".format(log_type, elapsed),
            )
        )
        return "Data Posted successfully to {}".format(log_type)
    except RubrikException as err:
        applogger.error(
            LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err)
        )
        return "Error while posting data to {}: {}".format(log_type, err)
    except Exception as err:
        applogger.error(
            LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err)
        )
        return "Unexpected error while posting data to {}: {}".format(
            log_type, err
        )
