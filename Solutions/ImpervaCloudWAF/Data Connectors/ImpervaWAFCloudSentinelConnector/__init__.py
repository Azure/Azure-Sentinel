import requests
from requests.packages.urllib3.util.retry import Retry
import urllib3
import os
import zlib
import json
import azure.functions as func
import base64
import hmac
import hashlib
import datetime
import re
import logging
from .state_manager import StateManager

customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']
imperva_waf_api_id = os.environ['ImpervaAPIID'] 
imperva_waf_api_key = os.environ['ImpervaAPIKey'] 
imperva_waf_log_server_uri = os.environ['ImpervaLogServerURI'] 
logs_encryption_private_key = ""

connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'
pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")


class ImpervaFilesHandler:

    def __init__(self):
        self.url = imperva_waf_log_server_uri
        retries = Retry(
            total=3,
            status_forcelist={500, 429},
            backoff_factor=1,
            respect_retry_after_header=True
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        self.session = requests.Session()
        self.session.mount('https://', adapter)
        self.auth = urllib3.make_headers(basic_auth='{}:{}'.format(imperva_waf_api_id, imperva_waf_api_key))
        self.files_array = self.list_index_file()
        self.sentinel = ProcessToSentinel()

    def list_index_file(self):
        files_array = []
        try:
            r = self.session.get(url="{}/{}".format(self.url, f"logs.index"),
                            headers= self.auth
                            )
            if 200 <= r.status_code <= 299:
                logging.info("Successfully downloaded index file.")
                for line in r.iter_lines():
                    files_array.append(line.decode('UTF-8'))
                return files_array
            elif r.status_code == 400:
                logging.error("Bad Request. The request was invalid or cannot be otherwise served."
                      " Error code: {}".format(r.status_code))
            elif r.status_code == 404:
                logging.error("Could not find index file. Response code is {}".format(r.status_code))
            elif r.status_code == 401:
                logging.error("Authorization error - Failed to download index file. Response code is {}".format(r.status_code))
            elif r.status_code == 429:
                logging.error("Rate limit exceeded - Failed to download index file. Response code is {}".format(r.status_code))
            else:
                if r.status_code is None:
                    logging.error("Something wrong. Error text: {}".format(r.text))
                else:
                    logging.error("Something wrong. Error code: {}".format(r.status_code))
        except Exception as err:
            logging.error("Something wrong. Exception error text: {}".format(err))

    def last_file_point(self):
        try:
            if self.files_array is not None:
                state = StateManager(connection_string=connection_string)
                past_file = state.get()
                if past_file is not None:
                    logging.info("The last file point is: {}".format(past_file))
                    try:
                        index = self.files_array.index(past_file)
                        files_arr = self.files_array[index + 1:]
                    except Exception as err:
                        logging.info("Last point file detection error: {}. So Processing all the files from index file".format(err))
                        files_arr = self.files_array
                else:
                    files_arr = self.files_array
                logging.info("There are {} files in the list index file.".format(len(files_arr)))
                if self.files_array is not None:
                    current_file = self.files_array[-1]
                state.post(current_file)
                return files_arr
        except Exception as err:
            logging.error("Last point file detection error. Exception error text: {}".format(err))

    def download_files(self):
        files_for_download = self.last_file_point()
        if files_for_download is not None:
            for file in files_for_download:
                logging.info("Downloading file {}".format(file))
                self.download_file(file)

    def download_file(self, file_name):
        try:
            r = self.session.get(url="{}/{}".format(self.url, file_name), stream=True, headers=self.auth)
            if 200 <= r.status_code <= 299:
                logging.info("Successfully downloaded file: {}".format(file_name))
                self.decrypt_and_unpack_file(file_name, r.content)
                return r.status_code
            elif r.status_code == 400:
                logging.error("Bad Request. The request was invalid or cannot be otherwise served."
                      " Error code: {}".format(r.status_code))
            elif r.status_code == 404:
                logging.error("Could not find file {}. Response code: {}".format(file_name, r.status_code))
            elif r.status_code == 401:
                logging.error("Authorization error - Failed to download file {}. Response code: {}".format(file_name, r.status_code))
            elif r.status_code == 429:
                logging.error("Rate limit exceeded - Failed to downloadfile {}. Response code: {}".format(file_name, r.status_code))
            else:
                if r.status_code is None:
                    logging.error("Something wrong. Error text: {}".format(r.text))
                else:
                    logging.error("Something wrong. Error code: {}".format(r.status_code))
        except Exception as err:
            logging.error("Something wrong. Exception error text: {}".format(err))

    def decrypt_and_unpack_file(self, file_name, file_content):
        logging.info("Unpacking and decrypting file {}".format(file_name))
        file_splitted = file_content.split(b"|==|\n")
        file_header = file_splitted[0].decode("utf-8")
        file_data = file_splitted[1]
        file_encryption_flag = file_header.find("key:")
        events_arr = []
        if file_encryption_flag == -1:
            try:
                events_data = zlib.decompressobj().decompress(file_data).decode("utf-8")
            except Exception as err:
                if 'while decompressing data: incorrect header check' in err.args[0]:
                    events_data = file_data.decode("utf-8")
                else:
                    logging.error("Error during decompressing and decoding the file with error message {}.".format(err))                   
        if events_data is not None:
            for line in events_data.splitlines():
                if "CEF" in line:
                    event_message = self.parse_cef(line)
                    events_arr.append(event_message)
        for chunk in self.gen_chunks_to_object(events_arr, chunksize=1000):
            self.sentinel.post_data(json.dumps(chunk), len(chunk), file_name)
    
    def parse_cef(self,cef_raw):
        rx = r'([^=\s]+)?=((?:[\\]=|[^=])+)(?:\s|$)'
        parsed_cef = {"EventVendor": "Imperva", "EventProduct": "Incapsula", "EventType": "SIEMintegration"}
        header_array = cef_raw.split('|')
        parsed_cef["Device Version"]=header_array[3]
        parsed_cef["Signature"]=header_array[4]
        parsed_cef["Attack Name"]=header_array[5]
        parsed_cef["Attack Severity"]=header_array[6]
        for key,val in re.findall(rx, cef_raw):
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            parsed_cef[key]=val
        cs_array = ['cs1','cs2','cs3','cs4','cs5','cs6','cs7','cs8']
        for elem in cs_array:
            if parsed_cef[elem] is not None:
                parsed_cef[(parsed_cef[f'{elem}Label']).replace(" ", "")] = parsed_cef[elem]
                parsed_cef.pop(f'{elem}Label')
                parsed_cef.pop(elem)

        if 'start' in parsed_cef.keys() and parsed_cef['start'] is not None and parsed_cef['start']!="":
            try:
                timestamp = datetime.datetime.utcfromtimestamp(int(parsed_cef['start'])/1000.0).isoformat()
                parsed_cef['EventGeneratedTime'] = timestamp
            except:
                parsed_cef['EventGeneratedTime'] = ""
        else:
            parsed_cef['EventGeneratedTime'] = ""

        return parsed_cef
                
    def gen_chunks_to_object(self, object, chunksize=100):
        chunk = []
        for index, line in enumerate(object):
            if (index % chunksize == 0 and index > 0):
                yield chunk
                del chunk[:]
            chunk.append(line)
        yield chunk

class ProcessToSentinel:

    def __init__(self):
        self.logAnalyticsUri = logAnalyticsUri

    def build_signature(self, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def post_data(self, body, chunk_count,file_name):
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
            'Log-Type': 'ImpervaWAFCloud',
            'x-ms-date': rfc1123date,
            'time-generated-field':'EventGeneratedTime'
        }
        response = requests.post(uri, data=body, headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            logging.info("Chunk was processed with {} events from the file: {}".format(chunk_count, file_name))
        else:
            logging.error("Error during sending events to Azure Sentinel. Response code:{}. File name: {}.".format(response.status_code,file_name))

def main(mytimer: func.TimerRequest)  -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    ifh = ImpervaFilesHandler()
    ifh.download_files()