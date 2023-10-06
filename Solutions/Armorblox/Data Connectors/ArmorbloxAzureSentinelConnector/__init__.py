import azure.functions as func
from armorblox.client import Client
import datetime
import json
import base64
import hashlib
import hmac
import requests
import re
import os
import logging

from urllib.parse import urlparse
from .state_manager import StateManager

ARMORBLOX_API_TOKEN = os.environ["ArmorbloxAPIToken"]
ARMORBLOX_INSTANCE_NAME = os.environ.get("ArmorbloxInstanceName", "").strip()
ARMORBLOX_INSTANCE_URL = os.environ.get("ArmorbloxInstanceURL", "").strip()
ARMORBLOX_INCIDENT_API_PAGE_SIZE = 100
ARMORBLOX_INCIDENT_API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
ARMORBLOX_INCIDENT_API_TIME_DELTA_IN_MINUTES = 60
CUSTOM_TABLE_NAME = "Armorblox"
CHUNKSIZE = 10000
SENTINEL_WORKSPACE_ID = os.environ["WorkspaceID"]
SENTINEL_WORKSPACE_KEY = os.environ["WorkspaceKey"]
CONNECTION_STRING = os.environ["AzureWebJobsStorage"]
LOG_ANALYTICS_URI = os.environ.get("LogAnalyticsUri", "").strip()

if LOG_ANALYTICS_URI == "":
    LOG_ANALYTICS_URI = "https://" + SENTINEL_WORKSPACE_ID + ".ods.opinsights.azure.com"

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Armorblox Data Connector: Invalid Log Analytics URI")

if (ARMORBLOX_INSTANCE_NAME == "") and (ARMORBLOX_INSTANCE_URL == ""):
    raise Exception("At least one of Armorblox instance name or URL need to be provided")


class Armorblox(Client):

    def __init__(self, api_key, instance_name=None, instance_url=None):
        super().__init__(api_key=api_key, instance_name=instance_name, instance_url=instance_url)
        self.incidents_list = []
        self.from_date, self.to_date = self.generate_date()

    @staticmethod
    def generate_date():
        current_time = datetime.datetime.utcnow().replace(second=0)
        state = StateManager(connection_string=CONNECTION_STRING)
        past_time = state.get()

        if past_time is not None:
            logging.info("The last time point is: {}".format(past_time))
        else:
            logging.info("There is no last time point, trying to get incidents for last day.")
            past_time = (current_time - datetime.timedelta(
                minutes=ARMORBLOX_INCIDENT_API_TIME_DELTA_IN_MINUTES)).strftime(ARMORBLOX_INCIDENT_API_TIME_FORMAT)

        state.post(current_time.strftime(ARMORBLOX_INCIDENT_API_TIME_FORMAT))
        return past_time, current_time.strftime(ARMORBLOX_INCIDENT_API_TIME_FORMAT)

    def _process_incidents(self, params):
        response_json, next_page_token, total_count = self.incidents.list(page_token=None, params=params)
        self.incidents_list.extend(response_json)
        while next_page_token:
            params["page_token"] = next_page_token
            response_json, next_page_token, total_count = self.incidents.list(page_token=None, params=params)
            self.incidents_list.extend(response_json)

    def get_incidents(self):

        params = {
            "from_date": self.from_date,
            "to_date": self.to_date,
            "page_size": ARMORBLOX_INCIDENT_API_PAGE_SIZE
        }

        self._process_incidents(params)
        return self.incidents_list


class Sentinel:

    @staticmethod
    def gen_chunks_to_object(data):
        chunk = []
        for index, line in enumerate(data):
            if (index % CHUNKSIZE == 0) and index > 0:
                yield chunk
                del chunk[:]
            chunk.append(line)
        yield chunk

    def gen_chunks(self, data):
        for chunk in self.gen_chunks_to_object(data):
            obj_array = []
            for row in chunk:
                if row is not None and row != "":
                    obj_array.append(row)
            body = json.dumps(obj_array)
            self._post_data(body, len(obj_array))

    @staticmethod
    def build_signature(date, content_length, method, content_type, resource):
        x_headers = "x-ms-date:" + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(SENTINEL_WORKSPACE_KEY)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(SENTINEL_WORKSPACE_ID, encoded_hash)
        return authorization

    def _post_data(self, body, chunk_count):
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"
        rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        content_length = len(body)
        signature = self.build_signature(rfc1123date, content_length, method, content_type, resource)
        uri = LOG_ANALYTICS_URI + resource + "?api-version=2016-04-01"
        headers = {
            "content-type": content_type,
            "Authorization": signature,
            "Log-Type": CUSTOM_TABLE_NAME,
            "x-ms-date": rfc1123date
        }
        response = requests.post(uri, data=body, headers=headers)
        if 200 <= response.status_code <= 299:
            logging.info("Chunk was sent to Azure Sentinel({} events)".format(chunk_count))
        else:
            logging.info("Error during sending events to Azure Sentinel. Response code:{}".format(response.status_code))


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)

    armorblox = Armorblox(ARMORBLOX_API_TOKEN, ARMORBLOX_INSTANCE_NAME, ARMORBLOX_INSTANCE_URL)
    sentinel = Sentinel()
    incidents_list = armorblox.get_incidents()
    sentinel.gen_chunks(incidents_list)
