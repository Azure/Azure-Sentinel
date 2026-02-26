import json
import logging
import os
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient


def _transform_schema(epm_events):
    dcr_events = []
    for event in epm_events:
        if not isinstance(event, dict):
            continue
        sanitized = {}
        for k, v in event.items():
            if isinstance(v, (dict, list)):
                sanitized[k] = json.dumps(v)
            else:
                sanitized[k] = v
        dcr_events.append(sanitized)
    return dcr_events


def send_dcr_data(data):
    endpoint = os.environ.get('DATA_COLLECTION_ENDPOINT')
    rule_id = os.environ.get('LOGS_DCR_RULE_ID')
    try:
        credential = DefaultAzureCredential()       # CodeQL [SM05139] This data connector (Function app based) is deprecated.
        client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)
        dcr_events = _transform_schema(data)
        client.upload(rule_id=rule_id, stream_name=os.environ.get('LOGS_DCR_STREAM_NAME'), logs=dcr_events)
    except Exception as e:
        logging.error(f"Upload failed: {e}")
