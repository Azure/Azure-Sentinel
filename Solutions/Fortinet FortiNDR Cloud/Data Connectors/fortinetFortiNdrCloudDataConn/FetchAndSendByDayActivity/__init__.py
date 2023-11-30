import logging
import os
from datetime import date, datetime, timedelta, timezone

from metastream import fetch_detections_by_day, fetch_events_by_day
from metastream.s3_client import Context
from sentinel.sentinel import post_data

AWS_ACCESS_KEY = os.environ.get('AwsAccessKeyId')
AWS_SECRET_KEY = os.environ.get('AwsSecretAccessKey')
ACCOUNT_CODE = os.environ.get("FncAccountCode")

def main(args: dict) -> str:
    events = args.get('events', [])
    day: int = args.get('day')
    for event_type in events:
        ctx = Context()
        start_day = datetime.now(tz=timezone.utc) - timedelta(days=day)
        logging.info(f'FetchAndSendByDayActivity: event: {event_type} day: {start_day.date()}')

        if event_type == 'detections':
            fetch_and_send_detections(ctx, event_type, start_day.date())
        else:
            fetch_and_send_events(ctx, event_type, start_day)

    # it's required to return something that is json serializable
    return 'success'


def fetch_and_send_events(ctx: Context, event_type: str, start_day: datetime):
    for events in fetch_events_by_day(context=ctx,
                                      name='sentinel',
                                      event_type=event_type,
                                      account_code=ACCOUNT_CODE,
                                      day=start_day,
                                      access_key=AWS_ACCESS_KEY,
                                      secret_key=AWS_SECRET_KEY):
        post_data(events, event_type)


def fetch_and_send_detections(ctx: Context, event_type: str, start_day: date):
    for events in fetch_detections_by_day(context=ctx,
                                          name='sentinel',
                                          account_code=ACCOUNT_CODE,
                                          day=start_day,
                                          access_key=AWS_ACCESS_KEY,
                                          secret_key=AWS_SECRET_KEY):
        post_data(events, event_type)
