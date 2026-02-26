import logging
import azure.functions as func
# Import ManagedIdentityCredential from the identity package that will be used for authentication
from azure.identity import ManagedIdentityCredential
# Import of SecurityInsights that allows to write to the Watclist API
from azure.mgmt.securityinsight import SecurityInsights
# Import the Watchlist model that allows us to create a watchlist
from azure.mgmt.securityinsight.models import Watchlist
# Import the service client to read from our storage account
from azure.storage.blob import BlobServiceClient
# Import the log ingestion client to write to the Log Analytics API for creating custom logs
from azure.monitor.ingestion import LogsIngestionClient
import csv
from io import StringIO
# Import os to read environment variables
import os
# Import HttpResponseError to handle errors from the Log Ingestion API
from azure.core.exceptions import HttpResponseError



app = func.FunctionApp()

credential = ManagedIdentityCredential()

@app.timer_trigger(schedule="0 0 2 * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def update_watchlist(myTimer: func.TimerRequest) -> None:

# Initialize variables from environment variables
    watchlist_name = os.getenv("WATCHLIST_NAME")
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group_name = os.getenv("RESOURCE_GROUP_NAME")
    workspace_name = os.getenv("WORKSPACE_NAME")
    file_name = os.getenv("FILE_NAME")
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    container_name = os.getenv("STORAGE_CONTAINER_NAME")
    provider = os.getenv("WATCHLIST_PROVIDER")
    search_key = os.getenv("WATCHLIST_SEARCH_KEY")
    description = os.getenv("WATCHLIST_DESCRIPTION")


    #If you want to use a custom table, please set the following variables in your environment
    # dce_url = os.getenv("DCE_URL")
    # rule_id = os.getenv("DCR_RULE_ID")
    # stream_name = os.getenv("STREAM_NAME")
    
    # Read watchlist items from storage
    watchlist_content, needsBatching = read_watchlist_from_storage(file_name, storage_account_name, container_name, credential)
    
    if needsBatching:
        batch_size = 800
        parsed_data = parse_csv_string(watchlist_content)
        for i in range(0, len(parsed_data), batch_size):
            batch = parsed_data[i+1:i + batch_size]
            csv_content = ",".join(parsed_data[0]) + "\n"
            for row in batch:
                csv_content += ",".join(row) + "\n"
            update_watchlist_sentinel(watchlist_name, csv_content, description, resource_group_name, workspace_name, search_key, provider,  credential, subscription_id)
            # update_custom_table(csv_content, dce_url, rule_id, stream_name, credential)
    else: 
        # Update the watchlist in Microsoft Sentinel
        update_watchlist_sentinel(watchlist_name, watchlist_content, description, resource_group_name, workspace_name, search_key, provider, credential, subscription_id)
        # update_custom_table(parsed_data, dce_url, rule_id, stream_name, credential)


def read_watchlist_from_storage(file_name, storage_account_name, container_name, credential):
    """
    Read data from a storage account container.
    
    :param file_name: Name of the file to read
    :param storage_account_name: Name of the storage account
    :param container_name: Name of the container in which the file is stored
    :param credential: Azure credentials for authentication
    :return: Content of the file as a string
    """
    if not file_name.endswith('.csv'):
        raise ValueError("File must be a CSV")

    blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    
    download_stream = blob_client.download_blob()
    file_content = download_stream.readall().decode('utf-8')

    logging.info("Read from Storage account:" + file_content[0:100])
    
    needsBatching = False
    
    # TODO: Check if file exists and is not empty
    
    if blob_client.get_blob_properties().get('size') >=  3984588:
        needsBatching = True 
    
    return file_content, needsBatching


def parse_csv_string(csv_string):
    csv_data = []
    csv_reader = csv.reader(StringIO(csv_string))
    for row in csv_reader:
        csv_data.append(row)
    return csv_data

def update_watchlist_sentinel(watchlist_name, watchlist_items, description, resource_group_name, workspace_name, search_key, provider, credential, subscription_id):
    """
    Update a watchlist in Microsoft Sentinel.
    
    :param watchlist_name: Name of the watchlist to update
    :param watchlist_items: List of items to add to the watchlist
    :param resource_group_name: Name of the resource group where the workspace is located
    :param workspace_name: Name of the workspace where the watchlist is located
    :param search_key: Key to search for in the watchlist items
    :param credential: Azure credentials for authentication
    :param subscription_id: Azure subscription ID
    """
    client = SecurityInsights(credential, subscription_id)

    watchlist = Watchlist()
    watchlist.display_name = watchlist_name 
    watchlist.items_search_key = search_key
    watchlist.provider = provider
    watchlist.source = "Local file"
    watchlist.raw_content = watchlist_items
    watchlist.number_of_lines_to_skip = 0
    watchlist.content_type = "text/csv"
    watchlist.description = description
    watchlist.watchlist_alias = watchlist_name
    client.watchlists.create_or_update(resource_group_name, workspace_name, watchlist_name, watchlist)


def csv_to_json(csv_string):
    """
    Convert CSV data to JSON format.
    
    :param csv_string: CSV data as a string
    :return: JSON data as a string
    """
    csv_reader = csv.DictReader(csv_string.splitlines())
    json_data = [row for row in csv_reader]
    return json_data

def update_custom_table(csv_data, dce, rule_id, stream_name, credential):
    """
    Upload CSV data to a table in Microsoft Sentinel. Required permissons: Monitoring Metrics Publisher for identity.

    :param csv_data: CSV data as a string
    :param dce: Data collection endpoint URL    
    :param rule_id: Rule ID for the DCR
    :param stream_name: Name of the stream to upload to in your DCR
    :param credential: Azure credentials for authentication
    :return: None
    """

    client = LogsIngestionClient(
        endpoint=dce, credential=credential, logging_enable=True
    )

    try:
        res = client.upload(rule_id=rule_id, stream_name=stream_name, logs=csv_to_json(csv_data))
        print(f"Upload succeeded: {res}")
    except HttpResponseError as e:
        print(f"Upload failed: {e}")
