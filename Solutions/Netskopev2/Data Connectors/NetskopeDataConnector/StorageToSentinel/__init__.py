"""Init for Netskope Azure storage to Sentinel."""
import datetime
import logging
import inspect

import azure.functions as func
from .netskope_azure_storage_to_sentinel import NetskopeAzureStorageToSentinel
from ..StorageToSentinel.remove_duplicates_in_azure_storage import RemoveDuplicatesInAzureStorage
from ..SharedCode import utils
from ..SharedCode.logger import applogger
from ..SharedCode import consts


async def main(mytimer: func.TimerRequest) -> None:
    """Driver method for azure storage to sentinel."""
    __method_name = inspect.currentframe().f_code.co_name
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    share_name_after_duplication = False
    event_type_sub_type = utils.get_event_alert_type_subtype()
    sharename = ''.join((event_type_sub_type.get("type_of_data"), event_type_sub_type.get("sub_type"), "data"))
    duplicate_share_name = (
        ''.join((event_type_sub_type.get("type_of_data"), event_type_sub_type.get("sub_type"), "duplicationcheck"))
    )
    try:
        remove_duplicates_obj = RemoveDuplicatesInAzureStorage(sharename, duplicate_share_name)
        remove_duplicates_obj.list_file_names_and_remove_duplicate_data()
        share_name_after_duplication = True
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Error occurred in deduplication or file share not available for share-{}"
            "Error-{}.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL, sharename, error
            )
        )
    if share_name_after_duplication:
        state_manager_to_sentinel_obj = NetskopeAzureStorageToSentinel(sharename)
        await state_manager_to_sentinel_obj.list_files_and_ingest_files_data_to_sentinel()
    else:
        applogger.warn(
            "{}(method={}) : {} : No logs found to send to Sentinel after executing deduplication.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
            )
        )
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
