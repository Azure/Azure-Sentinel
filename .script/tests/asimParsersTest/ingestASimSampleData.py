import requests
import yaml
import re
import os
import subprocess
import csv
import json
from azure.monitor.ingestion import LogsIngestionClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
import time
import sys

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
        print(f"::error::Error occurred while executing the command: {e}")
        return []

def get_current_commit_number():
    cmd = "git rev-parse HEAD"
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f"::error::Error occurred while executing the command: {e}")
        return None

def read_github_yaml(url):
    try:
        response = requests.get(url)
    except Exception as e:
        print(f"::error::An error occurred while trying to get content of YAML file located at {url}: {e}")
    return yaml.safe_load(response.text) if response.status_code == 200 else None    

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
    dcrname=table+"_DCR"+str(prnumber)
    request_object={ 
            "location": "eastus", 			
            "properties": {
                "streamDeclarations": {
                    "Custom-dcringest"+str(prnumber): {
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
                    "name": "DataCollectionEvent"+str(prnumber)
                  } 
                ] 
              }, 
              "dataFlows": [ 
                    {
                        "streams": [
                            "Custom-dcringest"+str(prnumber)
                        ],
                        "destinations": [
                            "DataCollectionEvent"+str(prnumber)
                        ],
                        "transformKql": "source",
                        "outputStream": f"{table_type}-{table}"
                    } 
                        ] 
                }
        }
    method="PUT"
    url=f"https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Insights/dataCollectionRules/{dcrname}?api-version=2022-06-01"
    return request_object , url , method ,"Custom-dcringest"+str(prnumber)

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

def senddtosentinel(immutable_id,data_result,stream_name,flag_status):
    if flag_status == 0:
        print("DCR is not created for the table. Please create DCR first")
        return
    print("Waiting for data to be sent to sentinel (This will take atleast 20 seconds)")
    time.sleep(20)
    credential = DefaultAzureCredential()
    client = LogsIngestionClient(endpoint=endpoint_uri, credential=credential, logging_enable=True)
    try:
        client.upload(rule_id=immutable_id, stream_name=stream_name, logs=data_result)
    except HttpResponseError as e:
        print(f"Upload failed: {e}")


def extract_event_vendor_product(parser_query,parser_file):
    match = re.search(r'(ASim\w+)/', parser_file)
    if match:
        schema_name = match.group(1)
    else:
        print(f'EventVendor field not mapped in parser. Please map it in parser query.{parser_file}')

    match = re.search(r'EventVendor\s*=\s*[\'"]([^\'"]+)[\'"]', parser_query)
    if match:
        event_vendor = match.group(1)
    # if equivalent_built_in_parser end with Native, then use 'EventVendor' as 'Microsoft'
    elif equivalent_built_in_parser.endswith('_Native'):
        event_vendor = 'Microsoft'
    else:
        print(f'EventVendor field not mapped in parser. Please map it in parser query.{parser_file}')

    match = re.search(r'EventProduct\s*=\s*[\'"]([^\'"]+)[\'"]', parser_query)
    if match:
        event_product = match.group(1)
    # if equivalent_built_in_parser end with Native, then use 'EventProduct' as SchemaName + 'NativeTable'
    elif equivalent_built_in_parser.endswith('_Native'):
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

workspace_id = "e9beceee-7d61-429f-a177-ee5e2b7f481a"
workspaceName = "ASIM-SchemaDataTester-GithubShared"
resourceGroupName = "asim-schemadatatester-githubshared"
subscriptionId = "4383ac89-7cd1-48c1-8061-b0b3c5ccfd97"
dataCollectionEndpointname = "asim-schemadatatester-githubshared"
endpoint_uri = "https://asim-schemadatatester-githubshared-uetl.eastus-1.ingest.monitor.azure.com" # logs ingestion endpoint of the DCR
SENTINEL_REPO_RAW_URL = f'https://raw.githubusercontent.com/Azure/Azure-Sentinel'
SAMPLE_DATA_PATH = 'Sample%20Data/ASIM/'
dcr_directory=[]

