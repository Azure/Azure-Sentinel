import logging
import os
from datetime import datetime, timezone

from metastream import fetch_detections, fetch_events
from metastream.s3_client import Context
from sentinel import post_data
from globalVariables import SUPPORTED_EVENT_TYPES

AWS_ACCESS_KEY = os.environ.get('AwsAccessKeyId')
AWS_SECRET_KEY = os.environ.get('AwsSecretAccessKey')  # is this encrypted
ACCOUNT_CODE = os.environ.get("FncAccountCode")


def main(args: dict) -> str:
    validate_args(args)

    event_type = args.get('event_type', '')
    checkpoint = args.get('checkpoint', '')

    if not checkpoint:
        return ""

    logging.info(
        f'FetchAndSendActivity: event type: {event_type} checkpoint: {checkpoint}')

    ctx = Context()
    start_date = datetime.fromisoformat(checkpoint).replace(tzinfo=timezone.utc)
    try:
        if event_type == 'detections':
            fetch_and_send_detections(ctx, event_type, start_date)
        else:
            fetch_and_send_events(ctx, event_type, start_date)

        new_checkpoint = ctx.checkpoint.isoformat()

    except Exception as ex:
        logging.error(
            f"Failure: FetchAcndSendActivity: event: {event_type} checkpoint: {checkpoint} error: {str(ex)}")
        raise Exception(
            f"Failure: FetchAcndSendActivity: event: {event_type} error: {str(ex)}")

    return new_checkpoint


def validate_args(args: dict):
    event_type = args.get('event_type', '')

    if not event_type or not event_type in SUPPORTED_EVENT_TYPES:
        raise AttributeError(
            "Event type was not provided or it is not supported. Event type must be one of (Observation | Suricata | Detection).")

def post_events_inc(events, event_type):
    limit = 5000
    count = len(events)
    start = 0
    while start < count:
        end = count if count - start <= limit else start + limit
        post_data(events[start:end], event_type)
        start = start + limit

def fetch_and_send_events(ctx: Context, event_type: str, start_date: datetime):
    for events in fetch_events(context=ctx,
                               name='sentinel',
                               event_types=[event_type],
                               account_code=ACCOUNT_CODE,
                               start_date=start_date,
                               access_key=AWS_ACCESS_KEY,
                               secret_key=AWS_SECRET_KEY):
        post_events_inc(events, event_type)


def fetch_and_send_detections(ctx: Context, event_type: str, start_date: datetime):
    for events in fetch_detections(context=ctx,
                                   name='sentinel',
                                   account_code=ACCOUNT_CODE,
                                   start_date=start_date,
                                   access_key=AWS_ACCESS_KEY,
                                   secret_key=AWS_SECRET_KEY):
        post_events_inc(events, event_type)
