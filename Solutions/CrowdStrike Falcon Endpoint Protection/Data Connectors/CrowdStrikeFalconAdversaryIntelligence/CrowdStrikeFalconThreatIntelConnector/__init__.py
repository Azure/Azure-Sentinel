import requests
import json
from datetime import datetime, timezone, timedelta
import uuid
import os
import logging
import hashlib
import azure.functions as func
import sys

from .utils import (
    StateManager,
    CrowdStrikeTokenRetriever,
    AADTokenRetriever,
    UnauthorizedTokenException,
    CONFIDENCE_MAPPING,
    STIX_PATTERN_MAPPING,
    APIError,
)


CROWDSTRIKE_CLIENT_ID = os.environ.get("CROWDSTRIKE_CLIENT_ID")
CROWDSTRIKE_CLIENT_SECRET = os.environ.get("CROWDSTRIKE_CLIENT_SECRET")
CROWDSTRIKE_BASE_URL = os.environ.get("CROWDSTRIKE_BASE_URL")
CROWDSTRIKE_TOKEN_EXP = ""
WORKSPACE_ID = os.environ.get("WORKSPACE_ID")
TENANT_ID = os.environ.get("TENANT_ID")
INDICATORS = os.environ.get("INDICATORS")
LOOK_BACK_DAYS = int(os.environ.get("LOOK_BACK_DAYS", 1))
if LOOK_BACK_DAYS > 60:
    LOOK_BACK_DAYS = 60
AAD_CLIENT_ID = os.environ.get("AAD_CLIENT_ID")
AAD_CLIENT_SECRET = os.environ.get("AAD_CLIENT_SECRET")
FILE_STORAGE_CONNECTION_STRING = os.environ.get("FILE_STORAGE_CONNECTION_STRING")
INDICATOR_COUNT = 0
USER_AGENT = "microsoft-sentinel-ioc/1.0.0"

CrowdStrikeToken = CrowdStrikeTokenRetriever(
    crowdstrike_base_url=CROWDSTRIKE_BASE_URL,
    crowdstrike_client_id=CROWDSTRIKE_CLIENT_ID,
    crowdstrike_client_secret=CROWDSTRIKE_CLIENT_SECRET,
)
AADToken = AADTokenRetriever(
    aad_client_id=AAD_CLIENT_ID,
    aad_client_secret=AAD_CLIENT_SECRET,
    tenant_id=TENANT_ID,
)


CrowdStrike_State = StateManager(
    connection_string=FILE_STORAGE_CONNECTION_STRING,
    share_name="csiocstateshare",
    file_path="_marker",
)


def get_look_back_date():
    """
    returns the respective date according to the look back days specified
    """

    right_now = datetime.now(timezone.utc)
    look_back_date = (right_now - timedelta(days=int(LOOK_BACK_DAYS))).isoformat()

    return look_back_date


def parse_indicator_type_filter():
    """
    returns the indicator type query filter based on the indicators provided
    """

    split_indicators = INDICATORS.split(",")
    indicator_query_filter = "',type:'".join(split_indicators)
    indicator_query_filter = f"type:'{indicator_query_filter}'"

    return indicator_query_filter


def get_query_filter():
    """
    returns the query filter to be used to extract indicators of compromise from the crowdstrike api
    """

    indicator_type_filter = parse_indicator_type_filter()
    marker_filter = CrowdStrike_State.get()
    if marker_filter is None:
        look_back_date = get_look_back_date()
        query_filter = f"({indicator_type_filter})+(last_updated:>'{look_back_date}')"
    else:
        query_filter = f"({indicator_type_filter})+(_marker:>'{marker_filter}')+(malicious_confidence:'high')"

    return query_filter


def fetch_crowdstrike_iocs():
    """
    returns indicators of compromise from the crodwstrike api
    """

    query_filter = get_query_filter()

    response = requests.get(
        url=f"{CROWDSTRIKE_BASE_URL}/intel/combined/indicators/v1",
        params={"filter": query_filter, "sort": "_marker|asc"},
        headers={
            "Authorization": f"Bearer {CrowdStrikeToken.get_token()}",
        },
    )

    if response.status_code not in (200, 201):
        logging.error(f"Error Code: {response.status_code}")
        logging.error(f"Error Response: {response.text}")
        raise APIError(response.text)
    elif response.status_code == 401:
        logging.error(f"Error Code: {response.status_code}")
        logging.error(f"Error Response: {response.text}")
        raise UnauthorizedTokenException(response.text)

    batch = json.loads(response.text)["resources"]
    marker = batch[-1]["_marker"]

    while len(batch) > 0:
        yield batch, marker

        if "Next-Page" not in response.headers:
            break
        else:
            response = requests.get(
                url=f"{CROWDSTRIKE_BASE_URL}/{response.headers['Next-Page']}",
                headers={
                    "Authorization": f"Bearer {CrowdStrikeToken.get_token()}",
                    "User-Agent": USER_AGENT,
                },
            )

            if response.status_code not in (200, 201):
                logging.error(f"Error Code: {response.status_code}")
                logging.error(f"Error Response: {response.text}")
                raise APIError(response.text)
            elif response.status_code == 401:
                logging.error(f"Error Code: {response.status_code}")
                logging.error(f"Error Response: {response.text}")
                raise UnauthorizedTokenException(response.text)

            batch = json.loads(response.text)["resources"]
            marker = batch[-1]["_marker"]


