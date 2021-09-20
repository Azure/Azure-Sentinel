import requests
import json
import base64
from datetime import datetime
import pickle
import os
from . import to_logs

log_type = 'InALogs'
 
account_id = os.environ['ACCOUNT_ID']
passkey = bytes(os.environ['PASSKEY'], 'utf-8')
customer_id = os.environ['CUSTOMER_ID']
shared_key = os.environ['SHARED_KEY']


#parsing the date in a specific format which DS api requires

def get_time_parse(date_var):
  date = date_var.strftime("%Y-%m-%d")
  hour = date_var.strftime("%H")
  minute = date_var.strftime("%M")
  second = date_var.strftime("%S")
  parsed_str = date + "T" + hour + "%3A" + minute + "%3A" + second + ".000Z"  
  return parsed_str
    

def get_incidents(max_time):
  now_utc = datetime.now()

  print(max_time)
  print(now_utc)
  api_url = "https://api.searchlight.app/v1/triage-item-events?event-created-before=" + get_time_parse(now_utc) + "&event-created-after=" +  get_time_parse(max_time)  # + str(now_utc)       #triage items url
  
  b64val = base64.b64encode(passkey).decode("ascii")        #decode to get back into the ascii from byte string

  response = requests.get(api_url, headers={"Authorization": "Basic %s" % b64val, "searchlight-account-id": "%s" % account_id})       # convert key and secret to base 64

  data = json.loads(response.text)
  

  for id in data:
    api_triage_url = "https://api.searchlight.app/v1/triage-items?id=" + str(id['triage-item-id'])           #triage-items url
    response = requests.get(api_triage_url, headers={"Authorization": "Basic %s" % b64val, "searchlight-account-id": "%s" % account_id})
    triage_data = json.loads(response.text)
    for id in triage_data:
      #incident-ids are somehow None
      if(id['source']['incident-id'] is not None):
        api_incident_url = "https://api.searchlight.app/v1/incidents?id=" + str(id['source']['incident-id'])
        response = requests.get(api_incident_url, headers={"Authorization": "Basic %s" % b64val, "searchlight-account-id": "%s" % account_id})
        to_logs.post_data(customer_id, shared_key, json.dumps(response.json()), log_type)
        
      #for alerts
      if(id['source']['alert-id'] is not None):
        api_incident_url = "https://api.searchlight.app/v1/alerts?id=" + str(id['source']['alert-id'])
        response = requests.get(api_incident_url, headers={"Authorization": "Basic %s" % b64val, "searchlight-account-id": "%s" % account_id})
        to_logs.post_data(customer_id, shared_key, json.dumps(response.json()), log_type)
        
