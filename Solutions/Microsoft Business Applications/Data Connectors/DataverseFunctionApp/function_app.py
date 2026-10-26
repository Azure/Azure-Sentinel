""" Dataverse Security Data Collector v1.1.1 """

import logging
import os
from datetime import datetime, timedelta
from typing import Union, List, Dict, Any
import json
import pandas as pd
import requests
import azure.functions as func
from dataverse_client import get_all_data
from azure.identity import ManagedIdentityCredential, ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

STORAGE_ACCOUNT_NAME = os.environ["AzureWebJobsStorage__accountName"]
DCR_IMMUTABLE_ID = os.environ["DCR_IMMUTABLE_ID"]
DCR_STREAM_NAME_USERS = os.environ["DCR_STREAM_NAME_USERS"]
DCR_STREAM_NAME_ROLES = os.environ["DCR_STREAM_NAME_ROLES"]
DCR_STREAM_NAME_USERROLES = os.environ["DCR_STREAM_NAME_USERROLES"]
DCR_STREAM_NAME_BUSINESSUNITS = os.environ["DCR_STREAM_NAME_BUSINESSUNITS"]
DCR_STREAM_NAME_TEAMS = os.environ["DCR_STREAM_NAME_TEAMS"]
DCR_STREAM_NAME_TEAMROLES = os.environ["DCR_STREAM_NAME_TEAMROLES"]
DCR_STREAM_NAME_TEAMMEMBERS = os.environ["DCR_STREAM_NAME_TEAMMEMBERS"]
DCR_DCE_URL = os.environ["DCR_DCE_URL"]
ODATA_API_HOST = os.environ["ODATA_API_HOST"].lower().rstrip("/")
ODATA_API_TIMEOUT_SECONDS = int(os.environ["ODATA_API_TIMEOUT_SECONDS"])
ODATA_API_MAX_PAGE_SIZE = int(os.environ["ODATA_API_MAX_PAGE_SIZE"])
TIMER_SCHEDULE_DATA = os.environ["TIMER_SCHEDULE_DATA"]
INSTANCE_URL = ODATA_API_HOST + "/"
CLIENT_CRED_CLIENT_ID = os.environ.get("CLIENT_CRED_CLIENT_ID", False)
CLIENT_CRED_CLIENT_SECRET = os.environ.get("CLIENT_CRED_CLIENT_SECRET", False)
CLIENT_CRED_TENANT_ID = os.environ.get("CLIENT_CRED_TENANT_ID", False)
FULL_SYNC_INTERVAL_DAYS = int(os.environ["FULL_SYNC_INTERVAL_DAYS"])
FILE_CACHE_CONTAINER_NAME = "filecache"
LAST_UPDATE_CONTAINER_NAME = "lastupdated"
LAST_UPDATE_FILENAME_DATA = "lastupdatedata.json"
DATA_MAPPINGS = [
    ("systemusers", DCR_STREAM_NAME_USERS, None),
    ("roles", DCR_STREAM_NAME_ROLES, None),
    ("systemuserrolescollection", DCR_STREAM_NAME_USERROLES, "cache_userroles.json"),
    ("businessunits", DCR_STREAM_NAME_BUSINESSUNITS, None),
    ("teams", DCR_STREAM_NAME_TEAMS, None),
    ("teamrolescollection", DCR_STREAM_NAME_TEAMROLES, "cache_teamroles.json"),
    ("teammemberships", DCR_STREAM_NAME_TEAMMEMBERS, "cache_teammemberships.json"),
]

azure_http_logger = logging.getLogger(
    "azure.core.pipeline.policies.http_logging_policy"
)
azure_http_logger.setLevel(logging.WARNING)


def create_container_client(
    cred: Union[ManagedIdentityCredential, ClientSecretCredential],
    container_name: str,
) -> ContainerClient:
    """Create a blob container client"""
    # create container client using managed identity
    return ContainerClient.from_container_url(
        container_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}",
        credential=cred,
    )


def get_cached_data(
    cache_file: str, cred: Union[ManagedIdentityCredential, ClientSecretCredential]
) -> List[Dict[str, Any]]:
    """Read cache file from blob storage"""
    with create_container_client(
        cred, FILE_CACHE_CONTAINER_NAME
    ) as file_cache_container:
        if not file_cache_container.exists():
            logging.info("No storage container for cache files found")
            return []

        try:
            logging.info("Downloading cache file")
            file_cache_blob = file_cache_container.download_blob(cache_file)
            file_cache_data = json.loads(file_cache_blob.readall())
            return file_cache_data
        except ResourceNotFoundError:
            logging.info("No cache file found in blob storage.")
            return []


def set_cached_data(
    cache_file: str,
    cred: Union[ManagedIdentityCredential, ClientSecretCredential],
    data: List[Dict[str, Any]],
) -> None:
    """Set the cache file in blob storage"""
    with create_container_client(
        cred, FILE_CACHE_CONTAINER_NAME
    ) as file_cache_container:
        if not file_cache_container.exists():
            logging.info("No storage container for cache files found")
            file_cache_container.create_container()

        logging.info("Updating cache file %s", cache_file)
        file_cache_container.upload_blob(
            cache_file,
            json.dumps(data),
            overwrite=True,
        )


def add_instance_url(data: list) -> list:
    """Add instance name to data"""
    for row in data:
        row["InstanceUrl"] = INSTANCE_URL
    return data


