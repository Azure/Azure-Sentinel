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

    logging.info("Ipinfo WHOIS_ORG timer trigger function executed.")

    def upload_data_to_WHOIS_ORG_table(dce_endpoint, dcr_immutableid, stream_name):
        credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        client = LogsIngestionClient(endpoint=dce_endpoint, credential=credential, logging_enable=True)
        csv_file_path = "/tmp/whois_org.csv.gz"
        chunk_size = 10000
        data_chunk = []
        csv.field_size_limit(sys.maxsize)
        logging.info("Uploading WHOIS_ORG Data.\n")
        with gzip.open(csv_file_path, mode='rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for ip_data in reader:
                result = {}
                result["whois_id"] = ip_data.get("id", "")
                result["name"] = ip_data.get("name", "")
                result["address"] = ip_data.get("address", "")
                result["street"] = ip_data.get("street", "")
                result["city"] = ip_data.get("city", "")
                result["state"] = ip_data.get("state", "")
                result["postalcode"] = ip_data.get("postalcode", "")
                result["country"] = ip_data.get("country", "")
                result["admin_id"] = ip_data.get("admin_id", "")
                result["tech_id"] = ip_data.get("tech_id", "")
                result["abuse_id"] = ip_data.get("abuse_id", "")
                result["mnt_id"] = ip_data.get("mnt_id", "")
                result["email"] = ip_data.get("email", "")
                result["domain"] = ip_data.get("domain", "")
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
        logging.info("WHOIS_ORG Data uploading completed.")

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
    check_and_create_table(WHOIS_ORG_TABLE_NAME, WHOIS_ORG_TABLE_SCHEMA, access_token)
    retries = 3
    while retries > 0:
        if get_table(WHOIS_ORG_TABLE_NAME, access_token):
            logging.info("Waiting for the table to be created properly, creating the data collection rule in 1 minute...")
            time.sleep(60)
            WHOIS_ORG_dcr_immutableid, WHOIS_ORG_stream_name = check_and_create_data_collection_rules(
                access_token,
                WHOIS_ORG_DCR_NAME,
                WHOIS_ORG_STREAM_DECLARATION,
                WHOIS_ORG_TABLE_COLUMNS,
                DATA_COLLECTION_ENDPOINT_NAME,
            )
            upload_data_to_WHOIS_ORG_table(dce_endpoint, WHOIS_ORG_dcr_immutableid, WHOIS_ORG_stream_name)
            break
        else:
            logging.info("Table not created yet, retrying in 1 minute...")
            time.sleep(60)
            retries -= 1
    if retries == 0:
        logging.error("Table creation timed out after 3 retries. Data collection rules were not created.")
