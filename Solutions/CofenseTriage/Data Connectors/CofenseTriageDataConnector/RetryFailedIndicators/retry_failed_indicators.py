"""Retry Failed Indicators."""

import inspect
import json
from ..SharedCode.cofense_exception import CofenseException
from ..SharedCode.consts import (
    LOGS_STARTS_WITH,
    CONNECTION_STRING,
    RETRY_FAILED_INDICATORS,
    FAILED_INDICATORS_TABLE_NAME,
    REPORTS_TABLE_NAME,
    FAILED_INDICATORS_FILE_SHARE,
)
from ..SharedCode.state_manager import StateManager
from ..SharedCode.logger import applogger
from .sentinel import MicrosoftSentinel
from azure.storage.fileshare import ShareDirectoryClient
from azure.core.exceptions import ResourceNotFoundError
from datetime import datetime, timezone, timedelta


class RetryFailedIndicators:
    """Retry Failed Indicators."""

    def __init__(self):
        """Initialize instance variable for class."""
        self.microsoft_obj = MicrosoftSentinel()
        self.log_type = REPORTS_TABLE_NAME

    def return_file_names_to_query_in_the_current_execution(self, file_names_list):
        """Return the file names to query in the current execution.

        Args:
            file_names_list (list): list of file names

        Returns:
            list: list of file names.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            files_to_query_in_current_execution = []
            now = datetime.now(timezone.utc)
            one_hour_ago = now - timedelta(hours=1)
            for file in file_names_list:
                if file.isnumeric() and int(file) < int(one_hour_ago.timestamp()):
                    files_to_query_in_current_execution.append(file)
            applogger.info(
                "{}(method={}) : {} : Found {} failed Indicator files.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    len(files_to_query_in_current_execution),
                )
            )
            return files_to_query_in_current_execution
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error in returning which files to process, Error : {}.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    error,
                )
            )
            raise CofenseException()

    def get_failed_indicator_files(self, parent_dir):
        """Get failed indicator's file names.

        Args:
            parent_dir (ShareDirectory.from_connection_string): Object of ShareDirectory to perform operations
            on file share.

        Returns:
            list: list of file names of failed indicators
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            files_list = list(parent_dir.list_directories_and_files())
            file_names = []
            if (len(files_list)) > 0:
                for file in files_list:
                    file_names.append(file["name"])
                return file_names
            else:
                return None
        except ResourceNotFoundError:
            applogger.info(
                "{}(method={}) : {} : No Failed Indicators File Found.".format(
                    LOGS_STARTS_WITH, __method_name, RETRY_FAILED_INDICATORS
                )
            )
            return None
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error while getting list of files, Error : {}.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    error,
                )
            )
            raise CofenseException()

    def delete_file_from_file_share(self, file_name, parent_dir):
        """Delete the file from azure file share.

        Args:
            file_name (str): name of the file to delete
            parent_dir (ShareDirectory.from_connection_string): Object of ShareDirectory to perform operations
            on file share.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            parent_dir.delete_file(file_name)
        except ResourceNotFoundError:
            applogger.info(
                "{}(method={}) : {} : No Failed Indicators File Found, filename-{}.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    file_name,
                )
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error while deleting file, Error : {}.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    error,
                )
            )
            raise CofenseException()

    def get_failed_indicators(self, file_name):
        """Get Failed indicators list from files."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            state_manager_obj = StateManager(
                CONNECTION_STRING, file_path=file_name, share_name=FAILED_INDICATORS_FILE_SHARE
            )
            failed_indicators = state_manager_obj.get(RETRY_FAILED_INDICATORS)
            if failed_indicators is None or failed_indicators == "":
                return None
            else:
                json_data = json.loads(failed_indicators)
                return json_data
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error while getting data for failed indicators, Error : {}.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    error,
                )
            )
            raise CofenseException()

    def post_failed_indicators(self, indicators_data):
        """Post indicators to Microsoft Sentinel Threat Intelligence.

        Args:
            indicators_data (dict): Failed Indicators Data

        Returns:
            dict: Dictionary containing the success_count and failure_count
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            success_count = 0
            failed_count = 0
            for indicator in indicators_data:
                failed_indicator = indicator.get("indicator", "")
                report_link = indicator.get("report_link", "")
                indicator_id = indicator.get("id", "")
                indicator_response = self.microsoft_obj.create_indicator(failed_indicator, indicator_id)
                if indicator_response is None:
                    failed_indicator['report_link'] = report_link
                    self.microsoft_obj.post_data(
                        body=json.dumps([failed_indicator]),
                        log_type=FAILED_INDICATORS_TABLE_NAME,
                    )
                    applogger.info(
                        "{}(method={}) : {} : Posted failed indicator to log analytics, indicatorId- {}".format(
                            LOGS_STARTS_WITH, __method_name, RETRY_FAILED_INDICATORS, indicator_id
                        )
                    )
                    failed_count += 1
                else:
                    indicator_externalId = indicator_response.get("properties", {}).get("externalId", "")
                    applogger.debug(
                        "{}(method={}) : {}: indicator created successfully, indicatorId- {}.".format(
                            LOGS_STARTS_WITH, __method_name, RETRY_FAILED_INDICATORS, indicator_id
                        )
                    )
                    updated_at = failed_indicator.get("properties", {}).get("externalLastUpdatedTimeUtc", "")
                    source_cofence = failed_indicator.get("properties", {}).get("source", "")
                    report_data = {
                        "indicator_id": indicator_id,
                        "external_id": "{}-{}".format(indicator_externalId, source_cofence),
                        "report_link": report_link,
                        "updated_at": updated_at,
                    }
                    self.microsoft_obj.post_data(json.dumps(report_data), self.log_type)
                    success_count += 1
            applogger.info(
                "{}(method={}) : {} : Total_Invocations: {}, Successful Indicators Posting: {},\
                    Failed Indicators Posting: {}.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    len(indicators_data),
                    success_count,
                    failed_count,
                )
            )
            return {"success_count": success_count, "failure_count": failed_count}
        except CofenseException:
            applogger.error(
                "{}(method={}) : {} : Indicator Creation Failed while retrying.".format(
                    LOGS_STARTS_WITH, __method_name, RETRY_FAILED_INDICATORS
                )
            )
            raise CofenseException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Indicator Creation Failed while retrying, Error : {}.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    error,
                )
            )
            raise CofenseException()

    def get_failed_indicators_and_retry(self):
        """Get failed indicators data from files and try creating them again."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            total_retry_indicators = 0
            retry_success = 0
            retry_failure = 0
            parent_dir = ShareDirectoryClient.from_connection_string(
                conn_str=CONNECTION_STRING,
                share_name=FAILED_INDICATORS_FILE_SHARE,
                directory_path="",
            )
            failed_indicator_files = self.get_failed_indicator_files(parent_dir)
            if not failed_indicator_files:
                applogger.info(
                    "{}(method={}) : {} : No failed indicators found.".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        RETRY_FAILED_INDICATORS,
                    )
                )
                return
            file_names_to_query = self.return_file_names_to_query_in_the_current_execution(failed_indicator_files)
            if not file_names_to_query:
                applogger.info(
                    "{}(method={}) : {} : No previously failed indicators found.".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        RETRY_FAILED_INDICATORS,
                    )
                )
                return
            for file in file_names_to_query:
                failed_indicators = self.get_failed_indicators(file)
                if not failed_indicators:
                    applogger.info(
                        "{}(method={}) : {} : No Failed indicators found in the file-{}.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            RETRY_FAILED_INDICATORS,
                            file,
                        )
                    )
                    continue

                result = self.post_failed_indicators(failed_indicators)
                total_retry_indicators += len(failed_indicators)
                retry_success += result["success_count"]
                retry_failure += result["failure_count"]
                self.delete_file_from_file_share(file, parent_dir)
                applogger.info(
                    "{}(method={}) : {} : Successfully deleted the file, filename : {}.".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        RETRY_FAILED_INDICATORS,
                        file,
                    )
                )
            applogger.info(
                "{}(method={}) : {} : Total collected Failed Indicators : {}, "
                "posted indicators into sentinel: {}, "
                "failed indicators while posting : {}.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    total_retry_indicators,
                    retry_success,
                    retry_failure,
                )
            )
        except CofenseException:
            raise CofenseException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Retrying Failed Indicators incurred an error, Error: {}.".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    RETRY_FAILED_INDICATORS,
                    error,
                )
            )
            raise CofenseException()
