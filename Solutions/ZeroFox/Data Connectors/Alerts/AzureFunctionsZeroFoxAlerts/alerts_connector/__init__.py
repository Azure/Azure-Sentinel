import logging
import os
from datetime import datetime, timezone, timedelta

import azure.functions as func
from connections.sentinel import SentinelConnector
from connections.zerofox import ZeroFoxClient
from dateutil import parser


async def main(mytimer: func.TimerRequest) -> None:
    now = datetime.now(timezone.utc)
    utc_timestamp = now.isoformat()

    if mytimer.past_due:
        logging.info("The timer is past due!")

    date_format = "%Y-%m-%dT%H:%M:%SZ"

    # Environment variables for Logs Ingestion API
    dce_endpoint = os.environ.get("DCE_ENDPOINT")
    dcr_immutable_id = os.environ.get("DCR_IMMUTABLE_ID")
    stream_name = os.environ.get("STREAM_NAME", "Custom-ZeroFoxAlertPoller_CL")

    days_ago = os.environ.get("SinceDaysAgo", "0")

    if is_first_run(mytimer):
        query_from = (now - timedelta(days=float(days_ago))).strftime(date_format)
    else:
        query_from = min(
            parse_last_update(mytimer), now
        ).strftime(date_format)
    query_to = now.strftime(date_format)

    logging.info(f"Querying ZeroFox alerts from {query_from} to {query_to}")

    zerofox = get_zf_client()

    log_type = "ZeroFoxAlertPoller"

    sentinel = SentinelConnector(
        dce_endpoint=dce_endpoint,
        dcr_immutable_id=dcr_immutable_id,
        stream_name=stream_name,
    )

    async with sentinel:
        batches = zerofox.get_alerts(
            last_modified_min_date=query_from,
            last_modified_max_date=query_to,
        )
        for batch in batches:
            await sentinel.send(batch)

    if sentinel.failed_sent_events_number:
        logging.error(f"Failed to send {sentinel.failed_sent_events_number} events")

    logging.info(
        f"Connector {log_type} ran at {utc_timestamp}, "
        f"sending {sentinel.successfull_sent_events_number} events to Sentinel."
    )


def is_first_run(mytimer: func.TimerRequest) -> bool:
    last_run = mytimer.schedule_status.get("Last")
    return last_run == "0001-01-01T00:00:00+00:00"

def parse_last_update(mytimer: func.TimerRequest) -> datetime:
    try:
        last = mytimer.schedule_status.get("Last")
        if last:
            return parser.parse(last)
    except (AttributeError, KeyError, TypeError):
        pass
    return datetime.now(timezone.utc)


def get_zf_client() -> ZeroFoxClient:
    """Create a ZeroFox client from environment variables."""
    api_token = os.environ.get("ZeroFoxApiToken")
    return ZeroFoxClient(api_token)
