import boto3
import json
import datetime
from botocore.config import Config as BotoCoreConfig
import tempfile
import os
import gzip
import time
import base64
import hashlib
import hmac
import requests
import threading
import azure.functions as func
import logging
import re

customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']
log_type = "CrowdstrikeReplicatorLogs"
AWS_KEY = os.environ['AWS_KEY']
AWS_SECRET = os.environ['AWS_SECRET']
AWS_REGION_NAME = os.environ['AWS_REGION_NAME']
QUEUE_URL = os.environ['QUEUE_URL']
VISIBILITY_TIMEOUT = 60
temp_dir = tempfile.TemporaryDirectory()

if 'logAnalyticsUri' in os.environ:
   logAnalyticsUri = os.environ['logAnalyticsUri']
   pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
   match = re.match(pattern,str(logAnalyticsUri))
   if not match:
       raise Exception("Invalid Log Analytics Uri.")
else:
    logAnalyticsUri = "https://" + customer_id + ".ods.opinsights.azure.com"

def get_sqs_messages():
    logging.info("Creating SQS connection")
    sqs = boto3.resource('sqs', region_name=AWS_REGION_NAME, aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
    queue = sqs.Queue(url=QUEUE_URL)
    logging.info("Queue connected")
    for msg in queue.receive_messages(VisibilityTimeout=VISIBILITY_TIMEOUT):
        msg_body = json.loads(msg.body)
        ts = datetime.datetime.utcfromtimestamp(msg_body['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        logging.info("Start processing bucket {0}: {1} files with total size {2}, bucket timestamp: {3}".format(msg_body['bucket'],msg_body['fileCount'],msg_body['totalSize'],ts))
        if "files" in msg_body:
            if download_message_files(msg_body) is True:
                msg.delete()

def process_message_files():
    for file in files_for_handling:
        process_file(file)

def download_message_files(msg):
    try:
        msg_output_path = os.path.join(temp_dir.name, msg['pathPrefix'])
        if not os.path.exists(msg_output_path):
            os.makedirs(msg_output_path)
        for s3_file in msg['files']:
            s3_path = s3_file['path']
            local_path = os.path.join(temp_dir.name, s3_path)
            logging.info("Start downloading file {}".format(s3_path))
            s3_client.download_file(msg['bucket'], s3_path, local_path)
            if check_damaged_archive(local_path) is True:
                logging.info("File {} successfully downloaded.".format(s3_path))
                files_for_handling.append(local_path)
            else:
                logging.warn("File {} damaged. Unpack ERROR.".format(s3_path))
        return True
    except Exception as ex:
        logging.error("Exception in downloading file from S3. Msg: {0}".format(str(ex)))
        return False

def check_damaged_archive(file_path):
    chunksize = 1024*1024  # 10 Mbytes
    with gzip.open(file_path, 'rb') as f:
        try:
            while f.read(chunksize) != '':
                return True
        except:
            return False

def process_file(file_path):
    global processed_messages_success, processed_messages_failed
    processed_messages_success = 0
    processed_messages_failed = 0
    size = 1024*1024
    # unzip archive to temp file
    out_tmp_file_path = file_path.replace(".gz", ".tmp")
    with gzip.open(file_path, 'rb') as f_in:
        with open(out_tmp_file_path, 'wb') as f_out:
            while True:
                data = f_in.read(size)
                if not data:
                    break
                f_out.write(data)
    os.remove(file_path)
    threads = []
    with open(out_tmp_file_path) as file_handler:
        for data_chunk in split_chunks(file_handler):
            chunk_size = len(data_chunk)
            logging.info("Processing data chunk of file {} with {} events.".format(out_tmp_file_path, chunk_size))
            data = json.dumps(data_chunk)
            t = threading.Thread(target=post_data, args=(data, chunk_size))
            threads.append(t)
            t.start()
    for t in threads:
        t.join()
    logging.info("File {} processed. {} events - successfully, {} events - failed.".format(file_path, processed_messages_success,processed_messages_failed))
    os.remove(out_tmp_file_path)

def split_chunks(file_handler, chunk_size=15000):
    chunk = []
    for line in file_handler:
        chunk.append(json.loads(line))
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

def post_data(body,chunk_count):
    global processed_messages_success, processed_messages_failed
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = logAnalyticsUri + resource + "?api-version=2016-04-01"
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        processed_messages_success = processed_messages_success + chunk_count
        logging.info("Chunk with {} events was processed and uploaded to Azure".format(chunk_count))
    else:
        processed_messages_failed = processed_messages_failed + chunk_count
        logging.warn("Problem with uploading to Azure. Response code: {}".format(response.status_code))

def cb_rename_tmp_to_json(file_path, file_size, lines_count):
    out_file_name = file_path.replace(".tmp", ".json")
    os.rename(file_path, out_file_name)

def create_s3_client():
    try:
        boto_config = BotoCoreConfig(region_name=AWS_REGION_NAME)
        return boto3.client('s3', region_name=AWS_REGION_NAME, aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET, config=boto_config)
    except Exception as ex:
        logging.error("Connect to S3 exception. Msg: {0}".format(str(ex)))
        return None

s3_client = create_s3_client()

def main(mytimer: func.TimerRequest)  -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    logging.info(logAnalyticsUri)
    global files_for_handling
    files_for_handling = []
    get_sqs_messages()
    process_message_files()