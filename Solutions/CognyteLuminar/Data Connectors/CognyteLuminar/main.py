"""
main.py
"""

import logging
import re
from datetime import datetime, timedelta, timezone
from ipaddress import ip_network
from os import environ
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import azure.functions as func  # type: ignore
import requests  # type: ignore

from .state_manager import StateManager

tenant_id = environ.get("TenantID", "")
client_id = environ.get("ApplicationID", "")
client_secret = environ.get("ClientSecret", "")
luminar_client_id = environ.get("LuminarAPIClientID", "")
luminar_client_secret = environ.get("LuminarAPIClientSecret", "")
luminar_account_id = environ.get("LuminarAPIAccountID", "")
luminar_initial_fetch_date = environ.get("LuminarInitialFetchDate", "")
state = StateManager(environ.get("AzureWebJobsStorage", ""))
session = requests.Session()

BATCH_DATA = []
TIMEOUT = 60.0
# There's a limit of 100 tiIndicators per request.
MAX_TI_INDICATORS_PER_REQUEST = 100
ENDPOINT = "https://graph.microsoft.com/beta/security/tiIndicators/submitTiIndicators"
LUMINAR_BASE_URL = "https://www.cyberluminar.com/"
SCOPE = "https://graph.microsoft.com/.default"


TOKEN_ENDPOINT = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
# STIX_PARSER = re.compile(
#     r"([\w-]+?):(\w.+?) (?:[!><]?=|IN|MATCHES|LIKE) '(.*?)' *[" r"OR|AND|FOLLOWEDBY]?"
# )
STIX_PARSER = re.compile(
    r"([\w-]+?):(\w.+?) (?:[!><]?=|IN|MATCHES|LIKE) '(.*?)' *[" + r"OR|AND|FOLLOWEDBY]?"
)
LUMINAR_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
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


