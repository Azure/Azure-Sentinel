import azure.functions as func
import datetime
import json
import base64
import hashlib
import hmac
import requests
import re
import os
import logging
from .state_manager import StateManager


token = os.environ['SentinelOneAPIToken']
domain = os.environ['SentinelOneUrl']
table_name = "SentinelOne"
chunksize = 10000
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
connection_string = os.environ['AzureWebJobsStorage']
logAnalyticsUri = os.environ.get('logAnalyticsUri')

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("SentinelOne Data Connector: Invalid Log Analytics Uri.")

class SOne():

    def __init__(self):
        """
            Initializes the sentinelone header.
            Dates are generated for historical poll. Historical time is fixed and is 1 day.
        """
        self.domain = domain
        self.header = {
            'Authorization': 'ApiToken {}'.format(token),
            'Content-Type': 'application/json',
            }
        self.from_date, self.to_date = self.generate_date()
        self.results_array = []
        self.threat_id_arr = []
        self.computer_name_arr = []

    def get_threat_id(self, json_obj_arr):
        """Stores all the threat IDs from the data obtained from threat endpoint in a list. 
            To be used for getting extended threat information.

        Args:
            json_obj_arr (dict): Contains the threat data JSON in form of dictionary.
        """
        for j in json_obj_arr['data']:
            if(j['threatInfo']['threatId'] not in self.threat_id_arr):
                self.threat_id_arr.append(j['threatInfo']['threatId'])

    def get_computer_name(self, json_obj_arr):
        """Stores all the computer names from the data obtained from agents endpoint in a list. 
            To be used for getting installed applications information.
        

        Args:
            json_obj_arr (dict): Contains the agent data JSON in form of dictionary.
        """
        for j in json_obj_arr['data']:
            if(j['computerName'] not in self.computer_name_arr):
                self.computer_name_arr.append(j['computerName'])

    def generate_date(self):
        """Fetches the date from the previously stored date in fileshare.
            Fetches from last 1 day if no fileshare present. Stores the current time after fetching.

        Returns:
            string, string: The last polled time and current time.
        """
        current_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
        state = StateManager(connection_string)
        past_time = state.get()
        if past_time is not None:
            logging.info("The last time point is: {}".format(past_time))
        else:
            logging.info("There is no last time point, trying to get events for last day.")
            past_time = (current_time - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        state.post(current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        logging.info("Getting data from: " + past_time)
        logging.info("To: " + current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        return (past_time, current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    
    def get_report(self, report_type_suffix, report_type_name, params = None):
        """Getting data for threats, agents, activities, groups and alerts.

        Args:
            report_type_suffix (string): The specific endpoint to be polled for.
            report_type_name (string): The name of the endpoint.
            params (dict, optional): Sends the parameters to filter the data. Defaults to None.

        Returns:
            string: The token pointing to the next page.
        """
        try:
            r = requests.get(self.domain + report_type_suffix, headers = self.header, params = params)
            if r.status_code == 200:
                if("Threats" in report_type_name):
                    self.get_threat_id(r.json())
                elif("Agents" in report_type_name):
                    self.get_computer_name(r.json())
                
                self.results_array_join(r.json(), report_type_name)
                next_page_token = (r.json().get('pagination', {})).get('nextCursor')
                logging.debug("Report returns: {}".format(next_page_token))
                return next_page_token
            elif r.status_code == 400:
                logging.error("Invalid user input received. See error details for further information."
                      " Error code: {}".format(r.status_code))
            elif r.status_code == 401:
                logging.error("Unauthorized access - please sign in and retry. Error code: {}".format(r.status_code))
            else:
                logging.error("Something wrong. Error code: {}".format(r.status_code))
        except Exception as err:
            logging.error("Something wrong. Exception error text: {}".format(err))

    def get_installed_apps(self, report_type_suffix, report_type_name, name, params = None):
        """Getting data for installed applications.

        Args:
            report_type_suffix (string): The specific endpoint to be polled for.
            report_type_name (string): The name of the endpoint.
            name (string): The computerName to get installed applications for.
            params (dict, optional): Sends the parameters to filter the data. Defaults to None.

        Returns:
            string: The token pointing to the next page.
        """
        try:
            url = self.domain + report_type_suffix + "?agentComputerName__contains=" + name
            r = requests.get(url, headers = self.header, params = params)
            
            if r.status_code == 200:
                self.results_array_join(r.json(), report_type_name)
                next_page_token = (r.json().get('pagination', {})).get('nextCursor')
                logging.debug("Report returns: {}".format(next_page_token))
                return next_page_token
            elif r.status_code == 400:
                logging.error("Invalid user input received. See error details for further information."
                      " Error code: {}".format(r.status_code))
            elif r.status_code == 401:
                logging.error("Unauthorized access - please sign in and retry. Error code: {}".format(r.status_code))
            else:
                logging.error("Something wrong. Error code: {}".format(r.status_code))
        except Exception as err:
            logging.error("Something wrong. Exception error text: {}".format(err))

    def get_threat_data(self, report_type_suffix, report_type_name, id, params = None):
        """Getting data for extended threat info: Events and Notes.

        Args:
            report_type_suffix (string): The specific endpoint to be polled for.
            report_type_name (string): The name of the endpoint.
            id (int): Threat ID for which to get extended threat data for.
            params (dict, optional): Sends the parameters to filter the data. Defaults to None.

        Returns:
            string: The token pointing to the next page.
        """
        try:
            if("Notes" in report_type_name):
                url = self.domain + report_type_suffix + str(id) + "/notes"
                r = requests.get(url, headers = self.header, params = params)
            elif("Events" in report_type_name):
                url = self.domain + report_type_suffix + str(id) + "/explore/events"
                r = requests.get(url, headers = self.header, params = params)
            if r.status_code == 200:
                self.results_array_join(r.json(), report_type_name, id)
                next_page_token = (r.json().get('pagination', {})).get('nextCursor')
                logging.debug("Report returns: {}".format(next_page_token))
                return next_page_token
            elif r.status_code == 400:
                logging.error("Invalid user input received. See error details for further information."
                      " Error code: {}".format(r.status_code))
            elif r.status_code == 401:
                logging.error("Unauthorized access - please sign in and retry. Error code: {}".format(r.status_code))
            else:
                logging.error("Something wrong. Error code: {}".format(r.status_code))
        except Exception as err:
            logging.error("Something wrong. Exception error text: {}".format(err))

    def results_array_join(self, result_element, api_req_name, threat_id = None):
        """Adds extra JSON element to the data for identifying what kind of data is polled in the logs, by event_name.

        Args:
            result_element (dict): The body with all results for a specific endpoint data. 
            api_req_name (string): Name from which to identify the endpoint used.
            threat_id (int, optional): Threat ID to append to extended threat data. Defaults to None.
        """
        for element in result_element['data']:
            element['event_name'] = api_req_name
            if(threat_id):
                element['threatInfo_threatId'] = threat_id
            self.results_array.append(element)

    def reports_list(self):
        """Main polling function for all the endpoints.
        """
        reports_api_requests_dict = \
            {
                "activities_created_events": {"api_req": "/web/api/v2.1/activities", "name": "Activities."},
                "agents_created_events": {"api_req": "/web/api/v2.1/agents", "name": "Agents."},
                "agents_updated_events": {"api_req": "/web/api/v2.1/agents", "name": "Agents."},
                "groups_updated_events": {"api_req": "/web/api/v2.1/groups", "name": "Groups."},
                "threats_created_events": {"api_req": "/web/api/v2.1/threats", "name": "Threats."},
                "threats_updated_events": {"api_req": "/web/api/v2.1/threats", "name": "Threats."},
                "alerts_created_events": {"api_req": "/web/api/v2.1/cloud-detection/alerts", "name": "Alerts."}
            }
        for api_req_id, api_req_info in reports_api_requests_dict.items():
            api_req = api_req_info['api_req']
            api_req_name = api_req_info['name']
            
            if "created_events" in api_req_id:
                api_req_params = {
                    "limit": 1000,
                    "createdAt__gt": self.from_date,
                    "createdAt__lt": self.to_date
                }
            elif "updated_events" in api_req_id:
                api_req_params = {
                    "limit": 200,
                    "updatedAt__gt": self.from_date,
                    "updatedAt__lt": self.to_date
                }
            logging.debug("Getting report: {}".format(api_req_id))
            next_page_token = self.get_report(report_type_suffix = api_req, report_type_name = api_req_name, params = api_req_params)
            
            while next_page_token:
                api_req_params.update({"cursor": next_page_token})
                next_page_token = self.get_report(report_type_suffix=api_req, report_type_name=api_req_name,
                                                  params = api_req_params)
        #gets threat notes and events for given id
        for id in self.threat_id_arr:    
            logging.debug("Getting report: notes")
            next_page_token = self.get_threat_data("/web/api/v2.1/threats/", "Notes", id)
            while next_page_token:
                api_req_params = {"cursor": next_page_token}
                next_page_token = self.get_threat_data("/web/api/v2.1/threats/", "Notes", id,
                                                  params = api_req_params)
            logging.debug("Getting report: events")
            next_page_token = self.get_threat_data("/web/api/v2.1/threats/", "Events", id)
            while next_page_token:
                api_req_params = {"cursor": next_page_token}
                next_page_token = self.get_threat_data("/web/api/v2.1/threats/", "Events", id,
                                                  params = api_req_params)

        #gets installed applications for given agent computer name
        for name in self.computer_name_arr:
            logging.debug("Getting report: installed apps")
            next_page_token = self.get_installed_apps("/web/api/v2.1/installed-applications", "Installed-apps", name)
            while next_page_token:
                api_req_params = {"cursor": next_page_token}
                next_page_token = self.get_installed_apps("/web/api/v2.1/installed-applications", "Installed-apps", name, params = api_req_params)
            

class Sentinel:

    def __init__(self):
        """Initializes variables for sentinel log ingesting.
        """
        self.logAnalyticsUri = logAnalyticsUri
        self.success_processed = 0
        self.fail_processed = 0
        self.table_name = table_name
        self.chunksize = chunksize
    def gen_chunks_to_object(self, data, chunksize=100):
        chunk = []
        for index, line in enumerate(data):
            if (index % chunksize == 0 and index > 0):
                yield chunk
                del chunk[:]
            chunk.append(line)
        yield chunk

    def gen_chunks(self, data):
        """posts the data chunks to azure logs.

        Args:
            data (dict): The body to be sent to the logs.
        """
        for chunk in self.gen_chunks_to_object(data, chunksize=self.chunksize):
            obj_array = []
            for row in chunk:
                if row != None and row != '':
                    obj_array.append(row)
            body = json.dumps(obj_array)
            self.post_data(body, len(obj_array))

    def build_signature(self, date, content_length, method, content_type, resource):
        """Builds the API signature.

        Args:
            date (datetime): Date when the signature was built.
            content_length (int): Length of content sending.
            method (string): The API call used.
            content_type (string): JSON content is being sent.
            resource (string): Where to post in sentinel.

        Returns:
            string: Authorization signature generated.
        """
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def post_data(self, body, chunk_count):
        """Build and send a request to the POST API

        Args:
            body (json string): Body to send.
            chunk_count (int): Number of events in the body.
        """
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
            'Log-Type': self.table_name,
            'x-ms-date': rfc1123date
        }
        response = requests.post(uri, data=body, headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            logging.debug("Chunk was processed({} events)".format(chunk_count))
            self.success_processed = self.success_processed + chunk_count
        else:
            logging.error("Error during sending events to Azure Sentinel. Response code:{}".format(response.status_code))
            self.fail_processed = self.fail_processed + chunk_count

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info("Python timer trigger function ran at %s", utc_timestamp)
    logging.info("Starting program") 
    SO = SOne()
    sentinel = Sentinel()
    SO.reports_list()
    SOne_class_vars = vars(SO)
    from_date, to_date = SOne_class_vars["from_date"], SOne_class_vars["to_date"]
    results_array = SOne_class_vars["results_array"]
    sentinel.gen_chunks(results_array)
    sentinel_class_vars = vars(sentinel)
    success_processed, fail_processed = sentinel_class_vars["success_processed"], \
                                        sentinel_class_vars["fail_processed"]
    logging.info("Total events processed successfully: {}, failed: {}. Period: {} - {}"
          .format(success_processed, fail_processed, from_date, to_date))
