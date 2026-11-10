"""Activity function: RSC classification hit-count gate.

Input:  {"objectId": str, "eventTimestamp": str}
Output: {"snapshotId": str|None, "hitCount": int, "error": str|None}

Never raises to the orchestrator — on any failure returns hitCount 0 with an error
string (fail-closed: the orchestrator will then skip ingestion).
"""
import inspect
from shared_code.logger import applogger
from shared_code.consts import LOGS_STARTS_WITH, LOG_FORMAT
from shared_code.rubrik_exception import RubrikException
from .rubrik_dspm import RubrikDSPM

FUNCTION_NAME = "RubrikClassificationActivity"


def main(name) -> dict:
    """Resolve snapshot and count policy hits for a classification event.

    Args:
        name (dict): {"objectId": str, "eventTimestamp": str}.

    Returns:
        dict: {"snapshotId": str|None, "hitCount": int, "error": str|None}.
    """
    __method_name = inspect.currentframe().f_code.co_name
    object_id = name.get("objectId")
    event_timestamp = name.get("eventTimestamp")
    applogger.info(
        LOG_FORMAT.format(
            LOGS_STARTS_WITH,
            FUNCTION_NAME,
            __method_name,
            "Classification gate invoked for object_id={}, event_timestamp={}.".format(
                object_id, event_timestamp
            ),
        )
    )
    try:
        if not object_id or not event_timestamp:
            applogger.warning(
                LOG_FORMAT.format(
                    LOGS_STARTS_WITH,
                    FUNCTION_NAME,
                    __method_name,
                    "Missing required parameter: objectId={}, eventTimestamp={}.".format(
                        object_id, event_timestamp
                    ),
                )
            )
            return {
                "snapshotId": None,
                "hitCount": 0,
                "error": "missing objectId or eventTimestamp",
            }
        client = RubrikDSPM()
        result = client.get_hit_count(object_id, event_timestamp)
        applogger.info(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "Classification gate result for object {}: hitCount={}, snapshotId={}, error={}".format(
                    object_id, result.get("hitCount"), result.get("snapshotId"), result.get("error")
                ),
            )
        )
        return result
    except RubrikException as err:
        applogger.error(
            LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err)
        )
        return {"snapshotId": None, "hitCount": 0, "error": str(err)}
    except Exception as err:
        applogger.error(
            LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err)
        )
        return {"snapshotId": None, "hitCount": 0, "error": str(err)}
