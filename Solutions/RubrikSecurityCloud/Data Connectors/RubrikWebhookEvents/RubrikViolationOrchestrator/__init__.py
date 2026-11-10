"""This __init__ file is called by the Http Starter to pass Violation data to the activity function.

For classification-results events, an RSC hit-count gate (RubrikClassificationActivity) decides
whether to ingest: the original webhook payload is ingested only when policy hits > 0.
"""
import inspect
import json
import azure.durable_functions as df
from shared_code.consts import (
    VIOLATION_LOG_TYPE,
    VIOLATION_STREAM,
    DCR_WEBHOOK_RULE_ID,
    LOGS_STARTS_WITH,
    LOG_FORMAT,
    CLASSIFICATION_CLASS,
    CLASSIFICATION_EVENT_NAME,
)
from shared_code.logger import applogger

FUNCTION_NAME = "RubrikViolationOrchestrator"


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Route Violation data; gate classification events on RSC policy-hit count.

    Args:
        context (df.DurableOrchestrationContext): durable orchestration context.

    Returns:
        str: result of the Activity function, or a status string when gated out.
    """
    __method_name = inspect.currentframe().f_code.co_name
    applogger.info(
        LOG_FORMAT.format(
            LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, "function called!"
        )
    )
    json_data = context.get_input()

    try:
        payload = json.loads(json_data) if isinstance(json_data, str) else json_data
    except (ValueError, TypeError) as err:
        applogger.error(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
                "Failed to parse webhook payload as JSON; treating as empty: {}".format(err),
            )
        )
        payload = {}
    if not isinstance(payload, dict):
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
                "Webhook payload is not a JSON object (got {}); treating as empty.".format(
                    type(payload).__name__
                ),
            )
        )
        payload = {}
    custom_details = payload.get("custom_details") or {}

    event_class = payload.get("class")
    event_name = custom_details.get("eventName")

    ingest_input = {
        "data": json_data,
        "log_type": VIOLATION_LOG_TYPE,
        "stream_name": VIOLATION_STREAM,
        "rule_id": DCR_WEBHOOK_RULE_ID,
    }

    if event_class == CLASSIFICATION_CLASS:
        object_name = custom_details.get("objectName")
        object_type = custom_details.get("objectType")

        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
                "Classification event detected: eventName={}, object={}, "
                "objectType={}.".format(event_name, object_name, object_type),
            )
        )

        if event_name != CLASSIFICATION_EVENT_NAME:
            applogger.debug(
                LOG_FORMAT.format(
                    LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
                    "Classification event '{}' for object {} of type {} is not '{}'; "
                    "not ingested.".format(
                        event_name,
                        object_name,
                        object_type,
                        CLASSIFICATION_EVENT_NAME,
                    ),
                )
            )
            return "Classification event is not {}; not ingested.".format(
                CLASSIFICATION_EVENT_NAME
            )

        object_id = custom_details.get("objectId")
        event_timestamp = payload.get("timestamp")

        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
                "Invoking hit-count gate (RubrikClassificationActivity) for "
                "objectId={}, eventTimestamp={}.".format(object_id, event_timestamp),
            )
        )
        gate = yield context.call_activity(
            "RubrikClassificationActivity",
            {"objectId": object_id, "eventTimestamp": event_timestamp},
        )
        hit_count = (gate or {}).get("hitCount", 0)
        snapshot_id = (gate or {}).get("snapshotId")
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
                "Hit-count gate result for object {}: hitCount={}, snapshotId={}, "
                "error={}.".format(
                    object_name, hit_count, snapshot_id, (gate or {}).get("error")
                ),
            )
        )

        if hit_count > 0:
            # Enrich the original webhook payload with the resolved snapshotId
            # (under custom_details) so it lands in the SnapshotId column.
            enriched = dict(payload)
            enriched_details = dict(custom_details)
            enriched_details["snapshotId"] = snapshot_id
            enriched["custom_details"] = enriched_details
            classification_ingest_input = {
                "data": json.dumps(enriched),
                "log_type": VIOLATION_LOG_TYPE,
                "stream_name": VIOLATION_STREAM,
                "rule_id": DCR_WEBHOOK_RULE_ID,
            }
            result1 = yield context.call_activity(
                "RubrikActivity", classification_ingest_input
            )
            applogger.info(
                LOG_FORMAT.format(
                    LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
                    "Classification event for object {} of type {} had {} hit(s) "
                    "(snapshot {}); ingested.".format(
                        object_name, object_type, hit_count, snapshot_id
                    ),
                )
            )
            return result1

        applogger.info(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
                "No violations/hits found for object {} of type {} for snapshot {} "
                "at time {}; not ingested.".format(
                    object_name, object_type, snapshot_id, event_timestamp
                ),
            )
        )
        return "No violations/hits found; classification event not ingested."

    applogger.debug(
        LOG_FORMAT.format(
            LOGS_STARTS_WITH, FUNCTION_NAME, __method_name,
            "Non-classification Violation event (class={}); routing to "
            "RubrikActivity.".format(event_class),
        )
    )
    result1 = yield context.call_activity("RubrikActivity", ingest_input)
    applogger.info(
        LOG_FORMAT.format(
            LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, "function completed!"
        )
    )
    return result1


main = df.Orchestrator.create(orchestrator_function)
