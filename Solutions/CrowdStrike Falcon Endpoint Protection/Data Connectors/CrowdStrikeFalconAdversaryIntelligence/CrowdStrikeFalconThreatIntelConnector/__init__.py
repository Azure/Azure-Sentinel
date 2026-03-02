"""
CrowdStrike Falcon Adversary Intelligence Connector for Microsoft Sentinel.

This Azure Function fetches threat intelligence indicators from CrowdStrike Falcon
and uploads them to Microsoft Sentinel in STIX 2.1 format.
"""

import json
from datetime import datetime, timezone, timedelta
import uuid
import logging
import hashlib
import requests
import azure.functions as func

from .utils import (
    StateManager,
    CrowdStrikeTokenRetriever,
    AADTokenRetriever,
    UnauthorizedTokenException,
    CONFIDENCE_MAPPING,
    STIX_PATTERN_MAPPING,
    APIError,
)
from .config import Config


def get_look_back_date(config):
    """
    Returns the date for looking back based on the configured look back days.

    Args:
        config: Configuration object containing look_back_days

    Returns:
        int: Unix epoch timestamp for the lookback period
    """

    right_now = datetime.now(timezone.utc)
    look_back_date = int((right_now - timedelta(days=int(config.look_back_days))).timestamp())

    return look_back_date


def parse_indicator_type_filter(config):
    """
    Parses the configured indicator types into a query filter string.

    Args:
        config: Configuration object containing indicators

    Returns:
        str: Formatted query filter string for indicator types
    """

    split_indicators = config.indicators.split(",")
    indicator_query_filter = "',type:'".join(split_indicators)
    indicator_query_filter = f"type:'{indicator_query_filter}'"

    return indicator_query_filter


def get_query_filter(config, state_manager):
    """
    Returns the query filter to be used to extract indicators of compromise
    from the CrowdStrike API.

    Args:
        config: Configuration object containing indicator settings
        state_manager: StateManager instance for tracking processing state

    Returns:
        str: Formatted query filter string for CrowdStrike API
    """

    indicator_type_filter = parse_indicator_type_filter(config)
    marker_filter = state_manager.get()
    if marker_filter is None:
        look_back_date = get_look_back_date(config)
        # Add confidence filter to match incremental processing behavior
        # pylint: disable=line-too-long
        query_filter = f"({indicator_type_filter})+(last_updated:>{look_back_date})"
    else:
        # pylint: disable=line-too-long
        query_filter = f"({indicator_type_filter})+(_marker:>'{marker_filter}')+(malicious_confidence:'high')"

    return query_filter


def fetch_crowdstrike_iocs(config, state_manager, crowdstrike_token):
    """
    Fetches indicators of compromise from the CrowdStrike API using pagination.

    Args:
        config: Configuration object containing base URL and other settings
        state_manager: StateManager instance for tracking processing state
        crowdstrike_token: CrowdStrikeTokenRetriever instance for authentication

    Yields:
        tuple: A tuple containing (indicator_batch, marker) for each page of results

    Raises:
        APIError: If API call returns an error response
        UnauthorizedTokenException: If authentication fails
    """

    query_filter = get_query_filter(config, state_manager)

    response = requests.get(
        url=f"{config.crowdstrike_base_url}/intel/combined/indicators/v1",
        params={"filter": query_filter, "sort": "_marker|asc"},
        headers={
            "Authorization": f"Bearer {crowdstrike_token.get_token()}",
        },
    )

    if response.status_code == 401:
        raise UnauthorizedTokenException(response)
    elif response.status_code not in (200, 201):
        raise APIError(response)

    batch = json.loads(response.text)["resources"]
    if len(batch) == 0:
        logging.info("No indicators found in initial API response")
        return  # No indicators to process

    marker = batch[-1]["_marker"]
    logging.info("Found %d indicators in initial batch", len(batch))

    while len(batch) > 0:
        yield batch, marker

        if "Next-Page" not in response.headers:
            logging.info("Reached end of paginated results")
            break
        else:
            response = requests.get(
                url=f"{config.crowdstrike_base_url}/{response.headers['Next-Page']}",
                headers={
                    "Authorization": f"Bearer {crowdstrike_token.get_token()}",
                    "User-Agent": config.user_agent,
                },
            )

            if response.status_code == 401:
                raise UnauthorizedTokenException(response)
            elif response.status_code not in (200, 201):
                raise APIError(response)

            batch = json.loads(response.text)["resources"]
            if len(batch) == 0:
                logging.info("No more indicators found in paginated response")
                break  # No more indicators in this page
            marker = batch[-1]["_marker"]
            logging.info("Found %d indicators in next page", len(batch))


