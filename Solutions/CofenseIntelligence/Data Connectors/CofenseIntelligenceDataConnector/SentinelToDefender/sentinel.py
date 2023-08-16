"""This file contains implementation of fetching sentinel TI indicator and creating defender indicator."""
import time
import json
import re
import inspect
from datetime import datetime, timedelta
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException
from ..SharedCode.state_manager import StateManager
from ..SharedCode.utils import Utils
from .defender import MicrosoftDefender
from .sentinel_to_defender_mapping import SentinelToDefenderMapping


class MicrosoftSentinel:
    """This class contains methods to get threat intelligence indicator from Microsoft Sentinel."""

    def __init__(self) -> None:
        """Initialize instance variable for class."""
        __method_name = inspect.currentframe().f_code.co_name
        # To check the environment variable.
        self.utils_obj = Utils(azure_function_name=consts.SENTINEL_TO_DEFENDER)
        self.utils_obj.validate_params()
        applogger.info(
            "{}(method={}) : {} : "
            "Started execution of posting cofense indicators into MS Defender from "
            "Microsoft Sentinel Threat Intelligence.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.SENTINEL_TO_DEFENDER,
            )
        )
        self.bearer_token = self.utils_obj.auth_sentinel()
        self.defender_object = MicrosoftDefender()
        self.sentinel_defender_mapping_obj = SentinelToDefenderMapping()
        self.get_sentinel_checkpoint_data()
        self.indicator_count = 0
        self.failed_indicator_count = 0
        self.failed_indicator_list = []
        self.total_indicator_count = 0
        self.total_failed_indicator_count = 0
        self.total_failed_indicator_list = []
        self.threat_id_regex = '[0-9]+'

    def convert_datetime_format(self, datetime_string):
        """To convert datetime string to datetime type for comparison of dates."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if datetime_string is None or datetime_string == "":
                return datetime_string
            else:
                return datetime.strptime(
                    (datetime_string).strip()[:26].rstrip("Z"),
                    consts.SENTINEL_DATETIME_FORMAT,
                )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} Error: {} : "
                "Expecting datetime in %Y-%m-%dT%H:%M:%S.%f format, getting datetime in {} format.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    error,
                    datetime_string,
                )
            )
            raise error

    def convert_sentinel_datetime_format(self, indicator):
        """To convert sentinel indicator lastUpdatedTimeUtc format."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            return self.convert_datetime_format(
                indicator.get("properties", {}).get("lastUpdatedTimeUtc")
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} Error: {} : "
                "Error occurred in Sentinel Threat Indicator with name: {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    error,
                    indicator.get("name", ""),
                )
            )
            raise error

    def complete_current_execution(self, __method_name):
        """To update the checkpoint fields in sentinel defender checkpoint state manager."""
        self.sentinel_checkpoint_json_data["new_execution_flag"] = "True"
        self.sentinel_checkpoint_json_data["last_execution_skip_token"] = ""
        self.sentinel_checkpoint_json_data[
            "current_checkpoint_indicator_date"
        ] = self.sentinel_checkpoint_json_data.get("next_checkpoint_indicator_date")
        self.sentinel_checkpoint_json_data["next_checkpoint_indicator_date"] = ""
        # Saving flag into the sentinel defender checkpoint state manager.
        try:
            self.sentinel_checkpoint_state.post(
                json.dumps(self.sentinel_checkpoint_json_data)
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} Error: {} : "
                "Error occurred while posting current checkpoint data to "
                "sentinel defender checkpoint state manager.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    error,
                )
            )
            raise error
        # Updating the flag value.
        self.new_execution_flag = self.sentinel_checkpoint_json_data.get(
            "new_execution_flag"
        )
        # Reset the checkpoint(skipToken) for next execution.
        self.sentinel_skiptoken = self.sentinel_checkpoint_json_data.get(
            "last_execution_skip_token"
        )
        self.current_checkpoint_indicator_date = self.convert_datetime_format(
            self.sentinel_checkpoint_json_data.get("current_checkpoint_indicator_date")
        )
        self.next_checkpoint_indicator_date = self.sentinel_checkpoint_json_data[
            "next_checkpoint_indicator_date"
        ]
        applogger.debug(
            "{}(method={}) : {}: "
            "Completed posting and updating current execution indicators from Microsoft Sentinel "
            "into MS Defender. Starting Next execution.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.SENTINEL_TO_DEFENDER,
            )
        )

        applogger.info(
            "{}(method={}) : {}: "
            "Checkpoint date stored : {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.SENTINEL_TO_DEFENDER,
                self.current_checkpoint_indicator_date,
            )
        )

    def check_cofense_indicator(self, indicator):
        """To check if the sentinel indicator is from cofense intelligence."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            source = indicator.get("properties", {}).get("source", None)
            if (
                source is not None
                and source.strip() != ""
                and source.startswith(consts.COFENSE_SOURCE_PREFIX)
            ):
                return True
            else:
                applogger.debug(
                    "{}(method={}) : {} : {} is not cofense indicator from Sentinel TI.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.SENTINEL_TO_DEFENDER,
                        indicator.get("properties", {}).get("displayName", None),
                    )
                )
                return False
        except CofenseIntelligenceException as error:
            applogger.error(
                "{}(method={}) : {} : Error occurred while checking cofense indicator from Sentinel TI. "
                "Sentinel indicator name : {}. Error : {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    indicator.get("properties", {}).get("displayName", None),
                    error,
                )
            )
            raise CofenseIntelligenceException()

    def create_indicator_data(self, indicator):
        """To create python dictionary for posting indicator into defender."""
        __method_name = inspect.currentframe().f_code.co_name
        sentinel_indicator_display_name = None
        try:
            sentinel_indicator_display_name = indicator.get("properties", {}).get(
                "displayName", None
            )
            indicator_data = {}
            # convert sentinel indicator type to defender indicator type.
            indicator_data[
                "indicatorType"
            ] = self.sentinel_defender_mapping_obj.get_defender_indicator_type(
                indicator
            )

            # Convert confidence integer to action and severity.
            (
                indicator_data["action"],
                indicator_data["severity"],
            ) = self.sentinel_defender_mapping_obj.get_defender_action_and_severity(
                indicator
            )

            # get the indicator value from the sentinel indicator data.
            indicator_data[
                "indicatorValue"
            ] = self.sentinel_defender_mapping_obj.get_defender_indicator_value(
                indicator
            )

            indicator_data[
                "title"
            ] = self.sentinel_defender_mapping_obj.get_defender_title(indicator)

            indicator_data[
                "description"
            ] = self.sentinel_defender_mapping_obj.get_defender_description(indicator)

        except CofenseIntelligenceException as error:
            applogger.error(
                "{}(method={}) : {} : Error occurred while generating MS Defender indicator payload. "
                "Sentinel indicator name : {}. Error : {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    sentinel_indicator_display_name,
                    error,
                )
            )
            self.total_failed_indicator_count += 1
            self.failed_indicator_count += 1
            threat_id = re.findall(self.threat_id_regex, sentinel_indicator_display_name)
            self.total_failed_indicator_list.append(threat_id[0])
            self.failed_indicator_list.append(threat_id[0])
        return indicator_data

    def new_execution_flag_is_true(self, current_indicator_updated_date, indicator):
        """Check if new execution flag is true. Created a method to reduce cognitive Complexity."""
        __method_name = inspect.currentframe().f_code.co_name
        if self.new_execution_flag == "True":
            if current_indicator_updated_date <= self.current_checkpoint_indicator_date:
                # exit the class. execution is completed.
                return False

            self.sentinel_checkpoint_json_data[
                "next_checkpoint_indicator_date"
            ] = indicator.get("properties", {}).get("lastUpdatedTimeUtc")
            self.sentinel_checkpoint_json_data["new_execution_flag"] = "False"
            try:
                self.sentinel_checkpoint_state.post(
                    json.dumps(self.sentinel_checkpoint_json_data)
                )
            except Exception as error:
                applogger.error(
                    "{}(method={}) : {} Error: {} : "
                    "Error occurred while posting checkpoint data to "
                    "sentinel defender checkpoint state manager.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.SENTINEL_TO_DEFENDER,
                        error,
                    )
                )
                raise error
            self.next_checkpoint_indicator_date = (
                self.sentinel_checkpoint_json_data.get("next_checkpoint_indicator_date")
            )
            applogger.debug(
                "{}(method={}) : {}: "
                "Next execution checkpoint date stored : {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    self.next_checkpoint_indicator_date,
                )
            )
            self.new_execution_flag = self.sentinel_checkpoint_json_data.get(
                "new_execution_flag"
            )
        return None
    def post_indicators(self, sentinel_json_indicator_list, defender_object):
        """To post and update the indicators into MS Defender."""
        try:
            __method_name = inspect.currentframe().f_code.co_name

            applogger.debug(
                "{}(method={}) : {} : "
                "Posting and updating indicators into MS Defender.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                )
            )
            # posting and updating indicators
            for indicator in sentinel_json_indicator_list:
                current_indicator_updated_date = self.convert_sentinel_datetime_format(
                    indicator=indicator
                )

                if (
                    self.new_execution_flag_is_true(
                        current_indicator_updated_date, indicator
                    )
                    is False
                ):
                    return False

                # Completed current execution.
                if (
                    current_indicator_updated_date
                    <= self.current_checkpoint_indicator_date
                ):
                    self.complete_current_execution(__method_name)
                    return True

                # Creating indicator into defender.
                try:
                    # bool to find cofense indicator.
                    cofense_indicator = self.check_cofense_indicator(indicator)

                    # Create indicator data for defender.
                    indicator_data = self.create_indicator_data(indicator)

                    if (
                        cofense_indicator
                        and indicator_data.get("indicatorValue", None)
                        and indicator_data.get("indicatorType", None)
                        and indicator_data.get("title", None)
                        and indicator_data.get("action", None)
                        and indicator_data.get("description", None)
                    ):
                        self.create_indicator(
                            defender_object=defender_object,
                            indicator_data=indicator_data,
                        )

                        # Update the total executed indicators count.
                        self.total_indicator_count += 1
                        self.indicator_count += 1
                except CofenseIntelligenceException as error:
                    applogger.error(
                        "{}(method={}) : {} : Error occurred while posting indicator into MS Defender. "
                        "Sentinel indicator name : {}. Error : {}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            indicator_data.get("title"),
                            error,
                        )
                    )
                    self.total_failed_indicator_count += 1
                    self.failed_indicator_count += 1
                    threat_id = re.findall(self.threat_id_regex, indicator_data.get("title"))
                    self.total_failed_indicator_list.append(threat_id[0])
                    self.failed_indicator_list.append(threat_id[0])
            # Completed current execution.
            return True

        except CofenseIntelligenceException as error:
            applogger.error(
                "{}(method={}) : {} : Error occurred while posting indicator into MS Defender : {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    error,
                )
            )
            raise CofenseIntelligenceException()

    def create_indicator(
        self,
        defender_object,
        indicator_data,
    ):
        """To create indicators into defender."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            # Posting indicator into defender.
            create_indicator_status_code = defender_object.create_defender_indicator(
                indicator_data=indicator_data
            )

            if create_indicator_status_code == 400:
                self.total_failed_indicator_count += 1
                self.failed_indicator_count += 1
                threat_id = re.findall(self.threat_id_regex, indicator_data.get("title"))
                self.total_failed_indicator_list.append(threat_id[0])
                self.failed_indicator_list.append(threat_id[0])

        except CofenseIntelligenceException as error:
            applogger.error(
                "{}(method={}) : {} : Error occurred while creating indicator in MS Defender : {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    error,
                )
            )
            raise CofenseIntelligenceException()

    def get_sentinel_checkpoint_data(self):
        """To get the sentinel defender checkpoint data from state manager."""
        __method_name = inspect.currentframe().f_code.co_name
        # Initializing state manager for sentinel and defender indicator id table.
        self.sentinel_checkpoint_state = StateManager(
            connection_string=consts.CONNECTION_STRING,
            file_path=consts.DEFENDER_CHECKPOINT_FILE_PATH,
        )
        try:
            sentinel_checkpoint_data = self.sentinel_checkpoint_state.get(
                consts.SENTINEL_TO_DEFENDER
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} Error: {} : "
                "Error occurred while getting sentinel defender checkpoint data from "
                "sentinel defender checkpoint state manager.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    error,
                )
            )
            raise error

        # If checkpoint data is not none, then fetch the checkpoint fields.
        if sentinel_checkpoint_data is not None:
            self.sentinel_checkpoint_json_data = json.loads(sentinel_checkpoint_data)
            self.new_execution_flag = self.sentinel_checkpoint_json_data.get(
                "new_execution_flag"
            )
            self.current_checkpoint_indicator_date = (
                self.sentinel_checkpoint_json_data.get(
                    "current_checkpoint_indicator_date"
                )
            )
            self.next_checkpoint_indicator_date = (
                self.sentinel_checkpoint_json_data.get("next_checkpoint_indicator_date")
            )
            if self.new_execution_flag == "False":
                self.sentinel_skiptoken = self.sentinel_checkpoint_json_data.get(
                    "last_execution_skip_token"
                )
                applogger.debug(
                    "{}(method={}) : {}: "
                    "Last checkpoint skip token is : {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.SENTINEL_TO_DEFENDER,
                        self.sentinel_skiptoken,
                    )
                )
            else:
                self.sentinel_skiptoken = ""
            applogger.debug(
                "{}(method={}) : {} : "
                "Sentinel defender checkpoint state manager data fetch successfully.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                )
            )

            # Convert string date to datetime object.
            self.current_checkpoint_indicator_date = self.convert_datetime_format(
                self.sentinel_checkpoint_json_data.get(
                    "current_checkpoint_indicator_date"
                )
            )
            applogger.info(
                "{}(method={}) : {} : "
                "Last checkpoint date is : {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    self.current_checkpoint_indicator_date,
                )
            )

        else:
            # If checkpoint is none then initialize from starting.
            # If checkpoint file is not found then, it is first run.
            self.sentinel_checkpoint_json_data = {}
            self.sentinel_checkpoint_json_data["new_execution_flag"] = "True"
            self.sentinel_checkpoint_json_data["last_execution_skip_token"] = ""
            # In first run we need to fetch last 15 days of indicators from sentinel TI.
            current_date = datetime.now()
            current_date_utc = current_date.utcnow()
            self.sentinel_checkpoint_json_data["current_checkpoint_indicator_date"] = (
                current_date_utc
                - timedelta(
                    days=15,
                    seconds=current_date_utc.second,
                    microseconds=(current_date_utc.microsecond - 1),
                    minutes=current_date_utc.minute,
                    hours=current_date_utc.hour,
                )
            ).isoformat()
            self.sentinel_checkpoint_json_data["next_checkpoint_indicator_date"] = ""
            try:
                self.sentinel_checkpoint_state.post(
                    json.dumps(self.sentinel_checkpoint_json_data)
                )
            except Exception as error:
                applogger.error(
                    "{}(method={}) : {} Error: {} : "
                    "Error occurred while posting checkpoint data to "
                    "sentinel defender checkpoint state manager.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.SENTINEL_TO_DEFENDER,
                        error,
                    )
                )
                raise error
            self.new_execution_flag = self.sentinel_checkpoint_json_data.get(
                "new_execution_flag"
            )
            self.sentinel_skiptoken = self.sentinel_checkpoint_json_data.get(
                "last_execution_skip_token"
            )
            self.next_checkpoint_indicator_date = (
                self.sentinel_checkpoint_json_data.get("next_checkpoint_indicator_date")
            )

            applogger.info(
                "{}(method={}) : {} : "
                "Sentinel defender checkpoint state manager data not found. Creating it.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                )
            )

            # Convert string date to datetime object.
            self.current_checkpoint_indicator_date = self.convert_datetime_format(
                self.sentinel_checkpoint_json_data.get(
                    "current_checkpoint_indicator_date"
                )
            )
            applogger.info(
                "{}(method={}) : {} : "
                "Getting indicators data of last 15 days from : {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    self.current_checkpoint_indicator_date,
                )
            )

    def update_checkpoint(self, sentinel_indicator_nextlink):
        """To update the checkpoint in state manager."""
        __method_name = inspect.currentframe().f_code.co_name

        if (
            sentinel_indicator_nextlink is not None
            and sentinel_indicator_nextlink != ""
        ):
            # Checkpoint is managed by skipToken fetched in nextLink in sentinel response.
            self.sentinel_skiptoken = sentinel_indicator_nextlink.split("$skipToken=")[
                1
            ]

            self.sentinel_checkpoint_json_data[
                "last_execution_skip_token"
            ] = self.sentinel_skiptoken
            try:
                self.sentinel_checkpoint_state.post(
                    json.dumps(self.sentinel_checkpoint_json_data)
                )
            except Exception as error:
                applogger.error(
                    "{}(method={}) : {} Error: {} : "
                    "Error occurred while posting current checkpoint data to "
                    "sentinel defender checkpoint state manager.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.SENTINEL_TO_DEFENDER,
                        error,
                    )
                )
                raise error
            applogger.debug(
                "{}(method={}) : {} : "
                "Skip Token stored as checkpoint : {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    self.sentinel_skiptoken,
                )
            )

        else:
            # If there is no further indicators from sentinel TI.
            self.complete_current_execution(__method_name)

    def get_indicators_from_sentinel(self):
        """To get indicators from Microsoft Sentinel threat intelligence."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            applogger.info(
                "{}(method={}) : {} : "
                "Started fetching cofense indicators from Microsoft Sentinel Threat Intelligence.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                )
            )
            retry_count_429 = 0
            retry_count_401 = 0
            while retry_count_429 <= 3 and retry_count_401 <= 1:
                query_indicator_url = consts.QUERY_SENTINEL_INDICATORS_URL.format(
                    subscriptionId=consts.AZURE_SUBSCRIPTION_ID,
                    resourceGroupName=consts.AZURE_RESOURCE_GROUP,
                    workspaceName=consts.AZURE_WORKSPACE_NAME,
                )
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(self.bearer_token),
                }
                body = {
                    "pageSize": consts.QUERY_SENTINEL_PAGESIZE,
                    "keywords": "Cofense",
                    "sortBy": [
                        {"itemKey": "lastUpdatedTimeUtc", "sortOrder": "descending"}
                    ],
                    "skipToken": self.sentinel_skiptoken,
                }
                utils_obj = Utils(azure_function_name=consts.SENTINEL_TO_DEFENDER)
                get_indicator_response = utils_obj.make_http_request(
                    url=query_indicator_url,
                    method="POST",
                    body=json.dumps(body),
                    headers=headers,
                )

                # If response status code is 200 to 299.
                if (
                    get_indicator_response.status_code >= 200
                    and get_indicator_response.status_code <= 299
                ):
                    sentinel_indicator_json = json.loads(get_indicator_response.text)
                    sentinel_indicator_json_list = sentinel_indicator_json.get(
                        "value", []
                    )
                    # Posting indicators into defender.
                    post_indicators_return = self.post_indicators(
                        sentinel_json_indicator_list=sentinel_indicator_json_list,
                        defender_object=self.defender_object,
                    )

                    applogger.info(
                        "{}(method={}) : {}. "
                        "In current page, Processed total Cofense Indicators - {}, Successfully created indicator(s) - {}, Failed  indicator(s) - {}."
                        " Failed indicator list: {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            self.indicator_count,
                            (self.indicator_count - self.failed_indicator_count),
                            self.failed_indicator_count,
                            self.failed_indicator_list,
                        )
                    )
                    self.indicator_count = 0
                    self.failed_indicator_count = 0
                    self.failed_indicator_list = []
                    applogger.info(
                        "{}(method={}) : {}. "
                        "In current function execution, Processed total Cofense Indicators - {}, Successfully created indicator(s) - {}, Failed  indicator(s) - {}."
                        " Failed indicator list: {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            self.total_indicator_count,
                            (
                                self.total_indicator_count
                                - self.total_failed_indicator_count
                            ),
                            self.total_failed_indicator_count,
                            self.total_failed_indicator_list,
                        )
                    )

                    # If return is False, it means no more indicator to fetch. So exit the python file.
                    if post_indicators_return is False:
                        applogger.warning(
                            "{}(method={}) : {}: url: {}, Status Code : {} : "
                            "No more indicators to fetch from Microsoft Sentinel. Exiting the function app.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.SENTINEL_TO_DEFENDER,
                                query_indicator_url,
                                get_indicator_response.status_code,
                            )
                        )
                        # Exit from function app.
                        return True

                    # Updating the checkpoint.
                    if self.new_execution_flag == "False":
                        sentinel_indicator_nextlink = sentinel_indicator_json.get(
                            "nextLink", ""
                        )
                        self.update_checkpoint(sentinel_indicator_nextlink)

                # response status code is 429.
                elif get_indicator_response.status_code == 429:
                    retry_count_429 += 1
                    applogger.error(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "Getting 429 from sentinel get indicators api call. Retrying again after {} seconds.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            consts.SENTINEL_429_SLEEP,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                        "Getting 429 from sentinel get indicators api call. Retry count: {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                            get_indicator_response.text,
                            retry_count_429,
                        )
                    )
                    # sleep for 60 seconds.
                    time.sleep(consts.SENTINEL_429_SLEEP)

                # response is 401, access token is expired.
                elif get_indicator_response.status_code == 401:
                    retry_count_401 = retry_count_401 + 1
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}:  Error Reason: {} : "
                        "Sentinel access token expired, generating new access token.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {} : url: {}, Status Code : {}, Error Reason: {}, Response: {} : Sentinel"
                        " access token expired, generating new access token. Retry count: {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                            get_indicator_response.text,
                            retry_count_401,
                        )
                    )
                    self.bearer_token = self.utils_obj.auth_sentinel()

                # response status code is not 200 to 299, 429 and 401.
                else:
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {} : Error while fetching indicators"
                        " from sentinel threat intelligence. Error Reason: {}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {} : url: {}, Status Code : {}, Error Reason: {}, Response: {} :"
                        " Error while fetching indicators from sentinel threat intelligence.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                            get_indicator_response.text,
                        )
                    )
                    # raise the exception to exit the function app.
                    raise CofenseIntelligenceException()

            # retry count exceeded.
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded for fetching indicators from sentinel.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                )
            )
            # raising the exception to exit the function app.
            raise CofenseIntelligenceException()

        except CofenseIntelligenceException:
            raise CofenseIntelligenceException()