lia_supported_builtin_table = ['ADAssessmentRecommendation','ADSecurityAssessmentRecommendation','Anomalies','ASimAuditEventLogs','ASimAuthenticationEventLogs','ASimDhcpEventLogs','ASimDnsActivityLogs','ASimDnsAuditLogs','ASimFileEventLogs','ASimNetworkSessionLogs','ASimProcessEventLogs','ASimRegistryEventLogs','ASimUserManagementActivityLogs','ASimWebSessionLogs','AWSCloudTrail','AWSCloudWatch','AWSGuardDuty','AWSVPCFlow','AzureAssessmentRecommendation','CommonSecurityLog','DeviceTvmSecureConfigurationAssessmentKB','DeviceTvmSoftwareVulnerabilitiesKB','ExchangeAssessmentRecommendation','ExchangeOnlineAssessmentRecommendation','GCPAuditLogs','GoogleCloudSCC','SCCMAssessmentRecommendation','SCOMAssessmentRecommendation','SecurityEvent','SfBAssessmentRecommendation','SharePointOnlineAssessmentRecommendation','SQLAssessmentRecommendation','StorageInsightsAccountPropertiesDaily','StorageInsightsDailyMetrics','StorageInsightsHourlyMetrics','StorageInsightsMonthlyMetrics','StorageInsightsWeeklyMetrics','Syslog','UCClient','UCClientReadinessStatus','UCClientUpdateStatus','UCDeviceAlert','UCDOAggregatedStatus','UCServiceUpdateStatus','UCUpdateAlert','WindowsEvent','WindowsServerAssessmentRecommendation']
reserved_columns = ["_ResourceId", "id", "_SubscriptionId", "TenantId", "Type", "UniqueId", "Title","_ItemId","verbose_b","verbose","MG","_ResourceId_s"]

SentinelRepoUrl = "https://github.com/Azure/Azure-Sentinel"
current_directory = os.path.dirname(os.path.abspath(__file__))
modified_files = get_modified_files(current_directory)

parser_yaml_files = filter_yaml_files(modified_files)

commit_number = get_current_commit_number()
prnumber = sys.argv[1]

for file in parser_yaml_files:
    SchemaNameMatch = re.search(r'ASim(\w+)/', file)
    if SchemaNameMatch:
        SchemaName = SchemaNameMatch.group(1)
    else:
        SchemaName = None
    # Check if changed file is a union or empty parser. If Yes, skip the file
    if file.endswith((f'ASim{SchemaName}.yaml', f'im{SchemaName}.yaml', f'vim{SchemaName}Empty.yaml')):
        print(f"Ignoring this {file} because it is a union or empty parser file")
        continue        
    print(f"Starting ingestion for sample data present in {file}")
    asim_parser_url = f'{SENTINEL_REPO_RAW_URL}/{commit_number}/{file}'
    print(f"Reading Asim Parser file from : {asim_parser_url}")
    asim_parser = read_github_yaml(asim_parser_url)
    parser_query = asim_parser.get('ParserQuery', '')
    normalization = asim_parser.get('Normalization', {})
    schema = normalization.get('Schema')
    equivalent_built_in_parser = asim_parser.get('EquivalentBuiltInParser')
    event_vendor, event_product, schema_name = extract_event_vendor_product(parser_query, file)

    SampleDataFile = f'{event_vendor}_{event_product}_{schema}_IngestedLogs.csv'
    sample_data_url = f'{SENTINEL_REPO_RAW_URL}/{commit_number}/{SAMPLE_DATA_PATH}'
    SampleDataUrl = sample_data_url+SampleDataFile
    print(f"Sample data log file reading from url: {SampleDataUrl}")
    response = requests.get(SampleDataUrl)
    if response.status_code == 200:
        with open('tempfile.csv', 'wb') as file:
            file.write(response.content)
    else:
        print(f"::error::An error occurred while trying to get content of Sample Data file located at {SampleDataUrl}: {response.text}")
        continue           
    data_result,table_name = convert_data_csv_to_json('tempfile.csv')   
    print(f"Table Name : {table_name}")
    log_ingestion_supported,table_type=check_for_custom_table(table_name)
    print(f"Log ingestion supported: {log_ingestion_supported}\n Table type: {table_type}")
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
        'DCRname':table_name+'_DCR'+str(prnumber),
        'imutableid':json.loads(response_body.text).get('properties').get('immutableId'),
        'stream_name':stream_name
        })
        print(dcr_directory)
        #ingestion start for sending data via DCR
        for dcr in dcr_directory:
            if table_name in dcr['DCRname'] and str(prnumber) in dcr['DCRname'] :
                immutable_id = dcr['imutableid']
                stream_name = dcr['stream_name']
                flag=1
                break 
        print(f"Ingestion started for {table_name}") 
        print(f"{immutable_id},{stream_name},{table_name}")      
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
        'DCRname':table_name+'_DCR'+str(prnumber),
        'imutableid':json.loads(response_body.text).get('properties').get('immutableId'),
        'stream_name':stream_name
        })
        print(dcr_directory)
        for dcr in dcr_directory:
            if table_name in dcr['DCRname'] and str(prnumber) in dcr['DCRname'] :
                immutable_id = dcr['imutableid']
                stream_name = dcr['stream_name']
                flag=1
                break
        print(dcr_directory)    
        print(f"Ingestion started for {table_name}")       
        senddtosentinel(immutable_id,data_result,stream_name,flag)
    else:
        print(f"Table {table_name} is not supported for log ingestion")
        continue
