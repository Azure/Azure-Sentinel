"""
init.py

This module provides a set of functions for communicating with the Luminar
API. The main purpose of these functions is
to retrieve and process security indicators and leaked credentials from
Luminar, transform them into a compatible format
, and save them into Azure Sentinel.

Main components:

LuminarManager: This class manages interactions with the Luminar API. It is
responsible for requesting and refreshing
access tokens, as well as managing the connection status.

process_malware, enrich_malware_items, enrich_incident_items: These functions
process malware and incident items and
create enriched data for each.

create_data, get_static_data: These functions transform raw indicators into a
format compatible with Azure Sentinel.

luminar_api_fetch: This function fetches data from the Luminar API, processes
the fetched items, and manages
relationships between items.

main: This function handles Luminar API requests. It initializes the Luminar
manager, requests and refreshes access
tokens, manages Luminar API calls, and handles pagination to ensure all pages
of data are retrieved. A timer trigger
allows it to run at specified intervals.

This module is designed for use as part of an Azure Function App and requires
certain environment variables to be set.
"""

import re
import requests
from ipaddress import ip_network
from os import environ
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union
import logging
import azure.functions as func
from .state_manager import StateManager

tenant_id = environ.get("TenantID")
client_id = environ.get("ApplicationID")
client_secret = environ.get("ClientSecret")
limit =  environ.get("Limit", 10)
luminar_client_id = environ.get("LuminarAPIClientID")
luminar_client_secret = environ.get("LuminarAPIClientSecret")
luminar_account_id = environ.get("LuminarAPIAccountID")
state = StateManager(environ.get("AzureWebJobsStorage"))
session = requests.Session()


TIMEOUT = 60.0
# There's a limit of 100 tiIndicators per request.
MAX_TI_INDICATORS_PER_REQUEST = 100
ENDPOINT = (
    "https://graph.microsoft.com/beta/security/tiIndicators/submitTiIndicators"
)
LUMINAR_BASE_URL = "https://demo.cyberluminar.com/"
SCOPE = "https://graph.microsoft.com/.default"


TOKEN_ENDPOINT = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
STIX_PARSER = re.compile(
    r"([\w-]+?):(\w.+?) (?:[!><]?=|IN|MATCHES|LIKE) '(.*?)' *[" r"OR|AND|FOLLOWEDBY]?"
)
IOC_MAPPING = {
    "file:hashes.'SHA-1'": "SHA1",
    "file:hashes.MD5": "MD5",
    "file:hashes.'SHA-256'": "SHA256",
    "file:hashes.'SHA-512'": "SHA512",
    "ipv4-addr": "IP",
    "file:name": "File_Extension",
    "file:size": "File_Size",
    "url": "URL",
    "email-addr": "EMAIL",
    "domain-name": "DOMAIN",
    "ipv6-addr": "IP",
    "mac-addr": "MAC",
    "directory": "DIR",
    "mutex": "MUTEX",
    "windows-registry-key": "WINDOWS_REGISTRY_KEY",
}

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "accept": "application/json",
}
PAYLOAD = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": SCOPE,
}


def get_last_saved_timestamp(date_format="%Y-%m-%d %H:%M:%S"):
    """
    This function retrieves the last saved timestamp from the state. If no
    timestamp is found, it returns 0.

    Parameters:
    date_format (str): The format in which the date and time are represented.
    Default is '%Y-%m-%d %H:%M:%S' which
    represents YYYY-MM-DD HH:MM:SS format.

    Returns:
    int: The timestamp of the last successful run of this function as a Unix
    timestamp. If the function is being run for
    the first time, it returns 0.
    """
    last_run_date_time = state.get()
    logging.debug("last saved time stamp is %s", last_run_date_time)

    return (
        int(datetime.strptime(last_run_date_time, date_format).timestamp())
        if last_run_date_time
        else 0
    )


def save_checkpoint(timestamp: datetime, date_format: str = "%Y-%m-%d %H:%M:%S") -> None:
    """
    This function saves the current UTC timestamp to the state.

    Parameters:
    date_format (str): The format in which the date and time are represented.
    Default is '%Y-%m-%d %H:%M:%S'
                       which represents the format as YYYY-MM-DD HH:MM:SS.

    Returns:
    None
    """
    current_date_time = timestamp
    state.post(format(current_date_time, date_format))


