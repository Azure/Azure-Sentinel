"""
Core Logic of Function App
"""

# pylint: disable=logging-fstring-interpolation
import logging
import re
import uuid
from datetime import datetime, timezone, timedelta
from os import environ
from time import sleep
from typing import Dict, Optional, Union

import requests

from .const import (
    CONFIDENCE,
    HASH_TYPE_LIST,
    IPV4REGEX,
    IPV6REGEX,
    RETRY_STATUS_CODE,
    SENTINEL_API,
    VMRay_CONFIG,
)
from .state_manager import StateManager
from .vmray_api import VMRay

FETCHED_SAMPLE_IOCS = {}

INDICATOR_LIST = []

vmray = VMRay(logging)
state = StateManager(environ.get("AzureWebJobsStorage"))

def get_last_saved_timestamp() -> Optional[int]:
    """
    Retrieves the last saved Unix timestamp from persistent state.

    Checks the system state for the last recorded timestamp of a previous
    successful operation. If no timestamp exists (e.g., on the first run),
    returns None.

    Returns
    -------
    Optional[int]
        The Unix timestamp of the last saved run, or None if not available.
    """
    last_run_date_time = state.get()
    logging.debug("Last saved timestamp is %s", last_run_date_time)

    return last_run_date_time if last_run_date_time else None


def save_checkpoint(timestamp: str) -> None:
    """
    Saves the provided timestamp as the current system checkpoint.

    Parameters
    ----------
    timestamp : str
        The timestamp representing when the checkpoint is created.

    Returns
    -------
    None
    """
    state.post(timestamp)


def get_submission(verdict: list, from_time: str, to_time: str) -> list:
    """
    Retrieves submissions filtered by verdict and a specified time range.

    Parameters
    ----------
    verdict : list of str
        A list of verdict strings used to filter submissions
    from_time : str
        Start point (ISO 8601 format).
    to_time : str
        End point (ISO 8601 format).

    Returns
    -------
    list of dict
        A list of submission dictionaries.
    """
    submission_response = []
    try:
        logging.info(f"Fetching submission from {from_time}~{to_time}")
        for ver in verdict:
            params = {
                "submission_finish_time": f"{from_time}~{to_time}",
                "submission_verdict": ver.strip().lower(),
            }
            response = vmray.retry_request("GET", "/rest/submission", param=params)
            submission_response.extend(response)
        return submission_response
    except Exception as err:
        logging.error(f"Error {err}")
        return submission_response


def get_sample_ioc(sample_id: str) -> dict:
    """
    Retrieves IOCs for a given sample ID.

    Parameters
    ----------
    sample_id : str
        Unique identifier for the sample whose IOCs should be retrieved.

    Returns
    -------
    dict
        A dictionary containing IOCs for the specified sample ID.
        Returns an empty dictionary if retrieval fails or no data is found.
    """
    try:
        if not sample_id in FETCHED_SAMPLE_IOCS:
            ioc_response = vmray.retry_request(
                "GET", f"/rest/sample/{sample_id}/iocs"
            ).get("iocs", {})
            FETCHED_SAMPLE_IOCS[sample_id] = ioc_response
            return ioc_response
        return FETCHED_SAMPLE_IOCS[sample_id]
    except Exception as err:
        logging.error(f"Error {err}")
        return {}


def add_domain_indicator(
    domains: list, sample_id: str, submission_id: str, verdicts: list
) -> None:
    """
    Adds domain indicators to the global indicator list if the verdict of the
    domains matches any of the provided verdicts.

    Parameters
    ----------
    domains : list
        List of domain ioc.
    sample_id : str
        ID of the related sample.
    submission_id : str
        ID of the related submission.
    verdicts : list
        List of accepted verdicts.
    """
    try:
        accepted_verdicts = {v.lower() for v in verdicts}

        for domain in domains:
            verdict = domain.get("verdict", "").lower()
            domain_value = domain.get("domain")

            if verdict not in accepted_verdicts:
                continue
            pattern = f"[domain-name:value = '{domain_value}']"
            unique_id = gen_unique_id("domain", domain_value)
            confidence = CONFIDENCE.get(verdict, 0)

            indicator_data = get_static_data(
                unique_id,
                domain,
                pattern,
                sample_id,
                submission_id,
                domain_value,
                confidence,
            )

            INDICATOR_LIST.append(indicator_data)
    except Exception as err:
        logging.error(f"Error processing domain indicators: {err}")


