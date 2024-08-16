import constants
import time

LOGS_TO_CONSUME = constants.LOGS_TO_CONSUME.downcase
FLOW_EVENTS = constants.FLOW_EVENTS
AUDIT_EVENTS = constants.AUDIT_EVENTS
MAX_SCRIPT_EXEC_TIME_MINUTES = constants.MAX_SCRIPT_EXEC_TIME_MINUTES


def skip_processing_file(file_path):
    """
    Customer can choose to ingest either audit or traffic or both
    When SQS messages are processed, this method helps filter which file paths should be filtered away

    Return whether a file indicated by file_path is filtered or not, and this is dependent on LOGS_TO_CONSUME

    So if LOGS_TO_CONSUME is set to All by customer, then all logs are consumed by default and the method returns False
    Else, either audit or traffic events are consumed
    """
    if LOGS_TO_CONSUME == "All":
        return False

    if "auditable" in file_path:
        return FLOW_EVENTS in LOGS_TO_CONSUME
    else:
        return AUDIT_EVENTS in LOGS_TO_CONSUME


def check_if_script_runs_too_long(percentage, script_start_time):
    """
        This method checks if the script has ran "percentage" amount of time from starting of the script
        percentage: double
        script_start_time : datetime

    Args:
        percentage (_type_): _description_
        script_start_time (_type_): _description_

    Returns:
        _type_: _description_
    """
    now = int(time.time())
    duration = now - script_start_time
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * percentage)
    return duration > max_duration


__all__ = ["skip_processing_file", "check_if_script_runs_too_long"]