def get_access_token() -> Optional[str]:
    """
    This function fetches the access token from Sentinel.
    Returns:
    str: The access token if the request was successful, None otherwise.
    """
    try:
        response = session.post(
            TOKEN_ENDPOINT, data=PAYLOAD, headers=HEADERS, timeout=TIMEOUT
        )
        response.raise_for_status()  # check if we got a HTTP error
        return response.json().get("access_token")
    except requests.HTTPError as http_err:
        logging.error("HTTP error occurred: %s", http_err)
        return None


def save_sentinel_data(data: dict) -> None:
    """
    This function sends the data to Sentinel using an access token.
    Parameters:
    data (dict): The data to be sent to Sentinel.
    Returns:
    None
    """
    access_token = get_access_token()
    if not access_token:
        logging.error("Unable to retrieve access token")
        return

    headers = {"Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json", "accept": "application/json"}

    try:
        response = session.post(ENDPOINT, headers=headers, json=data, timeout=TIMEOUT)
        response.raise_for_status()  # check if we got a HTTP error
    except requests.HTTPError as http_err:
        logging.error("HTTP error occurred: %s", http_err)


def get_static_data(
    indicator: Dict[str, Union[str, int, list, Dict[str, Any]]], value: str
) -> Dict[str, Union[str, int, list]]:
    """
    Generate static data dictionary based on the input indicator and value.

    Parameters:
    indicator (Dict[str, Union[str, int, list, Dict[str, Any]]]): A
    dictionary containing
    indicator information.
    value (str): A string value indicating the type of the indicator.

    Returns:
    Dict[str, Union[str, int, list]]: A dictionary of static data.
    """
    return {
        "action": "alert" if value == "INCIDENT" else "block",
        "description": indicator["name"],
        "expirationDateTime": indicator.get("valid_until")
        if indicator.get("valid_until")
        else (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
        "externalId": indicator["id"],
        "threatType": "Phishing" if value == "INCIDENT" else "Malware",
        "killChain": [],
        "severity": 3
        if value == "INCIDENT"
        else (4 if "Known Malicious IPs" in indicator["name"] else 3),
        "tags": ["Luminar Leaked Credentials"]
        if value == "INCIDENT"
        else ["Luminar IOCs"],
        "targetProduct": "Azure Sentinel",
        "tlpLevel": "green",
        "malwareFamilyNames": indicator.get("malware_details", {}).get(
            "malwareTypes", []
        ),
        "confidence": 80
        if value == "INCIDENT"
        else (90 if "Known Malicious IPs" in indicator["name"] else 80),
        "SourceSystem": "Cognyte Luminar",
    }


def get_network_address(value: str) -> str:
    """
    Get the network address from a given CIDR value.

    Args:
        value: A string representing a CIDR notation (e.g., '192.168.0.0/24').

    Returns:
        The network address as a string.

    If the given value is not a valid CIDR notation, the original value is
    returned.

    Example:
        >>> get_network_address('192.168.0.0/24')
        '192.168.0.0'
        >>> get_network_address('192.168.0.1')
        '192.168.0.1'
    """
    try:
        network = ip_network(value)
        return str(network.network_address)
    except ValueError:
        return value  # Return the original value if it's not a CIDR


def create_data(
    indicator: Dict[str, Union[str, int, list, Dict[str, Any]]], indicator_type: str
) -> Optional[Dict[str, Union[str, int, list]]]:
    """
    Create a data dictionary based on the given indicator and its type.

    Parameters:
    indicator (Dict[str, Union[str, int, list, Dict[str, Any]]]): A
    dictionary containing
    indicator information.
    indicator_type (str): A string indicating the type of the indicator.

    Returns:
    Dict[str, Union[str, int, list]]: A dictionary of data corresponding to
    the given
    indicator and its type.

    Raises:
    Exception: Any exception thrown during the processing of the data is
    caught and logged.
    """
    try:
        handlers: Dict[str, Callable[[], Dict[str, str]]] = {
            "URL": lambda: {"url": indicator["indicator_value"]},
            "IP": lambda: {
                "networkIPv4": get_network_address(indicator["indicator_value"])
            },
            "MD5": lambda: {
                "fileHashValue": indicator["indicator_value"],
                "fileHashType": "md5",
            },
            "SHA1": lambda: {
                "fileHashValue": indicator["indicator_value"],
                "fileHashType": "sha1",
            },
            "SHA256": lambda: {
                "fileHashValue": indicator["indicator_value"],
                "fileHashType": "sha256",
            },
            "SHA512": lambda: {
                "fileHashValue": indicator["indicator_value"],
                "fileHashType": "sha512",
            },
            "EMAIL": lambda: {"emailSenderAddress": indicator["indicator_value"]},
            "INCIDENT": lambda: {"emailSenderAddress": indicator["account_login"]},
            "DOMAIN": lambda: {"domainName": indicator["indicator_value"]},
            "DIR": lambda: {"filePath": indicator["indicator_value"]},
            "File_Size": lambda: {"fileSize": indicator["indicator_value"]},
            "File_Extension": lambda: {"filePath": indicator["indicator_value"]},
            "MUTEX": lambda: {"fileMutexName": indicator["indicator_value"]},
        }

        handler = handlers.get(indicator_type)
        if not handler:
            logging.warning("No handler for indicator type %s", indicator_type)
            return {}

        data = get_static_data(indicator, indicator_type)
        data.update(handler())
        return data

    except KeyError as err:
        logging.error("Missing key in indicator: %s", err)
    except Exception as err:
        logging.error(
            "Unexpected error occurred while creating azure sentinel IOC "
            "Format: %s: %s",
            type(err).__name__,
            err,
        )

    return {}


def chunks(data: List[Any], size: int) -> Generator[List[Any], None, None]:
    """
    Splits the provided data into chunks of the specified size.
    This is a generator function that yields chunks of data as lists.

    Parameters:
    data (List[Any]): The data to be chunked.
    size (int): The size of each chunk.

    Yields:
    List[Any]: A chunk of the original data.
    """
    for i in range(0, len(data), size):
        yield data[i : i + size]


def luminar_api_fetch(all_objects: List[Dict[str, Any]]) -> None:
    """
    Fetches data from Luminar API, identifies relationships between different
    objects,
    and enriches malware and incident items with additional data based on
    these relationships.

    Parameters:
    all_objects: A list of dictionary objects fetched from the Luminar API.
    Each dictionary represents
                 an object and contains its various attributes.

    Returns:
    None
    """
    try:
        luminar_expiration_iocs(all_objects)
        item_by_id, relationships = process_objects(all_objects)
        enrich_items(item_by_id, relationships)
    except (ValueError, TypeError, KeyError) as err:
        logging.error("Error while fetching and processing data: %s", err)


def process_objects(
    all_objects: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], Dict[str, List[str]]]:
    """
    Processes all objects and establishes relationships.

    Parameters:
    all_objects: A list of dictionary objects fetched from the Luminar API.

    Returns:
    Tuple containing dictionary of items indexed by id and relationships
    dictionary.
    """
    item_by_id = {}
    relationships = {}

    for item in all_objects:
        item_by_id[item["id"]] = item
        if item.get("type") == "relationship":
            relationships.setdefault(item["target_ref"], []).append(item["source_ref"])

    return item_by_id, relationships


