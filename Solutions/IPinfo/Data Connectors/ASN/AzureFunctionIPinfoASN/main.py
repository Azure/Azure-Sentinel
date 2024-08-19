import logging
import time
import maxminddb
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

    logging.info("Ipinfo ASN timer trigger function executed.")

    def upload_data_to_ASN_table(dce_endpoint, dcr_immutableid, stream_name):
        credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        client = LogsIngestionClient(endpoint=dce_endpoint, credential=credential, logging_enable=True)
        mmdb_file_path = "/tmp/asn.mmdb"
        reader = maxminddb.open_database(mmdb_file_path)
        chunk_size = 10000
        data_chunk = []
        logging.info("Uploading Standard ASN Data.\n")
        for ip, ip_data in reader:
            result = {}
            result["asn"] = ip_data.get("asn", "")
            result["name"] = ip_data.get("name", "")
            result["domain"] = ip_data.get("domain", "")
            result["route"] = ip_data.get("route", "")
            result["asn_type"] = ip_data.get("type", "")
            result["range"] = str(ip)
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
        reader.close()
        logging.info("Standard ASN Data uploading completed.")

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
    check_and_create_table(ASN_TABLE_NAME, ASN_TABLE_SCHEMA, access_token)
    retries = 3
    while retries > 0:
        if get_table(ASN_TABLE_NAME, access_token):
            logging.info("Waiting for the table to be created properly, creating the data collection rule in 1 minute...")
            time.sleep(60)
            ASN_dcr_immutableid, ASN_stream_name = check_and_create_data_collection_rules(
                access_token,
                ASN_DCR_NAME,
                ASN_STREAM_DECLARATION,
                ASN_TABLE_COLUMNS,
                DATA_COLLECTION_ENDPOINT_NAME,
            )
            upload_data_to_ASN_table(dce_endpoint, ASN_dcr_immutableid, ASN_stream_name)
            break
        else:
            logging.info("Table not created yet, retrying in 1 minute...")
            time.sleep(60)
            retries -= 1
    if retries == 0:
        logging.error("Table creation timed out after 3 retries. Data collection rules were not created.")
