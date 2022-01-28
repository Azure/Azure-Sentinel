""" polls data from DS to azure logs """
import logging
from . import DS_api
from . import AS_api
from .state_serializer import State
import json
from . import constant
from DigitalShadowsConnectorAzureFunction import state_serializer

class poller:

    def __init__(self, ds_id, ds_key, secret, as_id, as_key, connection_string, historical_days, url):
        """ 
            initializes all necessary variables from other classes for polling 
        """
        
        self.DS_obj = DS_api.api(ds_id, ds_key, secret, url)
        self.AS_obj = AS_api.logs_api(as_id, as_key)
        self.date = State(connection_string)
        logging.info("got inside the poller code")
        self.event = self.date.get_last_event(historical_days)
        if(isinstance(self.event, tuple)):
            self.after_time = self.event[0]
            self.before_time = self.event[1]
            logging.info("From time: %s", self.after_time)
            logging.info("to time: %s", self.before_time)
        else:
            logging.info("Polling from event number " + str(self.event))

    def parse_desc(self, data):
        """
            adds more newlines to description for good display on Azure sentinel incidents
        """
        arr = data.splitlines()
        res = ""
        for e in arr:
            res = res + e + "\n\n"
        return res


    def post_azure(self, response, item):
        """
            posts to azure after appending triage information on it
        """
        json_obj = json.loads(response.text)
        comment_data = json.loads(self.DS_obj.get_triage_comments(item['id']))
        json_obj[0]['status'] = item['state']
        json_obj[0]['triage_id'] = item['id']
        json_obj[0]['triage_raised_time'] = item['raised']
        json_obj[0]['triage_updated_time'] = item['updated']
        
        comment_data_filtered = []
        for comment in comment_data:
            if comment['content'] != "":
                comment_data_filtered.append(comment)


        json_obj[0]['comments'] = comment_data_filtered
        
        json_obj[0]['description'] = self.parse_desc(json_obj[0]['description'])

        if('id' in json_obj[0] and not isinstance(json_obj[0]['id'], str)):
            json_obj[0]['description'] = json_obj[0]['description'] + "\n\nSearchlight Portal Link: https://portal-digitalshadows.com/triage/alert-incidents/" + str(json_obj[0]['id'])

        self.AS_obj.post_data(json.dumps((json_obj[0])), constant.LOG_NAME)

    def get_data(self):
        """
            getting the incident and alert data from digital shadows
        """
        triage_id = []
        try:
            if(isinstance(self.event, int)):
                event_dataJSON = self.DS_obj.get_triage_events_by_num(self.event)
                event_data = json.loads(event_dataJSON)
                self.date.post_event(self.event + len(event_data[:20]))
            else:
                event_dataJSON = self.DS_obj.get_triage_events(self.before_time, self.after_time)
                event_data = json.loads(event_dataJSON)
                event_num = event_data[0]['event-num']
                self.date.post_event(event_num + len(event_data[:20]))
                logging.info("First poll from event number " + str(event_num))

            
            logging.info("total number of events are " + str(len(event_data)))
            
            for event in event_data[:20]:
                if(event is not None):
                    triage_id.append(event['triage-item-id'])

            
        except (ValueError, IndexError, UnboundLocalError):
            
            logging.info("JSON is of invalid format or no new incidents or alerts are found")
        
        item_data = json.loads(self.DS_obj.get_triage_items(triage_id))
        
        return item_data

    def poll(self):
        """
            main polling function, 
            makes api calls in following fashion:
            triage-events --> triage-items --> incidents and alerts 
        """
                    
        try:
            #sending data to sentinel
            item_data = self.get_data()
            logging.info("total number of items are " + str(len(item_data)))
            for item in item_data:
                if(item['source']['incident-id'] is not None):
                    response = self.DS_obj.get_incidents(item['source']['incident-id'])
                    self.post_azure(response, item)

                elif(item['source']['alert-id'] is not None):
                    response = self.DS_obj.get_alerts(item['source']['alert-id'])
                    self.post_azure(response, item)


        except (KeyError, TypeError, UnboundLocalError, IndexError):
            
            logging.info("Key error or type error has occured or no new incidents or alerts are found")