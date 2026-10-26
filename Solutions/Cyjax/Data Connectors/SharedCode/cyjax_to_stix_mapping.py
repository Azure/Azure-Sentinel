"""This module maps Cyjax IOC API response fields to STIX 2.1 indicator format."""

import inspect
import uuid
import ipaddress
from datetime import datetime, timezone
from SharedCode import consts
from SharedCode.logger import applogger
from SharedCode.exceptions import CyjaxException

# STIX pattern templates for each IOC type
STIX_PATTERN_MAP = {
    "IPv4": "[ipv4-addr:value = '{}']",
    "IPv6": "[ipv6-addr:value = '{}']",
    "Domain": "[domain-name:value = '{}']",
    "Hostname": "[domain-name:value = '{}']",
    "URL": "[url:value = '{}']",
    "Email": "[email-addr:value = '{}']",
    "FileHash-MD5": "[file:hashes.'MD5' = '{}']",
    "FileHash-SHA1": "[file:hashes.'SHA-1' = '{}']",
    "FileHash-SHA256": "[file:hashes.'SHA-256' = '{}']",
    "FileHash-SSDEEP": "[file:hashes.'SSDEEP' = '{}']",
}

# Confidence mapping from Cyjax handling_condition to STIX confidence (0-100)
CONFIDENCE_MAP = {
    "RED": 90,
    "AMBER": 70,
    "GREEN": 50,
    "WHITE": 30,
}

# TLP marking definition IDs per STIX 2.1 specification
TLP_MARKING_MAP = {
    "RED": "marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed",
    "AMBER": "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82",
    "GREEN": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da",
    "WHITE": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9",
}


def build_stix_pattern(ioc_type, ioc_value):
    """Build a STIX pattern string for a given IOC type and value.

    Args:
        ioc_type (str): The Cyjax IOC type (e.g., 'IPv4', 'Domain', 'FileHash-SHA256').
        ioc_value (str): The IOC value.

    Returns:
        str: The STIX pattern string, or None if the IOC type is unsupported.
    """
    __method_name = inspect.currentframe().f_code.co_name
    pattern_template = STIX_PATTERN_MAP.get(ioc_type)
    if pattern_template is None:
        applogger.warning(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Unsupported IOC type: {}".format(ioc_type),
            )
        )
        return None
    return pattern_template.format(ioc_value)


