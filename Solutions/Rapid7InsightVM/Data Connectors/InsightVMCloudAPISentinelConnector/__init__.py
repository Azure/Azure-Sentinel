from time import sleep
import requests
from requests.packages.urllib3.util.retry import Retry
import azure.functions as func
import base64
import hmac
import hashlib
import json
import datetime
import os
import re
import logging

insightvm_apikey = os.environ['InsightVMAPIKey']
region = os.environ['InsightVMCloudRegion']
insightvm_url = f"https://{region}.api.insight.rapid7.com/vm/v4/integration/"
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
chunksize = 100
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'
pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")

class InsightVMAPIv4integration:

    def __init__(self):
        self.sentinel = ProcessToSentinel()
        self.base_url = insightvm_url
        self.api_key = insightvm_apikey
        self.headers = {
            'Accept': "application/json",
            'Content-Type': "application/json",
            'X-Api-Key': self.api_key
        }
        retries = Retry(
            total=5,
            status_forcelist={500, 408, 413},
            backoff_factor=1,
            respect_retry_after_header=True
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        self.session = requests.Session()
        self.session.mount('https://', adapter)
        
    def get_asset_list(self):
        assets_data = "data"
        page_num = 0
        while assets_data is not None:
            try:
                r = self.session.post(url="{}/{}".format(self.base_url, "assets"),
                                headers=self.headers,
                                verify=True,
                                params = {
                                    "size": 100,
                                    "page": page_num,
                                    "includeSame": True,
                                    "includeUniqueIdentifiers": True
                                })
                assets_data = r.json().get("data")
                if assets_data is not None:
                    if len(assets_data) == 0:
                        assets_data = None
                if  200 <= r.status_code <= 299:
                    page_num += 1
                    if assets_data is not None:
                        self.sentinel.gen_chunks(assets_data, "assets")
                        vuln_data = self.vulnerabilities_info_enrich(assets_data)
                        if vuln_data is not None:
                            self.sentinel.gen_chunks(vuln_data, "vulnerabilities")            
                else:
                    logging.error("Error. Code: {}. Meaning: {}.".format(r.status_code,r.json().get("message")))
            except Exception as err:
                logging.error("Something wrong. Exception error text: {}".format(err))
        logging.info("Total events processed successfully: {}, failed: {}.".format(self.sentinel.processed_events_success, self.sentinel.processed_events_fail))

    def vulnerabilities_info_enrich(self, asset_chunk_data):
        vuln_list = []
        for asset in asset_chunk_data:
            for vuln in asset.get("same"):
                vuln_list.append(vuln.get("vulnerability_id")) if vuln.get(
                    "vulnerability_id") not in vuln_list else vuln_list
        vuln_dict_list = self.get_vulnerabilities_info_list(str(vuln_list))
        vuln_chunk_data = []
        for asset in asset_chunk_data:
            for vuln in asset.get("same"):
                for vuln_dict_list_item in vuln_dict_list:
                    if vuln.get("vulnerability_id") == vuln_dict_list_item.get("id"):
                        vuln_chunk_data.append({
                                                "asset_id": asset.get("id"),
                                                "host_name": asset.get("host_name"),
                                                "ip": asset.get("ip"),
                                                "vuln_details": vuln_dict_list_item
                                                })
        return vuln_chunk_data

    def get_vulnerabilities_info_list(self, vulns_array):
        data = "data"
        body = \
            {
            "vulnerability": f"id IN {vulns_array}"
            }
        page_num = 0
        vulnerabilities_results = []
        while data is not None:
            try:
                r = self.session.post(url="{}/{}".format(self.base_url, "vulnerabilities"),
                                      headers=self.headers,
                                      verify=True,
                                      data = json.dumps(body),
                                      params={
                                          "size": 1000,
                                          "page": page_num
                                      })
                data = r.json().get("data")
                if data is not None:
                    if len(data) == 0:
                        data = None
                if 200 <= r.status_code <= 299:
                    page_num += 1
                    if data is not None:
                        vulnerabilities_results.extend(data)
                else:
                    logging.error("Error. Code: {}. Meaning: {}.".format(r.status_code, r.json().get("message")))
            except Exception as err:
                logging.error("Something wrong. Exception error text: {}".format(err))
        return vulnerabilities_results

class ProcessToSentinel:

    def __init__(self):
        self.logAnalyticsUri = logAnalyticsUri
        self.processed_events_success = 0
        self.processed_events_fail = 0
        self.chunksize = chunksize
    
    def gen_chunks_to_object(self, data, chunksize=100):
        chunk = []
        for index, line in enumerate(data):
            if (index % chunksize == 0 and index > 0):
                yield chunk
                del chunk[:]
            chunk.append(line)
        yield chunk

    def gen_chunks(self, data, table):
        for chunk in self.gen_chunks_to_object(data, chunksize=self.chunksize):
            obj_array = []
            for row in chunk:
                if row != None and row != '':
                    obj_array.append(row)
            body = json.dumps(obj_array)
            self.post_data(body, len(obj_array), table)

    def build_signature(self, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def post_data(self, body, chunk_count, table):
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
            'Log-Type': 'NexposeInsightVMCloud_'+table,
            'x-ms-date': rfc1123date
        }
        response = requests.post(uri, data=body, headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            logging.info("Chunk was processed({} events) to the table: {}".format(chunk_count, table))
            self.processed_events_success = self.processed_events_success + chunk_count
        else:
            logging.error("Error during sending events to Azure Sentinel. Response code:{}".format(response.status_code))
            self.processed_events_fail = self.processed_events_fail + chunk_count

def main(mytimer: func.TimerRequest)  -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    api = InsightVMAPIv4integration()
    logging.info("Get Assets and Vulnerabilities reports.")
    api.get_asset_list()
