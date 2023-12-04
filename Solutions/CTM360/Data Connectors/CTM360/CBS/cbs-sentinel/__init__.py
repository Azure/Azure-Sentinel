import logging
import hashlib
import hmac
import os
import azure.functions as func
import json
import re
import base64
import requests
import datetime
import traceback
from time import time, localtime, strftime, gmtime
cbs_api_key = os.environ.get('api_key')
customer_id = os.environ.get('WorkspaceID')
shared_key = os.environ.get('WorkspaceKey')
logAnalyticsUri = os.environ.get('logAnalyticsUri')
olddate_from = os.environ.get('date_from')
olddate_to = os.environ.get('date_to')
backupflag = os.environ.get('backupflag')
log_type = 'CBSLog_Azure_1_CL'

logging.info(f"before main: {shared_key=}")
logging.info(f"before main: {customer_id=}")
logging.info(f"before main: {cbs_api_key=}")


if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'
pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(logAnalyticsUri))
if (not match):
    raise Exception("CBS Data Connector: Invalid Log Analytics Uri.")


# Set the timezone offset for Bahrain (in seconds)
bahrain_timezone_offset = 3 * 60 * 60  # Adjust this value based on the actual offset

def format_iso8601(timestamp):
    return strftime("%Y-%m-%dT%H:%M:%S", gmtime(timestamp))


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    logging.info(f"after main: {shared_key=}")
    logging.info(f"after main: {customer_id=}")
    logging.info(f"after main: {cbs_api_key=}")
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + \
        str(content_length) + "\n" + content_type + \
        "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(
        decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    logging.info(f"after main: {authorization=}")

    return authorization


def post_data_to_sentinel(body):
    logging.info("entring post fucn")

    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)

    signature = build_signature(
        customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)

    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'

    logging.info(uri)
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    logging.info(headers)
    try:
        response = requests.post(uri, data=body, headers=headers)
    except Exception :
        print(traceback.format_exc())

    logging.info(response.text)

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(
            "CBS event successfully processed to the Azure Sentinel.")
        return response.status_code
    else:
        logging.error("Event is not processed into Azure. Response code: {}".format(
            response.status_code))
        return None



def main(mytimer: func.TimerRequest, inputblob: func.InputStream, outputblob:  func.Out[str]) -> None:
    if mytimer.past_due:
        logging.warn('The timer is past due!')

    logging.info('Starting program')
        
    # Get current time in seconds since the epoch
    current_time = time()

    # Calculate date and time 5 minutes ago in the Bahrain timezone
    five_minutes_ago_bahrain = current_time - 5 * 60 + bahrain_timezone_offset

    # Format the time objects as strings in ISO 8601-like format
    current_time_str = format_iso8601(current_time + bahrain_timezone_offset)
    five_minutes_ago_str = format_iso8601(five_minutes_ago_bahrain)

    # Print the results
    print("Current Date and Time in Bahrain timezone:", current_time_str)
    print("Date and Time 5 Minutes Ago in Bahrain timezone:", five_minutes_ago_str)
    if backupflag == "true":
        if inputblob is not None:
            input1 = str(inputblob.read(), "utf-8")
            print(input1)
            if input1 == "false":
                print("no old data insert")
                date_from = olddate_from
                date_to = olddate_to
                url = f"https://cbs.ctm360.com/api/v2/incidents?date_from={date_from}&date_to={date_to}"
                logging.info(url)
                logging.info("old data not inserted 1st loop")
                headers = {
                    "accept": "application/json",
                    "api-key": cbs_api_key
                }
                response = requests.get(url, headers=headers)
                logging.info(response)
                message1 = response.json()
                logging.info(message1)
          
                post_data_to_sentinel(json.dumps(message1["incident_list"]))
                outputblob.set("true")

                    
            else:
                logging.info("old data alreay inserted")
                date_from = five_minutes_ago_str
                date_to = current_time_str
                url = f"https://cbs.ctm360.com/api/v2/incidents?date_from={date_from}&date_to={date_to}"
                logging.info(url)

                headers = {
                    "accept": "application/json",
                    "api-key": cbs_api_key
                }

                response = requests.get(url, headers=headers)


                message1 = response.json()
                post_data_to_sentinel(json.dumps(message1["incident_list"]))


        else:
            logging.error("no such file inide the blob")
            exit()
    else:
        logging.info('take all data for the past 5 min')
        date_from = five_minutes_ago_str
        date_to = current_time_str
        url = f"https://cbs.ctm360.com/api/v2/incidents?date_from={date_from}&date_to={date_to}"
        logging.info(url)
        headers = {
            "accept": "application/json",
            "api-key": cbs_api_key
        }

        response = requests.get(url, headers=headers)


        message1 = response.json()
        post_data_to_sentinel(json.dumps(message1["incident_list"]))