def add_file_indicators(
    files: list, sample_id: str, submission_id: str, verdicts: list
) -> None:
    """
    Processes files and adds hash-based indicators to a global list based on verdicts.

    Parameters
    ----------
    files : list
        List of file ioc.
    sample_id : str
        Unique sample id.
    submission_id : str
        Submission id.
    verdicts : list
        List of accepted verdicts.
    """
    try:
        accepted_verdicts = {v.lower() for v in verdicts}

        for file in files:
            verdict = file.get("verdict", "").lower()
            if verdict not in accepted_verdicts:
                continue

            file_hashes = file.get("hashes", [])
            if not file_hashes:
                logging.warning(f"No hashes found in file entry: {file}")
                continue

            hash_data = file_hashes[0]
            filename = file.get("filename", "")
            confidence = CONFIDENCE.get(verdict, 0)

            for hash_type, key in HASH_TYPE_LIST:
                hash_value = hash_data.get(key)
                if not hash_value:
                    logging.warning(f"{key} not found in file: {file}")
                    continue

                pattern = f"[file:hashes.'{hash_type}' = '{hash_value}']"
                unique_id = gen_unique_id("file", hash_value)
                label = filename or hash_value

                indicator_data = get_static_data(
                    unique_id,
                    file,
                    pattern,
                    sample_id,
                    submission_id,
                    label,
                    confidence,
                )

                INDICATOR_LIST.append(indicator_data)

    except Exception as err:
        logging.error(f"Error processing file indicators: {err}")


def check_ip(ip: str) -> str | None:
    """
    Determines the type of IP address based on its format.

    Parameters
    ----------
    ip : str
        The IP address to check.

    Returns
    -------
    str or None
    """
    if re.match(IPV4REGEX, ip):
        return "ipv4-addr"
    if re.match(IPV6REGEX, ip):
        return "ipv6-addr"

    return None


def add_ip_indicator(
    ips: list, sample_id: str, submission_id: str, verdicts: list
) -> None:
    """
    Adds IP indicators to the global indicator list based on verdict filtering.

    Parameters
    ----------
    ips : list
        List of IP.
    sample_id : str
        Sample ID.
    submission_id : str
        Submission ID.
    verdicts : list
        List of accepted verdicts.
    """
    try:
        accepted_verdicts = {v.lower() for v in verdicts}

        for ip_entry in ips:
            verdict = ip_entry.get("verdict", "").lower()
            ip_address = ip_entry.get("ip_address", "")

            if verdict not in accepted_verdicts:
                continue

            ip_type = check_ip(ip_address)
            if not ip_type:
                logging.warning(f"Unrecognized IP type for address: {ip_address}")
                continue

            pattern = f"[{ip_type}:value = '{ip_address}']"
            unique_id = gen_unique_id("ip", ip_address)
            confidence = CONFIDENCE.get(verdict, 0)

            indicator_data = get_static_data(
                unique_id,
                ip_entry,
                pattern,
                sample_id,
                submission_id,
                ip_address,
                confidence,
            )

            INDICATOR_LIST.append(indicator_data)

    except Exception as err:
        logging.error(f"Error processing IP indicators: {err}")


