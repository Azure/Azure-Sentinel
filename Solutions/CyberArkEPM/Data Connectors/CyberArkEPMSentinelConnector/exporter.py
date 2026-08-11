import json
import logging
import os
from datetime import datetime, timezone

from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient


_CONNECTOR_EVENT_TYPES = {
    'aggregated_events',
    'raw_event',
    'aggregated_policy_audits',
    'policy_audit_raw_event_details',
    'admin_audit',
}


def _to_rfc3339_utc(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    if not isinstance(value, str):
        return None

    s = value.strip()
    if not s:
        return None

    # Examples in docs:
    # - 2021-07-07T06:44:52Z
    # - 2022-02-28T11:28:16.069Z
    try:
        if s.endswith('Z'):
            # datetime.fromisoformat doesn't accept trailing 'Z' directly
            dt = datetime.fromisoformat(s[:-1])
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    except Exception:
        return None


def _pick_timegenerated(event: dict):
    for k in ('arrivalTime', 'lastEventDate', 'firstEventDate', 'date', 'Date', 'time', 'Time'):
        ts = _to_rfc3339_utc(event.get(k))
        if ts:
            return ts
    return _to_rfc3339_utc(datetime.now(timezone.utc))


def _get_first(event: dict, keys):
    for k in keys:
        v = event.get(k)
        if v is not None and v != '':
            return v
    return None


def _transform_schema(epm_events):
    dcr_events = []
    for event in epm_events:
        if not isinstance(event, dict):
            continue

        raw_event_type = event.get('eventType') or event.get('event_type')
        if isinstance(raw_event_type, str) and raw_event_type in _CONNECTOR_EVENT_TYPES:
            connector_event_type = raw_event_type
            cyberark_event_type = event.get('CyberArkEventType') or event.get('cyberArkEventType')
        else:
            connector_event_type = event.get('EventType') or event.get('event_type') or 'unknown'
            cyberark_event_type = raw_event_type

        normalized = {
            'TimeGenerated': _pick_timegenerated(event),
            'EventType': connector_event_type,
            'SetId': event.get('SetId') or event.get('setId'),
            'SetName': event.get('SetName') or event.get('set_name') or event.get('setName'),
            'EpmAgentId': event.get('agentId') or event.get('lastAgentId'),
            'ComputerName': event.get('computerName') or event.get('lastEventComputerName') or event.get('sourceWSName'),
            'UserName': _get_first(event, ('userName', 'lastEventUserName', 'firstEventUserName', 'owner')),
            'PolicyName': event.get('policyName') or event.get('lastEventDisplayName'),
            'PolicyAction': event.get('policyAction') or event.get('threatDetectionAction') or event.get('threatProtectionAction'),
            'CyberArkEventType': cyberark_event_type,
            'FileName': _get_first(event, ('fileName', 'lastEventFileName', 'lastEventOriginalFileName', 'originalFileName')),
            'FilePath': event.get('filePath') or event.get('fileLocation'),
            'Hash': event.get('hash'),
            'Publisher': event.get('publisher'),
            'SourceType': event.get('sourceType') or event.get('lastEventSourceType'),
            'SourceName': event.get('sourceName') or event.get('lastEventSourceName'),
            'FirstEventDate': _to_rfc3339_utc(event.get('firstEventDate')),
            'LastEventDate': _to_rfc3339_utc(event.get('lastEventDate')),
            'ArrivalTime': _to_rfc3339_utc(event.get('arrivalTime')),
            'TotalEvents': event.get('totalEvents'),
            'AffectedComputers': event.get('affectedComputers'),
            'AffectedUsers': event.get('affectedUsers'),
            'AggregatedBy': event.get('aggregatedBy'),
            'FileQualifier': event.get('fileQualifier'),
            'Skipped': event.get('skipped'),
            'SkippedCount': event.get('skippedCount'),
            'AdditionalFields': event,
        }

        # Drop None keys (keeps payload smaller and avoids type conflicts in DCR)
        normalized = {k: v for k, v in normalized.items() if v is not None}

        # Ensure non-dynamic fields don't accidentally become dict/list
        for k, v in list(normalized.items()):
            if k == 'AdditionalFields':
                continue
            if isinstance(v, (dict, list)):
                normalized[k] = json.dumps(v)

        dcr_events.append(normalized)

    return dcr_events


def send_dcr_data(data: list):
    endpoint = os.environ.get('DATA_COLLECTION_ENDPOINT')
    rule_id = os.environ.get('LOGS_DCR_RULE_ID')
    try:
        credential = DefaultAzureCredential()       # CodeQL [SM05139] This data connector (Function app based) is deprecated.
        client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)
        dcr_events = _transform_schema(data)
        client.upload(rule_id=rule_id, stream_name=os.environ.get('LOGS_DCR_STREAM_NAME'), logs=dcr_events)
    except Exception as e:
        logging.error(f"Upload failed: {e}")
