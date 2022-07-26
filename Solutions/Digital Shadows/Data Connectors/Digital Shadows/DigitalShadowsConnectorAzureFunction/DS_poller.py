""" polls data from DS to azure logs """
import logging
from . import DS_api
from . import AS_api
from .state_serializer import State
import json
from . import constant

logger = logging.getLogger("DS_poller")

class poller:

    def __init__(self, function_name, ds_id, ds_key, secret, as_id, as_key, connection_string, historical_days, url):
        """ 
            initializes all necessary variables from other classes for polling 
        """
        
        self.DS_obj = DS_api.api(ds_id, ds_key, secret, url)
        self.AS_obj = AS_api.logs_api(as_id, as_key)
        self.date = State(connection_string, function_name)
        logger.info("got inside the poller code")
        self.event = self.date.get_last_event(historical_days)
        if isinstance(self.event, tuple):
            self.after_time = self.event[0]
            self.before_time = self.event[1]
            logger.info("From time: %s", self.after_time)
            logger.info("to time: %s", self.before_time)
        else:
            logger.info("Polling from event number " + str(self.event))

    def parse_desc(self, data):
        """
            adds more newlines to description for good display on Azure sentinel incidents
        """
        arr = data.splitlines()
        res = ""
        for e in arr:
            res = res + e + "\n\n"
        return res


    def post_azure(self, alerts_and_incidents, triage_items, app):
        """
            posts to azure after appending triage information on it
        """

        data = {}
        for item in triage_items:
            # Getting all the present triage items into the data dict
            if 'alert-id' in item['source'] and item['source']['alert-id'] is not None:
                data[item['source']['alert-id']] = [item, None]
            elif 'incident-id' in item['source'] and item['source']['incident-id'] is not None:
                data[item['source']['incident-id']] = [item, None]
            else:
                raise Exception(f'Triage item missing expected source ID field: {item}')

        for item in alerts_and_incidents:
            # Replacing None in the list with the incident/alert corresponding to respective triage item. 
            if item['id'] in data:
                data[item['id']][1] = item
            else:
                raise Exception(f'No matching triage item found for alert/incident: {item}')

        for triage_item, alert_or_incident in data.values():
            # validate we actually have an alert/incident before proceeding
            if not alert_or_incident:
                raise Exception(f'Triage item had no matching alert/incident data: {triage_item}')
            alert_or_incident['status'] = triage_item['state']
            alert_or_incident['triage_id'] = triage_item['id']
            alert_or_incident['triage_raised_time'] = triage_item['raised']
            alert_or_incident['triage_updated_time'] = triage_item['updated']
            
            #creating a custom json data to post into azure
            azure_obj = {
                **alert_or_incident,
                'status': triage_item['state'],
                'triage_id': triage_item['id'],
                'triage_raised_time': triage_item['raised'],
                'triage_updated_time': triage_item['updated'],
                'comments': [],
                'app': app
            }

            comment_data = self.DS_obj.get_triage_comments(triage_item['id'])

            for comment in comment_data:
                if 'content' not in comment:
                    continue
                uname = comment['user']['name'] if comment['user'] and 'name' in comment['user'] else None
                azure_obj['comments'].append({
                    'user_name': uname,
                    'content': comment['content'],
                    'id': comment['id'],
                    'created': comment['created']
                })


            self.AS_obj.post_data(json.dumps(azure_obj), constant.LOG_NAME)

    def get_data(self, classification_filter_operation, classification_list):
        """
            getting the incident and alert data from digital shadows
        """
        triage_id = []
        max_event_num = -1
        item_data = []
        event_data = []

        if isinstance(self.event, int):
            event_data = self.DS_obj.get_triage_events_by_num(self.event, classification_filter_operation, classification_list)
            #calculating the max event number from current batch to  use in next call
            if event_data:
                max_event_num = max([e['event-num'] for e in event_data])

        else:
            event_data = self.DS_obj.get_triage_events(self.before_time, self.after_time, classification_filter_operation, classification_list)
            #calculating the max event number from current batch to  use in next call
            if event_data:
                max_event_num = max([e['event-num'] for e in event_data])
                logger.info("First poll from event number " + str(event_data[0]['event-num']))
                logger.info("Total number of events are " + str(len(event_data)))
        
        for event in event_data:
            if event is not None and event['triage-item-id'] not in triage_id:
                triage_id.append(event['triage-item-id'])

        logger.info(triage_id)
        
        if triage_id:
            item_data = self.DS_obj.get_triage_items(triage_id)
        
        return item_data, max_event_num

    def poll(self, classification_filter_operation, classification_list):
        """
            main polling function, 
            makes api calls in following fashion:
            triage-events --> triage-items --> incidents and alerts 
        """
        try:
            #sending data to sentinel
            inc_ids = []
            alert_ids = []
            item_data, max_event_num = self.get_data(classification_filter_operation, classification_list)
            if item_data:
                logger.info("total number of items are " + str(len(item_data)))
                #creating list of ids by alert and incidents
                alert_triage_items = list(filter(lambda item: item['source']['alert-id'] is not None, item_data))
                inc_triage_items = list(filter(lambda item: item['source']['incident-id'] is not None, item_data))
                
                #getting data from DS and posting to Sentinel
                if inc_triage_items:
                    inc_ids = [item['source']['incident-id'] for item in inc_triage_items]
                    response_inc = self.DS_obj.get_incidents(inc_ids)
                        
                if alert_triage_items:
                    alert_ids = [item['source']['alert-id'] for item in alert_triage_items]
                    response_alert = self.DS_obj.get_alerts(alert_ids)
                    
                if inc_triage_items:
                    self.post_azure(response_inc, inc_triage_items, classification_filter_operation)
                if alert_triage_items:
                    self.post_azure(response_alert, alert_triage_items, classification_filter_operation)
            else:
                logger.info("No new events found.")
                max_event_num = self.event

            #saving event num for next invocation
            self.date.post_event(max_event_num)
        except Exception:
            logger.exception("Error polling: ")
            