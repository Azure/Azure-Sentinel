import csv
import json
import logging
import os
# Assuming this is your custom class
from .sentinel_connector import AzureSentinelConnector
# Azure Sentinel Workspace details
WORKSPACE_ID = "d89eec33-fcd1-4ad6-a910-4cceb3663cf4"
SHARED_KEY = "WxDeKXpW3c18ny0K58bM3PYOrEga8Oomsojn+j7jmBXx6gHbcG30YYr3OKY2oYahHV3QNhGOYqneaV/kvAg9uw=="
LOG_TYPE = 'OCI_Logs_CL'  # Customize this according to your needs
# Log Analytics URI
LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')
if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'


def post_data_to_sentinel(event):
    try:
        # Modify event data before sending if it meets the condition
        if "data" in event:
            if "request" in event["data"] and event["type"] != "com.oraclecloud.loadbalancer.access":
                if event["data"]["request"] is not None:
                    # Serialize headers if they exist
                    if "headers" in event["data"]["request"]:
                        event["data"]["request"]["headers"] = json.dumps(
                            event["data"]["request"]["headers"])
                    # Serialize parameters if they exist
                    if "parameters" in event["data"]["request"]:
                        event["data"]["request"]["parameters"] = json.dumps(
                            event["data"]["request"]["parameters"])
            # Serialize response headers if they exist
            if "response" in event["data"] and event["data"]["response"] is not None:
                if "headers" in event["data"]["response"]:
                    event["data"]["response"]["headers"] = json.dumps(
                        event["data"]["response"]["headers"])
            # Serialize additionalDetails if they exist
            if "additionalDetails" in event["data"]:
                event["data"]["additionalDetails"] = json.dumps(
                    event["data"]["additionalDetails"])
            # Handle stateChange
            if "stateChange" in event["data"]:
                logging.info(
                    f"In data.stateChange: {event['data']['stateChange']}")
                if event["data"]["stateChange"] is not None and "current" in event["data"]["stateChange"]:
                    event["data"]["stateChange"]["current"] = json.dumps(
                        event["data"]["stateChange"]["current"])
        # Initialize Azure Sentinel Connector
        sentinel_connector = AzureSentinelConnector(
            log_analytics_uri=LOG_ANALYTICS_URI,
            workspace_id=WORKSPACE_ID,
            shared_key=SHARED_KEY,
            log_type=LOG_TYPE,
            queue_size=2000
        )
        # Send the data to Sentinel
        sentinel_connector.send(event)
        sentinel_connector.flush()
        logging.info("Event successfully sent to Azure Sentinel.")
    except Exception as e:
        logging.error(f"Error sending event to Azure Sentinel: {e}")
        raise


def read_csv_file(file_path):
    events = []
    try:
        with open(file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # Convert each row to a JSON-like dictionary
                # Simulating JSON structure from CSV row
                event = json.loads(json.dumps(row))
                events.append(event)
            logging.info(
                f"Read {len(events)} events from CSV file {file_path}")
    except Exception as e:
        logging.error(f"Failed to read CSV file {file_path}: {e}")
        raise
    return events


def main():
    # Path to the CSV file
    # Replace with the actual file path
    csv_file_path = 'C:\Users\v-sabiraj\OneDrive - Microsoft\Desktop\test2\OCI_07June Sample logs.csv'
    # Read the data from CSV file
    events = read_csv_file(csv_file_path)
    # Process each event
    for event in events:
        post_data_to_sentinel(event)


if __name__ == "__main__":
    main()
