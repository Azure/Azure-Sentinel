import datetime
import logging
import json
import requests
import os
from azureworker import post_data
from datetime import datetime, timezone
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableServiceClient, TableEntity
import azure.functions as func

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


def get_datetime(storage_connection_string, table_name, entity_id):
    try:
        table_service_client = TableServiceClient.from_connection_string(storage_connection_string)
        table_client = table_service_client.get_table_client(table_name)
        entity = table_client.get_entity(partition_key='datetime', row_key=entity_id)
        return entity.get('datetime')
    except ResourceNotFoundError:
        return None

def set_datetime(storage_connection_string, table_name, entity_id, datetime_value):
    table_service_client = TableServiceClient.from_connection_string(storage_connection_string)
    table_client = table_service_client.get_table_client(table_name)
    
    entity = TableEntity(partition_key='datetime', row_key=entity_id, datetime=datetime_value)
    try:
        table_client.upsert_entity(entity)
    except ResourceNotFoundError:
        table_client.create_entity(entity)

def searchIncident():
    logging.info('Python trigger function processed a request.')
    
    # Set Constants
    log_type = "Authomize_v2" # Sentinel Log Table
    URL = "https://api.authomize.com/v2/incidents/search" # Authomize API Endpoint

    
    # Retrieve secrets from Azure Key Vault
    credential = DefaultAzureCredential()
    vault_url = "https://authpt.vault.azure.net/"
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    
    token_secret = secret_client.get_secret("authomizeToken")
    token = token_secret.value
    
    customer_id_secret = secret_client.get_secret("CustomerID")
    customer_id = customer_id_secret.value
    
    shared_key_secret = secret_client.get_secret("sharedKey")
    shared_key = shared_key_secret.value
    
    # Access Azure Table Storage
    storage_connection_string = os.getenv("AzureWebJobsStorage")
    table_name = "authomizeDate"
    entity_id = "last_run_datetime"

    last_run_datetime = get_datetime(storage_connection_string, table_name, entity_id)

    TheCurrentDateTime = DateInZulu(datetime.now(timezone.utc))

    theheaders = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    logging.info("Status: Started processing.")
    MyCounter = 0
    nextPage = ""
    while True:
        MyCounter += 1
        logging.info(f"INFO: --Processing-- [{MyCounter}]")
        JsonData = GetJSONData(nextPage, TheCurrentDateTime, last_run_datetime)
        theData = json.dumps(JsonData)

        try:
            response = requests.post(url=URL, data=theData, headers=theheaders, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.warning(f"An error occurred making the API request: {e}")
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
                    logging.exception(f"Error posting data: {e}")
            else:
                logging.info(f"INFO: No data to send, skipping process steps.")

            # Handling pagination
            pagination = response_json.get('pagination', {})
            if pagination.get('hasMore'):
                nextPage = pagination.get('nextPage', "")
            else:
                logging.info(f"Status: Stopped processing.")
                break
        except Exception as e:
            logging.exception(f"Error processing response JSON: {e}")
            break

    # Update the timestamp in the table at the end of processing
    set_datetime(storage_connection_string, table_name, entity_id, TheCurrentDateTime)

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    searchIncident()