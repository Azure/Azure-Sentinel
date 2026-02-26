import json
import logging
import os

import FncRestClient
from fnc.api.api_client import ApiContext
from fnc.fnc_client import FncClient
from globalVariables import INTEGRATION_NAME
from sentinel import post_data

API_TOKEN = os.environ.get("FncApiToken")
ACCOUNT_UUID = os.environ.get("FncAccountUuid")
INCLUDE_EVENTS = os.environ.get("IncludeEvents")
POLLING_DELAY = int(os.environ.get("PollingDelay") or 10)
DOMAIN = os.environ.get("FncApiDomain")
DETECTION_STATUS = os.environ.get("DetectionStatus") or "all"
PULL_MUTED = os.environ.get("PullMuted") or "all"
INCLUDE_DESCRIPTION = os.environ.get("IncludeDescription") or True
INCLUDE_SIGNATURE = os.environ.get("IncludeSignature") or True
LOGGER_LEVEL = os.environ.get("LogLevel") or "INFO"


def main(args: dict) -> str:
    validate_args(args)

    event_type = args.get("event_type", "")
    checkpoint = args.get("checkpoint", "")
    start_date = checkpoint

    logging.info(
        f"FetchAndSendDetections: fetching for checkpoint, event type: {event_type} checkpoint: {checkpoint}"
    )

    ctx = ApiContext()
    try:
        fetch_and_send_detections(ctx, event_type, start_date)

        new_checkpoint = ctx.get_checkpoint()

        logging.info(
            f"Detections retrieved, checkpoint: {checkpoint} new_checkpoint: {new_checkpoint}"
        )

    except Exception as ex:
        logging.error(
            f"Failure: FetchAndSendDetections: event: {event_type} start_date: {start_date} error: {str(ex)}"
        )
        raise Exception(
            f"Failure: FetchAndSendDetections: event: {event_type} error: {str(ex)}"
        )

    return new_checkpoint


def validate_args(args: dict):
    event_type = args.get("event_type", "")
    checkpoint = args.get("checkpoint", "")

    if not event_type or not event_type.strip().lower() == "detections":
        raise AttributeError(
            "Event type was not provided or it is not supported. Event type must be detections."
        )

    if not checkpoint:
        raise AttributeError(
            "Checkpoint was not provided. Checkpoint is required to retrieve detections."
        )


def add_events_to_detections(detections, detection_events):
    logging.info("Start enriching detections with events")
    for detection in detections:
        detection["events"] = json.dumps(
            detection_events.get(detection["uuid"], [])
        )
    logging.info("Finished enriching detections with events")


def fetch_and_send_detections(
    ctx: ApiContext, event_type: str, start_date: str
):
    rest_client = FncRestClient.FncSentinelRestClient()
    client = FncClient.get_api_client(
        name=INTEGRATION_NAME, api_token=API_TOKEN, domain=DOMAIN, rest_client=rest_client
    )
    loggerLever = logging.getLevelName(LOGGER_LEVEL.upper())
    client.get_logger().set_level(level=loggerLever)
    polling_args = {
        "account_uuid": ACCOUNT_UUID,
        "polling_delay": POLLING_DELAY,
        "status": DETECTION_STATUS,
        "pull_muted_detections": PULL_MUTED,
        "pull_muted_rules": PULL_MUTED,
        "pull_muted_devices": PULL_MUTED,
        "include_description": INCLUDE_DESCRIPTION,
        "include_signature": INCLUDE_SIGNATURE,
        "include_events": INCLUDE_EVENTS,
        "filter_training_detections": True,
        "start_date": start_date,
    }

    for response in client.continuous_polling(context=ctx, args=polling_args):
        detections = list(response.get("detections"))
        detection_events = response.get("events")
        add_events_to_detections(detections, detection_events)
        post_data(detections, event_type)
