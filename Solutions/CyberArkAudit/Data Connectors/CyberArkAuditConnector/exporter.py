import logging
import os
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient


def _transform_schema(audit_events: list) -> list:
    dcr_events = [
        {
            'CyberArkTenantId': audit['tenantId'],
            'accountName': audit.get('accountName') or '',
            'action': audit.get('action') or '',
            'actionType': audit.get('actionType') or '',
            'applicationCode': audit.get('applicationCode') or '',
            'auditCode': audit.get('auditCode') or '',
            'auditType': audit.get('auditType') or '',
            'cloudAssets': audit.get('cloudAssets') or '',
            'cloudIdentities': audit.get('cloudIdentities') or '',
            'cloudProvider': audit.get('cloudProvider') or '',
            'command': audit.get('command') or '',
            'component': audit.get('component') or '',
            'identityType': audit.get('identityType') or '',
            'message': audit.get('message') or '',
            'target': audit.get('target') or '',
            'timestamp': int(audit.get('timestamp', 0)),
            'targetPlatform': audit.get('targetPlatform') or '',
            'targetAccount': audit.get('targetAccount') or '',
            'safe': audit.get('safe') or '',
            'sessionId': audit.get('sessionId') or '',
            'serviceName': audit.get('serviceName') or '',
            'source': audit.get('source') or '',
            'userId': audit.get('userId') or '',
            'username': audit.get('username') or ''
        }
        for audit in audit_events]
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
