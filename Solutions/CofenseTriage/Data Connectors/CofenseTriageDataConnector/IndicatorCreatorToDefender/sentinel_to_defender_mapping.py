"""This file contains function for mapping of sentinel and defender indicators."""
import inspect
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_exception import CofenseException


class SentinelToDefenderMapping:
    """To map field values of Sentinel and defender indicators."""

    def get_defender_indicator_value(self, indicator):
        """To convert sentinel indicator pattern to threat value."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            sentinel_pattern = indicator.get("properties", {}).get("pattern", None)
            if sentinel_pattern:
                return (sentinel_pattern.split("=")[1]).strip("' ]")
            else:
                raise CofenseException()
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Unknown indicator value from sentinel. "
                "Sentinel Indicator name : {}. Error : {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    indicator.get("properties", {}).get("displayName", None),
                    error,
                )
            )
            raise CofenseException()

    def get_defender_application_value(self, indicator):
        """To convert sentinel indicator pattern to threat value."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            sentinel_indicator_source = indicator.get("properties", {}).get(
                "source", None
            )
            if sentinel_indicator_source:
                return sentinel_indicator_source
            else:
                raise CofenseException()
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Unknown source value from sentinel. "
                "Sentinel Indicator name : {}. Error : {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    indicator.get("properties", {}).get("displayName", None),
                    error,
                )
            )
            raise CofenseException()

    def get_defender_indicator_type(self, indicator):
        """To convert sentinel indicator type to defender accepted indicator type."""
        # getting indicator type.
        __method_name = inspect.currentframe().f_code.co_name
        try:
            sentinel_indicator_pattern_type = indicator.get("properties", {}).get(
                "patternType", None
            )
            defender_indicator_pattern_type = None
            # if indicator type is url in sentinel then Url in defender.
            if sentinel_indicator_pattern_type == "url":
                defender_indicator_pattern_type = "Url"

            # if indicator type is domain-name in sentinel then DomainName in defender.
            elif sentinel_indicator_pattern_type == "domain-name":
                defender_indicator_pattern_type = "DomainName"

            elif (
                sentinel_indicator_pattern_type == "ipv4-addr"
                or sentinel_indicator_pattern_type == "ipv6-addr"
            ):
                defender_indicator_pattern_type = "IpAddress"

            # if indicator type is file in sentinel then FileMD5 or FileSha256 in defender.
            elif sentinel_indicator_pattern_type == "file":
                sentinel_indicator_pattern = indicator.get("properties", {}).get(
                    "pattern", None
                )
                if sentinel_indicator_pattern:
                    sentinel_file_pattern = sentinel_indicator_pattern.split("'")[1]
                    if sentinel_file_pattern == "MD5":
                        defender_indicator_pattern_type = "FileMd5"
                    elif sentinel_file_pattern == "SHA-256":
                        defender_indicator_pattern_type = "FileSha256"
                    else:
                        raise CofenseException()
                else:
                    raise CofenseException()
            else:
                raise CofenseException()
            return defender_indicator_pattern_type
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Unknown indicator type from sentinel. "
                "Sentinel Indicator name : {}. Error : {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    indicator.get("properties", {}).get("displayName", None),
                    error,
                )
            )
            raise CofenseException()

    def get_defender_action_and_severity(self, indicator):
        """To convert sentinel confidence value to defender action."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            confidence = indicator.get("properties", {}).get("confidence", "")
            actions = None
            severity = None
            if (
                confidence is None
                or confidence == ""
                or int(confidence) == 0
                or (
                    int(confidence) >= consts.THREAT_LEVEL_BENIGN
                    and int(confidence) <= consts.THREAT_LEVEL_INTERMEDIATE
                )
            ):
                actions = "Allowed"
                severity = "Informational"
                cofenes_threat_level = "Benign"
            elif (
                int(confidence) > consts.THREAT_LEVEL_INTERMEDIATE
                and int(confidence) <= consts.THREAT_LEVEL_SUSPICIOUS
            ):
                actions = "Warn"
                severity = "Medium"
                cofenes_threat_level = "Suspicious"
            elif (
                int(confidence) > consts.THREAT_LEVEL_SUSPICIOUS
                and int(confidence) <= consts.THREAT_LEVEL_MALICIOUS
            ):
                actions = "Block"
                severity = "High"
                cofenes_threat_level = "Malicious"
            else:
                raise CofenseException()
            return actions, severity, cofenes_threat_level
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Unknown confidence value from sentinel. "
                "Sentinel Indicator name : {}. Error : {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    indicator.get("properties", {}).get("displayName", None),
                    error,
                )
            )
            raise CofenseException()

    def get_defender_title(self, indicator):
        """To parse indicator title."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            sentinel_indicator_display_name = indicator.get("properties", {}).get(
                "displayName", None
            )
            if sentinel_indicator_display_name:
                return sentinel_indicator_display_name
            else:
                raise CofenseException()
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Unknown title from sentinel. "
                "Sentinel Indicator name : {}. Error : {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    indicator.get("properties", {}).get("displayName", None),
                    error,
                )
            )
            raise CofenseException()

    def get_defender_description(self, defender_severity, cofense_threat_level):
        """To parse defender indicator description."""
        return (
            consts.DEFENDER_CREATE_INDICATOR_DESCRIPTION
            + " Cofense Triage - {}. MS Defender - {}".format(
                cofense_threat_level, defender_severity
            )
        )