def enrich_items(
    item_by_id: Dict[str, Any], relationships: Dict[str, List[str]]
) -> None:
    """
    Enriches malware and incident items.

    Parameters:
    item_by_id: Dictionary of items indexed by id.
    relationships: Dictionary of relationships.

    Returns:
    None
    """
    for key, group in relationships.items():
        parent = item_by_id.get(key)
        if parent:
            children = [
                item_by_id.get(item_id) for item_id in group if item_by_id.get(item_id)
            ]
            if not children:
                continue
            if parent.get("type") == "malware":
                enrich_malware_items(parent, children)
            elif parent.get("type") == "incident":
                enrich_incident_items(parent, children)


def luminar_expiration_iocs(all_objects: List[Dict[str, Any]]) -> None:
    """
    Enriches and processes unique Indicators of Compromise (IoCs) that have
    an expiration date
    that is greater than or equal to the current date.

    Parameters:
    all_objects: A list containing dictionaries of various objects such as
                 malware, incidents, indicators etc.

    Returns:
    None
    """
    iocs = [
        x
        for x in all_objects
        if x.get("type") == "indicator"
        and x.get("valid_until")
        and datetime.strptime((x.get("valid_until"))[:19], "%Y-%m-%dT%H:%M:%S")
        >= datetime.today()
    ]
    enrich_malware_items({}, iocs)


