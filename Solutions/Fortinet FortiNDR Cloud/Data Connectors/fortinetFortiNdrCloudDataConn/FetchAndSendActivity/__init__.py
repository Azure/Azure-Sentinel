import logging
import os
from datetime import datetime, timezone

from metastream import fetch_detections, fetch_events
from metastream.s3_client import Context
from sentinel import post_data

AWS_ACCESS_KEY = os.environ.get('AwsAccessKeyId')
AWS_SECRET_KEY = os.environ.get('AwsSecretAccessKey')
ACCOUNT_CODE = os.environ.get("FncAccountCode")

def main(checkpoints: dict) -> str:
    new_checkpoints = {}
    for signal_type, checkpoint in checkpoints.items():
        if not checkpoints:
            return ""

        logging.info(f'FetchAndSendActivity: signal: {signal_type} checkpoint: {checkpoint}')

        ctx = Context()
        start_date = datetime.fromisoformat(checkpoint).replace(tzinfo=timezone.utc)
        if signal_type == 'detections':
            fetch_and_send_detections(ctx, signal_type, start_date)
        else:
            fetch_and_send_events(ctx, signal_type, start_date)

        if ctx.checkpoint is None:
            return ""
        new_checkpoints[signal_type] = ctx.checkpoint.isoformat()

    return new_checkpoints


def fetch_and_send_events(ctx: Context, signal_type: str, start_date: datetime):
    for events in fetch_events(context=ctx,
                               name='sentinel',
                               event_types=[signal_type],
                               account_code=ACCOUNT_CODE,
                               start_date=start_date,
                               access_key=AWS_ACCESS_KEY,
                               secret_key=AWS_SECRET_KEY):
        post_data(events, signal_type)


def fetch_and_send_detections(ctx: Context, signal_type: str, start_date: datetime):
    for events in fetch_detections(context=ctx,
                               name='sentinel',
                               account_code=ACCOUNT_CODE,
                               start_date=start_date,
                               access_key=AWS_ACCESS_KEY,
                               secret_key=AWS_SECRET_KEY):
        post_data(events, signal_type) 
