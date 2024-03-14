import logging
import os
from models import DCREventModel
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient


def _transform_schema(audit_events: list) -> list:
    dcr_events = [DCREventModel(**event).model_dump() for event in audit_events]
    return dcr_events


def send_dcr_data(data: list):
    endpoint = os.environ.get('DATA_COLLECTION_ENDPOINT')
    rule_id = os.environ.get('LOGS_DCR_RULE_ID')
    try:
        credential = DefaultAzureCredential()
        client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)
        dcr_events = _transform_schema(data)
        client.upload(rule_id=rule_id, stream_name=os.environ.get('LOGS_DCR_STREAM_NAME'), logs=dcr_events)
    except Exception as e:
        logging.error(f"Upload failed: {e}")
