import logging
import os
import json

from fnc.fnc_client import FncClient
from fnc.api.api_client import ApiContext
from logger import Logger
from sentinel import post_data

API_TOKEN = os.environ.get("FncApiToken")
ACCOUNT_UUID = os.environ.get("FncAccountUuid")
INCLUDE_PDNS = os.environ.get("FncAccountUuid")
INCLUDE_DHCP = os.environ.get("IncludeDhcp")
INCLUDE_EVENTS = os.environ.get("IncludeEvents")
POLLING_DELAY = int(os.environ.get("PollingDelay") or 10)
DOMAIN = os.environ.get("FncApiDomain")


def main(args: dict) -> str:
    validate_args(args)

    event_type = args.get("event_type", "")
    history = args.get("history", {})

    start_date = history.get("end_date_str")
    end_date = history.get("end_date_str")
    checkpoint = history.get("checkpoint")

    logging.info(
        f"FetchAndSendDetections: fetching for history, event type: {event_type} start_date: {checkpoint} end_date: {end_date}"
    )

    ctx = ApiContext()
    ctx.update_checkpoint(checkpoint=checkpoint)
    ctx.update_history(
        {
            "start_date": start_date,
            "end_date": end_date,
        }
    )
    try:
        fetch_and_send_detections(ctx, event_type, start_date)

        new_checkpoint = ctx.get_checkpoint()
        logging.info(
            f"Detections history retrieved, history: {history} checkpoint: {checkpoint} new_checkpoint: {new_checkpoint}"
        )

    except Exception as ex:
        logging.error(
            f"Failure: FetchAndSendDetections: checkpoint: {checkpoint} error: {str(ex)}"
        )
        raise Exception(f"Failure: FetchAndSendDetections: error: {str(ex)}")

    return new_checkpoint


def validate_args(args: dict):
    logging.info("Validating args to retrieve detections history")
    event_type = args.get("event_type", "")
    history = args.get("history", {})
    checkpoint = history.get("checkpoint")

    if not event_type or not event_type.strip().lower() == "detections":
        raise AttributeError(
            "Event type was not provided or it is not supported. Event type must be detections to pull detections history."
        )

    if not history:
        raise AttributeError(
            "History object was not provided or it is empty. History object is required to retrieve detection history"
        )

    if not checkpoint:
        raise AttributeError(
            "Checkpoint was not provided. Checkpoint is required to retrieve detections history"
        )

    logging.info("Args for retrieving detections history validated")


def add_events_to_detections(detections, detection_events):
    logging.info("Start enriching detections with events")
    for detection in detections:
        if detection_events.get(detection["uuid"]) is not None:
            detection["events"] = json.dumps(detection_events.get(detection["uuid"]))
        else:
            detection["events"] = json.dumps([])
    logging.info("Finished enriching detections with events")


def fetch_and_send_detections(ctx: ApiContext, event_type: str, start_date: str):
    client = (
        FncClient.get_api_client(
            name="sentinel-fetch-detections-history",
            api_token=API_TOKEN,
            logger=Logger("sentinel-fetch-detections-history"),
        )
        if not DOMAIN
        else FncClient.get_api_client(
            name="sentinel-fetch-detections-history",
            api_token=API_TOKEN,
            domain=DOMAIN,
            logger=Logger("sentinel-fetch-detections-history"),
        )
    )
    client.get_logger().set_level(level=logging.DEBUG)
    polling_args = {
        "account_uuid": ACCOUNT_UUID,
        "polling_delay": POLLING_DELAY,
        "status": "ALL",
        "pull_muted_detections": "ALL",
        "pull_muted_rules": "ALL",
        "pull_muted_devices": "ALL",
        "include_description": True,
        "include_signature": True,
        "include_pdns": INCLUDE_PDNS,
        "include_dhcp": INCLUDE_DHCP,
        "include_events": INCLUDE_EVENTS,
        "filter_training_detections": True,
        "limit": 500,
        "start_date": start_date,
    }

    for response in client.poll_history(context=ctx, args=polling_args):
        detections = list(response.get("detections"))
        detection_events = response.get("events")
        add_events_to_detections(detections, detection_events)
        post_data(detections, event_type)
