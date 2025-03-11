"""This file contains implementation of fetching sentinel TI indicator and creating cofense indicator."""
import time
import json
import inspect
from datetime import datetime, timedelta
from ..SharedCode.consts import (
    AZURE_SUBSCRIPTION_ID,
    AZURE_RESOURCE_GROUP,
    AZURE_WORKSPACE_NAME,
    LOGS_STARTS_WITH,
    CONNECTION_STRING,
    QUERY_SENTINEL_INDICATORS_URL,
    QUERY_SENTINEL_PAGESIZE,
    SENTINEL_TO_COFENSE,
    SENTINEL_429_SLEEP,
    SENTINEL_SOURCE_PREFIX,
    SENTINEL_DATETIME_FORMAT,
    NON_COFENSE_THROTTLE_LIMIT,
)
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_exception import CofenseException
from ..SharedCode.state_manager import StateManager
from ..SharedCode.utils import (
    auth_sentinel,
    make_rest_call,
    sentinel_to_cofense_threat_level_mapping,
    check_environment_var_exist,
)
from .cofense import CofenseTriage
from .sentinel_to_cofense_mapping import SentinelToCofenseMapping


class MicrosoftSentinel:
    """This class contains methods to get threat intelligence indicator from Microsoft Sentinel."""

    def __init__(self) -> None:
        """Initialize instance variable for class."""
        __method_name = inspect.currentframe().f_code.co_name
        # To check the environment variable.
        check_environment_var_exist(SENTINEL_TO_COFENSE)
        applogger.info(
            "{}(method={}) : {} : "
            "Started execution of posting indicators into Cofense Triage from "
            "Microsoft Sentinel Threat Intelligence.".format(
                LOGS_STARTS_WITH,
                __method_name,
                SENTINEL_TO_COFENSE,
            )
        )
        self.bearer_token = auth_sentinel(SENTINEL_TO_COFENSE)
        self.cofense_object = CofenseTriage()
        self.sentinel_cofense_mapping_obj = SentinelToCofenseMapping()
        self.get_sentinel_checkpoint_data()
        self.get_sentinel_cofense_id_table()
        self.indicator_count = 0
        self.page_size = 100
        self.throttle_flag = False
        self.set_throttle_limit()

    def set_throttle_limit(self):
        """To add a limit in indicator creation in MS Defender in one execution."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            throttle_input = NON_COFENSE_THROTTLE_LIMIT
            if throttle_input == "None":
                self.page_size = QUERY_SENTINEL_PAGESIZE
                self.throttle_flag = False
            elif (
                throttle_input.isdigit()
                and int(throttle_input) >= 1
                and int(throttle_input) <= 100
            ):
                self.page_size = int(throttle_input)
                self.throttle_flag = True
            else:
                raise CofenseException(
                    "Invalid non cofense throttle limit. Valid limit range is from 1 to 100 "
                    "and None(for no throttling)"
                )
        except Exception as error:
            applogger.warning(
                "{}(method={}) : {} : "
                "Error occurred while getting the throttle limit for non cofense indicators. "
                "Error : {}. Starting normal execution(without throttle limit).".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
                )
            )
            self.page_size = QUERY_SENTINEL_PAGESIZE
            self.throttle_flag = False

    def get_sentinel_checkpoint_data(self):
        """To get the sentinel checkpoint data from state manager."""
        __method_name = inspect.currentframe().f_code.co_name
        # Initializing state manager for sentinel and cofense indicator id table.
        self.sentinel_checkpoint_state = StateManager(
            connection_string=CONNECTION_STRING,
            file_path="sentinel_checkpoint",
        )
        try:
            sentinel_checkpoint_data = self.sentinel_checkpoint_state.get(
                SENTINEL_TO_COFENSE
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} Error: {} : "
                "Error occurred while getting sentinel checkpoint data from sentinel checkpoint state manager.".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
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
                        LOGS_STARTS_WITH,
                        __method_name,
                        SENTINEL_TO_COFENSE,
                        self.sentinel_skiptoken,
                    )
                )
            else:
                self.sentinel_skiptoken = ""
            applogger.debug(
                "{}(method={}) : {} : "
                "Sentinel checkpoint state manager data fetch successfully.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
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
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
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
            self.sentinel_checkpoint_json_data["current_checkpoint_indicator_date"] = (
                datetime.utcnow() - timedelta(days=15)
            ).isoformat()
            self.sentinel_checkpoint_json_data["next_checkpoint_indicator_date"] = ""
            try:
                self.sentinel_checkpoint_state.post(
                    json.dumps(self.sentinel_checkpoint_json_data)
                )
            except Exception as error:
                applogger.error(
                    "{}(method={}) : {} Error: {} : "
                    "Error occurred while posting checkpoint data to sentinel checkpoint state manager.".format(
                        LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
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
                "Sentinel checkpoint state manager data not found. Creating it.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
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
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
                    self.current_checkpoint_indicator_date,
                )
            )

    def convert_datetime_format(self, datetime_string):
        """To convert datetime string to datetime type for comparison of dates."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if datetime_string is None or datetime_string == "":
                return datetime_string
            else:
                # To do: Check with Z in datetime format.
                return datetime.strptime(
                    (datetime_string).strip()[:26].rstrip("Z"),
                    SENTINEL_DATETIME_FORMAT,
                )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} Error: {} : "
                "Expecting datetime in %Y-%m-%dT%H:%M:%S.%f format, getting datetime in {} format.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
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
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
                    error,
                    indicator.get("name", ""),
                )
            )
            raise error

    def get_sentinel_cofense_id_table(self):
        """To get sentinel cofense id table from state manager."""
        __method_name = inspect.currentframe().f_code.co_name
        # Initializing state manager for sentinel and cofense indicator id table.
        self.sentinel_cofense_id_table_state = StateManager(
            connection_string=CONNECTION_STRING,
            file_path="sentinel_cofense_id_table",
        )
        try:
            sentinel_cofense_id_table_data = self.sentinel_cofense_id_table_state.get(
                SENTINEL_TO_COFENSE
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} Error: {} : "
                "Error occurred while getting sentinel cofense mapping id table data "
                "from sentinel cofense id table state manager.".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
                )
            )
            raise error

        # To do: remove "is not None".
        if sentinel_cofense_id_table_data is not None:
            self.sentinel_cofense_id_table = json.loads(sentinel_cofense_id_table_data)
            applogger.info(
                "{}(method={}) : {} : "
                "Sentinel Cofense ID table successfully fetched.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
                )
            )
        else:
            # if table data is none then initialize the id table.
            self.sentinel_cofense_id_table = {}
            applogger.info(
                "{}(method={}) : {} : "
                "Sentinel Cofense ID table not found. Creating it.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
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
                    "Error occurred while posting current checkpoint data to sentinel checkpoint state manager.".format(
                        LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
                    )
                )
                raise error
            applogger.debug(
                "{}(method={}) : {} : "
                "Skip Token stored as checkpoint : {}".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
                    self.sentinel_skiptoken,
                )
            )

        else:
            # If there is no further indicators from sentinel TI.
            self.complete_current_execution(__method_name)

    def complete_current_execution(self, __method_name):
        """To update the checkpoint fields in sentinel checkpoint state manager."""
        self.sentinel_checkpoint_json_data["new_execution_flag"] = "True"
        self.sentinel_checkpoint_json_data["last_execution_skip_token"] = ""
        self.sentinel_checkpoint_json_data[
            "current_checkpoint_indicator_date"
        ] = self.sentinel_checkpoint_json_data.get("next_checkpoint_indicator_date")
        self.sentinel_checkpoint_json_data["next_checkpoint_indicator_date"] = ""
        # Saving flag into the sentinel checkpoint state manager.
        try:
            self.sentinel_checkpoint_state.post(
                json.dumps(self.sentinel_checkpoint_json_data)
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} Error: {} : "
                "Error occurred while posting current checkpoint data to sentinel checkpoint state manager.".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
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
            "into Cofense Triage. Starting Next execution.".format(
                LOGS_STARTS_WITH,
                __method_name,
                SENTINEL_TO_COFENSE,
            )
        )

        applogger.info(
            "{}(method={}) : {}: "
            "Checkpoint date stored : {}".format(
                LOGS_STARTS_WITH,
                __method_name,
                SENTINEL_TO_COFENSE,
                self.current_checkpoint_indicator_date,
            )
        )

    def get_indicators_from_sentinel(self):
        """To get indicators from Microsoft Sentinel threat intelligence."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            applogger.info(
                "{}(method={}) : {} : "
                "Started fetching indicators from Microsoft Sentinel Threat Intelligence.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
                )
            )
            retry_count_429 = 0
            retry_count_401 = 0
            while retry_count_429 <= 3 and retry_count_401 <= 1:
                query_indicator_url = QUERY_SENTINEL_INDICATORS_URL.format(
                    subscriptionId=AZURE_SUBSCRIPTION_ID,
                    resourceGroupName=AZURE_RESOURCE_GROUP,
                    workspaceName=AZURE_WORKSPACE_NAME,
                )
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(self.bearer_token),
                }
                body = {
                    "pageSize": self.page_size,
                    "sortBy": [
                        {"itemKey": "lastUpdatedTimeUtc", "sortOrder": "descending"}
                    ],
                    "skipToken": self.sentinel_skiptoken,
                }

                get_indicator_response = make_rest_call(
                    url=query_indicator_url,
                    method="POST",
                    azure_function_name=SENTINEL_TO_COFENSE,
                    payload=json.dumps(body),
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
                    # Posting indicators into cofense.
                    post_indicators_return = self.post_indicators(
                        sentinel_json_indicator_list=sentinel_indicator_json_list,
                        cofense_object=self.cofense_object,
                    )

                    applogger.info(
                        "{}(method={}) : {} : "
                        "Completed the execution of total {} indicators from Microsoft Sentinel"
                        " to Cofense Triage.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            self.indicator_count,
                        )
                    )

                    # If return is False, it means no more indicator to fetch. So exit the python file.
                    if post_indicators_return is False:
                        applogger.warning(
                            "{}(method={}) : {}: url: {}, Status Code : {} : "
                            "No more indicators to fetch from Microsoft Sentinel. Exiting the function.".format(
                                LOGS_STARTS_WITH,
                                __method_name,
                                SENTINEL_TO_COFENSE,
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

                    if self.throttle_flag:
                        applogger.warning(
                            "{}(method={}) : {}: url: {}, Status Code : {} : "
                            "Throttle limit reached. Exiting the function.".format(
                                LOGS_STARTS_WITH,
                                __method_name,
                                SENTINEL_TO_COFENSE,
                                query_indicator_url,
                                get_indicator_response.status_code,
                            )
                        )
                        return True

                # response status code is 429.
                elif get_indicator_response.status_code == 429:
                    retry_count_429 += 1
                    applogger.error(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "Getting 429 from sentinel get indicators api call. Retrying again after {} seconds.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            SENTINEL_429_SLEEP,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                        "Getting 429 from sentinel get indicators api call. Retry count: {}.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                            get_indicator_response.text,
                            retry_count_429,
                        )
                    )
                    # sleep for 60 seconds.
                    time.sleep(SENTINEL_429_SLEEP)

                # response is 401, access token is expired.
                elif get_indicator_response.status_code == 401:
                    retry_count_401 = retry_count_401 + 1
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}:  Error Reason: {} : "
                        "Sentinel access token expired, generating new access token.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {} : url: {}, Status Code : {}, Error Reason: {}, Response: {} : Sentinel"
                        " access token expired, generating new access token. Retry count: {}.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                            get_indicator_response.text,
                            retry_count_401,
                        )
                    )
                    self.bearer_token = auth_sentinel(SENTINEL_TO_COFENSE)

                # response status code is not 200 to 299, 429 and 401.
                else:
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {} : Error while fetching indicators"
                        " from sentinel threat intelligence. Error Reason: {}".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {} : url: {}, Status Code : {}, Error Reason: {}, Response: {} :"
                        " Error while fetching indicators from sentinel threat intelligence.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            query_indicator_url,
                            get_indicator_response.status_code,
                            get_indicator_response.reason,
                            get_indicator_response.text,
                        )
                    )
                    # raise the exception to exit the function app.
                    raise CofenseException()

            # retry count exceeded.
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded for fetching indicators from sentinel.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
                )
            )
            # raising the exception to exit the function app.
            raise CofenseException()

        except CofenseException:
            raise CofenseException()

    def post_indicators(self, sentinel_json_indicator_list, cofense_object):
        """To post and update the indicators into Cofense Triage."""
        try:
            __method_name = inspect.currentframe().f_code.co_name

            applogger.debug(
                "{}(method={}) : {} : "
                "Posting and updating indicators into Cofense Triage.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    SENTINEL_TO_COFENSE,
                )
            )
            # posting and updating indicators
            for indicator in sentinel_json_indicator_list:

                current_indicator_updated_date = self.convert_sentinel_datetime_format(
                    indicator=indicator
                )

                if self.new_execution_flag == "True":
                    if (
                        current_indicator_updated_date
                        <= self.current_checkpoint_indicator_date
                    ):
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
                            "Error occurred while posting sentinel checkpoint data to "
                            "sentinel checkpoint state manager.".format(
                                LOGS_STARTS_WITH,
                                __method_name,
                                SENTINEL_TO_COFENSE,
                                error,
                            )
                        )
                        raise error
                    self.next_checkpoint_indicator_date = (
                        self.sentinel_checkpoint_json_data.get(
                            "next_checkpoint_indicator_date"
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: "
                        "Next execution checkpoint date stored : {}".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            self.next_checkpoint_indicator_date,
                        )
                    )
                    self.new_execution_flag = self.sentinel_checkpoint_json_data.get(
                        "new_execution_flag"
                    )

                # Completed current execution.
                if (
                    current_indicator_updated_date
                    <= self.current_checkpoint_indicator_date
                ):
                    self.complete_current_execution(__method_name)
                    return True

                # getting indicator source and mapping sentinel source to cofense.
                sentinel_indicator_source = indicator.get("properties", {}).get(
                    "source", None
                )
                indicator_source = (
                    self.sentinel_cofense_mapping_obj.get_indicator_source(
                        sentinel_indicator_source
                    )
                )

                # convert sentinel indicator type to cofense indicator type.
                indicator_threat_type = (
                    self.sentinel_cofense_mapping_obj.get_cofense_threat_type(indicator)
                )

                # Convert confidence integer to Level of threat (Malicious, Suspicious, or Benign).
                confidence = indicator.get("properties", {}).get("confidence", "")
                threat_level = sentinel_to_cofense_threat_level_mapping(
                    confidence=confidence, azure_function_name=SENTINEL_TO_COFENSE
                )

                # get the threat value from the sentinel indicator data.
                sentinel_pattern = indicator.get("properties", {}).get("pattern", None)
                threat_value = self.sentinel_cofense_mapping_obj.get_threat_value(
                    sentinel_pattern
                )

                # if indicator source and sentinel indicator pattern type is not as need.
                # To do: remove "is not None".
                if (
                    indicator_source is not None
                    and indicator_threat_type is not None
                    and threat_level is not None
                    and threat_value is not None
                ):
                    # if the sentinel indicator name is connected with a cofense id then update,
                    # the indicator data into cofense triage.
                    sentinel_indicator_name = indicator.get("name", "")

                    if self.sentinel_cofense_id_table.get(sentinel_indicator_name):

                        # get the cofense id from the id table.
                        cofense_id = self.sentinel_cofense_id_table.get(
                            indicator.get("name", "")
                        )

                        # Update the indicator.
                        self.update_indicator(
                            cofense_object=cofense_object,
                            cofense_id=cofense_id,
                            threat_level=threat_level,
                        )

                    # or else create a new indicator into cofense triage and relate the sentinel and cofense id,
                    # into id table.
                    else:
                        # Create indicator into cofense.
                        self.create_indicator(
                            cofense_object=cofense_object,
                            indicator_threat_type=indicator_threat_type,
                            indicator_source=indicator_source,
                            threat_level=threat_level,
                            threat_value=threat_value,
                            sentinel_indicator_name=indicator.get("name"),
                        )

                # Update the total executed indicators count.
                self.indicator_count += 1
            # Completed current execution.
            return True

        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Error occurred while posting indicator in cofense : {}".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
                )
            )
            raise CofenseException()

    def create_indicator(
        self,
        cofense_object,
        indicator_threat_type,
        indicator_source,
        threat_level,
        threat_value,
        sentinel_indicator_name,
    ):
        """To create indicators into cofense triage."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            # Posting indicator into cofense triage.
            (
                post_indicator_status_code,
                post_response_json,
            ) = cofense_object.post_indicators(
                threat_level=threat_level,
                threat_type=indicator_threat_type,
                threat_value=threat_value,
                threat_source=SENTINEL_SOURCE_PREFIX + indicator_source,
                sentinel_indicator_name=sentinel_indicator_name,
            )

            # if status code is 200-299.
            if post_indicator_status_code >= 200 and post_indicator_status_code <= 299:
                # getting the cofense triage indicator id.
                cofense_id = post_response_json.get("data", {}).get("id")

                applogger.debug(
                    "{}(method={}) : {} : "
                    "Indicator successfully created into Cofense with id : {}.".format(
                        LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, cofense_id
                    )
                )

                # updating the sentinel name - cofense id into the id table.
                self.sentinel_cofense_id_table[sentinel_indicator_name] = cofense_id
                try:
                    self.sentinel_cofense_id_table_state.post(
                        json.dumps(self.sentinel_cofense_id_table)
                    )
                except Exception as error:
                    applogger.error(
                        "{}(method={}) : {} Error: {} : "
                        "Error occurred while posting sentinel cofense mapping id table data"
                        " to sentinel cofense id table state manager.".format(
                            LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
                        )
                    )
                    raise error

            # nothing for 422 status code.

        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Error occurred while creating indicator in cofense : {}".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
                )
            )
            raise CofenseException()

    def update_indicator(self, cofense_object, cofense_id, threat_level):
        """To update the indicator threat level in cofense triage."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            # Update the indicator data into cofense triage.
            __method_name = inspect.currentframe().f_code.co_name
            cofense_object.update_indicators(
                threat_level=threat_level,
                id=cofense_id,
            )
            applogger.debug(
                "{}(method={}) : {} : "
                "Indicator successfully updated into Cofense with id : {}.".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, cofense_id
                )
            )
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Error occurred while updating indicator in cofense : {}".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
                )
            )
            raise CofenseException()
