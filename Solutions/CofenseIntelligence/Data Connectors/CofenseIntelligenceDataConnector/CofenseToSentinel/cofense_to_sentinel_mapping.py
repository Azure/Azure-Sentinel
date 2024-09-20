"""This file contains methods for mapping between cofense and sentinel."""
import inspect
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException


def map_indicator_fields(indicator):
    """Map indicator fields for sentinel indicator.

    Args:
        indicator (dict): Indicator fetched from Cofense Intelligence
        azure_function_name (str): Azure Function Name

    Returns:
        dict: mapped indicator
    """
    try:
        __method_name = inspect.currentframe().f_code.co_name
        confidence = ""
        if indicator.get("impact", "") == "Major":
            confidence = 100
        elif indicator.get("impact", "") == "Medium":
            confidence = 70
        elif indicator.get("impact", "") == "Moderate":
            confidence = 50
        elif indicator.get("impact", "") == "Minor":
            confidence = 30
        elif indicator.get("impact", "") == "None":
            confidence = 1
        pattern = ""
        if indicator.get("indicator_type", "") == "URL":
            pattern = "url:value ="
        elif indicator.get("indicator_type", "") == "File":
            pattern = "file:hashes.'MD5' ="
        elif indicator.get("indicator_type", "") == "Domain Name":
            pattern = "domain-name:value ="

        sentinel_indicator = {
            "kind": "indicator",
            "properties": {
                "source": "Cofense Intelligence",
                "displayName": "Cofense intelligence: {}".format(
                    indicator.get("threat_id", "")
                ),
                "confidence": confidence,
                "description": "Role: {}".format(indicator.get("role", "")),
                "threatTypes": [indicator.get("indicator_type", "")],
                "indicatorTypes": [indicator.get("indicator_type", "")],
                "pattern": "[{} '{}']".format((pattern), indicator.get("ioc", "")),
                "patternType": indicator.get("indicator_type", ""),
                "labels": ["threatID-{}".format(indicator.get("threat_id", ""))],
            },
        }
        applogger.info(
            "{}(method={}) : {} : Indicator Field Mapping is done for threat {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.COFENSE_TO_SENTINEL,
                indicator.get("threat_id", ""),
            )
        )
        return sentinel_indicator
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Error occured :{}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.COFENSE_TO_SENTINEL,
                error
            )
        )
        raise CofenseIntelligenceException()
