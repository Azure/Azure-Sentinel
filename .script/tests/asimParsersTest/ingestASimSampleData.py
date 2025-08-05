import sys
import os
import random
import datetime
# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Remove the script's directory from sys.path to avoid importing local malicious modules
if script_dir in sys.path:
    sys.path.remove(script_dir)

import requests
import yaml
import re
import subprocess
import csv
import json
from azure.monitor.ingestion import LogsIngestionClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
import time

# Add debug flag for local testing
DEBUG_LOCAL = True  # Default to False, will be set by user input
random_number = random.randint(1, 1000)  # Global by default

def get_user_input_for_local_testing():
    """Get user input for local testing mode"""
    # Get sample data file path
    while True:
        sample_file_path = input("Enter the path to your sample data CSV file: ").strip()
        
        # Handle quoted paths
        if sample_file_path.startswith('"') and sample_file_path.endswith('"'):
            sample_file_path = sample_file_path[1:-1]
        
        if not sample_file_path:
            print("Please enter a valid file path")
            continue
        if not os.path.exists(sample_file_path):
            print(f"File not found: {sample_file_path}")
            continue
        if not sample_file_path.endswith('.csv'):
            print("File must be a CSV file")
            continue
        break
    
    # Get parser file path
    while True:
        parser_file_path = input("Enter the path to your parser YAML file (or press Enter to skip): ").strip()
        
        # Handle quoted paths
        if parser_file_path.startswith('"') and parser_file_path.endswith('"'):
            parser_file_path = parser_file_path[1:-1]
        
        if not parser_file_path:
            parser_file_path = None
            break
        if not os.path.exists(parser_file_path):
            print(f"Parser file not found: {parser_file_path}")
            continue
        if not parser_file_path.endswith('.yaml'):
            print("Parser file must be a YAML file")
            continue
        break

    return True, sample_file_path, parser_file_path

def get_modified_files(current_directory):
    # Add upstream remote if not already present
    git_remote_command = "git remote"
    remote_result = subprocess.run(git_remote_command, shell=True, text=True, capture_output=True, check=True)
    if 'upstream' not in remote_result.stdout.split():
        git_add_upstream_command = f"git remote add upstream '{SentinelRepoUrl}'"
        subprocess.run(git_add_upstream_command, shell=True, text=True, capture_output=True, check=True)
    # Fetch from upstream
    git_fetch_upstream_command = "git fetch upstream"
    subprocess.run(git_fetch_upstream_command, shell=True, text=True, capture_output=True, check=True)
    cmd = f"git diff --name-only upstream/master {current_directory}/../../../Parsers/"
    try:
        return subprocess.check_output(cmd, shell=True).decode().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing the command: {e}")
        return []

def get_current_commit_number():
    cmd = "git rev-parse HEAD"
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing the command: {e}")
        return None

def read_github_yaml(url):
    try:
        print(f"Attempting to fetch YAML from: {url}")
        response = requests.get(url)
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            print("Successfully fetched YAML content")
            return yaml.safe_load(response.text)
        else:
            print(f"Failed to fetch YAML: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred while trying to get content of YAML file located at {url}: {e}")
        return None    

def filter_yaml_files(modified_files):
    # Take only the YAML files
    return [line for line in modified_files if line.endswith('.yaml')]

