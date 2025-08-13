import logging
import time
import csv
import gzip
import sys
import azure.functions as func
from azure.identity import ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient
from .constants import *
from .utils import download_mmdbs
from .utils import check_and_create_data_collection_endpoint
from .utils import check_and_create_table
from .utils import check_and_create_data_collection_rules
from .utils import get_table

def main(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Ipinfo WHOIS_POC timer trigger function executed.")

    def upload_data_to_WHOIS_POC_table(dce_endpoint, dcr_immutableid, stream_name):
        credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        client = LogsIngestionClient(endpoint=dce_endpoint, credential=credential, logging_enable=True)
        csv_file_path = "/tmp/whois_poc.csv.gz"
        chunk_size = 10000
        data_chunk = []
        csv.field_size_limit(sys.maxsize)
        logging.info("Uploading WHOIS_POC Data.\n")
        with gzip.open(csv_file_path, mode='rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for ip_data in reader:
                result = {}
                result["whois_id"] = ip_data.get("id", "")
                result["name"] = ip_data.get("name", "")
                result["mobilephone"] = ip_data.get("mobilephone", "")
                result["officephone"] = ip_data.get("officephone", "")
                result["fax"] = ip_data.get("fax", "")
                result["address"] = ip_data.get("address", "")
                result["country"] = ip_data.get("country", "")
                result["email"] = ip_data.get("email", "")
                result["abuse_email"] = ip_data.get("abuse_email", "")
                result["created"] = ip_data.get("created", "")
                result["updated"] = ip_data.get("updated", "")
                result["source"] = ip_data.get("source", "")
                data_chunk.append(result)
                if len(data_chunk) >= chunk_size:
                    try:
                        client.upload(rule_id=dcr_immutableid, stream_name=stream_name, logs=data_chunk)
                    except Exception as e:
                        logging.error(f"Upload failed: {e}")
                        logging.info("Wait for the next schedule run.")
                        break
                    data_chunk = []
        if data_chunk:
            try:
                client.upload(rule_id=dcr_immutableid, stream_name=stream_name, logs=data_chunk)
            except Exception as e:
                logging.error(f"Upload failed: {e}")
        logging.info("WHOIS_POC Data uploading completed.")

    # Function flow starts here; above this line are function definitions
    credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    access_token = credential.get_token(AZURE_SCOPE).token
    if access_token:
        logging.info("\nAccess Token Retrieved\n")
        logging.info(access_token)
    else:
        logging.error("\nFailed to retrieve access token\n")

    download_mmdbs()
    dce_endpoint = check_and_create_data_collection_endpoint(DATA_COLLECTION_ENDPOINT_NAME, access_token)
    check_and_create_table(WHOIS_POC_TABLE_NAME, WHOIS_POC_TABLE_SCHEMA, access_token)
    retries = 3
    while retries > 0:
        if get_table(WHOIS_POC_TABLE_NAME, access_token):
            logging.info("Waiting for the table to be created properly, creating the data collection rule in 1 minute...")
            time.sleep(60)
            WHOIS_POC_dcr_immutableid, WHOIS_POC_stream_name = check_and_create_data_collection_rules(
                access_token,
                WHOIS_POC_DCR_NAME,
                WHOIS_POC_STREAM_DECLARATION,
                WHOIS_POC_TABLE_COLUMNS,
                DATA_COLLECTION_ENDPOINT_NAME,
            )
            upload_data_to_WHOIS_POC_table(dce_endpoint, WHOIS_POC_dcr_immutableid, WHOIS_POC_stream_name)
            break
        else:
            logging.info("Table not created yet, retrying in 1 minute...")
            time.sleep(60)
            retries -= 1
    if retries == 0:
        logging.error("Table creation timed out after 3 retries. Data collection rules were not created.")