def send_data(
    dcr_stream: str,
    cred: Union[ManagedIdentityCredential, ClientSecretCredential],
    data: list,
):
    """Send data to Logs Ingestion API"""
    with LogsIngestionClient(endpoint=DCR_DCE_URL, credential=cred) as client:
        try:
            logging.info("Uploading %s logs to Ingestion API", len(data))
            client.upload(rule_id=DCR_IMMUTABLE_ID, stream_name=dcr_stream, logs=data)
        except HttpResponseError as exc:
            logging.error("Logs Ingestion error: %s", exc)
            raise


def get_last_updated_timestamps(
    last_update_filename: str,
    cred: Union[ManagedIdentityCredential, ClientSecretCredential],
) -> dict:
    """Get the last updated timestamp from blob storage"""

    empty_timestamp = datetime(1970, 1, 1).isoformat()
    no_updated_timestamps = {
        "last_full_sync": empty_timestamp,
        "last_incremental_sync": empty_timestamp,
    }

    with create_container_client(
        cred, LAST_UPDATE_CONTAINER_NAME
    ) as last_update_blob_container:
        if not last_update_blob_container.exists():
            logging.info("No storage container for last update timestamp found")
            return no_updated_timestamps

        try:
            logging.info("Downloading last update timestamp file")
            last_update_blob = last_update_blob_container.download_blob(
                last_update_filename
            )
            last_updated_timestamps = json.loads(last_update_blob.readall())
            return last_updated_timestamps
        except ResourceNotFoundError:
            logging.info("No last update timestamp file found in blob storage.")
            return no_updated_timestamps


def set_last_updated_timestamps(
    last_update_filename: str,
    last_full_sync: datetime,
    last_delta_sync: datetime,
    cred: Union[ManagedIdentityCredential, ClientSecretCredential],
) -> None:
    """Set the last updated timestamp in blob storage"""
    with create_container_client(
        cred, LAST_UPDATE_CONTAINER_NAME
    ) as last_update_blob_container:
        if not last_update_blob_container.exists():
            logging.info("No storage container for last update timestamp found")
            last_update_blob_container.create_container()

        logging.info("Updating last update timestamp file")
        last_update_blob_container.upload_blob(
            last_update_filename,
            json.dumps(
                {
                    "last_full_sync": last_full_sync.isoformat(),
                    "last_incremental_sync": last_delta_sync.isoformat(),
                }
            ),
            overwrite=True,
        )


app = func.FunctionApp()


@app.timer_trigger(
    schedule=TIMER_SCHEDULE_DATA,
    arg_name="DataverseSecurityData",
    run_on_startup=False,
    use_monitor=True,
)
# pylint: disable=invalid-name
def dataverse_security_data(DataverseSecurityData: func.TimerRequest) -> None:
    """Main function for the Azure Function App"""
    if DataverseSecurityData.past_due:
        logging.info("The timer is past due!")

    function_start_time = datetime.utcnow()

    is_using_client_credentials = (
        CLIENT_CRED_TENANT_ID and CLIENT_CRED_CLIENT_SECRET and CLIENT_CRED_TENANT_ID
    )

    function_app_credential = (
        ClientSecretCredential(
            client_id=CLIENT_CRED_CLIENT_ID,
            client_secret=CLIENT_CRED_CLIENT_SECRET,
            tenant_id=CLIENT_CRED_TENANT_ID,
        )
        if is_using_client_credentials
        else ManagedIdentityCredential()
    )

    dataverse_token = function_app_credential.get_token(
        f"{ODATA_API_HOST}/.default"
    ).token

    client_headers = {
        "Content-Type": "application/json;odata.metadata=none",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Prefer": f"odata.maxpagesize={ODATA_API_MAX_PAGE_SIZE}",
        "authorization": f"Bearer {dataverse_token}",
    }

    last_update = get_last_updated_timestamps(
        last_update_filename=LAST_UPDATE_FILENAME_DATA, cred=function_app_credential
    )
    last_full_sync = datetime.fromisoformat(last_update["last_full_sync"])
    last_incremental_sync = datetime.fromisoformat(last_update["last_incremental_sync"])
    full_sync = last_full_sync < function_start_time - timedelta(
        days=FULL_SYNC_INTERVAL_DAYS
    )

    for odata_entity, dcr_stream, cache_file in DATA_MAPPINGS:
        with requests.Session() as client:
            client.headers.update(client_headers)
            request_url = f"{ODATA_API_HOST}/api/data/v9.2/{odata_entity}"

            current_data = []
            if not full_sync and cache_file is None:
                request_url += (
                    f"?$filter=modifiedon gt {last_incremental_sync.isoformat()}Z"
                )

            for data in get_all_data(
                client=client,
                request_url=request_url,
                timeout=ODATA_API_TIMEOUT_SECONDS,
            ):
                add_instance_url(data)
                current_data.extend(data)

            if full_sync or cache_file is None:
                data = current_data
            else:
                data = (
                    pd.merge(
                        pd.DataFrame(
                            get_cached_data(
                                cache_file=cache_file, cred=function_app_credential
                            )
                        ),
                        pd.DataFrame(current_data),
                        how="right",
                        indicator=True,
                    )
                    .query('_merge == "right_only"')
                    .drop(columns=["_merge"])
                    .to_dict(orient="records")
                )

            send_data(
                dcr_stream=dcr_stream,
                cred=function_app_credential,
                data=data,
            )

            if cache_file is not None:
                set_cached_data(
                    cache_file=cache_file,
                    cred=function_app_credential,
                    data=current_data,
                )

    set_last_updated_timestamps(
        last_update_filename=LAST_UPDATE_FILENAME_DATA,
        last_full_sync=function_start_time if full_sync else last_full_sync,
        last_delta_sync=function_start_time,
        cred=function_app_credential,
    )