def validate_ioc_value(ioc_type, ioc_value):
    """Validate the IOC value based on its type.

    Args:
        ioc_type (str): The Cyjax IOC type.
        ioc_value (str): The IOC value to validate.

    Returns:
        bool: True if the IOC value is valid, False otherwise.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        if not ioc_value or not ioc_value.strip():
            return False
        if ioc_type == "IPv4":
            ipaddress.IPv4Address(ioc_value)
            return True
        elif ioc_type == "IPv6":
            ipaddress.IPv6Address(ioc_value)
            return True
        elif ioc_type in ("Domain", "Hostname"):
            return "." in ioc_value and not ioc_value.startswith("http")
        elif ioc_type == "URL":
            return ioc_value.startswith("http://") or ioc_value.startswith("https://")
        elif ioc_type == "Email":
            return "@" in ioc_value
        return True
    except (ValueError, TypeError):
        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Validation failed for IOC type: {}, value: {}".format(ioc_type, ioc_value),
            )
        )
        return False


def map_confidence(handling_condition):
    """Map Cyjax handling_condition to STIX confidence score (0-100).

    Args:
        handling_condition (str): The Cyjax TLP handling condition (RED/AMBER/GREEN/WHITE).

    Returns:
        int: STIX confidence score.
    """
    if handling_condition:
        return CONFIDENCE_MAP.get(handling_condition.upper(), 50)
    return 50


def get_tlp_marking(handling_condition):
    """Get the STIX TLP marking definition reference for a handling condition.

    Args:
        handling_condition (str): The Cyjax TLP handling condition.

    Returns:
        str: The STIX marking definition ID, or None if not mapped.
    """
    if handling_condition:
        return TLP_MARKING_MAP.get(handling_condition.upper())
    return None


def _format_timestamp(timestamp_str):
    """Format a timestamp string to ISO 8601 with Z suffix.

    Args:
        timestamp_str (str): ISO8601 timestamp string.

    Returns:
        str: Formatted timestamp with Z suffix.
    """
    if not timestamp_str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if timestamp_str.endswith("Z"):
        return timestamp_str
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    except (ValueError, TypeError):
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _build_extensions(ioc_data, enrichment_data):
    """Build the STIX extensions object from IOC and enrichment data.

    Args:
        ioc_data (dict): The Cyjax IOC data.
        enrichment_data (dict): The Cyjax enrichment data (can be None).

    Returns:
        dict: The STIX extensions object.
    """
    __method_name = inspect.currentframe().f_code.co_name
    extension = {"extension_type": "property-extension"}
    if ioc_data.get("uuid"):
        extension["cyjax_uuid"] = ioc_data["uuid"]
    if ioc_data.get("source"):
        extension["cyjax_source"] = ioc_data["source"]
    if ioc_data.get("handling_condition"):
        extension["cyjax_handling_condition"] = ioc_data["handling_condition"]
    industry_type = ", ".join(ioc_data.get("industry_type", []))
    if industry_type:
        extension["cyjax_industry_type"] = industry_type
    ttp = ", ".join(ioc_data.get("ttp", []))
    if ttp:
        extension["cyjax_ttp"] = ttp
    if enrichment_data:
        if enrichment_data.get("type"):
            extension["enrichment_type"] = enrichment_data["type"]
        if enrichment_data.get("last_seen_timestamp"):
            extension["enrichment_last_seen_timestamp"] = enrichment_data["last_seen_timestamp"]
        geoip = enrichment_data.get("geoip", {})
        if geoip:
            if geoip.get("ip_address"):
                extension["enrichment_geoip_ip_address"] = geoip["ip_address"]
            if geoip.get("city"):
                extension["enrichment_geoip_city"] = geoip["city"]
            if geoip.get("country_name"):
                extension["enrichment_geoip_country_name"] = geoip["country_name"]
            if geoip.get("country_code"):
                extension["enrichment_geoip_country_code"] = geoip["country_code"]
        asn = enrichment_data.get("asn", {})
        if asn:
            if asn.get("organization"):
                extension["enrichment_asn_organization"] = asn["organization"]
            if asn.get("number") is not None:
                extension["enrichment_asn_number"] = str(asn["number"])
        sightings = enrichment_data.get("sightings", [])
        if sightings:
            total_sightings = sum(s.get("count", 0) for s in sightings)
            extension["enrichment_sightings_count"] = str(total_sightings)
            import json

            # Store only first 35 sightings to avoid Sentinel 25KB cell limit
            limited_sightings = sightings[: consts.SIGHTINGS_LIMIT]
            try:
                extension["enrichment_sightings"] = json.dumps(limited_sightings)
            except (TypeError, ValueError) as json_err:
                applogger.warning(
                    consts.LOG_FORMAT.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Failed to serialize sightings for IOC {}: {}".format(ioc_data.get("uuid", ""), json_err),
                    )
                )
            if len(sightings) > consts.SIGHTINGS_LIMIT:
                applogger.warning(
                    consts.LOG_FORMAT.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Sightings count {} exceeded limit {} for IOC: {}".format(
                            len(sightings), consts.SIGHTINGS_LIMIT, ioc_data.get("uuid", "")
                        ),
                    )
                )
                extension["enrichment_sightings_truncated"] = "true"
    return extension


def _build_external_references(ioc_data):
    """Build the STIX external_references array from IOC data.

    Args:
        ioc_data (dict): The Cyjax IOC data.

    Returns:
        list: The STIX external_references array.
    """
    references = []
    ref = {
        "source_name": "Cyjax",
        "description": "Cyjax IOC Source",
    }
    ioc_uuid = ioc_data.get("uuid", "")
    if ioc_uuid:
        ref["external_id"] = ioc_uuid
    source_url = ioc_data.get("source", "")
    if source_url:
        ref["url"] = source_url
    references.append(ref)
    return references


def _build_labels(ioc_data):
    """Build the STIX labels array from IOC data.

    Args:
        ioc_data (dict): The Cyjax IOC data.

    Returns:
        list: The STIX labels array.
    """
    labels = []
    ttp_list = ioc_data.get("ttp", [])
    if ttp_list:
        labels.extend(ttp_list)
    industry_list = ioc_data.get("industry_type", [])
    if industry_list:
        labels.extend(industry_list)
    handling = ioc_data.get("handling_condition", "")
    if handling:
        labels.append("TLP:{}".format(handling.upper()))
    return labels


def map_cyjax_ioc_to_stix(ioc_data, enrichment_data=None):
    """Map a Cyjax IOC record (with optional enrichment) to a STIX 2.1 indicator object.

    Args:
        ioc_data (dict): The Cyjax IOC data from the /indicator-of-compromise endpoint.
        enrichment_data (dict): The Cyjax enrichment data (optional, can be None).

    Returns:
        dict: A STIX 2.1 indicator object, or None if the IOC cannot be mapped.

    Raises:
        CyjaxException: If an unexpected error occurs during mapping.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        ioc_type = ioc_data.get("type", "")
        ioc_value = ioc_data.get("value", "")

        if not validate_ioc_value(ioc_type, ioc_value):
            applogger.warning(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    "Skipping invalid IOC: type={}, value={}".format(ioc_type, ioc_value),
                )
            )
            return None

        pattern = build_stix_pattern(ioc_type, ioc_value)
        if pattern is None:
            return None

        discovered_at = ioc_data.get("discovered_at", "")
        created_ts = _format_timestamp(discovered_at)
        valid_from_ts = created_ts

        handling_condition = ioc_data.get("handling_condition", "")
        confidence = map_confidence(handling_condition)
        tlp_marking = get_tlp_marking(handling_condition)

        stix_indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--{}".format(uuid.uuid4()),
            "created": created_ts,
            "modified": created_ts,
            "name": "Cyjax - {} - {}".format(ioc_type, ioc_value),
            "pattern": pattern,
            "pattern_type": "stix",
            "pattern_version": "2.1",
            "valid_from": valid_from_ts,
            "confidence": confidence,
            "labels": _build_labels(ioc_data),
            "description": ioc_data.get("description", ""),
            "external_references": _build_external_references(ioc_data),
            "extensions": _build_extensions(ioc_data, enrichment_data),
        }

        if tlp_marking:
            stix_indicator["object_marking_refs"] = [tlp_marking]

        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Mapped IOC to STIX: type={}, value={}".format(ioc_type, ioc_value),
            )
        )
        return stix_indicator

    except CyjaxException:
        raise
    except Exception as error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Error mapping IOC to STIX: {}".format(error),
            )
        )
        raise CyjaxException("Error mapping IOC to STIX: {}".format(error))
