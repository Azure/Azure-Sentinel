from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import requests
import logging
import re
import azure.functions as func
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os

requests.packages.urllib3.disable_warnings()
app = func.FunctionApp()

container_name = "sentinelcontainer"
blob_name = "timestamp"

cs = os.environ.get('AzureWebJobsStorage')

customer_id = os.environ.get('AzureSentinelWorkspaceId','')
shared_key = os.environ.get('AzureSentinelSharedKey')
verify = False
logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

key_vault_name = os.environ.get("KeyVaultName","Commvault-Integration-KV")
uri = None
url = None
qsdk_token = None
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

job_details_body = {
        "opType": 1,
        "entity": {"_type_": 0},
        "options": {"restoreIndex": True},
        "queries": [
            {
                "type": 0,
                "queryId": "MimeFileList",
                "whereClause": [
                    {
                        "criteria": {
                            "field": 38,
                            "dataOperator": 9,
                            "values": ["file"],
                        }
                    },
                    {
                        "criteria": {
                            "field": 147,
                            "dataOperator": 0,
                            "values": ["2"],
                        }
                    },
                ],
                "dataParam": {
                    "sortParam": {"ascending": True, "sortBy": [0]},
                    "paging": {"firstNode": 0, "pageSize": -1, "skipNode": 0},
                },
            },
            {
                "type": 1,
                "queryId": "MimeFileCount",
                "whereClause": [
                    {
                        "criteria": {
                            "field": 38,
                            "dataOperator": 9,
                            "values": ["file"],
                        }
                    },
                    {
                        "criteria": {
                            "field": 147,
                            "dataOperator": 0,
                            "values": ["2"],
                        }
                    },
                ],
                "dataParam": {
                    "sortParam": {"ascending": True, "sortBy": [0]},
                    "paging": {"firstNode": 0, "pageSize": -1, "skipNode": 0},
                },
            },
        ],
        "paths": [{"path": "/**/*"}],
    }


