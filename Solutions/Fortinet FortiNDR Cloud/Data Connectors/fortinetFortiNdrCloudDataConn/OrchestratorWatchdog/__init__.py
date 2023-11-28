import logging
import os
from datetime import datetime, timedelta, timezone
from time import sleep

from azure.durable_functions.models import DurableOrchestrationStatus
import azure.durable_functions as df
import azure.functions as func

from metastream.errors import InputError

ORCHESTRATION_NAME = 'SingletonEternalOrchestrator'

SUPPORTED_EVENTS = set(['observation', 'suricata'])

NOT_RUNNING_FUNCTION_STATES = [
    df.OrchestrationRuntimeStatus.Completed,
    df.OrchestrationRuntimeStatus.Failed,
    df.OrchestrationRuntimeStatus.Terminated,
    None
]

EVENT_TYPES =(os.environ.get("FncSignals") or "observation").split(",")
EVENT_TYPES = [event.strip() for event in EVENT_TYPES if event]
DETECTIONS = (os.environ.get("FncDetections") or "true").strip().lower() == 'true'
TERMINATE_APP = os.environ.get("FncTerminateApp").strip().lower() == 'true'

try:
    # DAYS_TO_COLLECT = int(os.getenv("FncDaysToCollect", 0))
    DAYS_TO_COLLECT = int(os.environ.get("FncDaysToCollect") or 0)
except ValueError:
    DAYS_TO_COLLECT = None

try:
    # INTERVAL = int(os.getenv("FncIntervalMinutes", "5"))
    INTERVAL = int(os.environ.get("FncIntervalMinutes") or "5")
except ValueError:
    INTERVAL = None


def validate_configuration():
    account_code = (os.environ.get("FncAccountCode") or '').strip()
    if not account_code:
        raise InputError(f'FncAccountCode is required.')

    if EVENT_TYPES and not SUPPORTED_EVENTS.issuperset(EVENT_TYPES):
        raise InputError(f"FncSignals must be one or more of {SUPPORTED_EVENTS}")

    sentinel_customer_id = (os.environ.get('WorkspaceId') or '').strip()
    if not sentinel_customer_id:
        raise InputError(f'WorkspaceId is required.')

    sentinel_shared_key = (os.environ.get('WorkspaceKey') or '').strip()
    if not sentinel_shared_key:
        raise InputError(f'WorkspaceKey is required.')

    if INTERVAL is None or INTERVAL < 1 or INTERVAL > 60:
        raise InputError(f'FncIntervalMinutes must be a number 1-60')

    if DAYS_TO_COLLECT and (DAYS_TO_COLLECT < 0 or DAYS_TO_COLLECT > 7):
        raise InputError(f'FncDaysToCollect must be a number 0-7')


async def main(mytimer: func.TimerRequest, starter: str) -> None:
    client = df.DurableOrchestrationClient(starter)
    instance_id = "FncIntegrationSentinelStaticInstanceId"

    existing_instance = await client.get_status(instance_id)
    logging.info(f'OrchestratorWatchdog: {ORCHESTRATION_NAME} status: {existing_instance.runtime_status}')

    if TERMINATE_APP:
        reason = f'FncTerminateApp set to {TERMINATE_APP}'
        await terminate_app(client, existing_instance.runtime_status, instance_id, reason)
        return

    # Only start the orchestrator if it's not already running.
    if existing_instance.runtime_status in NOT_RUNNING_FUNCTION_STATES:
        validate_configuration()
        await client.start_new(ORCHESTRATION_NAME, instance_id, create_args())
        logging.info(f"OrchestratorWatchdog: Started {ORCHESTRATION_NAME}")

    
async def terminate_app(client, status, instance_id, reason: str):
    if status not in NOT_RUNNING_FUNCTION_STATES:
        await client.terminate(instance_id=instance_id, reason=reason)
        logging.info(f'OrchestrationWatchdog: Termination request sent to {ORCHESTRATION_NAME}.')


def create_args():
    timestamp = datetime.now(tz=timezone.utc)
    if DAYS_TO_COLLECT:
        start_date = timestamp.replace(hour=0, minute=0, second=0).isoformat()
    else:
        start_date = (timestamp - timedelta(minutes=INTERVAL)).isoformat()

    args = {}
    args['checkpoints'] = {event_type.strip(): start_date for event_type in EVENT_TYPES}
    if DETECTIONS:
        args['checkpoints']['detections'] = start_date
    if DAYS_TO_COLLECT:
        args['days_to_collect'] = DAYS_TO_COLLECT

    args['interval'] = INTERVAL
    return args
