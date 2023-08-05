import json
import oci
import os
import logging
import re
from base64 import b64decode
import azure.functions as func
import time

from .sentinel_connector import AzureSentinelConnector


logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)


MessageEndpoint = os.environ['MessageEndpoint']
StreamOcid = os.environ['StreamOcid'] 
WORKSPACE_ID = os.environ['AzureSentinelWorkspaceId']
SHARED_KEY = os.environ['AzureSentinelSharedKey']
LOG_TYPE = 'OCI_Logs'
CURSOR_TYPE = os.getenv('CursorType', 'group')
MAX_SCRIPT_EXEC_TIME_MINUTES = 5
PARTITIONS = os.getenv('Partition',"0")
Message_Limit = os.getenv('Message_Limit',250)
limit = int(Message_Limit)

LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


def main(mytimer: func.TimerRequest):
    logging.info('Function started.')
    start_ts = int(time.time())
    config = get_config()
    oci.config.validate_config(config)

    sentinel_connector = AzureSentinelConnector(LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, LOG_TYPE, queue_size=2000)

    stream_client = oci.streaming.StreamClient(config, service_endpoint=MessageEndpoint)

    if CURSOR_TYPE.lower() == 'group' :
        cursor = get_cursor_by_group(stream_client, StreamOcid, "group1", "group1-instance1")
    else :
        cursor = get_cursor_by_partition(stream_client, StreamOcid, partition=PARTITIONS)
    
    process_events(stream_client, StreamOcid, cursor, limit, sentinel_connector, start_ts)
    logging.info(f'Function finished. Sent events {sentinel_connector.successfull_sent_events_number}.')

def parse_key(key_input):
    try:
        begin_line = re.search(r'-----BEGIN [A-Z ]+-----', key_input).group()
        key_input = key_input.replace(begin_line, '')
        end_line = re.search(r'-----END [A-Z ]+-----', key_input).group()
        key_input = key_input.replace(end_line, '')
        encr_lines = ''
        proc_type_line = re.search(r'Proc-Type: [^ ]+', key_input)
        if proc_type_line:
            proc_type_line = proc_type_line.group()
            dec_info_line = re.search(r'DEK-Info: [^ ]+', key_input).group()
            encr_lines += proc_type_line + '\n'
            encr_lines += dec_info_line + '\n'
            key_input = key_input.replace(proc_type_line, '')
            key_input = key_input.replace(dec_info_line, '')
        body = key_input.strip().replace(' ', '\n')
        res = ''
        res += begin_line + '\n'
        if encr_lines:
            res += encr_lines + '\n'
        res += body + '\n'
        res += end_line
    except Exception:
        raise Exception('Error while reading private key.')
    return res


def get_config():
    config = {
        "user": os.environ['user'],
        "key_content": parse_key(os.environ['key_content']),
        "pass_phrase": os.environ.get('pass_phrase', ''),
        "fingerprint": os.environ['fingerprint'],
        "tenancy": os.environ['tenancy'],
        "region": os.environ['region']
    }
    return config


def get_cursor_by_group(sc, sid, group_name, instance_name):
    logging.info("Creating a cursor for group {}, instance {}".format(group_name, instance_name))
    cursor_details = oci.streaming.models.CreateGroupCursorDetails(group_name=group_name, instance_name=instance_name,
                                                                   type=oci.streaming.models.
                                                                   CreateGroupCursorDetails.TYPE_TRIM_HORIZON,
                                                                   commit_on_get=True)
    response = sc.create_group_cursor(sid, cursor_details)
    return response.data.value

def get_cursor_by_partition(client, stream_id, partition):
    print("Creating a cursor for partition {}".format(partition))
    cursor_details = oci.streaming.models.CreateCursorDetails(
        partition=partition,
        type=oci.streaming.models.CreateCursorDetails.TYPE_TRIM_HORIZON)
    response = client.create_cursor(stream_id, cursor_details)
    cursor = response.data.value
    return cursor


def process_events(client: oci.streaming.StreamClient, stream_id, initial_cursor, limit, sentinel: AzureSentinelConnector, start_ts):
    cursor = initial_cursor
    while True:
        get_response = client.get_messages(stream_id, cursor, limit=limit, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        if not get_response.data:
            return

        for message in get_response.data:
            if message:
                event = b64decode(message.value.encode()).decode()
                logging.info('event details {}'.format(event))
                event = json.loads(event)
                if "data" in event:
                    if "request" in event["data"]:
                        if "headers" in event["data"]["request"]:
                            event["data"]["request"]["headers"] = json.dumps(event["data"]["request"]["headers"])
                        if "parameters" in event["data"]["request"]:
                            event["data"]["request"]["parameters"] = json.dumps(
                                event["data"]["request"]["parameters"])
                    if "response" in event["data"]:
                        if "headers" in event["data"]["response"]:
                            event["data"]["response"]["headers"] = json.dumps(event["data"]["response"]["headers"])
                    if "additionalDetails" in event["data"]:
                        event["data"]["additionalDetails"] = json.dumps(event["data"]["additionalDetails"])
                    if "stateChange" in event["data"]:
                        logging.info("In data.stateChange : {}".format(event["data"]["stateChange"]))
                        if event["data"]["stateChange"] is not None and "current" in event["data"]["stateChange"] :
                            event["data"]["stateChange"]["current"] = json.dumps(
                                event["data"]["stateChange"]["current"])
                sentinel.send(event)

        sentinel.flush()
        if check_if_script_runs_too_long(start_ts):
            logging.info('Script is running too long. Saving progress and exit.')
            break
        cursor = get_response.headers["opc-next-cursor"]


def check_if_script_runs_too_long(start_ts):
    now = int(time.time())
    duration = now - start_ts
    max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.85)
    return duration > max_duration