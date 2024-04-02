import logging
import os
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient


def _transform_schema(audit_events: list) -> list:
    dcr_events = []
    for audit in audit_events:
        dcr = dict()
        dcr['CyberArkTenantId'] = audit['tenantId']
        dcr['timestamp'] = int(audit.get('timestamp', 0))
        dcr['username'] = audit.get('username', '')
        dcr['applicationCode'] = audit.get('applicationCode', '')
        dcr['auditCode'] = audit.get('auditCode', '')
        dcr['auditType'] = audit.get('auditType', '')
        dcr['action'] = audit.get('action', '')
        dcr['userId'] = audit.get('userId', '')
        dcr['source'] = audit.get('source', '')
        dcr['actionType'] = audit.get('actionType', '')
        dcr['component'] = audit.get('component', '')
        dcr['serviceName'] = audit.get('serviceName', '')
        dcr['target'] = audit.get('target', '')
        dcr['command'] = audit.get('command', '')
        dcr['sessionId'] = audit.get('sessionId', '')
        dcr['message'] = audit.get('message', '')
        dcr_events.append(dcr)
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
