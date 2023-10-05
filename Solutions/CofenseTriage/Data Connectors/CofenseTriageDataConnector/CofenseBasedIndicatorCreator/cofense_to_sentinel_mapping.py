"""This file contains implementation of mapping of cofense data to sentinel indicator."""
import json
import inspect
import datetime
from .sentinel import MicrosoftSentinel
from ..SharedCode.consts import (
    LOGS_STARTS_WITH,
    COFENSE_BASE_URL,
    ENDPOINTS,
    CONNECTION_STRING,
    COFENSE_TO_SENTINEL,
    COFENSE_SOURCE_PREFIX,
    SENTINEL_SOURCE_PREFIX,
    REPORTS_TABLE_NAME,
    COFENSE_PAGE_NUMBER,
    COFENSE_PAGE_SIZE,
    DATETIMEFORMAT,
)
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_exception import CofenseException
from ..SharedCode.state_manager import StateManager
from ..SharedCode.utils import check_environment_var_exist, cofense_to_sentinel_threat_level_mapping
from .cofense import CofenseTriage


class CofenseToSentinelMapping:
    """This class contains methods to pull the data from cofense apis and transform it to create TI indicator."""

    def __init__(self):
        """Initialize instance variable for class."""
        check_environment_var_exist(COFENSE_TO_SENTINEL)
        self.cofense_triage_obj = CofenseTriage()
        self.microsoft_obj = MicrosoftSentinel()
        self.log_type = REPORTS_TABLE_NAME
        self.state_obj = StateManager(
            connection_string=CONNECTION_STRING, file_path="cofense"
        )
        self.cofense_page_number = "page[number]"

    def source_mapping(self, indicator):
        """To map cofense source with sentinel source for microsoft sentinel indicator data."""
        response_source = indicator.get("attributes", {}).get("threat_source", "")
        splitted_source = response_source.split(":")
        source = None
        if (
            splitted_source[0].lower().strip()
            != SENTINEL_SOURCE_PREFIX.split(":")[0].lower().strip()
        ):
            source = COFENSE_SOURCE_PREFIX + response_source
        return source

    def pattern_type_mapping(self, indicator_threat_type):
        """To map threat type with patternType for microsoft sentinel indicator data."""
        threat_type = ""
        indicator_threat_type = indicator_threat_type.lower()
        if indicator_threat_type == "url":
            threat_type = "url"
        elif indicator_threat_type == "hostname":
            threat_type = "domain-name"
        elif indicator_threat_type == "sha256" or indicator_threat_type == "md5":
            threat_type = "file"
        return threat_type

    def pattern_mapping(
        self, threat_type, indicator_threat_value, indicator_threat_type
    ):
        """To map threat value with pattern for microsoft sentinel indicator data."""
        pattern = ""
        if threat_type == "url":
            indicator_threat_value_url = (
                indicator_threat_value.replace("\\n", "").replace("\\r", "").replace("\\u", "").replace("\\", "")
            )
            pattern = "[url:value = '{}']".format(indicator_threat_value_url)
        elif threat_type == "domain-name":
            pattern = "[domain-name:value = '{}']".format(indicator_threat_value)
        elif threat_type == "file":
            if indicator_threat_type == "SHA256":
                pattern = "[file:hashes.'SHA-256' = '{}']".format(
                    indicator_threat_value
                )
            elif indicator_threat_type == "MD5":
                pattern = "[file:hashes.'MD5' = '{}']".format(indicator_threat_value)
        return pattern

    def report_link_mapping(self, indicator):
        """To get the report link from the cofense indicator."""
        report_link = (
            indicator.get("relationships", {})
            .get("reports", {})
            .get("links", {})
            .get("related", "")
        )
        return report_link

    def data_mapping(self, indicator_data):
        """To map the data and create indicators into sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            report_data = []
            checkpoint = ""
            for indicator in indicator_data:
                checkpoint = indicator.get("attributes", {}).get("updated_at", "")
                data = {"kind": "indicator"}
                data["properties"] = {}

                source_cofence = self.source_mapping(indicator)
                if source_cofence:
                    data["properties"]["source"] = source_cofence
                else:
                    applogger.debug(
                        "{}(method={}) : {} : skipping the sentinel indicator.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            COFENSE_TO_SENTINEL,
                        )
                    )
                    data = {}
                    continue
                indicator_id = indicator.get("id", "")
                data["properties"]["displayName"] = "Cofense Triage : {}".format(
                    indicator_id
                )
                indicator_threat_level = indicator.get("attributes", {}).get("threat_level", "")
                threat_level = cofense_to_sentinel_threat_level_mapping(indicator_threat_level, COFENSE_TO_SENTINEL)
                data["properties"]["confidence"] = threat_level

                indicator_threat_type = indicator.get("attributes", {}).get("threat_type", "")
                threat_type = self.pattern_type_mapping(indicator_threat_type)

                if threat_type:
                    data["properties"]["patternType"] = threat_type
                else:
                    applogger.debug(
                        "{}(method={}) : {} : skipping the threat type {}".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            COFENSE_TO_SENTINEL,
                            indicator_threat_type,
                        )
                    )
                    data = {}
                    continue
                data["properties"]["threatTypes"] = [threat_type]
                indicator_threat_value = indicator.get("attributes", {}).get("threat_value", "")
                pattern = self.pattern_mapping(
                    threat_type, indicator_threat_value, indicator_threat_type
                )
                if pattern:
                    data["properties"]["pattern"] = pattern
                else:
                    applogger.debug(
                        "{}(method={}) : {} : skipping the threat type {}".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            COFENSE_TO_SENTINEL,
                            indicator_threat_type,
                        )
                    )
                    data = {}
                    continue
                data["properties"]["created"] = indicator.get("attributes", {}).get(
                    "created_at", ""
                )
                data["properties"]["externalLastUpdatedTimeUtc"] = indicator.get(
                    "attributes", {}
                ).get("updated_at", "")
                report_link = self.report_link_mapping(indicator)
                if report_link:
                    applogger.debug(
                        "{}(method={}) : {} : report link : {}".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            COFENSE_TO_SENTINEL,
                            report_link,
                        )
                    )
                else:
                    applogger.warning(
                        "{}(method={}) : {} : no report link found.".format(
                            LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                        )
                    )
                indicator_response = self.microsoft_obj.create_indicator(data)
                indicator_externalId = indicator_response.get("properties", {}).get("externalId", "")
                applogger.debug(
                    "{}(method={}) : {}: indicator created successfully.".format(
                        LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                    )
                )
                updated_at = indicator.get("attributes", {}).get("updated_at", "")
                reportdata = {
                    "indicator_id": indicator_id,
                    "external_id": "{}-{}".format(indicator_externalId, source_cofence),
                    "report_link": report_link,
                    "updated_at": updated_at
                }
                report_data.append(reportdata)
                data = {}
            return report_data, checkpoint
        except CofenseException:
            applogger.error(
                "{}(method={}) : {} : error occurred while mapping data of indicators.".format(
                    LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                )
            )
            raise CofenseException()

    def create_sentinel_indicator(self):
        """To map cofense data to microsoft sentinel indicator data."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                "{}(method={}) : {}: started creating indicators in microsoft sentinel.".format(
                    LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                )
            )
            list_indicator_url = "{}{}".format(COFENSE_BASE_URL, ENDPOINTS["get_lists"])
            params = {
                self.cofense_page_number: COFENSE_PAGE_NUMBER,
                "page[size]": COFENSE_PAGE_SIZE,
                "sort": "updated_at",
            }
            last_checkpoint = self.state_obj.get(COFENSE_TO_SENTINEL)
            # To do: remove "is not None".
            if last_checkpoint is not None:
                params["filter[updated_at_gteq]"] = last_checkpoint
                applogger.info(
                    "{}(method={}) : {} : last checkpoint is {}".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        COFENSE_TO_SENTINEL,
                        last_checkpoint,
                    )
                )
            else:
                today_datetime = datetime.datetime.utcnow() - datetime.timedelta(
                    days=15
                )
                from_datetime = datetime.datetime.strftime(
                    today_datetime, DATETIMEFORMAT
                )
                params["filter[updated_at_gteq]"] = from_datetime
                applogger.info(
                    "{}(method={}) : {} : getting indicators data of last 15 days from {}".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        COFENSE_TO_SENTINEL,
                        from_datetime,
                    )
                )
            applogger.debug(
                "{}(method={}) : {} : when getting indicators URL: {}, headers: {}".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    COFENSE_TO_SENTINEL,
                    list_indicator_url,
                    self.cofense_triage_obj.headers,
                )
            )
            while True:
                indicators_data_json = (
                    self.cofense_triage_obj.get_indicators_from_cofense(
                        url=list_indicator_url, params=params
                    )
                )
                indicator_data = indicators_data_json.get("data", [])
                if indicator_data:
                    report_data, checkpoint = self.data_mapping(indicator_data)
                    if report_data:
                        self.microsoft_obj.post_data(
                            json.dumps(report_data), self.log_type
                        )
                    else:
                        applogger.warning(
                            "{}(method={}) : {} : no new report data found in the indicator.".format(
                                LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                            )
                        )
                    if checkpoint:
                        datetime_checkpoint = datetime.datetime.strptime(
                            checkpoint, DATETIMEFORMAT
                        ) + datetime.timedelta(milliseconds=1)
                        latest_checkpoint = datetime.datetime.strftime(
                            datetime_checkpoint, DATETIMEFORMAT
                        )
                        self.state_obj.post(latest_checkpoint)
                        applogger.info(
                            "{}(method={}) : {} : checkpoint saved {}".format(
                                LOGS_STARTS_WITH,
                                __method_name,
                                COFENSE_TO_SENTINEL,
                                latest_checkpoint,
                            )
                        )
                    else:
                        applogger.info(
                            "{}(method={}) : {} : no new checkpoint found.".format(
                                LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                            )
                        )
                    if not indicators_data_json.get("links", {}).get("next", ""):
                        applogger.info(
                            "{}(method={}) : {} : all indicators created successfully.".format(
                                LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                            )
                        )
                        break
                    params[self.cofense_page_number] += 1
                else:
                    applogger.warning(
                        "{}(method={}) : {} : no new indicator data found.".format(
                            LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                        )
                    )
                    break
        except CofenseException:
            raise CofenseException()
