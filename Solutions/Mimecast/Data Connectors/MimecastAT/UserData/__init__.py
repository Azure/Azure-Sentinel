"""Init module for UserData."""

import datetime
import logging
import time
import azure.functions as func
from .mimecast_user_data_to_sentinel import MimecastAwarenessUserData


def main(mytimer: func.TimerRequest) -> None:
    """Driver method for awareness training user data."""
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    function_start_time = time.time()
    user_data_obj = MimecastAwarenessUserData(function_start_time)
    user_data_obj.get_awareness_user_data_in_sentinel()
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
