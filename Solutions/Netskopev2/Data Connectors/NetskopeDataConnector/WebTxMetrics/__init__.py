"""Init for Web Transaction Metrics."""
import datetime
import logging

import azure.functions as func
from .ingest_message import ingest_backlog_unacked_message


def main(mytimer: func.TimerRequest) -> None:
    """Driver method WebTx metrics."""
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    ingest_backlog_unacked_message()
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
