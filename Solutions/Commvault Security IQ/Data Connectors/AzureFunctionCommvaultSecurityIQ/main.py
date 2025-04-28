from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import requests
import logging
import re
import azure.functions as func
import json
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os

requests.packages.urllib3.disable_warnings()
app = func.FunctionApp()

container_name = "sentinelcontainer"
blob_name = "timestamp"

cs = os.environ.get('AzureWebJobsStorage')
if not cs:
    raise ValueError("AzureWebJobsStorage environment variable is not set.")

backfill_days = int(os.environ.get('NumberOfDaysToBackfill', "2")) # this is just for testing

customer_id = os.environ.get('AzureSentinelWorkspaceId', '')
if not customer_id:
    raise ValueError("AzureSentinelWorkspaceId environment variable is not set.")

shared_key = os.environ.get('AzureSentinelSharedKey')
if not shared_key:
    raise ValueError("AzureSentinelSharedKey environment variable is not set.")

logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

key_vault_name = os.environ.get("KeyVaultName","Commvault-Integration-KV")
url = None
access_token = None
refresh_token = None
access_token_expiry = None
secret_client = None
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
    global access_token, url, headers, secret_client, access_token_expiry, refresh_token
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Executing Python timer trigger function.')

    pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
    match = re.match(pattern, str(logAnalyticsUri))
    if not match:
        logging.info(f"Invalid url : {logAnalyticsUri}")
        raise Exception("Lookout: Invalid Log Analytics Uri.")
    try:
        logging.debug("Initializing Azure credentials and secret client.")
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=f"https://{key_vault_name}.vault.azure.net", credential=credential)
        secret_name = "environment-endpoint-url"
        url = secret_client.get_secret(secret_name).value
        logging.debug(f"Fetched environment endpoint URL: {url}")

        secret_name = "access-token"
        headers["authtoken"] = access_token = secret_client.get_secret(secret_name).value
        logging.debug("Fetched access token.")

        access_token_expiry = int(os.environ.get("RefreshTokenExpiry", "-1"))
        secret_name = "refresh-token"
        try:
            refresh_token = secret_client.get_secret(secret_name).value
            logging.debug("Fetched refresh token.")
        except Exception as e:
            logging.error(f"Failed to fetch refresh token: {e}")
            refresh_token = None
            raise
        headers["authtoken"] = get_access_token()
        logging.debug("Set authorization token in headers.")

        companyId_url = f"{url}/v2/WhoAmI"
        logging.debug(f"Fetching company ID from URL: {companyId_url}")

        company_response = requests.get(companyId_url, headers=headers)
        if company_response.status_code == 200:
            company_data_json = company_response.json()
            logging.info(f"Company Response: {company_data_json}")
            company_data = company_data_json.get("company", {})
            companyId = company_data.get("id")
            logging.debug(f"Fetched company ID: {companyId}")

            audit_url = f"{url}/V4/Company/{companyId}/SecurityPartners/Register/6"
            logging.debug(f"Sending audit log request to URL: {audit_url}")

            audit_response = requests.put(audit_url, headers=headers)
            if audit_response.status_code == 200:
                logging.info(f"Audit Log request sent successfully. Response: {audit_response.json()}")
            else:
                logging.error(f"Failed to send Audit Log request. Status code: {audit_response.status_code}")
        else:
            logging.error(f"Failed to get Company ID. Status code: {company_response.status_code}")

        ustring = "/events?level=10&showInfo=false&showMinor=false&showMajor=true&showCritical=true&showAnomalous=true"
        f_url = url + ustring
        logging.debug(f"Constructed events URL: {f_url}")

        current_date = datetime.now(timezone.utc)
        to_time = int(current_date.timestamp())
        fromtime = read_blob(cs, container_name, blob_name)
        logging.debug(f"Read from time from blob: {fromtime}")

        if fromtime is None:
            fromtime = int((current_date - timedelta(days=backfill_days)).timestamp())
            logging.info(f"From Time: [{fromtime}], since the time read from blob is None.")
        else:
            fromtime_dt = datetime.fromtimestamp(fromtime, tz=timezone.utc)
            time_diff = current_date - fromtime_dt
            if time_diff > timedelta(days=backfill_days):
                updatedfromtime = int((current_date - timedelta(days=backfill_days)).timestamp())
                logging.info(f"From Time: [{updatedfromtime}], since the time read from blob: [{fromtime}] is older than {backfill_days} days.")
                fromtime = updatedfromtime
            elif time_diff < timedelta(minutes=5):
                updatedfromtime = int((current_date - timedelta(minutes=5)).timestamp())
                logging.info(f"From Time: [{updatedfromtime}], since the time read from blob: [{fromtime}] is less than 5 minutes.")
                fromtime = updatedfromtime

        max_fetch = 1000
        headers["pagingInfo"] = f"0,{max_fetch}"
        logging.debug(f"Set paging info in headers: {headers['pagingInfo']}")

        logging.info(f"Starts at: [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}]")
        event_endpoint = f"{f_url}&fromTime={fromtime}&toTime={to_time}"
        logging.debug(f"Event endpoint: {event_endpoint}")

        response = requests.get(event_endpoint, headers=headers)
        logging.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            events = response.json()
            logging.info("Events Data count : {}".format(len(events.get("commservEvents",[]))))
            data = events.get("commservEvents")
            data = [event for event in data if
                    event.get("eventCodeString") in "7:211|7:212|7:293|7:269|14:337|14:338|69:59|7:333|69:60|35:5575"]
            post_data = []
            if data:
                for event in data:
                    try:
                        temp = get_incident_details(event["description"])
                        if temp:
                            post_data.append(temp)
                    except Exception as e:
                        logging.error(f"Error while processing event: {e}")
                logging.info("Trying Post Data")
                gen_chunks(post_data)
                logging.info("Job Succeeded")
                print("***Job Succeeded*****")
                logging.info("Function App Executed")
            else:
                print("No new events found.")
            upload_timestamp_blob(cs, container_name, blob_name, to_time + 1)
        else:
            logging.error(f"Failed to get events. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"HTTP request error: {e}")
        raise


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


def is_access_token_expired_or_is_empty(expiry_time: str) -> bool:
    if expiry_time is None or expiry_time == "" or access_token_expiry ==-1:
        return True
    current_time = datetime.now(timezone.utc).timestamp()
    if int(expiry_time) <= current_time:
        return True
    return False


def get_current_sp() -> str:
    global url, headers, secret_client
    try:
        commserv_url = f"{url}/CommServ"
        response = requests.get(commserv_url, headers=headers)
        if response.status_code == 200:
            commserv_data = response.json()
            if "errorCode" in commserv_data:
                error_code = commserv_data["errorCode"]
                error_message = commserv_data.get("errorMessage")
                if error_message is not None and len(error_message) > 0 and error_code is not None and error_code != 0: 
                    logging.error(f"Error getting current service point: {error_code} - {error_message}")
                    raise Exception(f"Error getting current service point: {error_code} - {error_message}")
            return commserv_data.get("currentSPVersion")
    except Exception as e:
        logging.error(f"Error getting current service point: {e}")
        raise e


def get_access_token() -> str:
    global access_token_expiry, access_token, refresh_token
    try:
        spStr = get_current_sp()
        if spStr is not None and int(spStr) > 0:
            sp = int(spStr)
            if sp<38:
                return access_token    
            if access_token is None or access_token == "":
                raise Exception("Access token is None or empty")
            elif refresh_token is None or refresh_token == "":
                logging.error("Refresh token is None or empty, creating new access token, and refresh token")
                access_token = create_access_token()
            elif is_access_token_expired_or_is_empty(access_token_expiry):
                logging.error("Access token is expired or empty, refreshing access token")
                access_token = refresh_access_token()
            return access_token
        else:
            logging.error("Couldnt get service pack details")
            raise Exception("Couldnt get service pack details")
    except Exception as e:
        logging.error(f"Error getting refresh token: {e}")
        raise


def create_access_token() -> str:
    global access_token, url, headers, refresh_token, access_token_expiry, secret_client
    try:
        renew_token_url = f"{url}/V4/AccessToken"
        logging.error(f"Create Token URL: {renew_token_url}")
        token_name = f"{os.environ.get('WEBSITE_HOSTNAME')}-token"
        renewable_until = datetime.now(timezone.utc).timestamp() + (365*24*60*60)
        token_body = {
            "renewableUntilTimestamp": renewable_until,
            "tokenName": token_name
        }
        response = requests.post(renew_token_url, headers=headers, json=token_body)
                
        if response.status_code == 200:
            response_data = response.json()
            if "error" in response_data:
                error_code = response_data["error"]["errorCode"]
                error_message = response_data["error"]["errorMessage"]
                if error_message is not None and len(error_message) > 0 and error_code is not None and error_code != 0: 
                    logging.error(f"Error creating access token: {error_code} - {error_message}")
                    raise Exception(f"Error creating access token: {error_code} - {error_message}")
            token_data = response_data.get("tokenInfo")
            access_token = token_data.get("accessToken")
            refresh_token = token_data.get("refreshToken")
            access_token_expiry = token_data.get("renewableUntilTimestamp")
            secret_client.set_secret("access-token", access_token)
            secret_client.set_secret("refresh-token", refresh_token)
            os.environ["RefreshTokenExpiry"] = str(access_token_expiry)
            return access_token
        else:
            logging.error(f"Failed to create access token with status code: {response.status_code}")
            raise Exception(f"Failed to create access token with status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error creating access token: {e}")
        raise e


def refresh_access_token() -> str:
    global access_token, url, headers, refresh_token, access_token_expiry, secret_client
    try:
        renew_token_url = f"{url}/V4/AccessToken/Renew"
        token_body = {
            "accessToken": access_token,
            "refreshToken": refresh_token
        }
        response = requests.post(renew_token_url, headers=headers, json=token_body)
                
        if response.status_code == 200:
            response_data = response.json()
            if "error" in response_data:
                error_code = response_data["error"]["errorCode"]
                error_message = response_data["error"]["errorMessage"]
                if error_message is not None and len(error_message) > 0:
                    logging.error(f"Error renewing access token: {error_code} - {error_message}")
                    raise Exception(f"Error renewing access token: {error_code} - {error_message}")
            access_token = response_data.get("accessToken")
            access_token_expiry = response_data.get("renewableUntilTimestamp")
            secret_client.set_secret("access-token", access_token)
            os.environ["RefreshTokenExpiry"] = str(access_token_expiry)
            return access_token
        else:
            logging.error(f"Failed to renew access token with status code: {response.status_code}")
            raise Exception(f"Failed to renew access token with status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error renewing access token: {e}")
        raise e

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
    job_details_body["advOptions"] = {
        "advConfig": {"browseAdvancedConfigBrowseByJob": {"jobId": int(job_id)}}
    }
    f_url = url + "/DoBrowse"
    response = requests.post(f_url, headers=headers, json=job_details_body)
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
    f_url = url + "/Subclient/" + str(subclient_id)
    resp = requests.get(f_url, headers=headers).json()
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
    f_url = f"{url}/Job/{job_id}"
    response = requests.get(f_url, headers=headers)
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
    f_url = f"{url}/Client/byName(clientName='{client_name}')"
    response = requests.get(f_url, headers=headers).json()
    user_id = response.get('clientProperties', [{}])[0].get('clientProps', {}).get('securityAssociations', {}).get('associations', [{}])[0].get('userOrGroup', [{}])[0].get('userId', None)
    user_name = response.get('clientProperties', [{}])[0].get('clientProps', {}).get('securityAssociations', {}).get('associations', [{}])[0].get('userOrGroup', [{}])[0].get('userName', None)
    return user_id, user_name


def get_incident_details(message: str) -> dict | None:
    """
    Function to get incident details from the alert description
    
    Args:
        message (str): The alert message
        
    Returns:
        dict | None: Incident details or None if not found
    """
    try:
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
            "job_start_time": datetime.fromtimestamp(job_start_time, tz=timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "job_end_time": datetime.fromtimestamp(job_end_time, tz=timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "job_id": job_id,
            "external_link": extract_from_regex(
                message, "", "href='(.*?)'", 'href="(.*?)"'
            ),
            "description": description,
        }
        return details
    except Exception as e:
        logging.error(f"An error occurred : {e}")
        return None


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
    rfc1123date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
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
        logging.info("Chunk was processed {} events with status : {}".format(chunk_count, response.content))
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
        
        if not container_client.exists():
            container_client.create_container()

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