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

    logging.info("Ipinfo Privacy Extended timer trigger function executed.")

    def upload_data_to_privacy_extended_table(dce_endpoint, dcr_immutableid, stream_name):
        credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        client = LogsIngestionClient(endpoint=dce_endpoint, credential=credential, logging_enable=True)
        mmdb_file_path = "/tmp/privacy_extended.mmdb"
        reader = maxminddb.open_database(mmdb_file_path)
        chunk_size = 10000
        data_chunk = []
        logging.info("Uploading Standard Privacy Extended Data.\n")
        for ip, ip_data in reader:
            result = {}
            result["anycast"] = ip_data.get("anycast", "")
            result["census"] = ip_data.get("census", "")
            result["census_port"] = ip_data.get("census_port", "")
            result["device_activity"] = ip_data.get("device_activity", "")
            result["hosting"] = ip_data.get("hosting", "")
            result["network"] = ip_data.get("network", "")
            result["proxy"] = ip_data.get("proxy", "")
            result["relay"] = ip_data.get("relay", "")
            result["tor"] = ip_data.get("tor", "")
            result["vpn"] = ip_data.get("vpn", "")
            result["vpn_config"] = ip_data.get("vpn_config", "")
            result["vpn_name"] = ip_data.get("vpn_name", "")
            result["whois"] = ip_data.get("whois", "")
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
        logging.info("Standard Privacy Extended Data uploading completed.")

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
    check_and_create_table(PRIVACY_EXTENDED_TABLE_NAME, PRIVACY_EXTENDED_TABLE_SCHEMA, access_token)
    retries = 3
    while retries > 0:
        if get_table(PRIVACY_EXTENDED_TABLE_NAME, access_token):
            logging.info("Waiting for the table to be created properly, creating the data collection rule in 1 minute...")
            time.sleep(60)
            privacy_extended_dcr_immutableid, privacy_extended_stream_name = check_and_create_data_collection_rules(
                access_token,
                PRIVACY_EXTENDED_DCR_NAME,
                PRIVACY_EXTENDED_STREAM_DECLARATION,
                PRIVACY_EXTENDED_TABLE_COLUMNS,
                DATA_COLLECTION_ENDPOINT_NAME,
            )
            upload_data_to_privacy_extended_table(dce_endpoint, privacy_extended_dcr_immutableid, privacy_extended_stream_name)
            break
        else:
            logging.info("Table not created yet, retrying in 1 minute...")
            time.sleep(60)
            retries -= 1
    if retries == 0:
        logging.error("Table creation timed out after 3 retries. Data collection rules were not created.")