def convert_schema_csv_to_json(csv_file):
    data = []
    with open(csv_file, 'r',encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['ColumnName'] in reserved_columns:
                continue
            elif row['ColumnType'] == "bool":
                data.append({        
                'name': row['ColumnName'],
                'type': "boolean",
                })
            else:
                data.append({        
                'name': row['ColumnName'],
                'type': row['ColumnType'],
                })                       
    return data

def convert_data_csv_to_json(csv_file):
    def convert_value(value):
        # Try to convert the value to an integer, then to a float, and keep it as a string if those fail
        try:
            # Try integer conversion
            return int(value)
        except ValueError:
            try:
                # Try float conversion
                return float(value)
            except ValueError:
                # Return the value as-is (string) if it's not numeric
                return value

    data = []
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            table_name = row['Type']
            # Convert each value in the row to its appropriate type
            processed_row = {key: convert_value(value) for key, value in row.items()}
            data.append(processed_row)
        
        for item in data:
            for key in list(item.keys()):
                # If the key matches '[UTC]' or '[Local Time]', rename it
                if key.endswith(('[UTC]', '[Local Time]')):
                    substring = key.split(" [")[0]
                    item[substring] = item.pop(key)

    return data, table_name

def read_local_sample_data(file_path):
    """Read sample data from local file for debugging"""
    try:
        if os.path.exists(file_path):
            print(f"Reading local sample data from: {file_path}")
            data_result, table_name = convert_data_csv_to_json(file_path)
            return data_result, table_name
        else:
            print(f"Local file not found: {file_path}")
            return None, None
    except Exception as e:
        print(f"Error reading local file {file_path}: {e}")
        return None, None

def read_local_parser_data(file_path):
    """Read parser data from local YAML file"""
    try:
        if os.path.exists(file_path):
            print(f"Reading local parser data from: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            print(f"Local parser file not found: {file_path}")
            return None
    except Exception as e:
        print(f"Error reading local parser file {file_path}: {e}")
        return None

def check_for_custom_table(table_name):
    if table_name in lia_supported_builtin_table:
        log_ingestion_supported=True
        table_type="builtin"
    if table_name not in lia_supported_builtin_table:
        if table_name.endswith('_CL') or table_name.endswith('_cl'):
            log_ingestion_supported=True
            table_type="custom_log"           
        else:
            log_ingestion_supported=False
            table_type="unknown"
    return log_ingestion_supported,table_type

def create_table(schema,table):
     request_object = {
    "properties": {
        "schema": {
        "name": table,
        "columns": json.loads(schema)
        },
        "retentionInDays": 30,
        "totalRetentionInDays": 30
    }
    }
     method="PUT"
     url=f"https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}/tables/{table}?api-version=2022-10-01"
     return request_object , url , method

def get_table_status(table):
    while True:
        table_name=table
        url=f"https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}/tables/{table_name}?api-version=2022-10-01"
        method="GET"
        time.sleep(3)
        response = hit_api(url,"",method)
        if response.status_code == 200:
            print(f"Custom Table {table_name} is created successfully")
            break
    return response.status_code  

def get_schema_for_builtin(query_table):
    # Obtain the access token
    credential = DefaultAzureCredential()
    token = credential.get_token('https://api.loganalytics.io/.default').token
    # Set the API endpoint
    url = f'https://api.loganalytics.io/v1/workspaces/{workspace_id}/query'
    # Create the payload
    payload = json.dumps({
        'query': query_table+'|getschema'
    })
    # Set the headers
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    # Make the request
    query_response = requests.post(url, headers=headers, data=payload)
    schema=[]
    guid_columns = []
    for each in json.loads(query_response.text).get('tables')[0].get('rows'):
        if each[0] in reserved_columns:
            continue
        elif each[0] in guid_columns:
            continue
        elif each[3] == "bool":
            schema.append({        
            'name': each[0],
            'type': "boolean",
            })
        else:
            schema.append({        
            'name': each[0],
            'type': each[3],
            })
    return schema


def create_dcr(schema,table,table_type):
    #suffic_num = str(random.randint(100,999))

    print('random_number : ' + str(random_number))
    dcrname=table+"_DCR"+str(random_number)
    request_object={ 
            "location": "centralus", #"eastus2euap", 			
            "properties": {
                "streamDeclarations": {
                    "Custom-dcringest"+str(random_number): {
                        "columns": json.loads(schema)
                    }
                },				
			"dataCollectionEndpointId": f"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Insights/dataCollectionEndpoints/{dataCollectionEndpointname}",			
              "dataSources": {}, 
              "destinations": { 
                "logAnalytics": [ 
                  { 
                    "workspaceResourceId": f"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}",
                    "workspaceId": workspace_id,
                    "name": "DataCollectionEvent"+str(random_number)
                  } 
                ] 
              }, 
              "dataFlows": [ 
                    {
                        "streams": [
                            "Custom-dcringest"+str(random_number)
                        ],
                        "destinations": [
                            "DataCollectionEvent"+str(random_number)
                        ],
                        "transformKql": "source",
                        "outputStream": f"{table_type}-{table}"
                    } 
                        ] 
                }
        }
    method="PUT"
    url=f"https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Insights/dataCollectionRules/{dcrname}?api-version=2022-06-01"
    return request_object , url , method ,"Custom-dcringest"+str(random_number)

def get_access_token():
    credential = DefaultAzureCredential()
    token = credential.get_token('https://management.azure.com/')
    return token.token

def hit_api(url,request,method):
    access_token = get_access_token()
    headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
    }
    try:
        if method == "GET":
            response = requests.request(method, url, headers=headers)
        else:
            response = requests.request(method, url, headers=headers, json=request)
    except Exception as e:
        print(f"Upload failed: {e}")       
    return response

def check_dcr_permissions(dcr_immutable_id):
    """
    Check if the current identity has permissions to ingest data to the DCR
    """
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token('https://management.azure.com/.default')
        
        # Get current user/service principal info
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }
        
        # Try to get DCR details to verify access
        dcr_name = dcr_immutable_id.split('/')[-1] if '/' in dcr_immutable_id else f"*_DCR{random_number}"
        dcr_resource_id = f"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Insights/dataCollectionRules/{dcr_name}"
        
        url = f"https://management.azure.com{dcr_resource_id}?api-version=2022-06-01"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✓ Successfully accessed DCR metadata (management plane)")
        else:
            print(f"⚠ Cannot access DCR metadata: {response.status_code}")
            
        # Test monitor scope token
        monitor_token = credential.get_token('https://monitor.azure.com/.default')
        print("✓ Successfully obtained monitor ingestion token")
        
        return True
        
    except Exception as e:
        print(f"❌ Permission check failed: {e}")
        return False

def get_user_identity_info():
    """
    Get information about the current authenticated identity
    """
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token('https://management.azure.com/.default')
        
        # Call Azure REST API to get current user info
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }
        
        # Try to get subscription info to identify the current identity
        url = f"https://management.azure.com/subscriptions/{subscriptionId}?api-version=2020-01-01"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✓ Authentication successful")
            return True
        else:
            print(f"⚠ Authentication issue: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot determine identity: {e}")
        return False

