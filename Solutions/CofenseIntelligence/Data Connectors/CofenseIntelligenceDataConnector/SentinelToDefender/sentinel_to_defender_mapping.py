"""This file contains function for mapping of sentinel and defender indicators."""
import inspect
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException


class SentinelToDefenderMapping:
    """To map field values of Sentinel and defender indicators."""

    def get_defender_indicator_value(self, indicator):
        """To convert sentinel indicator pattern to threat value."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            sentinel_pattern = indicator.get("properties", {}).get(
                "parsedPattern", None
            )
            if sentinel_pattern:
                sentinel_parsed_pattern_value = sentinel_pattern[0].get(
                    "patternTypeValues", None
                )
                if sentinel_parsed_pattern_value:
                    defender_indicator_value = sentinel_parsed_pattern_value[0].get(
                        "value", None
                    )
                    if defender_indicator_value:
                        return defender_indicator_value
                    else:
                        raise CofenseIntelligenceException()
                else:
                    raise CofenseIntelligenceException()
            else:
                raise CofenseIntelligenceException()
        except CofenseIntelligenceException as error:
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
            raise CofenseIntelligenceException()

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
            if sentinel_indicator_pattern_type == "URL":
                defender_indicator_pattern_type = "Url"

            # if indicator type is domain-name in sentinel then DomainName in defender.
            elif sentinel_indicator_pattern_type == "Domain Name":
                defender_indicator_pattern_type = "DomainName"

            # if indicator type is file in sentinel then FileMD5 in defender.
            elif sentinel_indicator_pattern_type.lower() == "file":
                defender_indicator_pattern_type = "FileMd5"

            else:
                raise CofenseIntelligenceException()
            return defender_indicator_pattern_type
        except CofenseIntelligenceException as error:
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
            raise CofenseIntelligenceException()

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
                or int(confidence) == consts.IMPACT_NONE
            ):
                actions = "Allowed"
                severity = "Informational"
            elif int(confidence) == consts.IMPACT_MINOR:
                actions = "Alert"
                severity = "Informational"
            elif (
                int(confidence) == consts.IMPACT_MODERATE
                or int(confidence) == consts.IMPACT_MEDIUM
            ):
                actions = "Warn"
                severity = "Medium"
            elif int(confidence) == consts.IMPACT_MAJOR:
                actions = "Block"
                severity = "High"
            else:
                raise CofenseIntelligenceException()
            return actions, severity
        except CofenseIntelligenceException as error:
            applogger.error(
                "{}(method={}) : {} : Unknown confidence value from sentinel. "
                "Sentinel Indicator name. Error : {}{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    error,
                    confidence,
                )
            )
            raise CofenseIntelligenceException()

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
                raise CofenseIntelligenceException()
        except CofenseIntelligenceException as error:
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
            raise CofenseIntelligenceException()

    def get_defender_description(self, indicator):
        """To parse defender indicator description."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            sentinel_indicator_description = indicator.get("properties", {}).get(
                "description", None
            )
            if sentinel_indicator_description:
                return sentinel_indicator_description
            else:
                raise CofenseIntelligenceException()
        except CofenseIntelligenceException as error:
            applogger.error(
                "{}(method={}) : {} : Unknown description from sentinel. "
                "Sentinel Indicator description : {}. Error : {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    indicator.get("properties", {}).get("displayName", None),
                    error,
                )
            )
            raise CofenseIntelligenceException()