def main(mytimer: func.TimerRequest) -> None:
    global qsdk_token, url
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Executing Python timer trigger function.')

    pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
    match = re.match(pattern, str(logAnalyticsUri))
    if (not match):
        logging.info(f"Invalid url : {logAnalyticsUri}")
        raise Exception("Lookout: Invalid Log Analytics Uri.")
    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=f"https://{key_vault_name}.vault.azure.net", credential=credential)
        secret_name = "environment-endpoint-url"
        uri = client.get_secret(secret_name).value
        url = "https://" + uri + "/commandcenter/api"
        secret_name = "access-token"
        qsdk_token = client.get_secret(secret_name).value
        headers["authtoken"] = "QSDK " + qsdk_token
        ustring = "/events?level=10&showInfo=false&showMinor=false&showMajor=true&showCritical=true&showAnomalous=true"
        f_url = url + ustring
        current_date = datetime.now(timezone.utc)
        to_time = int(current_date.timestamp())
        fromtime = read_blob(cs, container_name, blob_name)
        if fromtime is None:
            fromtime = int((current_date - timedelta(days=2)).timestamp())
            logging.info("From Time : [{}] , since the time read from blob is None".format(fromtime))
        else:
            fromtime_dt = datetime.fromtimestamp(fromtime, tz=timezone.utc)
            time_diff = current_date - fromtime_dt
            if time_diff > timedelta(days=2):
                updatedfromtime = int((current_date - timedelta(days=2)).timestamp())
                logging.info("From Time : [{}] , since the time read from blob : [{}] is older than 2 days".format(updatedfromtime,fromtime))
                fromtime = updatedfromtime
            elif time_diff < timedelta(minutes = 5):
                updatedfromtime = int((current_date - timedelta(minutes=5)).timestamp())
                logging.info("From Time : [{}] , since the time read from blob : [{}] is less than 5 minutes".format(updatedfromtime,fromtime))
                fromtime = updatedfromtime
        max_fetch = 1000
        headers["pagingInfo"] = f"0,{max_fetch}"
        logging.info("Starts at: [{}]".format(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")))
        event_endpoint = f"{f_url}&fromTime={fromtime}&toTime={to_time}"
        logging.info("Event endpoint : [{}]".format(event_endpoint))
        response = requests.get(event_endpoint, headers=headers, verify=verify)
        logging.info("Response Status Code : " + str(response.status_code))
        if response.status_code == 200:
            events = response.json()
            logging.info("Events Data")
            logging.info(events)
            data = events.get("commservEvents")
            data = [event for event in data if
                    event.get("eventCodeString") in "7:211|7:212|7:293|7:269|14:337|14:338|69:59|7:333|69:60|35:5575"]
            post_data = []
            if data:
                for event in data:
                    temp = get_incident_details(event["description"])
                    post_data.append(temp)
                logging.info("Trying Post Data")
                gen_chunks(post_data)
                logging.info("Job Succeeded")
                print("***Job Succeeded*****")
                upload_timestamp_blob(cs, container_name, blob_name, to_time+1)
                logging.info("Function App Executed")
            else:
                print("No new events found.")

        else:
            logging.error("Failed to get events with status code : "+str(response.status_code))
    except Exception as e:
        logging.info("HTTP request error: %s", str(e))


class Constants:
    event_id: str = "event_id"
    event_time: str = "event_time"
    anomaly_sub_type: str = "AnomalyType"
    originating_client: str = "ClientName"
    originating_program: str = "originating_program"
    job_id: str = "JobId"
    affected_files_count: str = "SuspiciousFileCount"
    modified_files_count: str = "ModifiedFileCount"
    deleted_files_count: str = "DeletedFileCount"
    renamed_files_count: str = "RenamedFileCount"
    created_files_count: str = "CreatedFileCount"
    severity_high: str = "High"
    facility: str = "Commvault"
    severity_info: str = "Informational"
    path_key: str = "path"
    description: str = "description"


def get_backup_anomaly(anomaly_id: int) -> str:
    """
    Get Anomaly type from anomaly id
    
    Args:
        anomaly_id (int): The anomaly id
        
    Returns:
        str: The type of anomaly
    """

    anomaly_dict = {
        0: "Undefined",
        1: "File Activity",
        2: "File Type",
        3: "Threat Analysis",
    }
    return anomaly_dict.get(anomaly_id, "Undefined")


def define_severity(anomaly_sub_type: str) -> str | None:
    """
Function to get severity from anomaly sub type

Args:
    anomaly_sub_type (str): The sub type of anomaly

Returns:
    str | None: The severity of the anomaly or None if not found
"""

    severity = None
    if anomaly_sub_type in ("File Type", "Threat Analysis"):
        severity = Constants.severity_high
    elif anomaly_sub_type == "File Activity":
        severity = Constants.severity_info
    return severity


def if_zero_set_none(value: str | None | int) -> str | None | int:
    """
    If the value is zero, return None
    """
    if value and int(value) > 0:
        return value
    return None


def extract_from_regex(
    message: str, default_value: str | None, *regex_string_args: str
) -> str | None:
    """
    From the message, extract the strings matching the given patterns
    
    Args:
        message (str): The message to extract from
        default_value (str | None): The default value to return if extraction fails
        *regex_string_args (str): The regex patterns to use for extraction
        
    Returns:
        str | None: The extracted string or default value
    """

    for pattern in regex_string_args:
        matches = re.search(pattern, message, re.IGNORECASE)
        if matches and len(matches.groups()) > 0:
            return matches.group(1).strip()
    return default_value


def format_alert_description(msg: str) -> str:
    """
    Format alert description
    
    Args:
        msg (str): The message to format
        
    Returns:
        str: The formatted message
    """

    default_value = msg
    if msg.find("<html>") != -1 and msg.find("</html>") != -1:
        resp = msg[msg.find("<html>") + 6: msg.find("</html>")]
        msg = resp.strip()
        if msg.find("Detected ") != -1 and msg.find(" Please click ") != -1:
            msg = msg[msg.find("Detected "): msg.find(" Please click ")]
            return msg
    return default_value


def get_files_list(job_id) -> list:
    """
    Get file list from analysis job
    
    Args:
        job_id: Job Id
        
    Returns:
        list: List of files
    """

    job_details_body["advOptions"] = {
        "advConfig": {"browseAdvancedConfigBrowseByJob": {"jobId": int(job_id)}}
    }
    f_url = url+"/DoBrowse"
    response = requests.post(f_url, headers=headers, json=job_details_body, verify=verify)
    resp = response.json()
    browse_responses = resp.get("browseResponses", [])
    file_list = []
    for browse_resp in browse_responses:
        if browse_resp.get("respType") == 0:
            browse_result = browse_resp.get("browseResult")
            if "dataResultSet" in browse_result:
                for data_result_set in browse_result.get("dataResultSet"):
                    file = {}
                    filepath = data_result_set.get("path")
                    file["sizeinkb"] = data_result_set.get("size")
                    file["folder"] = "\\".join(filepath.split("\\")[:-1])
                    file["filename"] = data_result_set.get("displayName")
                    file_list.append(file)
    return file_list


def get_subclient_content_list(subclient_id) -> dict:
    """
    Get content from subclient
    
    Args:
        subclient_id: subclient Id
        
    Returns:
        dict: Content from subclient
    """

    f_url = url + "/Subclient/" + str(subclient_id)
    resp = requests.get(f_url, headers=headers, verify=verify).json()
    resp = resp.get("subClientProperties", [{}])[0].get("content")
    return resp


def fetch_file_details(job_id, subclient_id) -> tuple[list, list]:
    """
    Function to fetch the scanned folders list during the backup job
    
    Args:
        job_id: Job Id
        subclient_id: Subclient Id
        
    Returns:
        tuple[list, list]: Tuple containing files list and scanned folder list
    """

    folders_list = []
    if job_id is None:
        return [], []
    files_list = get_files_list(job_id)
    folder_response = get_subclient_content_list(subclient_id)
    if folder_response:
        for resp in folder_response:
            folders_list.append(resp[Constants.path_key])
    return files_list, folders_list


def get_job_details(job_id, url, headers):
    """
    Function to get job details
    
    Args:
        job_id: Job Id
        url: URL
        headers: Request headers
        
    Returns:
        dict | None: Job details or None if not found
    """

    f_url = f"{url}/Job/{job_id}"
    response = requests.get(f_url, headers=headers, verify=verify)
    data = response.json()
    if ("totalRecordsWithoutPaging" in data) and (
            int(data["totalRecordsWithoutPaging"]) > 0
    ):
        logging.info(f"Job Details for job_id : {job_id}")
        logging.info(data)
        return data
    else:
        logging.info(f"Failed to get Job Details for job_id : {job_id}")
        logging.info(data)
        return None


def get_user_details(client_name):
    """
    Retrieves the user ID and user name associated with a given client name.

    Args:
        client_name (str): The name of the client.

    Returns:
        int | None: The user ID and username associated with the client, or None if not found.
    """

    f_url = f"{url}/Client/byName(clientName='{client_name}')"
    response = requests.get(f_url, headers=headers, verify=False).json()
    user_id = response['clientProperties'][0]['clientProps']['securityAssociations']['associations'][0]['userOrGroup'][0]['userId']
    user_name = response['clientProperties'][0]['clientProps']['securityAssociations']['associations'][0]['userOrGroup'][0]['userName']
    return user_id, user_name


def get_incident_details(message: str) -> dict | None:
    """
    Function to get incident details from the alert description
    
    Args:
        message (str): The alert message
        
    Returns:
        dict | None: Incident details or None if not found
    """
    anomaly_sub_type = extract_from_regex(
        message,
        "0",
        rf"{Constants.anomaly_sub_type}:\[(.*?)\]",
    )
    if anomaly_sub_type is None or anomaly_sub_type == "0":
        return None
    anomaly_sub_type = get_backup_anomaly(int(anomaly_sub_type))
    job_id = extract_from_regex(
        message,
        "0",
        rf"{Constants.job_id}:\[(.*?)\]",
    )

    description = format_alert_description(message)

    job_details = get_job_details(job_id,url,headers)
    if job_details is None:
        print(f"Invalid job [{job_id}]")
        return None
    job_start_time = int(
        job_details.get("jobs", [{}])[0].get("jobSummary", {}).get("jobStartTime")
    )
    job_end_time = int(
        job_details.get("jobs", [{}])[0].get("jobSummary", {}).get("jobEndTime")
    )
    subclient_id = (
        job_details.get("jobs", [{}])[0]
        .get("jobSummary", {})
        .get("subclient", {})
        .get("subclientId")
    )
    files_list, scanned_folder_list = fetch_file_details(job_id, subclient_id)
    originating_client = extract_from_regex(message, "", r"{}:\[(.*?)\]".format(Constants.originating_client))
    user_id, username = get_user_details(originating_client)
    details = {
        "subclient_id": subclient_id,
        "files_list": files_list,
        "scanned_folder_list": scanned_folder_list,
        "anomaly_sub_type": anomaly_sub_type,
        "severity": define_severity(anomaly_sub_type),
        "originating_client": originating_client,
        "user_id": user_id,
        "username": username,
        "affected_files_count": if_zero_set_none(
            extract_from_regex(
                message,
                None,
                r"{}:\[(.*?)\]".format(
                        Constants.affected_files_count
                ),
            )
        ),
        "modified_files_count": if_zero_set_none(
            extract_from_regex(
                message,
                None,
                r"{}:\[(.*?)\]".format(
                        Constants.modified_files_count
                ),
            )
        ),
        "deleted_files_count": if_zero_set_none(
            extract_from_regex(
                message,
                None,
                r"{}:\[(.*?)\]".format(
                        Constants.deleted_files_count
                ),
            )
        ),
        "renamed_files_count": if_zero_set_none(
            extract_from_regex(
                message,
                None,
                r"{}:\[(.*?)\]".format(
                        Constants.renamed_files_count
                ),
            )
        ),
        "created_files_count": if_zero_set_none(
            extract_from_regex(
                message,
                None,
                r"{}:\[(.*?)\]".format(
                        Constants.created_files_count
                ),
            )
        ),
        "job_start_time": datetime.utcfromtimestamp(job_start_time).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "job_end_time": datetime.utcfromtimestamp(job_end_time).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "job_id": job_id,
        "external_link": extract_from_regex(
            message, "", "href='(.*?)'", 'href="(.*?)"'
        ),
        "description": description,
    }
    return details


def build_signature(date, content_length, method, content_type, resource):
    """
    Build the authorization signature
    
    Args:
        date: Date
        content_length: Content length
        method: HTTP method
        content_type: Content type
        resource: Resource path
        
    Returns:
        str: The authorization signature
    """

    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    logging.info(f"Authorication - {authorization}")
    return authorization


def post_data(body, chunk_count):
    """
    Post data to log analytics
    
    Args:
        body: Request body
        chunk_count: Count of chunks
        
    Returns:
        None
    """

    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    logging.info("Inside Post Data")
    rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    logging.info(f"Date :- {rfc1123date}")
    content_length = len(body)
    signature = build_signature(rfc1123date, content_length, method, content_type,
                                        resource)
    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'
    logging.info(f"URL - {uri}")
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': "CommvaultSecurityIQ_CL",
        'x-ms-date': rfc1123date
    }
    logging.info(f"Request URL : {uri}")
    logging.info(f"Data :- {body}")
    response = requests.post(uri, data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info("Chunk was processed{} events".format(chunk_count))
    else:
        logging.error("Error during sending events to Microsoft Sentinel. Response code:{}".format(response.status_code))


def gen_chunks(data):
    """This method is used to get the chunks and post the data to log analytics work space

    Args:
        data (_type_): _description_
    """        
    for chunk in gen_chunks_to_object(data, chunksize=10000):
        obj_array = []
        for row in chunk:
            if row != None and row != '':
                obj_array.append(row)
        body = json.dumps(obj_array)
        post_data(body, len(obj_array))


def gen_chunks_to_object(data, chunksize=100):
    """This is used to generate chunks to object based on chunk size

    Args:
        data (_type_): data from zoom reports api
        chunksize (int, optional): _description_. Defaults to 100.

    Yields:
        _type_: the chunk
    """
    chunk = []
    for index, line in enumerate(data):
        if (index % chunksize == 0 and index > 0):
            yield chunk
            del chunk[:]
        chunk.append(line)
    yield chunk


def upload_timestamp_blob(connection_string, container_name, blob_name, timestamp):
    """
    Upload timestamp to blob storage
    
    Args:
        connection_string: Connection string
        container_name: Container name
        blob_name: Blob name
        timestamp: Timestamp
        
    Returns:
        None
    """

    try:
        timestamp_str = str(timestamp)

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        container_client = blob_service_client.get_container_client(container_name)

        blob_client = container_client.get_blob_client(blob_name)

        blob_client.upload_blob(timestamp_str, overwrite=True)

        logging.info(f"Timestamp data uploaded to blob: {blob_name}")
    except Exception as e:
        logging.info(f"An error occurred: {str(e)}")


def read_blob(connection_string, container_name, blob_name):
    """
    Read blob from blob storage
    
    Args:
        connection_string: Connection string
        container_name: Container name
        blob_name: Blob name
        
    Returns:
        int | None: Timestamp or None if not found
    """

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob(encoding='UTF-8')
        content = blob_data.readall()
        timestamp = None
        if content:
            timestamp = int(content)
        logging.info(f"Timestamp read from blob {blob_name}: {timestamp}")
        return timestamp

    except ResourceNotFoundError:
        logging.info(f"Blob '{blob_name}' does not exist.")
        return None

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise e
