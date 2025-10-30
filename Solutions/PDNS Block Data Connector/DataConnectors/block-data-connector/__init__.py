import base64
from datetime import datetime
import hashlib
import hmac
import json
import logging
import os
from typing import Dict, List, Tuple


from .fetch_data import AWSDataFetcher, StixEvent
from .state_manager import StateManager
import azure.functions
import requests

# This number was derived by making a pessimistic estimate of how many events are needed to 
# violate the 30 MB cap on post requests to Log Analytics
MAX_NO_EVENTS_IN_REQUEST = 20000
LOG_ANALYTICS_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
FILE_SHARE_CONNECTION_STRING = os.environ['AzureWebJobsStorage']


def main(trigger: azure.functions.TimerRequest) -> None:
    if trigger.past_due:
        logging.warn('The timer is past due!')

    workspace_id, shared_key = get_log_analytics_configuration()
    data_fetcher = AWSDataFetcher(*get_aws_configuration())

    file_keys_and_dates = data_fetcher.get_recent_file_keys_and_dates()
    
    if len(file_keys_and_dates) == 0:
        return
    
    logging.info("Got all recent file keys in bucket")


    for key, _ in file_keys_and_dates:
        stix_events = data_fetcher.get_stix_events_from_file_key(key)

        logging.info(f"Got STIX events for {key}")

        for stix_events_chunk in chunk_list(stix_events, MAX_NO_EVENTS_IN_REQUEST):
            post_to_log_analytics(stix_events_chunk, workspace_id, shared_key)

        logging.info('Data sent to Azure Log Analytics')

        checkpoint = {
            "Key": file_keys_and_dates[-1][0],
            "Date": file_keys_and_dates[-1][1].isoformat()
        }

        state_manager = StateManager(FILE_SHARE_CONNECTION_STRING)
        state_manager.post(json.dumps(checkpoint))


def post_to_log_analytics(
        data: List[StixEvent],
        workspace_id: str, shared_key: str
) -> None:
    endpoint = f"https://{workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
    payload = json.dumps(data)
    headers = construct_headers(payload, shared_key, workspace_id)

    response = requests.post(endpoint, data=payload, headers=headers)

    if not response.ok:
        raise Exception(
            f"Error sending data to Azure Log Analytics: {response.status_code} \n Endpoint: {endpoint} \n Headers: {headers}")


def construct_headers(payload: str, shared_key: str, workspace_id: str) -> Dict[str, str]:
    formatted_date = datetime.utcnow().strftime(LOG_ANALYTICS_DATE_FORMAT)
    signature = construct_signature(payload, formatted_date, shared_key)
    return {
        "Content-Type": "application/json",
        "Log-Type": "PDNSDataBlock",
        "Authorization": f"SharedKey {workspace_id}:{signature}",
        "x-ms-date": formatted_date,
    }


def construct_signature(payload: str, formated_date: str, shared_key: str) -> str:
    content = (
        f"POST\n{str(len(payload))}\n"
        f"application/json\n"
        f"x-ms-date:{formated_date}\n"
        f"/api/logs"
    )

    hashed_content = hmac.new(
        base64.b64decode(shared_key),
        content.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    return base64.b64encode(hashed_content).decode('utf-8')


def get_log_analytics_configuration() -> Tuple[str, str]:
    workspace_id = os.environ['LogAnalyticsWorkspaceID']
    if not workspace_id:
        raise ValueError('LogAnalyticsWorkspaceID is not set')

    shared_key = os.environ['LogAnalyticsSharedKey']
    if not shared_key:
        raise ValueError('LogAnalyticsSharedKey is not set')

    return workspace_id, shared_key


def get_aws_configuration() -> Tuple[str, str, str, str, str, str]:
    bucket_arn = os.environ.get('S3BucketName', None)
    if not bucket_arn:
        raise ValueError("S3BucketName is not set")

    bucket_region = os.environ.get('S3BucketRegion', None)
    if not bucket_region:
        raise ValueError("S3BucketRegion is not set")

    client_prefix = os.environ.get('S3ClientPrefix', None)
    if not client_prefix:
        raise ValueError("S3ClientPrefix is not set")
    
    aws_key_id = os.environ.get("AWSKeyID", None)
    if not aws_key_id:
        raise ValueError("AWSKeyID is not set")
    
    aws_secret_key = os.environ.get("AWSSecretKey", None)
    if not aws_secret_key:
        raise ValueError("AWSSecretKey is not set")
    
    role_arn = os.environ.get('RoleARN')
    if not role_arn:
        raise ValueError("RoleARN is not set")

    return (bucket_arn, bucket_region, client_prefix, aws_key_id, aws_secret_key, role_arn)


def flatten(l):
    return [item for sublist in l for item in sublist]


def chunk_list(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]
