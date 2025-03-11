import logging
import os
from datetime import timedelta

from fnc.fnc_client import FncClient
from fnc.metastream.s3_client import MetastreamContext
from globalVariables import (DEFAULT_BUCKET_NAME, INTEGRATION_NAME,
                             SUPPORTED_EVENT_TYPES)
from sentinel.sentinel import post_data

AWS_ACCESS_KEY = os.environ.get("AwsAccessKeyId")
AWS_SECRET_KEY = os.environ.get("AwsSecretAccessKey")
ACCOUNT_CODE = os.environ.get("FncAccountCode")
BUCKET_NAME = os.environ.get("FncBucketName") or DEFAULT_BUCKET_NAME
LOGGER_LEVEL = os.environ.get("LogLevel") or "INFO"
POSTING_LIMIT = int(os.environ.get("PostingLimit", "3000"))


def main(args: dict) -> str:
    validate_args(args)

    event_type = args.get("event_type", "")
    history = args.get("history", {})

    try:
        ctx = MetastreamContext()
        ctx.update_history(event_type, history)
        logging.info(
            f"FetchAndSenEventsHistory: event: {event_type} history: {history}"
        )

        interval = (
            timedelta(minutes=10) if event_type == "suricata" else timedelta(
                hours=1)
        )

        fetch_and_post_events(ctx, event_type, interval)
        next_history = ctx.get_history(event_type=event_type)
        logging.info(
            f"Events history retrieved event_type: {event_type} history: {history} next_history: {next_history}"
        )

        return next_history
    except Exception as ex:
        logging.error(
            f"Failure: FetchAndSenEventsHistory: event: {event_type}  history: {history} error: {str(ex)}"
        )
        raise Exception(
            f"Failure: FetchAndSenEventsHistory failed. Event: {event_type} error: {str(ex)}"
        )


def validate_args(args: dict):
    logging.info("Validating args to retrieve events history")
    event_type = args.get("event_type", "").lower()
    history = args.get("history", None)

    if not event_type or event_type not in SUPPORTED_EVENT_TYPES:
        raise AttributeError(
            "Event type was not provided or it is not supported. Event type must be one of (Observation | Suricata)."
        )

    if not history:
        raise AttributeError(
            "History object is not provided. History object is required to pull event history."
        )

    logging.info(f"Args for retrieving {event_type} history validated.")


def post_events_inc(events, event_type):
    limit = POSTING_LIMIT
    count = len(events)
    start = 0
    while start < count:
        end = count if count - start <= limit else start + limit
        post_data(events[start:end], event_type)
        start = start + limit


def fetch_and_post_events(
    ctx: MetastreamContext, event_type: str, interval: timedelta
):
    client = FncClient.get_metastream_client(
        name=INTEGRATION_NAME,
        account_code=ACCOUNT_CODE,
        access_key=AWS_ACCESS_KEY,
        secret_key=AWS_SECRET_KEY,
        bucket=BUCKET_NAME,
    )
    loggerLever = logging.getLevelName(LOGGER_LEVEL.upper())
    client.get_logger().set_level(level=loggerLever)
    for events in client.poll_history(ctx, event_type, interval):
        post_events_inc(events, event_type)
