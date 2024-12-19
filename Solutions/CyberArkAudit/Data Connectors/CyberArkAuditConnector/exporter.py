import logging
import os
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient


def _transform_schema(audit_events: list) -> list:
    dcr_events = [
        {
            'CyberArkTenantId': audit['tenantId'],
            'accountName': audit.get('accountName', ''),
            'action': audit.get('action', ''),
            'actionType': audit.get('actionType', ''),
            'applicationCode': audit.get('applicationCode', ''),
            'auditCode': audit.get('auditCode', ''),
            'auditType': audit.get('auditType', ''),
            'cloudAssets': audit.get('cloudAssets', ''),
            'cloudIdentities': audit.get('cloudIdentities', ''),
            'cloudProvider': audit.get('cloudProvider', ''),
            'cloudWorkspacesAndRoles': audit.get('cloudWorkspacesAndRoles', ''),
            'command': audit.get('command', ''),
            'component': audit.get('component', ''),
            'identityType': audit.get('identityType', ''),
            'message': audit.get('message', ''),
            'target': audit.get('target', ''),
            'timestamp': int(audit.get('timestamp', 0)),
            'targetPlatform': audit.get('targetPlatform', ''),
            'targetAccount': audit.get('targetAccount', ''),
            'safe': audit.get('safe', ''),
            'sessionId': audit.get('sessionId', ''),
            'serviceName': audit.get('serviceName', ''),
            'source': audit.get('source', ''),
            'userId': audit.get('userId', ''),
            'username': audit.get('username', '')
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
