"""This file contains methods for mapping between Dataminr and sentinel."""
import inspect
import json
from ipaddress import ip_address, IPv4Address
from ..shared_code import consts
from ..shared_code.logger import applogger
from ..shared_code.dataminrpulse_exception import DataminrPulseException

hash_types = {"MD5": "MD5", "SHA256": "SHA-256", "SHA512": "SHA-512"}


def validate_ip_address(ip_addr: str) -> str:
    """Validate Ip address and return the type of IP address.

    Args:
        IP (string): ip address to validate

    Returns:
        string: type of IP address, IPv4 or IPv6
    """
    try:
        return "IPv4" if type(ip_address(ip_addr)) is IPv4Address else "IPv6"
    except ValueError:
        return "Invalid"


def get_urls(embedded):
    """Get Urls from the dataminr data.

    Args:
        embedded (dict): embedded field data

    Returns:
        list: list of urls
    """
    results = []
    urls = embedded.get("data", "").get("URLs", "")
    if urls != "":
        for url in urls:
            results.append({"value": url, "type": "URL"})
    return results


def get_ip_addresses(embedded):
    """Get Ip addresses from embedded field data.

    Args:
        embedded (dict): embedded field data

    Returns:
        list: list of ip addresses
    """
    results = []
    addresses = embedded.get("data", "").get("addresses", "")
    if addresses != "":
        for address in addresses:
            ip_addr = address.get("ip", "")
            ip_addr = ip_addr.replace("[", "")
            ip_addr = ip_addr.replace("]", "")
            if ip_addr != "" or ip_addr != "[]":
                type_of_ip = validate_ip_address(ip_addr)
                if type_of_ip != "Invalid":
                    results.append({"value": ip_addr, "type": type_of_ip})
    return results


def get_file_hashes(embedded):
    """Get File hashes from embedded field data.

    Args:
        embedded (dict): embedded field data

    Returns:
        list: list of file hashes
    """
    results = []
    hash_values = embedded.get("data", "").get("hashValues", "")
    if hash_values != "":
        for hash_value in hash_values:
            results.append(
                {
                    "value": hash_value.get("value", ""),
                    "type": "File",
                    "hashType": hash_value.get("type", ""),
                }
            )
    return results


def get_pattern_and_values(embedded_fields_data):
    """Parse Embedded array and return data for pattern type and value.

    Args:
        embedded_fields_data (list): Embedded Fields Data

    Returns:
        list: list of dictionary with value for pattern type and it's values.
    """
    final_results = []
    for embedded in embedded_fields_data:
        # check for URLs:
        final_results.extend(get_urls(embedded))
        # check for ips:
        final_results.extend(get_ip_addresses(embedded))
        # check for File Hashes
        final_results.extend(get_file_hashes(embedded))
    return final_results


def map_indicator_fields(indicator):
    """Map indicator fields for sentinel indicator.

    Args:
        indicator (dict): Data fetched from DataminrPulse
        azure_function_name (str): Azure Function Name

    Returns:
        list: mapped indicators' data
    """
    try:
        mapped_indicators = []
        __method_name = inspect.currentframe().f_code.co_name
        parsed_embedded_data = json.loads(indicator.get("_embedded_labels_s"))
        confidence = ""
        if indicator.get("alertType_id_s", "") == "flash":
            confidence = 100
        elif indicator.get("alertType_id_s", "") == "urgentUpdate":
            confidence = 60
        elif indicator.get("alertType_id_s", "") == "urgent":
            confidence = 60
        elif indicator.get("alertType_id_s", "") == "alert":
            confidence = 30
        parsed_patterns = get_pattern_and_values(parsed_embedded_data)
        for parsed_data in parsed_patterns:
            pattern = ""
            pattern_type = ""
            if parsed_data.get("type") == "URL":
                pattern = "url:value ="
                pattern_type = "URL"
            elif parsed_data.get("type") == "File":
                pattern = "file:hashes.'{}' =".format(
                    hash_types.get(parsed_data.get("hashType", ""), "")
                )
                pattern_type = "File"
            elif parsed_data.get("type") == "IPv4":
                pattern = "ipv4-addr:value ="
                pattern_type = "ipv4-addr"
            elif parsed_data.get("type") == "IPv6":
                pattern = "ipv6-addr:value ="
                pattern_type = "ipv6-addr"
            sentinel_indicator = {
                "kind": "indicator",
                "properties": {
                    "source": "Dataminr: {}".format(indicator.get("Source", "")),
                    "displayName": "Dataminr: {}".format(indicator.get("index_s", "")),
                    "confidence": confidence,
                    "description": indicator.get("headline_s", ""),
                    "threatTypes": [pattern_type],
                    "pattern": "[{} '{}']".format(
                        (pattern), parsed_data.get("value", "")
                    ),
                    "patternType": pattern_type,
                },
            }
            mapped_indicators.append(sentinel_indicator)
        applogger.info(
            "{}(method={}) : {} : Indicator Field Mapping is done for index {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                indicator.get("index_s", ""),
            )
        )
        return mapped_indicators
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Error occured :{}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                error,
            )
        )
        raise DataminrPulseException(error)