def generate_uuid(id: str):
    """
    converts a sttring identifier to a guid using the hashvalue
    """

    hash_value = hashlib.md5(id.encode())
    return uuid.UUID(hash_value.hexdigest())


def convert_to_stix(indicators: list):
    """
    converts crowdstrike indicators of compromise to stix 2.1 format
    """

    stix_batch = []

    for indicator in indicators:
        stix_object = {
            "id": f"indicator--{generate_uuid(indicator['indicator'])}",
            "spec_version": "2.1",
            "type": "indicator",
            "created": datetime.fromtimestamp(indicator["published_date"]).isoformat(),
            "modified": datetime.fromtimestamp(indicator["last_updated"]).isoformat(),
            "name": indicator["indicator"],
            "descripton": "",
            "indicator_types": indicator["threat_types"],
            "pattern_type": "stix",
            "valid_from": datetime.fromtimestamp(
                indicator["published_date"]
            ).isoformat(),
            "kill_chain_phases": [
                {"kill_chain_name": "crowdstrike-falcon-killchain", "phase_name": x}
                for x in indicator["kill_chains"]
            ],
            "labels": (
                [x["name"] for x in indicator["labels"]]
                if indicator.get("labels")
                else []
            ),
            "lang": "en",
            "confidence": CONFIDENCE_MAPPING.get(indicator["malicious_confidence"], 10),
            "pattern": f"[{STIX_PATTERN_MAPPING[indicator['type']]} = '{indicator['indicator']}']",
            "revoked": indicator["deleted"],
            "extensions": {
                "crowdstrike-ext": {
                    "vulnerabilities": indicator["vulnerabilities"],
                    "targets": indicator["targets"],
                    "reports": indicator["reports"],
                    "actors": indicator["actors"],
                }
            },
        }

        stix_batch.append(stix_object)

    return stix_batch


def send_to_threat_intel(stix_batch):
    """
    send stix indicators to Microsoft Sentinel Threat Intel api
    """

    uri = f"https://sentinelus.azure-api.net/workspaces/{WORKSPACE_ID}/threatintelligenceindicators:upload?api-version=2022-07-01"
    headers = {
        "Authorization": f"Bearer {AADToken.get_token()}",
        "Content-Type": "application/json",
    }
    body = {
        "SourceSystem": "CrowdStrike Falcon Adversary Intelligence",
        "Indicators": stix_batch,
    }
    response = requests.post(uri, data=json.dumps(body), headers=headers)

    if response.status_code not in (200, 201):
        logging.error(f"Error Code: {response.status_code}")
        logging.error(f"Error Response: {response.text}")
        raise APIError(response.text)
    elif response.status_code == 401:
        logging.error(f"Error Code: {response.status_code}")
        logging.error(f"Error Response: {response.text}")
        raise UnauthorizedTokenException(response.text)

    return response


def main(mytimer: func.TimerRequest):

    global INDICATOR_COUNT
    next_execution = datetime.now(timezone.utc) + timedelta(minutes=10)

    for ioc_batch, marker in fetch_crowdstrike_iocs():
        seconds_to_next_execution = next_execution - datetime.now(timezone.utc)
        logging.info(seconds_to_next_execution)
        if (
            seconds_to_next_execution.seconds > 60
        ):  # if next execution is 60 seconds away
            stix_batch = convert_to_stix(ioc_batch)
            send_to_threat_intel(stix_batch)
            CrowdStrike_State.post(marker)
            INDICATOR_COUNT += len(stix_batch)
            logging.info(f"{INDICATOR_COUNT} indicators uploaded")
        else:  # exit before next execution
            logging.info("less than 60 seconds to next execution. Exiting...")
            sys.exit("less than 60 seconds to next execution.")
