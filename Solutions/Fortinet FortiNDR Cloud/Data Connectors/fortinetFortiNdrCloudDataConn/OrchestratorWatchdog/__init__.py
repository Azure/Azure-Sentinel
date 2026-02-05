import logging
import os
from datetime import datetime, timedelta, timezone

import azure.durable_functions as df
import azure.functions as func
import FncRestClient
from azure.durable_functions.models import DurableOrchestrationStatus
from errors import InputError
from fnc.fnc_client import FncClient
from fnc.utils import datetime_to_utc_str
from globalVariables import (DEFAULT_BUCKET_NAME, INTEGRATION_NAME,
                             ORCHESTRATION_NAME, SUPPORTED_EVENT_TYPES)

NOT_RUNNING_FUNCTION_STATES = [
    df.OrchestrationRuntimeStatus.Completed,
    df.OrchestrationRuntimeStatus.Failed,
    df.OrchestrationRuntimeStatus.Terminated,
    None,
]

EVENT_TYPES = (os.environ.get("FncEvents", "observation")).split(",")
EVENT_TYPES = [event.strip() for event in EVENT_TYPES if event]
TERMINATE_APP = os.environ.get("FncTerminateApp").strip().lower() == "true"

try:
    DAYS_TO_COLLECT_EVENTS = int(os.environ.get("FncDaysToCollectEvents", "7"))
except ValueError:
    DAYS_TO_COLLECT_EVENTS = 7

try:
    DAYS_TO_COLLECT_DETECTIONS = int(
        os.environ.get("FncDaysToCollectDetections", "7"))
except ValueError:
    DAYS_TO_COLLECT_DETECTIONS = 7

try:
    INTERVAL = int(os.environ.get("FncIntervalMinutes", "5"))
except ValueError:
    INTERVAL = 5

try:
    POLLING_DELAY = int(os.environ.get("PollingDelay", "10"))
except ValueError:
    POLLING_DELAY = 10

API_TOKEN = os.environ.get("FncApiToken", None)
AWS_ACCESS_KEY = os.environ.get("AwsAccessKeyId", None)
AWS_SECRET_KEY = os.environ.get("AwsSecretAccessKey", None)
ACCOUNT_CODE = os.environ.get("FncAccountCode", None)
BUCKET_NAME = os.environ.get("FncBucketName", DEFAULT_BUCKET_NAME)
DOMAIN = os.environ.get("FncApiDomain", None)


def validate_configuration():
    if EVENT_TYPES and not SUPPORTED_EVENT_TYPES.issuperset(EVENT_TYPES):
        raise InputError(
            f"FncEvents must be one or more of {SUPPORTED_EVENT_TYPES}")

    sentinel_shared_key = (os.environ.get("WorkspaceKey") or "").strip()
    if not sentinel_shared_key:
        raise InputError("WorkspaceKey is required.")

    if INTERVAL is None or INTERVAL < 1 or INTERVAL > 60:
        raise InputError("FncIntervalMinutes must be a number 1-60")

    if DAYS_TO_COLLECT_EVENTS and (
        DAYS_TO_COLLECT_EVENTS < 0 or DAYS_TO_COLLECT_EVENTS > 7
    ):
        raise InputError("FncDaysToCollectEvents must be a number 0-7")

    if "detections" in EVENT_TYPES and API_TOKEN is None:
        raise InputError("FncApiToken must be provided to fetch detections")

    if "suricata" in EVENT_TYPES or "observation" in EVENT_TYPES:
        if not AWS_ACCESS_KEY or not AWS_SECRET_KEY or not ACCOUNT_CODE:
            raise InputError(
                "AwsAccessKeyId, AwsSecretAccessKey, and FncAccountCode are required to pull Suricata and Observation."
            )


async def main(mytimer: func.TimerRequest, starter: str) -> None:
    client = df.DurableOrchestrationClient(starter)
    instance_id = "FncIntegrationSentinelStaticInstanceId"

    existing_instance = await client.get_status(instance_id)
    logging.info(
        f"OrchestratorWatchdog: {ORCHESTRATION_NAME} status: {existing_instance.runtime_status}"
    )

    if TERMINATE_APP:
        reason = f"FncTerminateApp set to {TERMINATE_APP}"
        await terminate_app(
            client, existing_instance.runtime_status, instance_id, reason
        )
        return

    # Only start the orchestrator if it's not already running.
    if existing_instance.runtime_status in NOT_RUNNING_FUNCTION_STATES:
        validate_configuration()
        await client.start_new(ORCHESTRATION_NAME, instance_id, create_args())
        logging.info(f"OrchestratorWatchdog: Started {ORCHESTRATION_NAME}")


async def terminate_app(client, status, instance_id, reason: str):
    if status not in NOT_RUNNING_FUNCTION_STATES:
        await client.terminate(instance_id=instance_id, reason=reason)
        logging.info(
            f"OrchestrationWatchdog: Termination request sent to {ORCHESTRATION_NAME}."
        )


def get_detection_args():
    timestamp = datetime.now(tz=timezone.utc)
    days_to_collect_detections = (
        DAYS_TO_COLLECT_DETECTIONS if DAYS_TO_COLLECT_DETECTIONS else 0
    )
    start_date_detections = datetime_to_utc_str(
        timestamp - timedelta(days=days_to_collect_detections)
    )
    detection_args = {
        "polling_delay": POLLING_DELAY,
        "start_date": start_date_detections,
    }

    # Create detection client to get context for history
    # and real time detections
    rest_client = FncRestClient.FncSentinelRestClient()
    detection_client = FncClient.get_api_client(
        name=INTEGRATION_NAME, api_token=API_TOKEN, domain=DOMAIN, rest_client=rest_client
    )
    h_context, context = detection_client.get_splitted_context(
        args=detection_args)
    history = h_context.get_history()

    return {
        "checkpoint": (context.get_checkpoint()),
        "history_detections": {
            "start_date_str": history.get("start_date", None),
            "end_date_str": history.get("end_date", None),
            "checkpoint": history.get("start_date", None),
        },
    }


def get_event_args():
    timestamp = datetime.now(tz=timezone.utc)
    days_to_collect_events = DAYS_TO_COLLECT_EVENTS if DAYS_TO_COLLECT_EVENTS else 0
    start_date_events = datetime_to_utc_str(
        timestamp - timedelta(days=days_to_collect_events)
    )

    # Create metastream client to get context for history and realtime events
    metastream_client = FncClient.get_metastream_client(
        name=INTEGRATION_NAME,
        account_code=ACCOUNT_CODE,
        access_key=AWS_ACCESS_KEY,
        secret_key=AWS_SECRET_KEY,
        bucket=BUCKET_NAME,
    )
    h_context, context = metastream_client.get_splitted_context(
        start_date_str=start_date_events
    )
    history = h_context.get_history("suricata")

    return {
        "checkpoint": (context.get_checkpoint()),
        "history_events": history,
    }


def create_args():
    logging.info("Start creating args")

    args = {"event_types": {}, "interval": INTERVAL}

    for event_type in EVENT_TYPES:
        event_type = event_type.strip()
        res = None

        if event_type == "detections":
            res = get_detection_args()
        else:
            res = get_event_args()

        args["event_types"][event_type] = res

    logging.info("Finished setting up args to fetch and send events.")
    logging.info("===ARGS===")
    logging.info(args)
    return args