def field_mapping(ind: str, value: str) -> dict:
    """
    Assigning associated indicator type and indicator value
    :param ind: {str} indicator type
    :param value: {str} indicator value
    :return: {dict}
    """
    return {"indicator_type": ind, "indicator_value": value}


IndicatorTypes = {
    "file:hashes.'SHA-1'": field_mapping,
    "file:hashes.MD5": field_mapping,
    "file:hashes.'SHA-256'": field_mapping,
    "file:hashes.'SHA-512'": field_mapping,
    "ipv4-addr": field_mapping,
    "file:name": field_mapping,
    "file:size": field_mapping,
    "url": field_mapping,
    "email-addr": field_mapping,
    "domain-name": field_mapping,
    "ipv6-addr": field_mapping,
    "mac-addr": field_mapping,
    "directory": field_mapping,
    "mutex": field_mapping,
    "windows-registry-key": field_mapping,
}


def process_malware(children: Dict[str, Any], parent: Dict[str, Any]) -> None:
    """
    Process a malware item and enrich it with parent item's data.

    Parameters:
    children (Dict[str, Any]): A dictionary representing a child object.
    parent (Dict[str, Any]): A dictionary representing the parent object.

    Returns:
    None
    """
    pattern = children.get("pattern")
    if isinstance(pattern, str):
        try:
            matches = STIX_PARSER.findall(pattern)
        except TypeError as err:
            logging.error("Error on pattern: %s and %s", pattern, err)
            return
        for match in matches:
            stix_type, stix_property, value = match
            indicator_type = (
                f"{stix_type}:{stix_property}" if stix_type == "file" else stix_type
            )
            if indicator_type and IOC_MAPPING.get(indicator_type):
                mapping_method = IndicatorTypes.get(indicator_type)
                ioc = mapping_method(IOC_MAPPING[indicator_type], value)
                children.update(
                    {
                        "malware_details": parent,
                        "indicator_type": ioc["indicator_type"],
                        "indicator_value": ioc["indicator_value"],
                    }
                )
                parent["name"] = children["name"]
    else:
        logging.error(
            "Unexpected pattern type: %s in children: %s", type(pattern), children
        )


def enrich_malware_items(
    parent: Dict[str, Any], childrens: List[Dict[str, Any]]
) -> None:
    """
    Enrich malware items with the data from the parent object.

    Parameters:
    parent (Dict[str, Any]): A dictionary representing the parent object.
    childrens (List[Dict[str, Any]]): A list of dictionaries each
    representing a child object.

    Returns:
    None
    """
    batch_data = []
    for children in childrens:
        process_malware(children, parent)
        try:
            if "indicator_type" not in children:
                continue
            chunk_data = create_data(children, children["indicator_type"])
            if not chunk_data:
                continue
            batch_data.append(chunk_data)
        except (KeyError, TypeError) as err:
            logging.error("Error while creating data: %s", err)
    save_batch_data(batch_data)


def enrich_incident_items(
    parent: Dict[str, Any], childrens: List[Dict[str, Any]]
) -> None:
    """
    Enrich incident items with the data from the parent object.

    Parameters:
    parent (Dict[str, Any]): A dictionary representing the parent object.
    childrens (List[Dict[str, Any]]): A list of dictionaries each
    representing a child object.

    Returns:
    None
    """
    batch_data = []
    for children in childrens:
        children.update(parent)
        try:
            chunk_data = create_data(children, "INCIDENT")
            if not chunk_data:
                continue
            batch_data.append(chunk_data)
        except (KeyError, TypeError) as err:
            logging.error("Error while creating data: %s", err)
    save_batch_data(batch_data)


def save_batch_data(batch_data: List[Dict[str, Any]]) -> None:
    """
    Save batch data in chunks.

    Parameters:
    batch_data (List[Dict[str, Any]]): A list of dictionaries each
    representing an item of batch data.

    Returns:
    None
    """
    for chunk in chunks(batch_data, MAX_TI_INDICATORS_PER_REQUEST):
        try:
            save_sentinel_data({"value": chunk})
        except Exception as err:
            logging.error("Error while saving sentinel data: %s", err)


