"""
utils functions
"""

# pylint: disable=logging-fstring-interpolation
import logging
from ipaddress import ip_address, IPv4Address, IPv6Address
from uuid import uuid5, NAMESPACE_DNS
from datetime import datetime, timedelta, timezone
from json import loads
from os import environ

JOE_SANDBOX_BASE_URL= environ["JoeSandboxBaseURL"]
IOC_LIST = ["domains", "ips", "urls", "files"]
CONFIDENCE = {"malicious": "100", "suspicious": "75"}
INDICATOR_LIST = []
HASH_TYPE_LIST = [
    ("MD5", "md5"),
    ("SHA-1", "sha1"),
    ("SHA-256", "sha256"),
]
UTC_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
VALID_UNTIL = 180


def add_domain_indicators(domains: list, analysis_data: dict) -> list:
    """
    Adds domain indicators indicator list if the verdict of the
    domains matches any of the provided verdicts.

    Parameters
    ----------
    domains : list
        List of domain ioc.
    analysis_data: dict
        analysis data

    Returns:
        indicators: list
    """
    indicators = []
    for domain in domains:
        if not domain.get("malicious"):
            continue
        try:
            domain_value = domain.get("name")
            pattern = f"[domain-name:value = '{domain_value}']"
            unique_id = generate_unique_id("domain", domain_value)

            indicator_data = get_static_data(
                unique_id, analysis_data, pattern, domain_value, "domain"
            )

            indicators.append(indicator_data)
        except Exception as err:
            logging.error(f"Error processing domain indicators: {err}")
    return indicators


def add_file_indicators(files: list, analysis_data: dict) -> list:
    """
    Processes files and adds hash-based indicators to a indicator list based on verdicts.

    Parameters
    ----------
    files : list
        List of file ioc.
    analysis_data : dict
        Analysis data

    Returns
    ----------
    indicators: list
        List of IOCs

    """
    indicators = []
    for file in files:
        if not file.get("malicious"):
            continue
        try:
            filename = file.get("name", "")
            for hash_type, key in HASH_TYPE_LIST:
                hash_value = file.get(key)
                if not hash_value:
                    continue

                pattern = f"[file:hashes.'{hash_type}' = '{hash_value}']"
                unique_id = generate_unique_id("file", hash_value)
                label = filename or hash_value

                indicator_data = get_static_data(
                    unique_id, analysis_data, pattern, label, "file"
                )

                indicators.append(indicator_data)

        except Exception as err:
            logging.error(f"Error processing file indicators: {err}")
    return indicators


def check_ip(ip: str) -> str | None:
    """
    Determines the type of IP address using the ipaddress module.

    Parameters
    ----------
    ip : str
        The IP address to check.

    Returns
    -------
    str or None
        "ipv4-addr" for IPv4 addresses,
        "ipv6-addr" for IPv6 addresses,
        None if not a valid IP.
    """
    try:
        parsed_ip = ip_address(ip)
        if isinstance(parsed_ip, IPv4Address):
            return "ipv4-addr"
        if isinstance(parsed_ip, IPv6Address):
            return "ipv6-addr"
    except ValueError:
        return None


def str_to_bool(value: str) -> bool:
    """
    Convert string to bool type
    """
    return loads(value.strip().lower()) if isinstance(value, str) else bool(value)


def add_ip_indicators(ips: list, analysis_data: dict) -> list:
    """
    Adds IP indicators to the indicator list based on verdict filtering.

    Parameters
    ----------
    ips : list
        List of IP.
    analysis_data : dict
        Analysis data

    Returns
    ----------
    indicators: list
        List of IOCs
    """
    indicators = []
    for ip_entry in ips:
        if not str_to_bool(ip_entry.get("@malicious")):
            continue
        try:
            ip_add = ip_entry.get("$", "")
            ip_type = check_ip(ip_add)
            if not ip_type:
                logging.warning(f"Unrecognized IP type for address: {ip_add}")
                continue

            pattern = f"[{ip_type}:value = '{ip_add}']"
            unique_id = generate_unique_id("ip", ip_add)

            indicator_data = get_static_data(
                unique_id, analysis_data, pattern, ip_add, ip_type
            )

            indicators.append(indicator_data)

        except Exception as err:
            logging.error(f"Error processing IP indicators: {err}")
    return indicators


