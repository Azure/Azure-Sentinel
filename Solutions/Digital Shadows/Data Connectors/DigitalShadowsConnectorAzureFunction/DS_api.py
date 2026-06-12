""" handles all DS api related functions """
import logging
import requests
import base64
from urllib.parse import urlparse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

logger = logging.getLogger("DS_api")

class api:

    def __init__(self, id, key, secret, url):
        """ 
            constructer initializes the DS creds and creates passkey.
            Parses the url recieved from user.
        """
        u = urlparse(url)

        self.url = "https://" + u.netloc + u.path + "/"
        passkey = key + ":" + secret
        self.id = id
        self.b64val = base64.b64encode(bytes(passkey, 'utf-8')).decode("ascii")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": "Basic %s" % self.b64val,
            "searchlight-account-id": "%s" % self.id,
            "User-Agent": "DigitalShadowsAzureSentinelIntegration"
        })

        # Add retry logic to the session object
        retries = Retry(
            total=3,
            status_forcelist=frozenset({429, 500, 502, 503, 504}),
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=1,
            raise_on_status=False,
            connect=3,
            read=2,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)

    def get_alerts(self, alert_ids):
        """ 
            function for getting alerts using id
        """

        alert_url = self.url + "alerts"
        params = dict(id=alert_ids)
        response = self.session.get(alert_url, params=params)
        response.raise_for_status()
        return response.json()

    def get_incidents(self, incident_ids):
        """ 
            function for getting incidents using id list
        """
        incident_url = self.url + "incidents"
        params = dict(id=incident_ids)
        response = self.session.get(incident_url, params=params)
        response.raise_for_status()
        return response.json()

    def get_triage_events(self, before_date, after_date, classification_filter_operation, classification_list):
        """ 
            function for getting triage events,
            send only the DS converted dates using state serializer functions to get triage events
        """
        def _get_triage_events_by_date(before_date, after_date, classification_filter_operation, classification_list):
            params = self._get_classification_list(classification_filter_operation, classification_list)
            triage_url = self.url + "triage-item-events?limit=1000&event-created-before=" + str(before_date) + "&event-created-after=" +  str(after_date)
            response = self.session.get(triage_url, params=params)
            logger.info("Response for url: %s \t is : %s" % (triage_url, response.text))
            response.raise_for_status()
            return response.json()
        triage_events = _get_triage_events_by_date(before_date, after_date, classification_filter_operation, classification_list)

        if len(triage_events) == 1000:
            last_event_num = triage_events[len(triage_events) - 1].get("event-num")
            next_triage_events =self.get_triage_events_by_num(last_event_num, classification_filter_operation, classification_list)
            triage_events.extend(next_triage_events)
        
        return triage_events


    def get_triage_items(self, triage_ids):
        """  
            gets triage items from the triage events
        """

        items_url = self.url + "triage-items"
        params = dict(id=triage_ids)
        response = self.session.get(items_url, params=params)
        response.raise_for_status()
        return response.json()

    def get_triage_comments(self, item_id):
        """  
            gets triage comments from the triage items
        """

        items_url = self.url + "triage-items/" + str(item_id) + "/comments"
        response = self.session.get(items_url)
        response.raise_for_status()
        return response.json()
    
    def get_triage_events_by_num(self, event, classification_filter_operation, classification_list):
        """
            gets triage events by number
        """
        def _get_triage_events_by_num_in_chunck(event, classification_filter_operation, classification_list):
            triage_url = self.url + "triage-item-events?limit=1000&event-num-after=" + str(event)
            params = self._get_classification_list(classification_filter_operation, classification_list)
            response = self.session.get(triage_url, params=params)
            return response.json()
        triage_events = _get_triage_events_by_num_in_chunck(event, classification_filter_operation, classification_list)

        if len(triage_events) == 1000:
            triage_event_exists = True
            while triage_event_exists:
                event = event + 1000
                next_triage_events = _get_triage_events_by_num_in_chunck(event, classification_filter_operation, classification_list)
                if len(next_triage_events) > 0:
                    triage_events.extend(next_triage_events)
                else:
                    triage_event_exists = False
        
        return triage_events
        


    def _get_classification_list(self, classification_filter_operation, classification_list):
        params = None
        if classification_filter_operation == "include" and len(classification_list) > 0:
            params = {
                "risk-type": classification_list
            }
        elif classification_filter_operation == "exclude" and len(classification_list) > 0:
            params = {
                "risk-type-exclusion": classification_list,
            }
        else:
            raise Exception("Invalid Classification Filter Operation: %s. Valid operations can be one of (include, exclude)" % classification_filter_operation)
        return params
        