import logging
import os
from datetime import datetime, timezone, timedelta

from metastream import fetch_detections, fetch_events
from metastream.s3_client import Context
from sentinel import post_data

AWS_ACCESS_KEY = os.environ.get('AwsAccessKeyId')
AWS_SECRET_KEY = os.environ.get('AwsSecretAccessKey')
ACCOUNT_CODE = os.environ.get("FncAccountCode")

def main(checkpoints: dict) -> str:
    new_checkpoints = {}
    for event_type, checkpoint in checkpoints.items():
        if not checkpoints:
            return ""

        logging.info(f'FetchAndSendActivity: event: {event_type} checkpoint: {checkpoint}')

        ctx = Context()
        start_date = datetime.fromisoformat(checkpoint).replace(tzinfo=timezone.utc)
        try:
            if event_type == 'detections':
                fetch_and_send_detections(ctx, event_type, start_date)
            else:
                fetch_and_send_events(ctx, event_type, start_date)
                
            current_date = datetime.now(tz=timezone.utc).date()
            if current_date > start_date.date():
                days_to_fetch = (current_date - start_date.date()).days - 1
                for day in range(days_to_fetch , -1, -1):
                    day_to_fetch = current_date - timedelta(days=day)
                    if event_type == 'detections':
                        fetch_and_send_detections(ctx, event_type, day_to_fetch)
                    else:
                        fetch_and_send_events(ctx, event_type, day_to_fetch)

            if ctx.checkpoint is None:
                return ""
            new_checkpoints[event_type] = ctx.checkpoint.isoformat()
        except Exception as ex:
            logging.error(f"Failure: FetchAcndSendActivity: event: {event_type} checkpoint: {checkpoint} error: {ex}")
            new_checkpoints[event_type] = checkpoints[event_type]

    return new_checkpoints


def fetch_and_send_events(ctx: Context, event_type: str, start_date: datetime):
    for events in fetch_events(context=ctx,
                               name='sentinel',
                               event_types=[event_type],
                               account_code=ACCOUNT_CODE,
                               start_date=start_date,
                               access_key=AWS_ACCESS_KEY,
                               secret_key=AWS_SECRET_KEY):
        post_data(events, event_type)
    
    

def fetch_and_send_detections(ctx: Context, event_type: str, start_date: datetime):
    for events in fetch_detections(context=ctx,
                               name='sentinel',
                               account_code=ACCOUNT_CODE,
                               start_date=start_date,
                               access_key=AWS_ACCESS_KEY,
                               secret_key=AWS_SECRET_KEY):
        post_data(events, event_type)
