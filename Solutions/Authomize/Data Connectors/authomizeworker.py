import json
import requests
import configparser
import os
from azureworker import post_data
from datetime import datetime, timezone

# Load settings
config = configparser.ConfigParser()
try:
    config.read('config.cfg')
    # Assign Variables
    URL = config.get('DEFAULT', 'authomizeURL')
    token = config.get('DEFAULT', 'authomizeToken')
    customer_id = config.get('DEFAULT', 'customer_id')
    shared_key = config.get('DEFAULT', 'shared_key')
    log_type = config.get('DEFAULT', 'sentinelLog')
    DateFileCFG = config.get('DEFAULT', 'DateFileCFG')
except configparser.Error as e:
    print(f"Error reading or parsing config file: {e}")
    exit(1)

currentDate = ""


def GetJSONData(nextPage, TheCurrentDateTime, last_run_datetime=None):
    filter_criteria = {
        "createdAt": {
            "$lte": TheCurrentDateTime
        },
        "status": {
            "$in": ["Open"]
        }
    }

    if last_run_datetime:
        filter_criteria["createdAt"]["$gte"] = last_run_datetime

    return {
        "filter": filter_criteria,
        "expand": [
            "policy"
        ],
        "sort": [
            {
                "fieldName": "createdAt",
                "order": "ASC"
            }
        ],
        "pagination": {
            "limit": 10,
            "nextPage": nextPage
        }
    }


def DateInZulu(currentDate):
    currentDate = datetime.now(timezone.utc).isoformat()
    return currentDate


def CheckFileExists():
    try:
        # Checking if file exists
        return os.path.exists(DateFileCFG)
    except Exception as e:
        # Log or print the exception message
        print(f"An error occurred while checking if the file exists: {e}")
        # Return False, assuming file does not exist in case of an error
        return False

def WriteFileContent(FileContent):
    try:
        # Opening file for writing
        with open(DateFileCFG, "w") as f:
            f.write(FileContent)
    except Exception as e:
        # Log or print the exception message
        print(f"An error occurred while writing to the file: {e}")

def ReadFileContent():
    try:
        # Opening file for reading
        with open(DateFileCFG, "r") as f:
            return f.read()
    except Exception as e:
        # Log or print the exception message
        print(f"An error occurred while reading from the file: {e}")
        # Return None in case of an error
        return None

def searchIncident():
    FileState = CheckFileExists()

    last_run_datetime = None
    if FileState:
        last_run_datetime = ReadFileContent()

    TheCurrentDateTime = DateInZulu(currentDate)

    theheaders = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    print(f"Status: Started processing.")
    MyCounter = 0
    nextPage = ""
    while True:
        MyCounter += 1
        print(f"INFO: --Processing-- [", MyCounter, "]")
        JsonData = GetJSONData(nextPage, TheCurrentDateTime, last_run_datetime)
        theData = json.dumps(JsonData)
        
        try:
            response = requests.post(url=URL, data=theData, headers=theheaders, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Warning: An error occurred making the API request: {e}")
            break

        try:
            response_json = response.json()

            # Handling data element
            data_element = response_json.get('data', [])
            if data_element:
                body = json.dumps(data_element)
                try:
                    post_data(customer_id, shared_key, body, log_type)
                except Exception as e:
                    print(f"Error posting data: {e}")
            else:
                print(f"INFO: No data to send, skipping process steps.")

            # Handling pagination
            pagination = response_json.get('pagination', {})
            if pagination.get('hasMore'):
                nextPage = pagination.get('nextPage', "")
            else:
                print(f"Status: Stopped processing.")
                break
        except Exception as e:
            print(f"Error processing response JSON: {e}")
            break

    # Update the timestamp file at the end of processing
    WriteFileContent(TheCurrentDateTime)

if __name__ == "__main__":
    searchIncident()