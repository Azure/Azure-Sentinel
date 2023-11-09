from typing import Any, Dict

from azure.durable_functions.models.history.HistoryEvent import HistoryEvent
from azure.durable_functions.models.utils.json_utils \
    import add_attrib, add_json_attrib, add_datetime_attrib


def convert_history_event_to_json_dict(
        history_event: HistoryEvent) -> Dict[str, Any]:
    json_dict = {}

    add_attrib(json_dict, history_event, 'event_id', 'EventId')
    add_attrib(json_dict, history_event, 'event_type', 'EventType')
    add_attrib(json_dict, history_event, 'is_played', 'IsPlayed')
    add_datetime_attrib(json_dict, history_event, 'timestamp', 'Timestamp')
    add_attrib(json_dict, history_event, 'Input')
    add_attrib(json_dict, history_event, 'Reason')
    add_attrib(json_dict, history_event, 'Details')
    add_attrib(json_dict, history_event, 'Result')
    add_attrib(json_dict, history_event, 'Version')
    add_attrib(json_dict, history_event, 'RetryOptions')
    add_attrib(json_dict, history_event, 'TaskScheduledId')
    add_attrib(json_dict, history_event, 'Tags')
    add_attrib(json_dict, history_event, 'FireAt')
    add_attrib(json_dict, history_event, 'TimerId')
    add_attrib(json_dict, history_event, 'Name')
    add_attrib(json_dict, history_event, 'InstanceId')
    add_json_attrib(json_dict, history_event,
                    'orchestration_instance', 'OrchestrationInstance')
    return json_dict
