"""init module for NetskopeToAzureStorage activity function."""
import datetime
import logging

from .netskope_to_azure_storage import NetskopeToAzureStorage
from ..SharedCode import utils

import azure.functions as func


async def main(mytimer: func.TimerRequest) -> None:
    """Initialize netskope_to_azure_storage object and start execution."""
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    event_type_sub_type = utils.get_event_alert_type_subtype()
    netskope_to_azure_storage = NetskopeToAzureStorage(
        event_type_sub_type.get("type_of_data"), event_type_sub_type.get("sub_type")
    )
    await netskope_to_azure_storage.initiate_and_manage_iterators()
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
