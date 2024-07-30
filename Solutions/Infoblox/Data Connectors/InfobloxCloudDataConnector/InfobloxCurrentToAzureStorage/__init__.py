"""Init file for Infoblox Current Function App."""
import datetime
import logging
import azure.functions as func
from .infoblox_to_azure_storage import InfobloxToAzureStorage
from ..SharedCode.logger import applogger
from ..SharedCode import consts
import time


def main(mytimer: func.TimerRequest) -> None:
    """Run the main logic of the Function App triggered by a timer."""
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    start = time.time()
    applogger.info(
        "{} : {}, Function App started at {}".format(
            consts.LOGS_STARTS_WITH,
            consts.CURRENT_I_TO_S_FUNCTION_NAME,
            datetime.datetime.fromtimestamp(start),
        )
    )
    infoblox_to_azure_storage_obj = InfobloxToAzureStorage(str(int(start)))
    infoblox_to_azure_storage_obj.get_infoblox_data_into_azure_storage()
    end = time.time()

    applogger.info(
        "{} : {}, Function App ended at {}".format(
            consts.LOGS_STARTS_WITH,
            consts.CURRENT_I_TO_S_FUNCTION_NAME,
            datetime.datetime.fromtimestamp(end),
        )
    )
    applogger.info(
        "{} : {}, Total time taken = {}".format(
            consts.LOGS_STARTS_WITH, consts.CURRENT_I_TO_S_FUNCTION_NAME, end - start
        )
    )
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