def senddtosentinel(immutable_id,data_result,stream_name,flag_status):
    if flag_status == 0:
        print("DCR is not created for the table. Please create DCR first")
        return
    print("Waiting for data to be sent to sentinel (This will take atleast 20 seconds)")
    time.sleep(20)
    
    # Initialize credential with detailed error handling
    try:
        credential = DefaultAzureCredential()
        # Test credential by getting a token
        token = credential.get_token('https://monitor.azure.com/.default')
        print(f"Successfully obtained authentication token")
    except Exception as e:
        print(f"Authentication failed: {e}")
        print("Please ensure you are logged in with 'az login' or have proper managed identity configured")
        return
    
    client = LogsIngestionClient(endpoint=endpoint_uri, credential=credential, logging_enable=True)
    
    try:
        print(f"Attempting to upload {len(data_result)} records to DCR: {immutable_id}")
        print(f"Stream name: {stream_name}")
        print(f"Endpoint: {endpoint_uri}")
        
        # Split large datasets into smaller chunks to avoid timeout
        chunk_size = 100
        total_records = len(data_result)
        
        for i in range(0, total_records, chunk_size):
            chunk = data_result[i:i + chunk_size]
            chunk_num = (i // chunk_size) + 1
            total_chunks = (total_records + chunk_size - 1) // chunk_size
            
            print(f"Uploading chunk {chunk_num}/{total_chunks} containing {len(chunk)} log entries")
            
            try:
                client.upload(rule_id=immutable_id, stream_name=stream_name, logs=chunk)
                print(f"Successfully uploaded chunk {chunk_num}/{total_chunks}")
            except HttpResponseError as e:
                print(f"Failed to upload chunk containing {len(chunk)} log entries")
                print(f"Upload failed: {e}")
                print(f"Error code: {e.error.code if hasattr(e, 'error') and hasattr(e.error, 'code') else 'Unknown'}")
                # "Monitoring Metrics Publisher" role is need to upload data to DCR
                print("Please ensure you have the 'Monitoring Metrics Publisher' role assigned.")
                # Continue with next chunk on error
                continue
        
        print(f"Data ingestion completed for {immutable_id}")
        
    except Exception as e:
        print(f"Unexpected error during upload: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


def extract_event_vendor_product(parser_query,parser_file,schema_name,equivalent_built_in_parser=None):
    match = re.search(r'(ASim\w+)/', parser_file)
    # schema_name = None
    # if match:
    #     schema_name = match.group(1)
    # else:
    #     print(f'EventVendor field not mapped in parser. Please map it in parser query.{parser_file}')

    match = re.search(r'EventVendor\s*=\s*[\'"]([^\'"]+)[\'"]', parser_query)
    if match:
        event_vendor = match.group(1)
    # if equivalent_built_in_parser end with Native, then use 'EventVendor' as 'Microsoft'
    elif equivalent_built_in_parser and equivalent_built_in_parser.endswith('_Native'):
        event_vendor = 'Microsoft'
    else:
        print(f'EventVendor field not mapped in parser. Please map it in parser query.{parser_file}')

    match = re.search(r'EventProduct\s*=\s*[\'"]([^\'"]+)[\'"]', parser_query)
    if match:
        event_product = match.group(1)
    # if equivalent_built_in_parser end with Native, then use 'EventProduct' as SchemaName + 'NativeTable' 
    elif equivalent_built_in_parser and equivalent_built_in_parser.endswith('_Native'):
        event_product = 'NativeTable'
    else:
        print(f'Event Product field not mapped in parser. Please map it in parser query.{parser_file}')
    return event_vendor, event_product ,schema_name   

def convert_data_type(schema_result, data_result):
    for data in data_result:
        for schema in schema_result:
            field_name = schema["name"]
            field_type = schema["type"]
            
            if field_name in data:
                value = data[field_name]
                
                # Handle conversion based on schema type
                
                if field_type == "string":
                    # Convert to string
                    data[field_name] = str(value)
                elif field_type == "boolean":
                    # Convert to boolean
                    if isinstance(value, str) and value.lower() in ["true", "false"]:
                        data[field_name] = value.lower() == "true"

    return data_result


#main starting point of script
workspaceName = "v-amol"
resourceGroupName = "v-amol"
subscriptionId = "4383ac89-7cd1-48c1-8061-b0b3c5ccfd97"
dataCollectionEndpointname = "TestAmol"
endpoint_uri = "https://testamol-s1wi.centralus-1.ingest.monitor.azure.com"
workspace_id = "5b8e8aa3-8102-4c8c-aa5d-3ce5a96f0be6"  # Replace with your actual workspace ID

# below details are where you want to send the data
# workspace_id = "WorkspaceId"  # Replace with your actual workspace ID
# workspaceName = "WorkspaceName" # Replace with your actual workspace name
# resourceGroupName = "ResourceGroupName" # Replace with your actual resource group name
# subscriptionId = "SubscriptionId" # Replace with your actual subscription ID
# dataCollectionEndpointname = "dataCollectionEndpointName" # Replace with your actual DCE name
# endpoint_uri = "dataCollectionEndpointUrl" # Replace with your actual DCE URL

SENTINEL_REPO_RAW_URL = f'https://raw.githubusercontent.com/Azure/Azure-Sentinel'
SAMPLE_DATA_PATH = 'Sample%20Data/ASIM/'
dcr_directory=[]

lia_supported_builtin_table = ['ADAssessmentRecommendation','ADSecurityAssessmentRecommendation','Anomalies','ASimAuditEventLogs','ASimAuthenticationEventLogs','ASimDhcpEventLogs','ASimDnsActivityLogs','ASimDnsAuditLogs','ASimFileEventLogs','ASimNetworkSessionLogs','ASimProcessEventLogs','ASimRegistryEventLogs','ASimUserManagementActivityLogs','ASimWebSessionLogs','AWSCloudTrail','AWSCloudWatch','AWSGuardDuty','AWSVPCFlow','AzureAssessmentRecommendation','CommonSecurityLog','DeviceTvmSecureConfigurationAssessmentKB','DeviceTvmSoftwareVulnerabilitiesKB','ExchangeAssessmentRecommendation','ExchangeOnlineAssessmentRecommendation','GCPAuditLogs','GoogleCloudSCC','SCCMAssessmentRecommendation','SCOMAssessmentRecommendation','SecurityEvent','SfBAssessmentRecommendation','SharePointOnlineAssessmentRecommendation','SQLAssessmentRecommendation','StorageInsightsAccountPropertiesDaily','StorageInsightsDailyMetrics','StorageInsightsHourlyMetrics','StorageInsightsMonthlyMetrics','StorageInsightsWeeklyMetrics','Syslog','UCClient','UCClientReadinessStatus','UCClientUpdateStatus','UCDeviceAlert','UCDOAggregatedStatus','UCServiceUpdateStatus','UCUpdateAlert','WindowsEvent','WindowsServerAssessmentRecommendation']
reserved_columns = ["_ResourceId", "id", "_SubscriptionId", "TenantId", "Type", "UniqueId", "Title","_ItemId","verbose_b","verbose","MG","_ResourceId_s"]

SentinelRepoUrl = "https://github.com/Azure/Azure-Sentinel"
current_directory = os.path.dirname(os.path.abspath(__file__))

def extract_schema_name_from_path(file_path):
    """
    Extract schema name from parser file path, handling various path formats
    
    Args:
        file_path (str): Parser file path
        
    Returns:
        str: Schema name or None if not found
    """
    # Normalize path separators to forward slashes
    normalized_path = file_path.replace('\\', '/')
    
    # Try different patterns for schema extraction
    patterns = [
        r'ASim(\w+)/',      # Standard ASim parser pattern
        r'vim(\w+)/',       # vim parser pattern
        r'/ASim(\w+)/',     # Pattern with leading slash
        r'/vim(\w+)/',      # vim parser with leading slash
        r'ASim(\w+)\\',     # Backslash pattern (before normalization)
        r'vim(\w+)\\',      # vim backslash pattern
        r'ASim(\w+)$',      # Just the schema name at end
        r'vim(\w+)$'        # vim schema name at end
    ]
    
    for pattern in patterns:
        match = re.search(pattern, normalized_path)
        if match:
            return match.group(1)
    
    # If no match found, try to extract from filename
    filename = normalized_path.split('/')[-1]
    if filename.startswith('ASim') or filename.startswith('vim'):
        # Extract from filename like "ASimWebSessionZscaler.yaml"
        match = re.search(r'(?:ASim|vim)(\w+)', filename)
        if match:
            # Handle cases like "ASimWebSessionZscaler" -> extract "WebSession"
            schema_part = match.group(1)
            # Remove common suffixes to get clean schema name
            for suffix in ['Zscaler', 'Microsoft', 'Palo', 'Alto', 'Fortinet', 'Cisco', 'Native']:
                if schema_part.endswith(suffix):
                    return schema_part.replace(suffix, '')
            return schema_part
    
    return None

def read_csv_file(file_path):
    """
    Read CSV file and return data as a list of dictionaries
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        list: List of dictionaries where each dict represents a row
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

def get_csv_column_names(csv_file_path):
    """
    Get column names from CSV file
    
    Args:
        csv_file_path (str): Path to the CSV file
        
    Returns:
        list: List of column names
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            column_names = reader.fieldnames
            return column_names if column_names else []
    except Exception as e:
        print(f"Error reading CSV column names: {e}")
        return []

def count_csv_records(csv_file_path):
    """
    Count the number of data records in CSV file (excluding header)
    
    Args:
        csv_file_path (str): Path to the CSV file
        
    Returns:
        int: Number of data records
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return sum(1 for row in reader)
    except Exception as e:
        print(f"Error counting CSV records: {e}")
        return 0

def generate_sample_data_with_openai(column_names, schema_name="WebSession", num_records=10, parser_query=None):
    """
    Generate sample data using Azure OpenAI based on column names, schema, and KQL parser query
    
    Args:
        column_names (list): List of column names from CSV
        schema_name (str): Schema name for context
        num_records (int): Number of sample records to generate (default: 10)
        parser_query (str): KQL parser query to ensure data compatibility
        
    Returns:
        list: List of dictionaries with sample data compatible with the parser query
    """
    try:
        # Try to import openai - if not available, fall back to default generation
        try:
            import os
            import base64
            import json
            from openai import AzureOpenAI
            from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        except ImportError:
            print("OpenAI package not available, falling back to default sample data generation")
            return generate_default_sample_data(column_names, num_records, schema_name)
        
        # Azure OpenAI configuration using your provided settings
        try:
            endpoint = os.getenv("ENDPOINT_URL", "https://test-openai.azure.com/")
            deployment = os.getenv("DEPLOYMENT_NAME", "testamoldeployment")

            # Validate configuration
            if endpoint == "https://test-openai.azure.com/" or deployment == "test":
                print("Warning: Using default Azure OpenAI configuration values.")
                print("Please set environment variables ENDPOINT_URL and DEPLOYMENT_NAME for real Azure OpenAI service.")
                print("")
                print("To use Azure OpenAI, you need to:")
                print("1. Create an Azure OpenAI resource in Azure portal")
                print("2. Deploy a model (like gpt-4 or gpt-35-turbo)")
                print("3. Set environment variables:")
                print("   - ENDPOINT_URL: Your Azure OpenAI endpoint (e.g., https://your-resource.openai.azure.com/)")
                print("   - DEPLOYMENT_NAME: Your model deployment name")
                print("4. Ensure you have proper Azure authentication (az login)")
                print("")
                print("Falling back to default sample data generation...")
                return generate_default_sample_data(column_names, num_records, schema_name)

            # Initialize Azure credential (equivalent to DefaultAzureCredential in C#)
            credential = DefaultAzureCredential()
            
            # Get token for Azure OpenAI (similar to Semantic Kernel approach)
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default"
            )
            # token = credential.get_token("https://cognitiveservices.azure.com/.default")
            
            # Initialize Azure OpenAI client with simpler approach (like Semantic Kernel)
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,  # Use token directly instead of token provider
                api_version="2025-01-01-preview"  # Use stable API version
            )

            print(f"Successfully initialized Azure OpenAI client with endpoint: {endpoint}")
            print(f"Using deployment: {deployment}")
            
            # Test the connection with a simple request first (like Semantic Kernel validation)
            try:
                print("Testing Azure OpenAI connection...")
                test_messages = [{"role": "user", "content": "Hello"}]
                test_completion = client.chat.completions.create(
                    model=deployment,
                    messages=test_messages,
                    max_tokens=800,
                    temperature=0.7,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None,
                    stream=False
                )
                # test_completion = client.chat.completions.create(
                #     model=deployment,
                #     messages=test_messages,
                #     max_tokens=5,
                #     temperature=0.1
                # )
                print("✓ Azure OpenAI connection test successful")
            except Exception as test_error:
                print(f"✗ Azure OpenAI connection test failed: {test_error}")
                print("Attempting token refresh and retry...")
                
                # Try refreshing token and retry (similar to Semantic Kernel error handling)
                try:
                    new_token = credential.get_token("https://cognitiveservices.azure.com/.default")
                    client = AzureOpenAI(
                        azure_endpoint=endpoint,
                        api_key=new_token.token,
                        api_version="2024-05-01-preview"
                    )
                    retry_completion = client.chat.completions.create(
                        model=deployment,
                        messages=test_messages,
                        max_tokens=5,
                        temperature=0.1
                    )
                    print("✓ Azure OpenAI connection successful after token refresh")
                except Exception as retry_error:
                    print(f"✗ Azure OpenAI connection failed after retry: {retry_error}")
                    print("Falling back to default sample data generation...")
                    return generate_default_sample_data(column_names, num_records, schema_name)
            
        except Exception as e:
            print(f"Failed to initialize Azure OpenAI client: {e}")
            return generate_default_sample_data(column_names, num_records, schema_name)
        
        # Analyze parser query to extract key requirements
        query_analysis = ""
        if parser_query:
            query_analysis = f"""
            
            IMPORTANT: The generated data must be compatible with this KQL parser query:
            {parser_query}
            
            Analyze this query and ensure the generated data:
            1. Matches any specific field patterns, values, or formats referenced in the query
            2. Contains realistic values that would be found in the source data this parser processes
            3. Includes appropriate values for any filters, where clauses, or data transformations
            4. Uses consistent naming conventions and data types as expected by the parser
            5. Generates data that would realistically appear in the original log source
            """
        
        # Create prompt for generating sample data based on CSV column names and KQL query
        columns_str = ", ".join(column_names)
        prompt = f"""
        You are an expert cybersecurity data generator specializing in ASIM (Advanced Security Information Model) and VIM (Vendor Independent Model) schemas.
        
        Generate {num_records} realistic sample records for a {schema_name} schema that will be processed by a KQL parser.
        
        CSV COLUMNS: {columns_str}
        {query_analysis}
        
        GENERATION REQUIREMENTS:
        
        For ASIM/VIM compatibility, ensure realistic values for these column patterns:
        
        TEMPORAL FIELDS:
        - TimeGenerated, EventStartTime, EventEndTime: Use ISO 8601 format (e.g., "2024-01-15T10:30:45.123Z")
        - Ensure temporal consistency (StartTime <= EndTime <= TimeGenerated)
        
        NETWORK FIELDS:
        - SrcIpAddr, DstIpAddr: Mix of private (192.168.x.x, 10.x.x.x) and public IPs
        - SrcPortNumber, DstPortNumber: Realistic port numbers (80, 443, 1024-65535)
        - NetworkProtocol: TCP, UDP, ICMP, etc.
        - NetworkDirection: Inbound, Outbound, Local
        
        USER/IDENTITY FIELDS:
        - ActorUsername, TargetUsername: Realistic usernames (john.doe, admin, service accounts)
        - ActorUserId, TargetUserId: UUIDs or domain\\username format
        - ActorUserType: Regular, Admin, System, Service
        
        DEVICE/HOST FIELDS:
        - SrcHostname, DstHostname: Realistic hostnames (DC01, WS-USER01, web-server-01)
        - SrcDeviceType, DstDeviceType: Workstation, Server, Firewall, Router
        
        EVENT/ACTIVITY FIELDS:
        - EventType: Login, Logout, FileAccess, NetworkConnection, etc.
        - EventResult: Success, Failure, Partial
        - EventSeverity: Informational, Low, Medium, High, Critical
        - EventOriginalSeverity: Original vendor severity levels
        
        WEB SESSION SPECIFIC (if schema is WebSession):
        - HttpRequestMethod: GET, POST, PUT, DELETE
        - Url: Realistic URLs with domains, paths, query parameters
        - HttpStatusCode: 200, 404, 500, 403, etc.
        - HttpUserAgent: Realistic browser/application user agents
        - HttpReferrer: Realistic referrer URLs
        
        AUTHENTICATION SPECIFIC (if schema is Authentication):
        - LogonType: Interactive, Network, Batch, Service, etc.
        - AuthenticationMethod: NTLM, Kerberos, Forms, Certificate
        - LogonResult: Success, Failure, Timeout
        
        PROCESS SPECIFIC (if schema is ProcessEvent):
        - ProcessName: cmd.exe, powershell.exe, notepad.exe, etc.
        - ProcessCommandLine: Realistic command lines with parameters
        - ProcessId: Numeric process IDs
        - ParentProcessName, ParentProcessId: Parent process information
        
        DNS SPECIFIC (if schema is DnsActivity):
        - DnsQuery: Realistic domain names (microsoft.com, google.com, malicious.example)
        - DnsQueryType: A, AAAA, MX, CNAME, TXT
        - DnsResponseCode: 0 (Success), 2 (Server Failure), 3 (Name Error)
        
        VENDOR FIELDS:
        - EventVendor: Microsoft, Cisco, Palo Alto Networks, Fortinet, etc.
        - EventProduct: Windows, ASA, Panorama, FortiGate, etc.
        - EventProductVersion: Realistic version numbers
        
        ADDITIONAL REQUIREMENTS:
        - Mix successful and failed operations (70% success, 30% failures)
        - Include both normal and suspicious activities
        - Use realistic timestamps within the last 24 hours
        - Ensure data variety to test different query conditions
        - Make values consistent within each record (e.g., matching IP geolocation)
        - Include edge cases that parsers typically need to handle
        
        Return ONLY a valid JSON array of {num_records} objects. Each object must have ALL the specified columns with realistic, ASIM/VIM-compatible values.
        Do not include any additional text, explanations, or formatting - just the JSON array.
        """
        
        # Create chat history (equivalent to ChatHistory in C# Semantic Kernel)
        chat_messages = [
            {
                "role": "system",
                "content": "You are an expert cybersecurity data generator specializing in ASIM/VIM schemas and KQL parsing. Generate realistic, parser-compatible security log data in JSON format only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Generate sample data using Azure OpenAI (equivalent to GetChatMessageContentAsync in C#)
        try:
            print(f"Calling Azure OpenAI with model: {deployment}")
            
            # Equivalent to AzureOpenAIPromptExecutionSettings in C#
            completion = client.chat.completions.create(
                model=deployment,
                messages=chat_messages,
                max_tokens=4000,  # Reduced token limit for better reliability
                temperature=0.7,
                top_p=0.95,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stream=False
            )
            print("Successfully received response from Azure OpenAI")
        except Exception as openai_error:
            print(f"Azure OpenAI API call failed: {openai_error}")
            print(f"Error type: {type(openai_error).__name__}")
            
            # Try with refreshed token (similar to Semantic Kernel retry logic)
            try:
                print("Attempting retry with token refresh...")
                new_token = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default")
                retry_client = AzureOpenAI(
                    azure_endpoint=endpoint,
                    api_key=new_token.token,
                    api_version="2024-05-01-preview"
                )
                completion = retry_client.chat.completions.create(
                    model=deployment,
                    messages=chat_messages,
                    max_tokens=4000,
                    temperature=0.7,
                    stream=False
                )
                print("Successfully received response from Azure OpenAI after retry")
            except Exception as retry_error:
                print(f"Retry also failed: {retry_error}")
                print("Falling back to default sample data generation...")
                return generate_default_sample_data(column_names, num_records, schema_name)

        # Extract and parse the response
        response_content = completion.choices[0].message.content.strip()
        print(f"OpenAI Response received, content length: {len(response_content)}")
        
        # Clean the response to ensure it's valid JSON
        if response_content.startswith('```json'):
            response_content = response_content[7:]  # Remove ```json
        if response_content.endswith('```'):
            response_content = response_content[:-3]  # Remove ```
        
        response_content = response_content.strip()
        
        try:
            sample_data = json.loads(response_content)
            
            # Validate that we got the expected number of records
            if isinstance(sample_data, list) and len(sample_data) > 0:
                print(f"Successfully generated {len(sample_data)} sample records using Azure OpenAI")
                
                # Ensure all records have all required columns
                for i, record in enumerate(sample_data):
                    for col in column_names:
                        if col not in record:
                            # Generate schema-appropriate default values for missing columns
                            record[col] = generate_schema_appropriate_value(col, schema_name, i+1)
                
                return sample_data[:num_records]  # Return exactly the requested number
            else:
                print("OpenAI returned invalid data structure, falling back to default generation")
                return generate_default_sample_data(column_names, num_records, schema_name)
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI response as JSON: {e}")
            print(f"Response content preview: {response_content[:500]}...")
            print("Falling back to default sample data generation")
            return generate_default_sample_data(column_names, num_records, schema_name)
        
    except Exception as e:
        print(f"Error generating sample data with OpenAI: {e}")
        print("Falling back to default sample data generation...")
        return generate_default_sample_data(column_names, num_records, schema_name)

def generate_schema_appropriate_value(column_name, schema_name, record_index):
    """
    Generate schema-appropriate default values for missing columns
    
    Args:
        column_name (str): Name of the column
        schema_name (str): Schema name (WebSession, Authentication, etc.)
        record_index (int): Record number for uniqueness
        
    Returns:
        Appropriate default value for the column
    """
    import datetime
    import random
    
    col_lower = column_name.lower()
    
    # Time-based fields
    if any(keyword in col_lower for keyword in ['time', 'date', 'timestamp']):
        base_time = datetime.datetime.now() - datetime.timedelta(minutes=record_index * 5)
        return base_time.isoformat() + "Z"
    
    # Network fields
    elif 'srcipaddr' in col_lower or 'sourceip' in col_lower:
        return f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
    elif 'dstipaddr' in col_lower or 'destinationip' in col_lower:
        return f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}"
    elif 'port' in col_lower:
        return random.choice([80, 443, 22, 8080, 3389, 1433, 445])
    
    # User fields
    elif 'username' in col_lower or 'user' in col_lower:
        users = ['admin', 'john.doe', 'alice.smith', 'service.account', 'guest']
        return f"{random.choice(users)}{record_index}"
    
    # Device/Host fields
    elif 'hostname' in col_lower or 'device' in col_lower:
        prefixes = ['WS', 'SRV', 'DC', 'FW', 'SW']
        return f"{random.choice(prefixes)}-{record_index:03d}"
    
    # Schema-specific defaults
    elif schema_name == "WebSession":
        if 'url' in col_lower:
            domains = ['example.com', 'microsoft.com', 'github.com']
            return f"https://{random.choice(domains)}/api/data?id={record_index}"
        elif 'method' in col_lower:
            return random.choice(['GET', 'POST', 'PUT', 'DELETE'])
        elif 'statuscode' in col_lower:
            return random.choice([200, 404, 403, 500])
    
    elif schema_name == "Authentication":
        if 'logontype' in col_lower:
            return random.choice(['Interactive', 'Network', 'Service'])
        elif 'result' in col_lower:
            return random.choice(['Success', 'Failure'])
    
    # Generic defaults
    elif 'id' in col_lower:
        return f"ID{random.randint(1000, 9999)}{record_index}"
    elif 'type' in col_lower:
        return f"{schema_name}Log_CL"
    elif 'vendor' in col_lower:
        return random.choice(['Microsoft', 'Cisco', 'Palo Alto'])
    elif 'product' in col_lower:
        return random.choice(['Windows', 'Firewall', 'Proxy'])
    
    # Default fallback
    return f"Generated_{column_name}_{record_index}"

def generate_default_sample_data(column_names, num_records=10, schema_name="WebSession"):
    """
    Generate default sample data when OpenAI is not available
    
    Args:
        column_names (list): List of column names
        num_records (int): Number of sample records to generate (default: 10)
        
    Returns:
        list: List of dictionaries with sample data
    """
    import datetime
    import random
    
    sample_data = []
    
    for i in range(num_records):
        record = {}
        for col in column_names:
            col_lower = col.lower()
            
            # Generate sample data based on column name patterns
            if 'time' in col_lower or 'date' in col_lower:
                # Generate different timestamps
                base_time = datetime.datetime.now() - datetime.timedelta(hours=i)
                record[col] = base_time.isoformat() + "Z"
            elif 'ip' in col_lower or 'address' in col_lower:
                record[col] = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            elif 'port' in col_lower:
                record[col] = random.choice([80, 443, 22, 21, 25, 53, 110, 143, 993, 995, 8080, 3389])
            elif 'url' in col_lower:
                domains = ['example.com', 'testsite.org', 'sampleapp.net', 'demo.io']
                paths = ['login', 'dashboard', 'api/data', 'admin', 'search', 'upload']
                record[col] = f"https://{random.choice(domains)}/{random.choice(paths)}?id={i+1}"
            elif 'user' in col_lower or 'email' in col_lower:
                users = ['alice', 'bob', 'charlie', 'diana', 'eve', 'frank', 'grace', 'henry']
                domains = ['company.com', 'example.org', 'testcorp.net']
                record[col] = f"{random.choice(users)}{i+1}@{random.choice(domains)}"
            elif 'event' in col_lower:
                events = ['Login', 'Logout', 'FileAccess', 'NetworkConnection', 'ProcessStart', 'DataTransfer', 'SecurityAlert', 'UserActivity']
                record[col] = f"{random.choice(events)}Event{i+1}"
            elif 'type' in col_lower:
                record[col] = f"SecurityLog_CL"
            elif 'vendor' in col_lower:
                vendors = ['Microsoft', 'Cisco', 'Palo Alto', 'Fortinet', 'Zscaler', 'CrowdStrike', 'Splunk']
                record[col] = random.choice(vendors)
            elif 'product' in col_lower:
                products = ['Firewall', 'Proxy', 'Endpoint Protection', 'SIEM', 'Cloud Security', 'Network Monitor']
                record[col] = random.choice(products)
            elif 'severity' in col_lower or 'level' in col_lower:
                record[col] = random.choice(['Low', 'Medium', 'High', 'Critical'])
            elif 'status' in col_lower:
                record[col] = random.choice(['Success', 'Failed', 'Warning', 'Error'])
            elif 'id' in col_lower:
                record[col] = f"ID{random.randint(1000, 9999)}{i+1}"
            elif 'count' in col_lower or 'size' in col_lower:
                record[col] = random.randint(1, 1000)
            elif 'bool' in col_lower or col_lower.startswith('is') or col_lower.startswith('has'):
                record[col] = random.choice([True, False])
            else:
                # Generic string value
                record[col] = f"SampleValue{i+1}_{col[:5]}"
        
        sample_data.append(record)
    
    return sample_data

def save_sample_data_to_csv(sample_data, csv_file_path):
    """
    Save sample data back to CSV file
    
    Args:
        sample_data (list): List of dictionaries with sample data
        csv_file_path (str): Path to save the CSV file
    """
    try:
        if not sample_data:
            print("No sample data to save")
            return False
            
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            if sample_data:
                fieldnames = sample_data[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sample_data)
        
        print(f"Successfully saved {len(sample_data)} sample records to {csv_file_path}")
        return True
        
    except Exception as e:
        print(f"Error saving sample data to CSV: {e}")
        return False

def main():
    """Main function to handle execution flow"""
    # Get user input for local testing
    global DEBUG_LOCAL, local_sample_file, local_parser_file
    DEBUG_LOCAL, local_sample_file, local_parser_file = get_user_input_for_local_testing()
    DEBUG_LOCAL = True  # Set to True for local debugging, False for production
    if DEBUG_LOCAL:
        print("Running in LOCAL DEBUG mode")
        print(f"Sample data file: {local_sample_file}")
        if local_parser_file:
            print(f"Parser file: {local_parser_file}")
        else:
            print("Parser file: Will be auto-detected or skipped")
        # For local debugging, use the provided file paths
        if local_parser_file:
            # Extract parser file pattern for processing
            parser_yaml_files = [local_parser_file.replace(os.path.dirname(local_parser_file), '').strip('\\').strip('/')]
        else:
            # Create a mock parser file path
            parser_yaml_files = ["Parsers/ASimWebSession/Parsers/vimWebSessionZscalerZIA.yaml"]
        commit_number = "master"

    # Process parser files
    for file in parser_yaml_files:
        SchemaName = extract_schema_name_from_path(file) #re.search(r'ASim(\w+)$', file)
        # if SchemaNameMatch:
        #     SchemaName = SchemaNameMatch.group(1)
        # else:
        #     SchemaName = None
        
        # Check if changed file is a union or empty parser. If Yes, skip the file
        # if SchemaName and file.endswith((f'ASim{SchemaName}.yaml', f'im{SchemaName}.yaml', f'vim{SchemaName}Empty.yaml')):
        #     print(f"Ignoring this {file} because it is a union or empty parser file")
        #     continue        
        
        print(f"Starting ingestion for sample data present in {file}")
        
        # Read parser file - local or remote
        if DEBUG_LOCAL and local_parser_file:
            print(f"Reading local parser file: {local_parser_file}")
            asim_parser = read_local_parser_data(local_parser_file)
        else:
            asim_parser_url = f'{SENTINEL_REPO_RAW_URL}/{commit_number}/{file}'
            print(f"Reading ASIM Parser file from : {asim_parser_url}")
            asim_parser = read_github_yaml(asim_parser_url)
        
        # Add error handling for None response
        if asim_parser is None:
            print(f"Failed to read parser YAML file")
            if DEBUG_LOCAL:
                print("Creating mock parser object for debugging...")
                asim_parser = {
                    'ParserQuery': 'EventVendor="Zscaler" | EventProduct="ZIA Proxy"',
                    'Normalization': {'Schema': 'WebSession'},
                    'EquivalentBuiltInParser': 'CommonSecurityLog'
                }
            else:
                continue
        
        # Add type checking before calling .get()
        if not isinstance(asim_parser, dict):
            print(f"Parser data is not a dictionary, got type: {type(asim_parser)}")
            print(f"Parser content: {asim_parser}")
            continue
        
        parser_query = asim_parser.get('ParserQuery', '')
        normalization = asim_parser.get('Normalization', {})
        schema = normalization.get('Schema') if isinstance(normalization, dict) else 'WebSession'
        equivalent_built_in_parser = asim_parser.get('EquivalentBuiltInParser', '')
        
        # Add debug output for parser content
        if DEBUG_LOCAL:
            print(f"Parser keys: {list(asim_parser.keys())}")
            print(f"Schema: {schema}")
            print(f"Equivalent built-in parser: {equivalent_built_in_parser}")
            print(f"Parser query preview: {parser_query[:100]}...")
        
        try:
            event_vendor, event_product, schema_name = extract_event_vendor_product(parser_query, file, SchemaName, equivalent_built_in_parser)
            print(f"Extracted - Vendor: {event_vendor}, Product: {event_product}, Schema: {schema_name}")
        except Exception as e:
            print(f"Failed to extract event vendor/product: {e}")
            # For debugging, set default values
            if DEBUG_LOCAL:
                event_vendor = "Zscaler"
                event_product = "ZIA Proxy"
                schema_name = "WebSession"
                print(f"Using default values - Vendor: {event_vendor}, Product: {event_product}, Schema: {schema_name}")
            else:
                continue

        # Use local file for debugging
        if DEBUG_LOCAL and local_sample_file:
            print("Using local sample data file")
            
            # Check if CSV file has only column names (no data records)
            column_names = get_csv_column_names(local_sample_file)
            record_count = count_csv_records(local_sample_file)
            
            print(f"Found {len(column_names)} columns: {column_names}")
            print(f"Found {record_count} data records")
            
            # If CSV has more than 1-2 records, skip generation and use existing data
            if record_count > 2:
                print(f"CSV file has {record_count} records (more than 2), using existing data")
                data_result, table_name = read_local_sample_data(local_sample_file)
                if data_result is None:
                    continue
            # If CSV has only column names or very few records, generate sample data
            elif record_count <= 2 and len(column_names) > 0:
                print(f"CSV file has {record_count} records (2 or fewer), generating sample data")
                
                # Generate sample data using OpenAI or default method
                try:
                    sample_data = generate_sample_data_with_openai(
                        column_names=column_names,
                        schema_name=schema_name if 'schema_name' in locals() else "WebSession",
                        num_records=10,  # Generate 10 sample records
                        parser_query=parser_query if 'parser_query' in locals() else None
                    )
                    
                    if sample_data and len(sample_data) > 0:
                        # Save generated data back to CSV file
                        if save_sample_data_to_csv(sample_data, local_sample_file):
                            print("Successfully generated and saved sample data to CSV file")
                            # Now read the updated CSV file
                            data_result, table_name = read_local_sample_data(local_sample_file)
                            if data_result is None:
                                continue
                        else:
                            print("Failed to save sample data, using generated data directly")
                            # Use the generated data directly without saving to file
                            data_result = sample_data
                            table_name = f"{schema_name if 'schema_name' in locals() else 'Sample'}_CL"
                    else:
                        print("Failed to generate sample data")
                        continue
                        
                except Exception as e:
                    print(f"Error during sample data generation: {e}")
                    continue
            else:
                print("CSV file has no columns or invalid structure")
                continue
        else:
            SampleDataFile = f'{event_vendor}_{event_product}_{schema}_IngestedLogs.csv'
            sample_data_url = local_sample_file #f'{SENTINEL_REPO_RAW_URL}/{commit_number}/{SAMPLE_DATA_PATH}'
            SampleDataUrl = local_sample_file # sample_data_url + SampleDataFile
            print(f"Sample data log file reading from url: {SampleDataUrl}")
            
            # For remote URLs, use requests to get the file
            try:
                response = read_csv_file(SampleDataUrl)
                if len(response) > 0:
                    data_result, table_name = convert_data_csv_to_json(SampleDataUrl) #'tempfile.csv')
                else:
                    print(f"No data found in the sample data file at {SampleDataUrl}")
                    continue
            except Exception as e:
                print(f"Error fetching sample data from Path {SampleDataUrl}: {e}")
                continue   
        
        print(f"Table Name : {table_name}")
        log_ingestion_supported,table_type=check_for_custom_table(table_name)
        print(f"Log ingestion supported: {log_ingestion_supported}\n Table type: {table_type}")
        
        # Add debug output
        if DEBUG_LOCAL:
            print(f"Sample data preview (first 2 records):")
            for i, record in enumerate(data_result[:2]):
                print(f"Record {i+1}: {record}")
            print(f"Total records: {len(data_result)}")
        
        # Continue with the rest of the ingestion logic only if not in local debug mode
        log_ingestion_supported = True
        DEBUG_LOCAL = False  # Set to False for production ingestion
        if not DEBUG_LOCAL:
            if log_ingestion_supported == True and table_type =="custom_log":
                flag=0 #flag value is used to check if DCR is created for the table or not
                schema_file_name = f"{table_name}_Schema.csv"
                schemaUrl = sample_data_url+schema_file_name
                response = requests.get(schemaUrl)
                if response.status_code == 200:
                    with open('tempfile.csv', 'wb') as file:
                        file.write(response.content)
                else:
                    print(f"::error::An error occurred while trying to get content of Schema file located at {schemaUrl}: {response.text}")
                    continue        
                schema_result = convert_schema_csv_to_json('tempfile.csv')
                data_result = convert_data_type(schema_result, data_result)
                # conversion of datatype is needed for boolean and string values because during testing it has been observed that 
                # boolean values are consider as string and numerical value of type string are consider 
                # as integer which leds to non ingestion of those value in sentinel    
                # create table 
                request_body, url_to_call , method_to_use = create_table(json.dumps(schema_result, indent=4),table_name)
                response_body=hit_api(url_to_call,request_body,method_to_use)
                print(f"Response of table creation: {response_body.text} {response_body.status_code}")
                if response_body.status_code != 202 and response_body.status_code != 200:
                    print(f"Table creation failed for {table_name}")
                    continue
                else:
                    get_table_status(table_name)
                #Once table is created now creating DCR
                request_body, url_to_call , method_to_use ,stream_name = create_dcr(json.dumps(schema_result, indent=4),table_name,"Custom")  
                response_body=hit_api(url_to_call,request_body,method_to_use)
                print(f"Response of DCR creation: {response_body.text}")
                dcr_directory.append({
                'DCRname':table_name+'_DCR'+str(random_number),
                'imutableid':json.loads(response_body.text).get('properties').get('immutableId'),
                'stream_name':stream_name
                })
                print(dcr_directory)
                #ingestion start for sending data via DCR
                for dcr in dcr_directory:
                    if table_name in dcr['DCRname'] and str(random_number) in dcr['DCRname'] :
                        immutable_id = dcr['imutableid']
                        stream_name = dcr['stream_name']
                        flag=1
                        break 
                print(f"Ingestion started for {table_name}") 
                print(f"{immutable_id},{stream_name},{table_name}")
                
                # Check permissions before attempting ingestion
                print("Checking permissions for data ingestion...")
                if not check_dcr_permissions(immutable_id):
                    print("⚠ Permission check indicates potential issues")
                    
                if not get_user_identity_info():
                    print("⚠ Cannot verify current identity")
                    
                senddtosentinel(immutable_id,data_result,stream_name,flag)
            elif log_ingestion_supported == True and table_type == "builtin":
                flag=0 #flag value is used to check if DCR is created for the table or not
                #create dcr for ingestion
                guid_columns = []
                schema = get_schema_for_builtin(table_name)
                data_result = convert_data_type(schema, data_result)
                request_body, url_to_call , method_to_use ,stream_name = create_dcr(json.dumps(schema, indent=4),table_name,"Microsoft")
                response_body=hit_api(url_to_call,request_body,method_to_use)
                print(f"Response of DCR creation: {response_body.text}")
                if response_body.status_code == 400 and "InvalidTransformOutput" in response_body.text:
                    guid_flag=0
                    print("*********Checking if failure reason is GUID Type columns and present in schema***********")
                    str_match = json.loads(response_body.text).get('error').get('details')[0].get('message')
                    match = re.findall(r'(\w+\s*\[produced:\s*\'String\',\s*output:\s*\'Guid\'\])', str_match)
                    print(f"Mismatched Column and there types : {match}")
                    for item in match:
                        if "Guid" not in item:
                            guid_flag=1
                            print(f"Provided column Type other than GUID TYPE is not matching with Output Stream : {item}")
                    if guid_flag == 1:
                        print("Please provide Same Type of columns in stream declaration that matches with output stream of DCR")
                        exit(1)
                    cleaned_guid_columns = [item.replace(" [produced:'String', output:'Guid']", "") for item in match]
                    guid_columns = cleaned_guid_columns
                    print("Re trying DCR creation after removing GUID columns")
                    schema = get_schema_for_builtin(table_name)
                    request_body, url_to_call , method_to_use ,stream_name = create_dcr(json.dumps(schema, indent=4),table_name,"Microsoft")
                    response_body=hit_api(url_to_call,request_body,method_to_use)
                    print(f"Response of DCR creation: {response_body.text}")       
                dcr_directory.append({
                'DCRname':table_name+'_DCR'+str(random_number),
                'imutableid':json.loads(response_body.text).get('properties').get('immutableId'),
                'stream_name':stream_name
                })
                print(dcr_directory)
                for dcr in dcr_directory:
                    if table_name in dcr['DCRname'] and str(random_number) in dcr['DCRname'] :
                        immutable_id = dcr['imutableid']
                        stream_name = dcr['stream_name']
                        flag=1
                        break
                print(dcr_directory)    
                print(f"Ingestion started for {table_name}")
                
                # Check permissions before attempting ingestion
                print("Checking permissions for data ingestion...")
                if not check_dcr_permissions(immutable_id):
                    print("⚠ Permission check indicates potential issues")
                    
                if not get_user_identity_info():
                    print("⚠ Cannot verify current identity")
                       
                senddtosentinel(immutable_id,data_result,stream_name,flag)
            else:
                print(f"Table {table_name} is not supported for log ingestion")
                continue
        else:
            print("Local debug mode - skipping actual data ingestion to Azure")
            print(f"Would have ingested {len(data_result)} records to table: {table_name}")

# Script entry point
if __name__ == "__main__":
    # Initialize global variables
    DEBUG_LOCAL = True
    local_sample_file = None
    local_parser_file = None
    
    # Run main function
    main()
