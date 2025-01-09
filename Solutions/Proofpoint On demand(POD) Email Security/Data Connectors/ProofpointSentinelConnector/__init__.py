import os
import datetime
import socket
import websocket
import json
import ssl
import time
import base64
import hashlib
import hmac
import requests
import azure.functions as func
import logging
import certifi
import re

from .sentinel_connector import AzureSentinelConnector

customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']
cluster_id = os.environ['ProofpointClusterID']
_token = os.environ['ProofpointToken']
time_delay_minutes = 60
event_types = ["maillog","message"]
logAnalyticsUri = os.environ.get('logAnalyticsUri')

FIELD_SIZE_LIMIT_BYTES = 1000 * 32


if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("ProofpointPOD: Invalid Log Analytics Uri.")

def check_size(queue):
        data_bytes_len = len(json.dumps(queue).encode())
        return data_bytes_len < FIELD_SIZE_LIMIT_BYTES


def split_big_request(queue):
        if check_size(queue):
            return [queue]
        else:
            middle = int(len(queue) / 2)
            queues_list = [queue[:middle], queue[middle:]]
            return split_big_request(queues_list[0]) + split_big_request(queues_list[1])

def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Starting program')
    if datetime.datetime.utcnow().minute < 2:
        time.sleep(120)
    api = Proofpoint_api()
    for evt_type in event_types:
        api.get_data(event_type=evt_type)

class Proofpoint_api:
    def __init__(self):
        self.cluster_id = cluster_id
        self.logAnalyticsUri = logAnalyticsUri
        self._token = _token
        self.time_delay_minutes = int(time_delay_minutes)
        self.gen_timeframe(time_delay_minutes=self.time_delay_minutes)

    def gen_timeframe(self, time_delay_minutes):
        before_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=time_delay_minutes)
        self.before_time = before_time.strftime("%Y-%m-%dT%H:59:59.999999")
        self.after_time = before_time.strftime("%Y-%m-%dT%H:00:00.000000")

    def set_websocket_conn(self, event_type):
        max_retries = 3
        url = f"wss://logstream.proofpoint.com:443/v1/stream?cid={self.cluster_id}&type={event_type}&sinceTime={self.after_time}&toTime={self.before_time}"
        # defining headers for websocket connection (do not change this)
        header = {
            "Connection": "Upgrade",
            "Upgrade": "websocket",
            "Authorization": f"Bearer {self._token}",
            "Sec-WebSocket-Key": "SGVsbG8sIHdvcmxkIQ==",
            "Sec-WebSocket-Version": "13"
        }
        sslopt = {
            'cert_reqs': ssl.CERT_REQUIRED,
            'ca_certs': certifi.where(),
            'check_hostname': True
        }
        for attempt in range(max_retries):
            try:
                logging.info('Opening Websocket logstream {}'.format(url))
                ws = websocket.create_connection(url, header=header, sslopt=sslopt)
                ws.settimeout(20)
                time.sleep(2)
                logging.info(
                    'Websocket connection established to cluster_id={}, event_type={}'.format(self.cluster_id, event_type))
                print('Websocket connection established to cluster_id={}, event_type={}'.format(self.cluster_id, event_type))
                return ws
            except Exception as err:
                logging.error('Error while connectiong to websocket {}'.format(err))
                print('Error while connectiong to websocket {}'.format(err))
                if attempt < max_retries - 1:
                    logging.info('Retrying connection in 5 seconds...')
                    time.sleep(5)  # Wait for a while before retrying
                else:
                    return None

    def gen_chunks_to_object(self,data,chunksize=100):
        chunk = []
        for index, line in enumerate(data):
            if (index % chunksize == 0 and index > 0):
                yield chunk
                del chunk[:]
            chunk.append(line)
        yield chunk

    def gen_chunks(self,data,event_type):
        for chunk in self.gen_chunks_to_object(data, chunksize=10000):
            print(len(chunk))
            obj_array = []
            for row in chunk:
                if row != None and row != '':
                    y = json.loads(row)
                    if ('msgParts' in y) and (len(json.dumps(y['msgParts']).encode()) > FIELD_SIZE_LIMIT_BYTES):
                        if isinstance(y['msgParts'],list):
                            queue_list = split_big_request(y['msgParts'])
                            count = 1
                            for q in queue_list:
                                columnname = 'msgParts' + str(count)
                                y[columnname] = q
                                count+=1
                            del y['msgParts']
                            
                        elif isinstance(y['msgParts'],dict):
                            queue_list = list(y['msgParts'].keys())
                            for count, key in enumerate(queue_list, 1):
                                if count > 10:
                                    break
                                y[f"msgParts{key}"] = y['msgParts'][key]

                            del y['msgParts']
                        else:
                            pass
                    y.update({'event_type': event_type})
                    obj_array.append(y)

            sentinel = AzureSentinelConnector(
                log_analytics_uri=logAnalyticsUri,
                workspace_id=customer_id,
                shared_key=shared_key,
                log_type=event_type,
                queue_size=5000
            )
            for event in obj_array:
                sentinel.send(event)
            sentinel.flush()

    def get_data(self, event_type=None):
        sent_events = 0
        ws = self.set_websocket_conn(event_type)
        time.sleep(2)
        if ws is not None:
            events = []
            while True:
                try:
                    data = ws.recv()
                    events.append(data)
                    sent_events += 1
                    if len(events) > 500:
                        self.gen_chunks(events,event_type)
                        events = []
                except websocket._exceptions.WebSocketTimeoutException:
                    break
                except Exception as err:
                    logging.error('Error while receiving data: {}'.format(err))
                    print('Error while receiving data: {}'.format(err))
                    break
            try:
                ws.close()
            except Exception as err:
                logging.error('Error while closing socket: {}'.format(err))
                print('Error while closing socket: {}'.format(err))                
            if sent_events > 0:
                self.gen_chunks(events,event_type)           
        logging.info('Total events sent: {}. Type: {}. Period(UTC): {} - {}'.format(sent_events, event_type,
                                                                                            self.after_time,
                                                                                            self.before_time))
        print('Total events sent: {}. Type: {}. Period(UTC): {} - {}'.format(sent_events, event_type,
                                                                                            self.after_time,
                                                                                           self.before_time))