def add_url_indicators(urls: list, analysis_data: dict) -> list:
    """
    Adds URL indicators to the global indicator list (INDICATOR_LIST) based on verdict filtering.

    Parameters
    ----------
    urls : list
        List of URL.
    analysis_data : dict
        Analysis data

    Returns
    ----------
    indicators: list
        List of IOCs
    """
    indicators = []
    for url_entry in urls:
        if not url_entry.get("malicious"):
            continue
        try:

            url_value = url_entry.get("name", "")
            pattern = f"[url:value = '{url_value}']"
            unique_id = generate_unique_id("url", url_value)
            indicator_data = get_static_data(
                unique_id, analysis_data, pattern, url_value, "url"
            )

            indicators.append(indicator_data)

        except Exception as err:
            logging.error(f"Error processing URL indicators: {err}")
    return indicators


def parse_analysis_data(analysis_data: dict) -> dict:
    """
    Extracts relevant IOCs (files, domains, IPs, URLs, etc.) from JoeSandbox analysis data.

    Parameters
    ----------
    analysis_data : dict
        The full analysis JSON response from JoeSandbox (IRJSON format).

    Returns
    -------
    dict
        A dictionary containing categorized IOCs (e.g., 'files', 'domains', 'ips').
    """
    ioc_dict = {}

    analysis = analysis_data.get("analysis", {})
    contacted = analysis.get("contacted", {})
    dropped = analysis.get("dropped", {})

    if isinstance(dropped, dict):
        ioc_dict["files"] = dropped.get("file", [])

    if isinstance(contacted, dict):
        for key, value in contacted.items():
            if isinstance(value, dict):
                singular_key = key.rstrip("s")
                ioc_dict[key] = value.get(singular_key, [])
            elif isinstance(value, list):
                ioc_dict[key] = value

    return ioc_dict


def generate_unique_id(
    indicator_type: str, indicator_value: str, threat_source: str = "JoeSandbox"
) -> str:
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
    custom_namespace = uuid5(NAMESPACE_DNS, threat_source)
    name_string = f"{indicator_type}:{indicator_value}"
    indicator_uuid = uuid5(custom_namespace, name_string)
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
        current_time.strftime(UTC_DATE_FORMAT)
        + f"{current_time.microsecond // 1000:03d}Z"
    )
    return formatted_time


def get_static_data(
        unique_uuid: str,
        analysis_data: dict,
        pattern: str,
        ioc_value: str,
        ioc_type:str
) -> dict:
    """
    Constructs a structured dictionary representing a static threat indicator.

    Parameters
    ----------
    unique_uuid : str
        A globally unique identifier for the indicator.
    analysis_data : dict
        analysis metadata.
    pattern : str
        A STIX pattern string.
    ioc_value : str
        Indicator value.
    ioc_type: str
        type of ioc
    Returns
    -------
    dict
        A dictionary representing the structured threat indicator
    """
    web_id = analysis_data.get("webid")
    tags = [
        f"web_id: {web_id}",
        f"threat_names: {analysis_data.get('threatname', '')}",
        f"classification: {analysis_data.get('classification', '')}",
        f"detection: {analysis_data.get('detection', '')}",
    ]
    expiration_date = (
        datetime.now(timezone.utc) + timedelta(days=VALID_UNTIL)
    ).strftime(UTC_DATE_FORMAT)

    data = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": unique_uuid,
        "created": get_utc_time(),
        "modified": get_utc_time(),
        "revoked": False,
        "labels": tags,
        "confidence": CONFIDENCE.get(analysis_data.get("detection", ""), 0),
        "name": ioc_value,
        "description": f"Analysis URL: {JOE_SANDBOX_BASE_URL}/analysis/{web_id}",
        "indicator_types": [ioc_type],
        "pattern": pattern,
        "pattern_type": "stix",
        "pattern_version": "2.1",
        "valid_from": get_utc_time(),
        "valid_until": expiration_date,
    }
    return data

IOC_MAPPING_FUNCTION = {
    "domains": add_domain_indicators,
    "ips": add_ip_indicators,
    "urls": add_url_indicators,
    "files": add_file_indicators,
}
