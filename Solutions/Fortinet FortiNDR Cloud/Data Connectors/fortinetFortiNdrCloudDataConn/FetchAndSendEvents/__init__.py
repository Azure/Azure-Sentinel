import logging
import os
from datetime import datetime, timedelta, timezone

from fnc.fnc_client import FncClient
from fnc.metastream.s3_client import MetastreamContext
from fnc.utils import str_to_utc_datetime
from globalVariables import (DEFAULT_BUCKET_NAME, INTEGRATION_NAME,
                             SUPPORTED_EVENT_TYPES)
from sentinel import post_data

AWS_ACCESS_KEY = os.environ.get("AwsAccessKeyId")
AWS_SECRET_KEY = os.environ.get("AwsSecretAccessKey")
ACCOUNT_CODE = os.environ.get("FncAccountCode")
API_TOKEN = os.environ.get("ApiToken")
BUCKET_NAME = os.environ.get("FncBucketName") or DEFAULT_BUCKET_NAME
LOGGER_LEVEL = os.environ.get("LogLevel") or "INFO"
POSTING_LIMIT = int(os.environ.get("PostingLimit", "3000"))


def main(args: dict) -> str:
    validate_args(args)

    event_type = args.get("event_type", "")
    checkpoint = args.get("checkpoint", "")

    if not checkpoint:
        return ""

    logging.info(
        f"FetchAndSendEvents: event type: {event_type} checkpoint: {checkpoint}"
    )

    ctx = MetastreamContext()
    start_date = str_to_utc_datetime(checkpoint)
    try:
        now = datetime.now(tz=timezone.utc).replace(microsecond=0)
        end_date = start_date + timedelta(minutes=10)
        is_done = False
        if event_type == "suricata" and now > end_date:
            fetch_and_send_events(ctx, event_type, start_date, end_date)
        else:
            fetch_and_send_events(ctx, event_type, start_date)
            is_done = True

        new_checkpoint = ctx.get_checkpoint()

    except Exception as ex:
        logging.error(
            f"Failure: FetchAndSendEvents: event: {event_type} checkpoint: {checkpoint} error: {str(ex)}"
        )
        raise Exception(
            f"Failure: FetchAndSendEvents: event: {event_type} error: {str(ex)}"
        )

    return new_checkpoint, is_done


def validate_args(args: dict):
    logging.info("Validating args to retrieve events.")
    event_type = args.get("event_type", "")
    checkpoint = args.get("checkpoint", "")

    if not event_type or event_type not in SUPPORTED_EVENT_TYPES:
        raise AttributeError(
            "Event type was not provided or it is not supported. Event type must be one of (Observation | Suricata)"
        )

    if not checkpoint:
        raise AttributeError(
            "Checkpoint was not provided. Checkpoint is required to retrieve events."
        )

    logging.info(f"Args for retrieving {event_type} validated.")


def post_events_inc(events, event_type):
    limit = POSTING_LIMIT
    count = len(events)
    start = 0
    while start < count:
        end = count if count - start <= limit else start + limit
        post_data(events[start:end], event_type)
        start = start + limit


def fetch_and_send_events(
    ctx: MetastreamContext,
    event_type: str,
    start_date: datetime,
    end_date: datetime = None,
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
    for events in client.fetch_events(
        context=ctx, event_type=event_type,
        start_date=start_date, end_date=end_date
    ):
        post_events_inc(events, event_type)
