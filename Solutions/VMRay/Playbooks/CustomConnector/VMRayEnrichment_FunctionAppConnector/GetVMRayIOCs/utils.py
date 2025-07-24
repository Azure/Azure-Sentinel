"""
utils functions
"""

# pylint: disable=logging-fstring-interpolation
import logging
import re
import uuid
from datetime import datetime, timezone, timedelta
from os import environ

vmrayBaseURL = environ["vmrayBaseURL"]
IOC_LIST = ["domains", "ips", "urls", "files"]
CONFIDENCE = {"malicious": "100", "suspicious": "75"}
INDICATOR_LIST = []
HASH_TYPE_LIST = [
    ("MD5", "md5_hash"),
    ("SHA-1", "sha1_hash"),
    ("SHA-256", "sha256_hash"),
]
ipv4Regex = r"^(?P<ipv4>(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))[:]?(?P<port>\d+)?$"
ipv6Regex = r"^(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:(?:(:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"  # noqa: E501


def add_domain_indicator(
    domains: list,
    sample_id: str,
    submission_id: str,
    verdicts: list,
    incident_id: str,
    valid_until: str,
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
    incident_id: str
        Sentinel Incident ID
    valid_until: str
        Indicator Expiration time in days
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
                incident_id,
                valid_until,
            )

            INDICATOR_LIST.append(indicator_data)
    except Exception as err:
        logging.error(f"Error processing domain indicators: {err}")


def add_file_indicators(
    files: list,
    sample_id: str,
    submission_id: str,
    verdicts: list,
    incident_id: str,
    valid_until: str,
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
    incident_id: str
        Sentinel Incident ID
    valid_until: str
        Indicator Expiration time in days
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
                    incident_id,
                    valid_until,
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
    if re.match(ipv4Regex, ip):
        return "ipv4-addr"
    if re.match(ipv6Regex, ip):
        return "ipv6-addr"

    return None


def add_ip_indicator(
    ips: list,
    sample_id: str,
    submission_id: str,
    verdicts: list,
    incident_id: str,
    valid_until: str,
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
    incident_id: str
        Sentinel Incident ID
    valid_until: str
        Indicator Expiration time in days
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
                incident_id,
                valid_until,
            )

            INDICATOR_LIST.append(indicator_data)

    except Exception as err:
        logging.error(f"Error processing IP indicators: {err}")


def add_url_indicator(
    urls: list,
    sample_id: str,
    submission_id: str,
    verdicts: list,
    incident_id: str,
    valid_until: str,
):
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
    incident_id: str
        Sentinel Incident ID
    valid_until: str
        Indicator Expiration time in days
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
                incident_id,
                valid_until,
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
    unique_uuid,
    indicator,
    pattern,
    sample_id,
    submission_id,
    name,
    confidence,
    incident_id,
    valid_until,
) -> dict:
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
    incident_id: str
        Sentinel Incident ID
    valid_until: str
        Indicator Expiration time in days
    Returns
    -------
    dict
        A dictionary representing the structured threat indicator
    """
    analysis = ", ".join(map(str, indicator.get("analysis_ids", [])))
    categories = ", ".join(indicator.get("categories", []))
    threat_names = indicator.get("threat_names", [])
    t_type = []
    for threat in threat_names:
        if re.match(r"^[a-zA-Z0-9\s]+$", threat):
            t_type.append(threat)
    tags = [
        f"sample_id: {sample_id}",
        f"submission_id: {submission_id}",
        f"incident_id: {incident_id}",
        f"threat_names: {','.join(t_type)}",
    ] + indicator.get("classifications", [])
    expiration_date = (
        datetime.now(timezone.utc) + timedelta(days=int(valid_until))
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
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
                "url": f"{vmrayBaseURL}/sample/{sample_id}#summary",
            }
        ],
        "name": name,
        "description": f"Sample URL: {vmrayBaseURL}/sample/{sample_id}#summary,"
        f"\nAnalysis IDs: {analysis},\nCategories: {categories}",
        "indicator_types": [indicator.get("ioc_type", "")],
        "pattern": pattern,
        "pattern_type": "stix",
        "pattern_version": "2.1",
        "valid_from": get_utc_time(),
        "valid_until": expiration_date,
    }
    return data


IOC_MAPPING_FUNCTION = {
    "domains": add_domain_indicator,
    "ips": add_ip_indicator,
    "urls": add_url_indicator,
    "files": add_file_indicators,
}