def generate_uuid(identifier: str):
    """
    Converts a string identifier to a UUID using MD5 hash.

    Args:
        identifier: String identifier to convert to UUID

    Returns:
        uuid.UUID: Generated UUID object based on the identifier hash
    """

    hash_value = hashlib.md5(identifier.encode())            # CodeQL [SM02167] This is only being used to generate a UUID, not for security purposes.
    return uuid.UUID(hash_value.hexdigest())


def convert_to_stix(indicators: list):
    """
    Converts CrowdStrike indicators of compromise to STIX 2.1 format.

    Args:
        indicators: List of CrowdStrike indicator dictionaries

    Returns:
        list: List of STIX 2.1 formatted indicator objects
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
            "description": "",
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


def send_to_threat_intel(stix_batch, workspace_id, aad_token):
    """
    Sends STIX indicators to Microsoft Sentinel Threat Intelligence API.

    Args:
        stix_batch: List of STIX 2.1 formatted indicator objects
        workspace_id: Microsoft Sentinel workspace identifier
        aad_token: AADTokenRetriever instance for authentication

    Returns:
        requests.Response: HTTP response object from the API call

    Raises:
        APIError: If API call returns an error response
        UnauthorizedTokenException: If authentication fails
    """

    # pylint: disable=line-too-long
    uri = f"https://sentinelus.azure-api.net/workspaces/{workspace_id}/threatintelligenceindicators:upload?api-version=2022-07-01"
    headers = {
        "Authorization": f"Bearer {aad_token.get_token()}",
        "Content-Type": "application/json",
    }
    body = {
        "SourceSystem": "CrowdStrike Falcon Adversary Intelligence",
        "Indicators": stix_batch,
    }
    response = requests.post(uri, data=json.dumps(body), headers=headers)

    if response.status_code == 401:
        raise UnauthorizedTokenException(response)
    elif response.status_code not in (200, 201):
        raise APIError(response)

    return response


def main(mytimer: func.TimerRequest) -> None:
    """
    Main Azure Function entry point that fetches CrowdStrike indicators
    and uploads them to Microsoft Sentinel as STIX 2.1 format.

    Args:
        mytimer: Azure Functions timer trigger request object
    """
    # Initialize configuration and validate all required environment variables
    config = Config()
    if not config.validate_required_variables():
        logging.error("Environment variable validation failed. Function execution stopped.")
        return

    # Initialize services
    state_manager = StateManager(
        config.file_storage_connection_string,
        "csiocstateshare",
        "_marker"
    )
    crowdstrike_token = CrowdStrikeTokenRetriever(
        config.crowdstrike_client_id,
        config.crowdstrike_client_secret,
        config.crowdstrike_base_url
    )
    aad_token = AADTokenRetriever(
        config.tenant_id,
        config.aad_client_id,
        config.aad_client_secret
    )

    logging.info("Starting CrowdStrike Falcon Adversary Intelligence connector execution")
    indicator_count = 0
    batch_count = 0
    next_execution = datetime.now(timezone.utc) + timedelta(minutes=10)

    for ioc_batch, marker in fetch_crowdstrike_iocs(config, state_manager, crowdstrike_token):
        seconds_to_next_execution = next_execution - datetime.now(timezone.utc)
        if (
            seconds_to_next_execution.total_seconds() > 60
        ):  # if next execution is 60 seconds away
            stix_batch = convert_to_stix(ioc_batch)
            send_to_threat_intel(stix_batch, config.workspace_id, aad_token)
            state_manager.post(marker)
            indicator_count += len(stix_batch)
            batch_count += 1
            logging.info("Batch %d: uploaded %d indicators (total: %d)",
                        batch_count, len(stix_batch), indicator_count)
        else:  # exit before next execution
            logging.info("Less than 60 seconds to next execution. Exiting early...")
            break

    # Log final summary
    logging.info("Execution completed: processed %d indicators across %d batches",
                indicator_count, batch_count)