def is_valid_date(date_str: str) -> bool:
    """
    Checks if a given string is a valid date in the format 'YYYY-MM-DD'.

    Args:
        date_str (str): The date string to validate.

    Returns:
        bool: True if the string is a valid date, False otherwise.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_last_saved_timestamp() -> Optional[str]:
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

    return last_run_date_time or ""


def save_checkpoint(current_date_time) -> None:
    """
    This function saves the current UTC timestamp to the state.

    Parameters:
    date_format (str): The format in which the date and time are represented.
    Default is 'YYYY-MM-DDTHH:MM:SS.mmmmmmZ'.

    Returns:
    None
    """
    state.post(current_date_time)


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

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    try:
        logging.info("Ingesting data into Sentinel Threat Intelligence...")
        response = session.post(ENDPOINT, headers=headers, json=data, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        logging.error("HTTP error occurred: %s", http_err)


def get_static_data(
    indicator: Dict[str, Union[str, int, list, Dict[str, Any]]], value: str
) -> Dict[str, Union[str, int, list]]:
    """
    Generate static data dictionary based on the input indicator and value.

    Parameters:
    indicator (Dict[str, Union[str, int, list, Dict[str, Any]]]): A
    dictionary containing indicator information.
    value (str): A string value indicating the type of the indicator.

    Returns:
    Dict[str, Union[str, int, list]]: A dictionary of static data.
    """
    malware_details = indicator.get("malware_details", {})
    return {
        "action": "alert" if value == "INCIDENT" else "block",
        "description": str(indicator.get("name", "")),
        "expirationDateTime": (
            str(indicator.get("valid_until"))
            if indicator.get("valid_until") is not None
            else (datetime.now(timezone.utc) + timedelta(days=30)).isoformat() + "Z"
        ),
        "externalId": str(indicator.get("id", "")),
        "threatType": "Phishing" if value == "INCIDENT" else "Malware",
        "killChain": [],
        "severity": (
            3
            if value == "INCIDENT"
            else (4 if "Known Malicious IPs" in str(indicator.get("name", "")) else 3)
        ),
        "tags": (
            ["Luminar Leaked Credentials"] if value == "INCIDENT" else ["Luminar IOCs"]
        ),
        "targetProduct": "Azure Sentinel",
        "tlpLevel": "green",
        "malwareFamilyNames": (
            malware_details.get("malware_types", [])
            if isinstance(malware_details, dict)
            else []
        ),
        "confidence": (
            80
            if value == "INCIDENT"
            else (90 if "Known Malicious IPs" in str(indicator.get("name", "")) else 80)
        ),
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
        # Return the original value if it's not a CIDR
        return value


def create_data(
    indicator: Dict[str, Union[str, int, List[Any], Dict[str, Any]]],
    indicator_type: str,
) -> Optional[Dict[str, Union[str, int, List[Any]]]]:
    """
    Create a data dictionary based on the given indicator and its type.

    Parameters:
    indicator (Dict[str, Union[str, int, List[Any], Dict[str, Any]]]): A
    dictionary containing indicator information.
    indicator_type (str): A string indicating the type of the indicator.

    Returns:
    Optional[Dict[str, Union[str, int, List[Any]]]]: A dictionary of data
    corresponding to the given indicator and its type, or None if an error occurs.

    Raises:
    Exception: Any exception thrown during the processing of the data is
    caught and logged.
    """
    try:
        handlers: Dict[str, Callable[[], Dict[str, Union[str, int, List[Any]]]]] = {
            "URL": lambda: {"url": str(indicator.get("indicator_value", ""))},
            "IP": lambda: {
                "networkIPv4": get_network_address(
                    str(indicator.get("indicator_value", ""))
                )
            },
            "MD5": lambda: {
                "fileHashValue": str(indicator.get("indicator_value", "")),
                "fileHashType": "md5",
            },
            "SHA1": lambda: {
                "fileHashValue": str(indicator.get("indicator_value", "")),
                "fileHashType": "sha1",
            },
            "SHA256": lambda: {
                "fileHashValue": str(indicator.get("indicator_value", "")),
                "fileHashType": "sha256",
            },
            "SHA512": lambda: {
                "fileHashValue": str(indicator.get("indicator_value", "")),
                "fileHashType": "sha512",
            },
            "EMAIL": lambda: {
                "emailSenderAddress": str(indicator.get("indicator_value", ""))
            },
            "INCIDENT": lambda: {
                "emailSenderAddress": str(indicator.get("account_login", ""))
            },
            "DOMAIN": lambda: {"domainName": str(indicator.get("indicator_value", ""))},
            "DIR": lambda: {"filePath": str(indicator.get("indicator_value", ""))},
            "File_Size": lambda: {
                "fileSize": str(indicator.get("indicator_value", ""))
            },
            "File_Extension": lambda: {
                "filePath": str(indicator.get("indicator_value", ""))
            },
            "MUTEX": lambda: {
                "fileMutexName": str(indicator.get("indicator_value", ""))
            },
        }

        handler = handlers.get(indicator_type)
        if handler is None:
            logging.warning("No handler for indicator type %s", indicator_type)
            return None

        data = get_static_data(indicator, indicator_type)
        data.update(handler())
        return data

    except KeyError as err:
        logging.error("Missing key in indicator: %s", err)
    except Exception as err:
        logging.error(
            "Unexpected error occurred while creating azure sentinel IOC Format: %s: %s",
            type(err).__name__,
            err,
        )

    return None


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
    all_objects: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Dict[str, List[str]]]:
    """
    Processes all objects and establishes relationships.

    Parameters:
    all_objects: A list of dictionary objects fetched from the Luminar API.

    Returns:
    Tuple containing dictionary of items indexed by id and relationships dictionary.
    """
    item_by_id: Dict[str, Any] = {}
    relationships: Dict[str, List[str]] = {}

    for item in all_objects:
        item_by_id[item["id"]] = item
        if item.get("type") == "relationship":
            relationships.setdefault(str(item["target_ref"]), []).append(
                str(item["source_ref"])
            )

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
                item
                for item_id in group
                if (item := item_by_id.get(item_id)) is not None
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
        and isinstance(x.get("valid_until"), str)
        and datetime.strptime(x["valid_until"][:19], "%Y-%m-%dT%H:%M:%S")
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

                if mapping_method is None:
                    raise ValueError(f"Invalid indicator type: {indicator_type}")

                # Ensure indicator_type exists in IOC_MAPPING before use
                ioc_mapping_value = IOC_MAPPING.get(indicator_type)

                if ioc_mapping_value is None:
                    raise ValueError(
                        f"Missing IOC mapping for indicator type: {indicator_type}"
                    )

                # Call the mapping function safely
                ioc = mapping_method(ioc_mapping_value, value)
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
    BATCH_DATA.extend(batch_data)


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
        if children.get("type") == "malware":
            continue
        children.update(parent)
        try:
            chunk_data = create_data(children, "INCIDENT")
            if not chunk_data:
                continue
            batch_data.append(chunk_data)
        except (KeyError, TypeError) as err:
            logging.error("Error while creating data: %s", err)
    BATCH_DATA.extend(batch_data)


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
            logging.error("Error while saving Sentinel data: %s", err)


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
            "scope": "externalAPI/stix.readonly",
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
        req_url = f"{self.base_url}/externalApi/v2/realm/{self.account_id}/token"
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

    def get_taxi_collections(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Fetches TAXII collections from the Cognyte Luminar API and maps collection
         aliases to their IDs.

        Args:
            headers (Dict[str, str]): HTTP headers, including authentication tokens.

        Returns:
            Dict[str, str]: A dictionary mapping collection aliases to their IDs.
        """
        taxii_collection_ids = {}
        try:
            req_url = f"{self.base_url}/externalApi/taxii/collections/"
            resp = requests.get(req_url, headers=headers, timeout=TIMEOUT)
            resp.raise_for_status()
            collections_data = resp.json().get("collections", [])

            logging.info("Cognyte Luminar collections: %s", collections_data)

            # Store collection alias and id mapping
            for collection in collections_data:
                taxii_collection_ids[collection.get("alias")] = collection.get("id")
        except Exception as e:
            logging.error("Error fetching collections: %s", e)

        return taxii_collection_ids

    def get_collection_objects(
        self, headers: Dict[str, str], collection: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Fetches objects from a TAXII collection, handling pagination and token expiration.

        Args:
            headers (Dict[str, str]): HTTP headers, including authentication tokens.
            collection (str): The TAXII collection ID.
            params (Dict[str, Any]): Query parameters for filtering results.

        Returns:
            List[Dict[str, Any]]: A list of objects retrieved from the collection.
        """

        parameters = params.copy()
        collection_objects = []

        while True:
            # Send a request to fetch objects from the collection
            resp = requests.get(
                f"{self.base_url}/externalApi/taxii/collections/{collection}/objects/",
                params=parameters,
                headers=headers,
                timeout=TIMEOUT,
            )
            if resp.status_code == 401:
                logging.info(
                    "Access token has expired, status_code=%s and response=%s,"
                    " Regenerating token...",
                    resp.status_code,
                    resp.text,
                )

                access_token, _ = self.access_token()
                headers = {"Authorization": f"Bearer {access_token}"}
                continue

            # Process the response when it is successful (status code 200)
            if resp.status_code == 200:
                response_json = resp.json()
                all_objects = response_json.get("objects", [])
                collection_objects.extend(all_objects)
                logging.info(
                    "Fetched objects from collection: %s", len(collection_objects)
                )

                # Check if there is a "next" page of objects and update the params
                if "next" in response_json:
                    parameters["next"] = response_json["next"]
                else:
                    break
            else:
                logging.info(
                    "Error occurred while fetching objects from collection %s:"
                    " status_code=%s and response=%s",
                    collection,
                    resp.status_code,
                    resp.text,
                )
                break

        logging.info("Fetched all objects from collection: %s", collection)

        return collection_objects


def check_created_date(obj_date: str, from_date: datetime) -> bool:
    """
    Validates whether the given object creation date is greater than or equal
    to the specified 'from_date'.

    :param obj_date: A string representing the creation date of the object in
                    ISO 8601 format ("%Y-%m-%dT%H:%M:%S.%fZ").
    :param from_date: A datetime object representing the threshold date.
    :return: True if obj_date is valid and greater than or equal to from_date,
            otherwise False.
    """
    try:
        return datetime.strptime(obj_date, LUMINAR_DATE_FORMAT) >= from_date
    except Exception as ex:
        logging.error("Invalid date format: %s; %s", obj_date, ex)
        return False


def get_timestamp(days=0):
    """
    Retrieves the current timestamp in UTC format with microsecond precision.

    This function fetches the current time in UTC, formats it into an ISO 8601 string
    with microsecond precision, and appends a 'Z' to indicate that the time is in UTC.

    Returns:
        str: The current timestamp in UTC with microsecond precision, formatted as
             'YYYY-MM-DDTHH:MM:SS.mmmmmmZ'.
    """
    if days:
        current_time = datetime.now(timezone.utc) + timedelta(days=days)
    else:
        current_time = datetime.now(timezone.utc)
    return (
        current_time.strftime("%Y-%m-%dT%H:%M:%S.") + f"{current_time.microsecond:06d}Z"
    )


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

    try:
        if not is_valid_date(luminar_initial_fetch_date):
            logging.error("Invalid initial fetch date. Format should be YYYY-MM-DD")
            return

        luminar_manager = LuminarManager(
            luminar_client_id,
            luminar_client_secret,
            luminar_account_id,
            LUMINAR_BASE_URL,
        )
        # Getting access token
        access_token, message = luminar_manager.access_token()

        if not access_token:
            logging.error("Failed to get access token: %s", message)
            return

        headers = {"Authorization": f"Bearer {access_token}"}

        taxii_collection = luminar_manager.get_taxi_collections(headers)
        if not taxii_collection:
            return

        params = {"limit": 9999}
        last_checkpoint = (
            get_last_saved_timestamp()
            or f"{luminar_initial_fetch_date}T00:00:00.000000Z"
        )

        logging.info("Getting records added after timestamp: %s", last_checkpoint)
        params["added_after"] = str(last_checkpoint)  # type: ignore

        next_checkpoint = get_timestamp()
        ioc_records = luminar_manager.get_collection_objects(
            headers, taxii_collection["iocs"], params
        )
        leaked_records = luminar_manager.get_collection_objects(
            headers, taxii_collection["leakedrecords"], params
        )

        logging.info("IOC records found: %s", len(ioc_records))
        logging.info("Leaked records found: %s", len(leaked_records))

        from_date = datetime.strptime(last_checkpoint, LUMINAR_DATE_FORMAT)

        ioc_and_leaked_records = ioc_records + leaked_records
        ioc_and_leaked_records = [
            record
            for record in ioc_and_leaked_records
            if not record.get("created")
            or check_created_date(record.get("created", ""), from_date)
        ]
        logging.info(
            "Filtered records based on created date: %s", len(ioc_and_leaked_records)
        )

        luminar_api_fetch(ioc_and_leaked_records)
        if BATCH_DATA:
            logging.info("Batching %s records", len(BATCH_DATA))
            save_batch_data(BATCH_DATA)

        save_checkpoint(next_checkpoint)
        logging.info("Checkpoint created for next run: %s", next_checkpoint)

    except Exception as err:
        logging.error("Error occurred during API call: %s", err)
