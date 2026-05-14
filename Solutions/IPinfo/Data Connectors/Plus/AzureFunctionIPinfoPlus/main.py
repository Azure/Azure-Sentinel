import logging
import time
import maxminddb
import azure.functions as func
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError
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

    logging.info("Ipinfo PLUS timer trigger function executed.")

    def upload_data_to_PLUS_table(dce_endpoint, dcr_immutableid, stream_name):
        credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        client = LogsIngestionClient(endpoint=dce_endpoint, credential=credential, logging_enable=True)
        mmdb_file_path = "/tmp/ipinfo_plus.mmdb"
        reader = maxminddb.open_database(mmdb_file_path)
        chunk_size = 10000
        data_chunk = []
        logging.info("Uploading PLUS Data.\n")
        for ip, ip_data in reader:
            result = {}
            result["range"] = str(ip)
            result["city"] = ip_data.get("city", "")
            result["region"] = ip_data.get("region", "")
            result["region_code"] = ip_data.get("region_code", "")
            result["country"] = ip_data.get("country", "")
            result["country_code"] = ip_data.get("country_code", "")
            result["continent"] = ip_data.get("continent", "")
            result["continent_code"] = ip_data.get("continent_code", "")
            result["latitude"] = ip_data.get("latitude", "")
            result["longitude"] = ip_data.get("longitude", "")
            result["timezone"] = ip_data.get("timezone", "")
            result["postal_code"] = ip_data.get("postal_code", "")
            result["geoname_id"] = ip_data.get("geoname_id", "")
            result["radius"] = ip_data.get("radius", "")
            result["asn"] = ip_data.get("asn", "")
            result["as_name"] = ip_data.get("as_name", "")
            result["as_domain"] = ip_data.get("as_domain", "")
            result["as_type"] = ip_data.get("as_type", "")
            result["as_changed"] = ip_data.get("as_changed", "")
            result["geo_changed"] = ip_data.get("geo_changed", "")
            result["is_anonymous"] = ip_data.get("is_anonymous", "")
            result["is_anycast"] = ip_data.get("is_anycast", "")
            result["is_hosting"] = ip_data.get("is_hosting", "")
            result["is_mobile"] = ip_data.get("is_mobile", "")
            result["is_satellite"] = ip_data.get("is_satellite", "")
            result["is_proxy"] = ip_data.get("is_proxy", "")
            result["is_relay"] = ip_data.get("is_relay", "")
            result["is_tor"] = ip_data.get("is_tor", "")
            result["is_vpn"] = ip_data.get("is_vpn", "")
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
        logging.info("PLUS Data uploading completed.")

    # Function flow starts here; above this line are function definitions
    credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    try:
        access_token = credential.get_token(AZURE_SCOPE).token
    except ClientAuthenticationError as e:
        if "AADSTS700016" in e.message:
            logging.error("\nAuthentication Failed: Please verify your Client ID\n")
        elif "AADSTS7000215" in e.message:
            logging.error("\nAuthentication Failed: Please verify your Client Secret\n")
        elif "check your tenant name" in e.message:
            logging.error("\nAuthentication Failed: Please verify your Tenant ID\n")
        else:
            logging.error(f"\nUnexpected error - {e.message}\n")
    if access_token:
        logging.info("\nAccess Token Retrieved\n")
    else:
        logging.error("\nFailed to retrieve access token\n")

    download_mmdbs()
    dce_endpoint = check_and_create_data_collection_endpoint(DATA_COLLECTION_ENDPOINT_NAME, access_token)
    check_and_create_table(PLUS_TABLE_NAME, PLUS_TABLE_SCHEMA, access_token)
    retries = 3
    while retries > 0:
        if get_table(PLUS_TABLE_NAME, access_token):
            logging.info("Waiting for the table to be created properly, creating the data collection rule in 1 minute...")
            time.sleep(60)
            PLUS_dcr_immutableid, PLUS_stream_name = check_and_create_data_collection_rules(
                access_token,
                PLUS_DCR_NAME,
                PLUS_STREAM_DECLARATION,
                PLUS_TABLE_COLUMNS,
                DATA_COLLECTION_ENDPOINT_NAME,
            )
            upload_data_to_PLUS_table(dce_endpoint, PLUS_dcr_immutableid, PLUS_stream_name)
            break
        else:
            logging.info("Table not created yet, retrying in 1 minute...")
            time.sleep(60)
            retries -= 1
    if retries == 0:
        logging.error("Table creation timed out after 3 retries. Data collection rules were not created.")
