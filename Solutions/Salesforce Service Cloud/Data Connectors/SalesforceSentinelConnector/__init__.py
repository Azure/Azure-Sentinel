import base64
import csv
import datetime
import hashlib
import hmac
import json
import logging
import os
import re
import sys
import tempfile

import azure.functions as func
import requests

customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']
log_type = 'SalesforceServiceCloud'
user = os.environ['SalesforceUser']
password = os.environ['SalesforcePass']
security_token = os.environ['SalesforceSecurityToken']
consumer_key = os.environ['SalesforceConsumerKey']
consumer_secret = os.environ['SalesforceConsumerSecret']
object =  "EventLogFile"
interval = os.getenv("timeInterval","hourly")
hours_interval = 1
days_interval = 1
url = os.environ['SalesforceTokenUri']
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Salesforce Service Cloud: Invalid Log Analytics Uri.")

def _get_token():
    params = {
        "grant_type": "password",
        "client_id": consumer_key,
        "client_secret": consumer_secret,
        "username": user,
        "password": f'{password}{security_token}'
    }
    try:
        r = requests.post(url, params=params)
        _token = json.loads(r.text)['access_token']
        _instance_url = json.loads(r.text)['instance_url']
        return _token,_instance_url
    except Exception as err:
        logging.error(f'Token getting failed. Exiting program. {err}')
        exit()


def generate_date():
    if interval == 'hourly':
        current_time = datetime.datetime.utcnow().replace(second=0, microsecond=0)
        past_time = current_time - datetime.timedelta(hours=hours_interval)
    elif interval == 'daily':
        current_time = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        past_time = current_time - datetime.timedelta(days=days_interval, hours=1)
    return past_time.strftime("%Y-%m-%dT%H:%M:%SZ")


def pull_log_files():
    past_time = generate_date()

    if interval == 'hourly':
        query = "/services/data/v44.0/query?q=SELECT+Id+,+EventType+,+Interval+,+LogDate+,+LogFile+,+LogFileLength" + \
        "+FROM+EventLogFile" + \
        f"+WHERE+Interval+=+'Hourly'+and+CreatedDate+>+{past_time}"

    elif interval == 'daily':
        query = "/services/data/v44.0/query?q=SELECT+Id+,+CreatedDate+,+EventType+,+LogDate+,+LogFile+,+LogFileLength" + \
                "+FROM+EventLogFile" + \
                f"+WHERE+LogDate+>+{past_time}"
    try:
        logging.info('Searching files last modified from {}'.format(past_time))
        r = requests.get(f'{instance_url}{query}', headers=headers)
    except Exception as err:
        logging.error(f'File list getting failed. Exiting program. {err}')
    if r.status_code == 200:
        files = json.loads(r.text)['records']
        done_status = json.loads(r.text)['done']
        while done_status is False:
            query = json.loads(r.text)['nextRecordsUrl']
            try:
                r = requests.get(f'{instance_url}{query}', headers=headers)
            except Exception as err:
                logging.error(f'File list getting failed. Exiting program. {err}')
            if r.status_code == 200:
                done_status = json.loads(r.text)['done']
                for file in json.loads(r.text)['records']:
                    files.append(file)
            else:
                done_status = True
        logging.info('Total number of files is {}.'.format(len(files)))
        return files
    else:
        logging.error(f'File list getting failed. Exiting program. {r.status_code} {r.text}')


def get_file_raw_lines(file_url, file_in_tmp_path):
    url = f'{instance_url}{file_url}'
    try:
        with requests.get(url, stream=True, headers=headers) as r:
            if r.status_code == 200:
                print('File successfully downloaded from url {} '.format(url))
                with open(file_in_tmp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
            else:
                print('File downloading failed. {r.status_code} {r.text} {file_url}')
    except Exception as err:
        print('File downloading failed. {err} {file_url}')


def gen_chunks_to_object(file_in_tmp_path, chunksize=100):
    field_names = [name.lower() for name in list(csv.reader(open(file_in_tmp_path)))[0]]
    field_names = [x if x != 'type' else 'type_' for x in field_names]
    reader = csv.DictReader(open(file_in_tmp_path), fieldnames=field_names)
    chunk = []
    next(reader)
    for index, line in enumerate(reader):
        if (index % chunksize == 0 and index > 0):
            yield chunk
            del chunk[:]
        chunk.append(line)
    yield chunk

def gen_chunks(file_in_tmp_path):
    for chunk in gen_chunks_to_object(file_in_tmp_path, chunksize=2000):
        obj_array = []
        for row in chunk:
            row = enrich_event_with_user_email(row)
            obj_array.append(row)
        body = json.dumps(obj_array)
        post_data(customer_id, shared_key, body, log_type, len(obj_array))


def get_users(url=None):
    if url is None:
        query = "/services/data/v44.0/query?q=SELECT+Id+,+Email+FROM+User"
    else:
        query = url
    try:
        r = requests.get(f'{instance_url}{query}', headers=headers)

        for x in r.json()['records']:
            users.update({x['Id']: x['Email']})

        if not r.json()['done']:
            next_url = r.json()['nextRecordsUrl']
            get_users(url=next_url)
    except Exception as err:
        logging.error(f'Users getting failed. {err}')


def enrich_event_with_user_email(event):
    user_id = event.get('user_id_derived')
    if user_id:
        user_email = users.get(user_id)
        if user_email:
            event.update({'user_email': user_email})
    return event


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization


def post_data(customer_id, shared_key, body, log_type, chunk_count):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'
    
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(uri, data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
        logging.info("Chunk was processed({} events)".format(chunk_count))
    else:
        print("Response code: {}".format(response.status_code))
        logging.warn("Response code: {}".format(response.status_code))


def main(mytimer: func.TimerRequest) -> None:
    logging.info(f'Script started')
    global instance_url,token,headers,customer_id,shared_key,log_type,users,temp_dir,file_in_tmp_path
    csv.field_size_limit(sys.maxsize)
    logging.info('Checking limit')
    sys.setrecursionlimit(10**9)
    logging.info('Checking recurssion')
    users = dict()
    token = _get_token()[0]
    instance_url = _get_token()[1]
    headers = {
        'Authorization': f'Bearer {token}'
    }
    temp_dir = tempfile.TemporaryDirectory()
    get_users()
    for line in pull_log_files():
        logging.info('Started downloading {}'.format(line["LogFile"]))
        local_filename = line["LogFile"].replace('/', '_').replace(':', '_')
        file_in_tmp_path = "{}/{}".format(temp_dir.name, local_filename)
        get_file_raw_lines(line["LogFile"],file_in_tmp_path)
        if os.path.isfile(file_in_tmp_path):
            file_size = os.path.getsize(file_in_tmp_path)
            if file_size > 0:
                gen_chunks(file_in_tmp_path)
                logging.info('File processed {}'.format(line["LogFile"]))
            else:
                logging.info('Empty file: {}'.format(line["LogFile"]))
        else:
            logging.info('File Not Found: {}'.format(line["LogFile"]))
    logging.info('Program finished.')
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)