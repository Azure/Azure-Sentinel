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


customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']
cluster_id = os.environ['ProofpointClusterID']
_token = os.environ['ProofpointToken']
time_delay_minutes = 60
event_types = ["maillog","message"]
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):    
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("ProofpointPOD: Invalid Log Analytics Uri.")

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
        url = f"wss://logstream.proofpoint.com:443/v1/stream?cid={self.cluster_id}&type={event_type}&sinceTime={self.after_time}&toTime={self.before_time}"
        logging.info('Opening Websocket logstream {}'.format(url))
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
        try:
            ws = websocket.create_connection(url, header=header, sslopt=sslopt)
            ws.settimeout(20)
            time.sleep(2)
            logging.info(
                'Websocket connection established to cluster_id={}, event_type={}'.format(self.cluster_id, event_type))
            print(
                'Websocket connection established to cluster_id={}, event_type={}'.format(self.cluster_id, event_type))
            return ws
        except Exception as err:
            logging.error('Error while connectiong to websocket {}'.format(err))
            print('Error while connectiong to websocket {}'.format(err))
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
                    y.update({'event_type': event_type})
                    obj_array.append(y)
            body = json.dumps(obj_array)
            self.post_data(body,len(obj_array),event_type)

    def build_signature(self, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def post_data(self,body,chunk_count,event_type):
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self.build_signature(rfc1123date, content_length, method, content_type,
                                    resource)
        
        uri = self.logAnalyticsUri + resource + '?api-version=2016-04-01'

        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': 'ProofpointPOD_' + event_type,
            'x-ms-date': rfc1123date
        }    
        response = requests.post(uri, data=body, headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            logging.info("Chunk was processed({} events)".format(chunk_count))
            print("Chunk was processed({} events)".format(chunk_count))
        else:
            print("Error during sending events to Azure Sentinel. Response code:{}".format(response.status_code))
            logging.warn("Error during sending events to Azure Sentinel. Response code: {}".format(response.status_code))

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