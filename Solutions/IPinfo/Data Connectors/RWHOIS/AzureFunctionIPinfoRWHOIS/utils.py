import requests
import logging
import os
from .constants import *

def generate_url(resource_type, **kwargs):
    url_templates = {
        "dataCollectionEndpoint": f"{AZURE_BASE_URL}Insights/dataCollectionEndpoints/{{endpoint_name}}?api-version=2022-06-01",
        "dataCollectionRule": f"{AZURE_BASE_URL}Insights/dataCollectionRules/{{rule_name}}?api-version=2022-06-01",
        "table": f"{AZURE_BASE_URL}OperationalInsights/workspaces/{WORKSPACE_NAME}/tables/{{table_name}}?api-version=2022-10-01",
    }
    template = url_templates.get(resource_type)
    if template:
        return template.format(**kwargs)
    return "Invalid resource type"

def download_with_retry(url, file_path, retries=3):
    for attempt in range(retries):
        try:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
            return True
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                logging.info("Retrying...")
                continue
    return False
            
def download_mmdbs():
    url = f"{IPINFO_BASE_URL}/{CSV_NAME}?token="
    logging.info(f"Downloading '{CSV_NAME}'...")
    file_path = os.path.join("/tmp/", CSV_NAME)
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"Previous file '{CSV_NAME}' deleted.")
    success = download_with_retry(url + IPINFO_TOKEN, file_path)
    if success:
        logging.info(f"File '{CSV_NAME}' downloaded successfully.")
    else:
        logging.error(f"Failed to download the file '{CSV_NAME}'.")

def create_data_collection_endpoint(data_collection_endpoint_name, access_token):
    url = generate_url("dataCollectionEndpoint", endpoint_name=data_collection_endpoint_name)
    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    payload = {"location": LOCATION, "properties": {"networkAcls": {"publicNetworkAccess": "Enabled"}}}
    response = requests.put(url, json=payload, headers=headers)
    if response.status_code == 200:
        logging.info("\nData collection endpoint created successfully.\n")
    else:
        logging.error(f"Failed to create data collection endpoint. Status code: {response.status_code}")
        logging.error("Response body: %s", response.text)

def get_data_collection_endpoint_url(data_collection_endpoint_name, access_token):
    url = generate_url("dataCollectionEndpoint", endpoint_name=data_collection_endpoint_name)
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        endpoint = data.get("properties", {}).get("logsIngestion", {}).get("endpoint")
        if endpoint:
            return endpoint
    logging.info(f"\nData collection endpoint not exist. Status code: {response.status_code}. Creating ...")
    create_data_collection_endpoint(data_collection_endpoint_name, access_token)
    return get_data_collection_endpoint_url(data_collection_endpoint_name, access_token)

def check_and_create_data_collection_endpoint(data_collection_endpoint_name, access_token):
    endpoint = get_data_collection_endpoint_url(data_collection_endpoint_name, access_token)
    logging.info(f"Endpoint: {endpoint}\n")
    return endpoint

def create_table(table_name, schema_payload, access_token):
    url = generate_url("table", table_name=table_name)
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    response = requests.put(url, json=schema_payload, headers=headers)
    if response.status_code == 200:
        logging.info(f"\n{table_name} Table created successfully.\n")
    elif response.status_code == 202:
        logging.info(f"\n{table_name} Table creation initiated successfully.\n")
    else:
        logging.error(f"Failed to create {table_name} Table. Status code: {response.status_code}")
        logging.error("Response body: %s", response.text)

def get_table(table_name, access_token):
    url = generate_url("table", table_name=table_name)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        logging.info(f"\n{table_name} table not exists.\n")
        return False
    elif response.status_code == 200:
        logging.info(f"\n{table_name} table already exists.\n")
        return True
    else:
        logging.error(f"Failed to check {table_name}. Status code: {response.status_code}")
        logging.error("Response body: %s", response.text)
        return False

def check_and_create_table(table_name, schema_payload, access_token):
    table_status = get_table(table_name, access_token)
    if table_status == False:
        create_table(table_name, schema_payload, access_token)

def get_data_collection_rule(access_token, data_collection_rule_name):
    url = generate_url("dataCollectionRule", rule_name=data_collection_rule_name)
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        immutableId = data["properties"]["immutableId"]
        streamDeclarations = list(data["properties"]["streamDeclarations"].keys())[0]
        return immutableId, streamDeclarations
    
    logging.info(f"{data_collection_rule_name} Data Rule endpoint not exist. Status code:{response.status_code}")
    return None, None
    
def create_data_collection_rule(access_token, data_collection_rule_name, stream_declaration, columns, endpoint):
    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    url = generate_url("dataCollectionRule", rule_name=data_collection_rule_name)
    payload = {
        "properties": {
            "dataCollectionEndpointId": f"/subscriptions/{SUBCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Insights/dataCollectionEndpoints/{endpoint}",
            "streamDeclarations": {stream_declaration: {"columns": columns["columns"]}},
            "dataSources": {},
            "destinations": {
                "logAnalytics": [
                    {
                        "workspaceResourceId": f"/subscriptions/{SUBCRIPTION_ID}/resourcegroups/{RESOURCE_GROUP_NAME}/providers/microsoft.operationalinsights/workspaces/{WORKSPACE_NAME}",
                        "name": WORKSPACE_NAME,
                    }
                ]
            },
            "dataFlows": [
                {
                    "streams": [stream_declaration],
                    "destinations": [WORKSPACE_NAME],
                    "transformKql": "source\n| extend TimeGenerated = now()\n| project-rename ip_range=range\n",
                    "outputStream": stream_declaration,
                }
            ],
        },
        "location": LOCATION,
    }
    response = requests.put(url, json=payload, headers=headers)
    if response.status_code == 200:
        logging.info(f"\nData collection Rule for {data_collection_rule_name} created successfully.\n")
    else:
        logging.error(
            f"Failed to create data collection Rule for {data_collection_rule_name}. Status code: {response.status_code}"
            
        )
        logging.error("Response body: %s", response.text)

def check_and_create_data_collection_rules(
    access_token, data_collection_rule_name, stream_declaration, columns, endpoint
):
    dcr_immutableid, stream_name = get_data_collection_rule(access_token, data_collection_rule_name)
    if dcr_immutableid is not None and stream_name is not None:
        logging.info(f"\nData collection Rule `{data_collection_rule_name}` already exists.")
        return dcr_immutableid, stream_name
    logging.info(f"\nData collection Rule for {data_collection_rule_name} doesn't exist. Creating...")
    create_data_collection_rule(access_token, data_collection_rule_name, stream_declaration, columns, endpoint)
    return get_data_collection_rule(access_token, data_collection_rule_name)
