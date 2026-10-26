""" polls data from DS to azure logs """
import datetime
import json
import logging

from . import AS_api
from . import DS_api
from .state_serializer import State

logger = logging.getLogger("DS_poller")


def _stringify(value):
    """Coerce a SearchLight field value to a string suitable for a DCR
    string column. Lists/dicts are JSON-serialised; None becomes ''."""
    if value is None:
        return ''
    if isinstance(value, (list, dict)):
        return json.dumps(value, separators=(',', ':'))
    return str(value)


def _datetime_or_none(value):
    """Coerce a SearchLight datetime field for a DCR `datetime` column.
    Missing / empty values must be `None`, not `''` — the Logs Ingestion
    endpoint rejects empty strings for datetime-typed columns with HTTP 400.
    SearchLight already emits ISO-8601 strings, so the value is passed
    through unchanged when present."""
    if value is None or value == '':
        return None
    return value


def _build_v2_row(alert_or_incident, triage_item, app, is_incident, comments):
    """Map raw SearchLight fields → DigitalShadows_V2_CL columns.

    The single SearchLight `id` field is routed to IncidentId (real) or
    AlertId (string) by *context* — i.e. which call site invoked this — to
    avoid per-value typing logic in the DCR's transformKql.
    """
    risk_assessment = alert_or_incident.get('risk-assessment') or {}

    row = {
        'TimeGenerated':           datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'App':                      _stringify(app),
        'Title':                    _stringify(alert_or_incident.get('title')),
        'TimeRaised':               _datetime_or_none(alert_or_incident.get('raised')),
        'TimeUpdated':              _datetime_or_none(alert_or_incident.get('updated')),
        'Classification':           _stringify(alert_or_incident.get('classification')),
        'RiskLevel':                _stringify(alert_or_incident.get('risk-level')),
        'RiskAssessmentRiskLevel':  _stringify(risk_assessment.get('risk-level') if isinstance(risk_assessment, dict) else None),
        'GreyMatterLink':           _stringify(alert_or_incident.get('gm_link')),
        'Assets':                   _stringify(alert_or_incident.get('assets')),
        'Description':              _stringify(alert_or_incident.get('description')),
        'ImpactDescription':        _stringify(alert_or_incident.get('impact_description')),
        'Mitigation':               _stringify(alert_or_incident.get('mitigation')),
        'RiskFactors':              _stringify(alert_or_incident.get('risk_factors')),
        'Comments':                 _stringify(comments),
        'PortalId':                 _stringify(alert_or_incident.get('portal_id')),
        'Status':                   _stringify(triage_item.get('state')),
        'TriageId':                 _stringify(triage_item.get('id')),
        'TriageRaisedTime':         _datetime_or_none(triage_item.get('raised')),
        'TriageUpdatedTime':        _datetime_or_none(triage_item.get('updated')),
    }

    raw_id = alert_or_incident.get('id')
    if is_incident:
        try:
            row['IncidentId'] = float(raw_id) if raw_id is not None else None
        except (TypeError, ValueError):
            row['IncidentId'] = None
    else:
        row['AlertId'] = _stringify(raw_id)

    return row