class LuminarManager:
    """
    Class to manage Luminar API interactions.
    """

    STATUS_MESSAGES = {
        400: "Bad request. The server could not understand the request due to "
        "invalid syntax.",
        401: "Unauthorized. The client must authenticate itself to get the "
        "requested response.",
        403: "Forbidden. The client does not have access rights to the " "content.",
        404: "Not Found. The server can not find the requested resource.",
        408: "Request Timeout. The server would like to shut down this unused "
        "connection.",
        429: "Too Many Requests. The user has sent too many requests in a "
        "given amount of time.",
        500: "Internal Server Error. The server has encountered a situation "
        "it doesn't know how to handle.",
        502: "Bad Gateway. The server was acting as a gateway or proxy and "
        "received an invalid response from the "
        "upstream server.",
        503: "Service Unavailable. The server is not ready to handle the " "request.",
    }

    def __init__(
        self,
        cognyte_client_id: str,
        cognyte_client_secret: str,
        cognyte_account_id: str,
        cognyte_base_url: str,
    ) -> None:
        self.base_url = cognyte_base_url
        self.account_id = cognyte_account_id
        self.client_id = cognyte_client_id
        self.client_secret = cognyte_client_secret
        self.payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        self.req_headers = HEADERS

    def access_token(self) -> Tuple[Union[bool, str], str]:
        """
        Make a request to the Luminar API.

        :return: Tuple[Union[bool, str], str]
            The access token (if successful) or False (if unsuccessful),
            and a message indicating the status of the
            request.
        """
        req_url = f"{self.base_url}/externalApi/realm/{self.account_id}/token"
        response = None
        try:
            response = requests.post(
                req_url, headers=self.req_headers, data=self.payload, timeout=TIMEOUT
            )
            response.raise_for_status()
            return (
                response.json().get("access_token", False),
                "Luminar API Connected successfully",
            )
        except requests.HTTPError:
            if response is not None:
                return False, self.STATUS_MESSAGES.get(
                    response.status_code, "An error occurred"
                )
            return False, "An error occurred while making HTTP request"
        except Exception as err:
            return False, f"Failed to connect to Luminar API... Error is {err}"


def main(mytimer: func.TimerRequest) -> None:
    """
    Main function to handle Luminar API requests.

    This function initializes the Luminar manager, requests and refreshes
    access tokens, handles Luminar API calls,
    and handles pagination to ensure all pages of data are retrieved. It uses
    a timer trigger to run at specified
    intervals.

    :param mytimer: func.TimerRequest, timer for triggering the function at
    specified intervals.

    Note:
    - This function will log an error message and exit if an access token
    cannot be retrieved or refreshed.
    - If no more indicators are left to ingest, the function will log an
    informational message and stop iterating over
    the pages.
    - The function will save a timestamp after each run.
    """

    if mytimer.past_due:
        logging.info("The timer is past due!")
        return
    luminar_manager = LuminarManager(
        luminar_client_id, luminar_client_secret, luminar_account_id, LUMINAR_BASE_URL
    )

    # Define the params with the timestamp
    params = {"limit": int(limit), "offset": 0, "timestamp": get_last_saved_timestamp()}

    
    # params = {"limit": 100, "offset": 0}

    has_more_data = True

    try:
        # Getting access token
        access_token, message = luminar_manager.access_token()

        if not access_token:
            logging.error("Failed to get access token: %s", message)
            return

        headers = {"Authorization": f"Bearer {access_token}"}

        while has_more_data:
            logging.info("Inside while loop with params: %s", params)

            response = requests.get(
                LUMINAR_BASE_URL + "/externalApi/stix",
                params=params,
                headers=headers,
                timeout=TIMEOUT,
            )
            if (
                response.status_code == 401
            ):  # Assuming 401 is the status code for an expired token
                # If the token has expired, refresh it and continue the loop
                access_token, _ = luminar_manager.access_token()
                if not access_token:
                    logging.error("Failed to refresh access token")
                    break
                headers = {"Authorization": f"Bearer {access_token}"}
                continue
            # Getting Luminar data page wise
            params["offset"] += params["limit"]

            response_json = response.json()
            all_objects = response_json.get("objects", [])
            logging.info("len(all_objects): %s", len(all_objects))

            if not all_objects or len(all_objects) == 1:
                logging.info("No more indicators to ingest.")
                has_more_data = False
            else:
                luminar_api_fetch(all_objects)

    except Exception as err:
        logging.error("Error occurred during API call: %s", err)
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    logging.info("Python timer trigger function ran at %s", utc_timestamp)
    save_checkpoint(datetime.utcnow().replace(second=0, microsecond=0))
