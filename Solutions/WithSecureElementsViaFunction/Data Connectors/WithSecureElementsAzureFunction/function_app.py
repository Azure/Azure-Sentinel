import logging
import os

import azure.functions as func
import requests
from azure.data.tables import TableServiceClient
from azure.identity import ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient

from lib.azure_storage_table import StorageTableClient
from lib.log_ingestion_api import IngestionApiClient
from lib.withsecure_client import WithSecureClient
from lib.ws_connector import Connector

app = func.FunctionApp()

API_URL = "ELEMENTS_API_URL"
ENGINE = "ENGINE"
ENGINE_GROUP = "ENGINE_GROUP"

CLIENT_ID_KEY = "ELEMENTS_API_CLIENT_ID"
CLIENT_SECRET_KEY = "ELEMENTS_API_CLIENT_SECRET"
ENTRA_ID_KEY = "ENTRA_CLIENT_ID"
ENTRA_SECRET_KEY = "ENTRA_CLIENT_SECRET"
ENTRA_TENANT_KEY = "ENTRA_TENANT_ID"

CONNECTION_STRING = "STATE_TABLE_CS"
TABLE_NAME = "STATE_TABLE"
DATA_COLLECTION_ENDPOINT = "LOGS_ENDPOINT"
DCR_RULE_ID = "LOGS_DCR_RULE_ID"
DCR_STREAM = "LOGS_DCR_STREAM_NAME"

log = logging.getLogger(__name__)


@app.schedule(
    schedule="0 * * * * *", arg_name="timer", run_on_startup=True, use_monitor=True
)
def upload_security_events(timer):
    if timer.past_due:
        log.info("The timer is past due!")
    try:
        elements_api_url = os.environ.get(API_URL)
        state_conn_str = os.environ.get(CONNECTION_STRING)
        state_table = os.environ.get(TABLE_NAME)
        logs_endpoint = os.environ.get(DATA_COLLECTION_ENDPOINT)
        dcr_rule_id = os.environ.get(DCR_RULE_ID)
        dcr_stream = os.environ.get(DCR_STREAM)
        client_id = os.environ.get(CLIENT_ID_KEY)
        client_secret = os.environ.get(CLIENT_SECRET_KEY)
        entra_client = os.environ.get(ENTRA_ID_KEY)
        entra_secret = os.environ.get(ENTRA_SECRET_KEY)
        entra_tenant = os.environ.get(ENTRA_TENANT_KEY)

        log.info("Secret values ok " + client_id)

        storage_client = storage_table_client(state_conn_str, state_table)

        ingestion_client = ingestion_api_client(
            logs_endpoint,
            dcr_rule_id,
            dcr_stream,
            entra_tenant,
            entra_client,
            entra_secret,
        )

        engine = os.environ.get(ENGINE, "default")
        engine_group = os.environ.get(ENGINE_GROUP, "default")
        withsecure_client = WithSecureClient(
            elements_api_url, client_id, client_secret, engine, engine_group, requests
        )

        connector = Connector(
            storage_client=storage_client,
            ingestion_client=ingestion_client,
            withsecure_client=withsecure_client,
        )

        connector.execute()
    except Exception:
        log.exception("Execution error")


def storage_table_client(connection_str, table_name):
    table_service_client = TableServiceClient.from_connection_string(connection_str)
    return StorageTableClient(table_service_client.get_table_client(table_name))


def ingestion_api_client(
    api_url, dcr_rule_id, dcr_stream, entra_tenant, entra_client, entra_secret
):
    creds = ClientSecretCredential(
        tenant_id=entra_tenant, client_id=entra_client, client_secret=entra_secret
    )
    azure_client = LogsIngestionClient(api_url, credential=creds)
    return IngestionApiClient(azure_client, dcr_rule_id, dcr_stream)