class poller:

    def __init__(self, function_name, ds_id, ds_key, secret, dce_url, dcr_immutable_id, stream_name, connection_string, historical_days, url):
        """
            initializes all necessary variables from other classes for polling
        """

        self.DS_obj = DS_api.api(ds_id, ds_key, secret, url)
        self.AS_obj = AS_api.logs_api(dce_url, dcr_immutable_id, stream_name)
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
            adds more newlines to description for good display on Microsoft Sentinel incidents
        """
        arr = data.splitlines()
        res = ""
        for e in arr:
            res = res + e + "\n\n"
        return res


    def post_azure(self, alerts_and_incidents, triage_items, app, is_incident):
        """Pair alerts/incidents with their triage items, build V2-schema rows
        for each, and POST the batch via the Logs Ingestion API.

        `is_incident` decides whether the SearchLight `id` lands in
        IncidentId (numeric) or AlertId (string) — see _build_v2_row.
        """

        data = {}
        for item in triage_items:
            if 'alert-id' in item['source'] and item['source']['alert-id'] is not None:
                data[item['source']['alert-id']] = [item, None]
            elif 'incident-id' in item['source'] and item['source']['incident-id'] is not None:
                data[item['source']['incident-id']] = [item, None]
            else:
                raise Exception(f'Triage item missing expected source ID field: {item}')

        for item in alerts_and_incidents:
            if item['id'] in data:
                data[item['id']][1] = item
            else:
                raise Exception(f'No matching triage item found for alert/incident: {item}')

        rows = []
        for triage_item, alert_or_incident in data.values():
            if not alert_or_incident:
                raise Exception(f'Triage item had no matching alert/incident data: {triage_item}')

            comment_data = self.DS_obj.get_triage_comments(triage_item['id'])
            comments = []
            for comment in comment_data:
                if 'content' not in comment:
                    continue
                uname = comment['user']['name'] if comment['user'] and 'name' in comment['user'] else None
                comments.append({
                    'user_name': uname,
                    'content': comment['content'],
                    'id': comment['id'],
                    'created': comment['created']
                })

            rows.append(_build_v2_row(alert_or_incident, triage_item, app, is_incident, comments))

        if rows:
            self.AS_obj.post_data(json.dumps(rows))

    def get_last_polled_triage_items(self, triage_ids, state_serializer_obj):
        """ 
            gets the last triage items list, if the file is not there then create a file
            and upload new triage items if file is already there then return the triage item list    
        """
        existing_triage_id = set()
        existing_triage_id_str = state_serializer_obj.get_triage_items()

        try:
            if existing_triage_id_str:
                existing_triage_id = set(existing_triage_id_str.splitlines())

            logger.info('existing triage items length : {}'.format(len(existing_triage_id)))

            new_triage_id = set(triage_ids)
            unique_triage_id = existing_triage_id.union(new_triage_id)
            unique_triage_id_list = list(unique_triage_id)
            num_items = len(unique_triage_id_list)
            logger.info('unique triage list length: {}'.format(num_items))


            # Determine how many items to return
            id = unique_triage_id_list[:150]
            state_serializer_obj.post_triage_items('\n'.join(unique_triage_id_list[150:]))
            return id
        
        except Exception as e:
            logger.info("An error occurred while getting the last polled triage items: {}".format(e))
            return None



    def get_data(self, classification_filter_operation, classification_list):
        """
            getting the incident and alert data from digital shadows
        """
        triage_ids = []
        max_event_num = -1
        item_data = []
        event_data = []

        if isinstance(self.event, int):
            max_event_num = self.event
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
            if event is not None and event['triage-item-id'] not in triage_ids:
                triage_ids.append(event['triage-item-id'])

        #fetch the triage id's from azure fileshare if file exist
        logger.info('triage length from api call: {}'.format(len(triage_ids)))
        triage_ids = self.get_last_polled_triage_items(triage_ids, self.date)

        
        return triage_ids, max_event_num

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
            triage_ids_to_process, max_event_num = self.get_data(classification_filter_operation, classification_list)

            if triage_ids_to_process:
                while len(triage_ids_to_process) > 0:
                    sub_triage_ids = triage_ids_to_process[:50]
                    triage_ids_to_process = triage_ids_to_process[50:]
                    item_data = self.DS_obj.get_triage_items(sub_triage_ids)
                    
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
                            self.post_azure(response_inc, inc_triage_items, classification_filter_operation, is_incident=True)
                        if alert_triage_items:
                            self.post_azure(response_alert, alert_triage_items, classification_filter_operation, is_incident=False)
            else:
                logger.info("No new events found.")
                max_event_num = self.event

            #saving event num for next invocation
            if max_event_num != -1:
                self.date.post_event(max_event_num)
        except Exception:
            logger.exception("Error polling: ")
            