def add_url_indicator(urls: list, sample_id: str, submission_id: str, verdicts: list):
    """
    Adds URL indicators to the global indicator list (INDICATOR_LIST) based on verdict filtering.

    Parameters
    ----------
    urls : list
        List of URL.
    sample_id : str
        Sample ID.
    submission_id : str
        Submission ID.
    verdicts : list
        List of accepted verdicts.
    """
    try:
        accepted_verdicts = {v.lower() for v in verdicts}

        for url_entry in urls:
            verdict = url_entry.get("verdict", "").lower()
            url_value = url_entry.get("url", "")

            if verdict not in accepted_verdicts:
                continue

            pattern = f"[url:value = '{url_value}']"
            unique_id = gen_unique_id("url", url_value)
            confidence = CONFIDENCE.get(verdict, 0)

            indicator_data = get_static_data(
                unique_id,
                url_entry,
                pattern,
                sample_id,
                submission_id,
                url_value,
                confidence,
            )

            INDICATOR_LIST.append(indicator_data)

    except Exception as err:
        logging.error(f"Error processing URL indicators: {err}")


def gen_unique_id(
    indicator_type: str, indicator_value: str, threat_source: str = "VMRay"
):
    """
    Generates a unique identifier string for a threat indicator.

    Parameters
    ----------
    indicator_type : str
        The type of indicator.
    indicator_value : str
        The indicator value such.
    threat_source : str, optional
        Indicator source.

    Returns
    -------
    str
        Unique indicator id.
    """
    custom_namespace = uuid.uuid5(uuid.NAMESPACE_DNS, threat_source)
    name_string = f"{indicator_type}:{indicator_value}"
    indicator_uuid = uuid.uuid5(custom_namespace, name_string)
    return f"indicator--{indicator_uuid}"


def get_utc_time() -> str:
    """
    Returns the current UTC time formatted as an ISO 8601 timestamp.

    Returns
    -------
    str
        The current UTC time as an ISO 8601 timestamp with milliseconds,
        e.g., '2025-06-26T14:03:12.123Z'.
    """
    current_time = datetime.now(timezone.utc)
    formatted_time = (
        current_time.strftime("%Y-%m-%dT%H:%M:%S.")
        + f"{current_time.microsecond // 1000:03d}Z"
    )
    return formatted_time


def get_static_data(
    unique_uuid, indicator, pattern, sample_id, submission_id, name, confidence
) -> Dict[str, Union[str, int, list]]:
    """
    Constructs a structured dictionary representing a static threat indicator.

    Parameters
    ----------
    unique_uuid : str
        A globally unique identifier for the indicator.
    indicator : dict
        Indicators metadata.
    pattern : str
        A STIX pattern string.
    sample_id : str
        Sample ID.
    submission_id : str
        Submission ID.
    name : str
        Name of the indicator.
    confidence : int
        An integer representing the confidence score (0–100) assigned to the indicator.

    Returns
    -------
    dict
        A dictionary representing the structured threat indicator
    """
    analysis = ", ".join(map(str, indicator.get("analysis_ids", [])))
    categories = ", ".join(indicator.get("categories", []))
    classifications = ", ".join(indicator.get("classifications", []))
    threat_names = indicator.get("threat_names", [])
    expiration_date = (
        datetime.now(timezone.utc) + timedelta(days=int(VMRay_CONFIG.VALID_UNTIL))
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    t_type = []
    for threat in threat_names:
        if re.match(r"^[a-zA-Z0-9\s]+$", threat):
            t_type.append(threat)
    tags = [
        f"sample_id: {sample_id}",
        f"submission_id: {submission_id}",
        f"threat_names: {', '.join(t_type)}",
        f"Classifications: {classifications}",
    ]

    data = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": unique_uuid,
        "created": get_utc_time(),
        "modified": get_utc_time(),
        "revoked": False,
        "labels": tags,
        "confidence": confidence,
        "external_references": [
            {
                "source_name": "VMRay Threat Intelligence",
                "description": f"Sample ID {sample_id}\nSubmission ID {submission_id}",
                "url": f"{VMRay_CONFIG.BASE_URL}/samples/{sample_id}#summary",
            }
        ],
        "name": name,
        "description": f"Sample URL: {VMRay_CONFIG.BASE_URL}/samples/{sample_id}#summary,"
        f"\nAnalysis IDs: {analysis},\nCategories: {categories}",
        "indicator_types": [indicator.get("ioc_type", "")],
        "pattern": pattern,
        "pattern_type": "stix",
        "pattern_version": "2.1",
        "valid_from": get_utc_time(),
        "valid_until": expiration_date
    }
    return data


