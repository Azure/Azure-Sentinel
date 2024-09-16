import requests
import yaml
import hashlib
import hmac
import base64
import json
import re
from datetime import datetime
import logging
# Function to build the authorization signature


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + \
        str(content_length) + "\n" + content_type + \
        "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, 'utf-8')
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(
        decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode('utf-8')
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization
# Function to clean column names by removing trailing '_s'


def clean_column_names(data):
    clean_data = {}
    for key, value in data.items():
        # Remove trailing '_s' from the key
        new_key = re.sub(r'_s$', '', key)
        clean_data[new_key] = value
    return clean_data
# Function to apply the event processing condition


def process_event(event):
    if "data" in event:
        if "request" in event["data"] and event["type"] != "com.oraclecloud.loadbalancer.access":
            if event["data"]["request"] is not None:
                if "headers" in event["data"]["request"]:
                    event["data"]["request"]["headers"] = json.dumps(
                        event["data"]["request"]["headers"])
                if "parameters" in event["data"]["request"]:
                    event["data"]["request"]["parameters"] = json.dumps(
                        event["data"]["request"]["parameters"])
        if "response" in event["data"]:
            if event["data"]["response"] is not None and "headers" in event["data"]["response"]:
                event["data"]["response"]["headers"] = json.dumps(
                    event["data"]["response"]["headers"])
        if "additionalDetails" in event["data"]:
            event["data"]["additionalDetails"] = json.dumps(
                event["data"]["additionalDetails"])
        if "stateChange" in event["data"]:
            logging.info("In data.stateChange : {}".format(
                event["data"]["stateChange"]))
            if event["data"]["stateChange"] is not None and "current" in event["data"]["stateChange"]:
                event["data"]["stateChange"]["current"] = json.dumps(
                    event["data"]["stateChange"]["current"])
    return event
# Function to post data to the Azure Log Analytics API


def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(
        customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = "https://{}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01".format(
        customer_id)
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(uri, data=body, headers=headers)
    if response.status_code >= 200 and response.status_code <= 299:
        print('Ingesting the sample data..!')
    else:
        print("Response code: {}".format(response.status_code))


# Main script
if __name__ == '__main__':
    customer_id = input('Enter the Workspace ID: ')
    shared_key = input('Enter the Shared Key: ')
    log_type = input('Enter the Log Type: ')
    iterations = int(input('Enter the number of iterations: '))
    github_raw_url = input('Enter the GitHub raw URL of Sample data: ')
    # Fetching the YAML content from GitHub
    response = requests.get(github_raw_url)
    if response.status_code == 200:
        yaml_content = yaml.safe_load(response.content)
        # Clean the column names in the entire JSON body if it's a list of records
        if isinstance(yaml_content, list):
            cleaned_data = [clean_column_names(
                record) for record in yaml_content]
        else:
            cleaned_data = clean_column_names(yaml_content)
        # Process each event with the given condition
        processed_data = [process_event(event) for event in cleaned_data]
        json_body = json.dumps(processed_data)
        for _ in range(iterations):
            post_data(customer_id, shared_key, json_body, log_type)
