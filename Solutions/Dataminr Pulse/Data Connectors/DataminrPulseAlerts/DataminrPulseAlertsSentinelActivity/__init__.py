"""This __init__ file will be called by Orchastrator function to ingest data in Sentinel."""
import time
from .dataminr_pulse import DataminrPulse
from shared_code.logger import applogger
from shared_code.consts import LOGS_STARTS_WITH
from shared_code.dataminrpulse_exception import DataminrPulseException


def main(name):
    """Start Execution of Activity Function.

    Args:
        name (dict): data received via Dataminr RTAP.

    Returns:
        str: status message of activity function.
    """
    try:
        applogger.info("Activity function called.")
        start = time.time()
        dataminr_pulse_obj = DataminrPulse()
        status = dataminr_pulse_obj.send_alert_data_to_sentinel(name)
        end = time.time()
        applogger.info(
            "{} :time taken for data ingestion is {} sec".format(
                LOGS_STARTS_WITH, int(end - start)
            )
        )
    except DataminrPulseException as err:
        return err
    return status
