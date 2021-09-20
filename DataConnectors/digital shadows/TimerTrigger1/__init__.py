import datetime
import logging

import azure.functions as func

from . import from_DS

max_time = datetime.datetime.strptime("2021-08-30 05:23:25", "%Y-%m-%d %H:%M:%S")

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    from_DS.get_incidents(max_time)