IOC_MAPPING_FUNCTION = {
    "domains": add_domain_indicator,
    "ips": add_ip_indicator,
    "urls": add_url_indicator,
    "files": add_file_indicators,
}


def create_indicator(indicator_data: list) -> requests.Response:
    """
    Creates a threat intelligence indicator in the Sentinel system.

    Parameters
    ----------
    indicator_data : list
        The STIX-formatted threat intelligence data to be submitted.

    Returns
    -------
    requests.Response
        The HTTP response from the indicator creation API call.

    Raises
    ------
    Exception
        Raised if the maximum retry attempts are exceeded due to specific
        errors such as rate limiting or connection failures.
    Exception
        Raised for any other unexpected errors during indicator creation.
    """
    retry_count_429 = 0
    retry_connection = 0
    indicator = {
        "sourcesystem": "VMRayThreatIntelligence",
        "stixobjects": indicator_data,
    }

    azure_login_payload = {
        "grant_type": "client_credentials",
        "client_id": SENTINEL_API.APPLICATION_ID,
        "client_secret": SENTINEL_API.APPLICATION_SECRET,
        "resource": SENTINEL_API.RESOURCE_APPLICATION_ID_URI,
    }

    while retry_count_429 <= 3:
        try:
            response = requests.post(
                url=SENTINEL_API.AUTH_URL,
                data=azure_login_payload,
                timeout=SENTINEL_API.TIMEOUT,
            )
            response.raise_for_status()
            access_token = response.json().get("access_token")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": SENTINEL_API.USER_AGENT,
                "Content-Type": "application/json",
            }
            response = requests.post(
                SENTINEL_API.URL,
                headers=headers,
                json=indicator,
                timeout=SENTINEL_API.TIMEOUT,
            )
            response.raise_for_status()
            return response
        except requests.HTTPError as herr:
            if response.status_code in RETRY_STATUS_CODE:
                retry_count_429 += 1
                logging.warning(
                    f"Attempt {retry_count_429}: HTTP {response.status_code}."
                    f" Retrying after {SENTINEL_API.SLEEP}s..."
                )
                sleep(SENTINEL_API.SLEEP)
                continue
            logging.error(f"HTTPError from Sentinel API: {herr}")
            raise Exception(herr) from herr
        except (
            requests.ConnectionError,
            requests.exceptions.RequestException,
        ) as conn_err:
            if retry_connection < 3:
                retry_connection += 1
                logging.warning(
                    f"Attempt {retry_connection}: Connection error."
                    f" Retrying after {SENTINEL_API.SLEEP}s..."
                )
                sleep(SENTINEL_API.SLEEP)
                continue
            logging.error(f"Connection failed after retries: {conn_err}")
            raise Exception(conn_err) from conn_err

        except Exception as err:
            logging.error(f"Unexpected error: {err}")
            raise Exception(err) from err

    raise Exception("Failed to create indicator after multiple retries.")


def submit_indicator() -> bool:
    """
    Submit Indicator to sentinel

    Returns
    -------
        bool
    """
    try:
        logging.info(f"length of indicator {len(INDICATOR_LIST)}")
        for i in range(0, len(INDICATOR_LIST), SENTINEL_API.MAX_TI_INDICATORS_PER_REQUEST):
            create_indicator(
                INDICATOR_LIST[i : i + SENTINEL_API.MAX_TI_INDICATORS_PER_REQUEST]
            )
        return True
    except Exception as err:
        logging.info(f"Error occurred during IOC creation: {err}")
        raise

