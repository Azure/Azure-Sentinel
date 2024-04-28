import logging
import os
from datetime import date, datetime, timedelta, timezone

from metastream import fetch_detections_by_day, fetch_events_by_day
from metastream.s3_client import Context
from sentinel.sentinel import post_data
from globalVariables import SUPPORTED_EVENT_TYPES

AWS_ACCESS_KEY = os.environ.get('AwsAccessKeyId')
AWS_SECRET_KEY = os.environ.get('AwsSecretAccessKey')
ACCOUNT_CODE = os.environ.get("FncAccountCode")


def main(args: dict) -> str:
    validate_args(args)

    event_type = args.get('event_type', '')
    day: int = args.get('day', '')

    try:
        ctx = Context()
        start_day = datetime.now(tz=timezone.utc) - timedelta(days=day)
        logging.info(
            f'FetchAndSendByDayActivity: event: {event_type} day: {start_day.date()}')

        if event_type == 'detections':
            fetch_and_post_detections(ctx, event_type, start_day.date())
        else:
            fetch_and_post_events(ctx, event_type, start_day)

        # it's required to return something that is json serializable
        return 'success'
    except Exception as ex:
        logging.error(
            f'Failure: FetchAndSendByDayActivity: event: {event_type} day: {start_day.date()} error: {str(ex)}')
        raise Exception(
            f"Failure: FetchAndSendByDayActivity failed. Event: {event_type} error: {str(ex)}")


def validate_args(args: dict):
    event_type = args.get('event_type', '').lower()
    day: int = args.get('day', '')

    if not event_type or not event_type in SUPPORTED_EVENT_TYPES:
        raise AttributeError(
            "Event type was not provided or it is not supported. Event type must be one of (Observation | Suricata | Detection).")
    if not day:
        raise AttributeError(
            "The day for which to retrieve event is required for the FetchAndSendByDayActivity.")

def post_events_inc(events, event_type):
    limit = 5000
    count = len(events)
    start = 0
    while start < count:
        end = count if count - start <= limit else start + limit
        post_data(events[start:end], event_type)
        start = start + limit
    
def fetch_and_post_events(ctx: Context, event_type: str, start_day: datetime):
    for events in fetch_events_by_day(context=ctx,
                                      name='sentinel',
                                      event_type=event_type,
                                      account_code=ACCOUNT_CODE,
                                      day=start_day,
                                      access_key=AWS_ACCESS_KEY,
                                      secret_key=AWS_SECRET_KEY):
        post_events_inc(events, event_type)
            


def fetch_and_post_detections(ctx: Context, event_type: str, start_day: date):
    for events in fetch_detections_by_day(context=ctx,
                                          name='sentinel',
                                          account_code=ACCOUNT_CODE,
                                          day=start_day,
                                          access_key=AWS_ACCESS_KEY,
                                          secret_key=AWS_SECRET_KEY):
        post_events_inc(events, event_type)
