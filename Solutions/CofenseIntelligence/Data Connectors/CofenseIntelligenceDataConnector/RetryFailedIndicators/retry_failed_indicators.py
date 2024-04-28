"""Retry Failed Indicators."""
import asyncio
import inspect
import json
import aiohttp
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException
from ..SharedCode import consts
from ..SharedCode.state_manager import StateManager
from ..SharedCode.logger import applogger
from .sentinel import MicrosoftSentinel
from ..SharedCode.sentinel import post_data
from azure.storage.fileshare import ShareDirectoryClient
from azure.core.exceptions import ResourceNotFoundError
from datetime import datetime, timezone, timedelta


def return_file_names_to_query_in_the_current_execution(file_names_list):
    """Return the file names except the ones from the current invocation's date.

    Args:
        file_names_list (list): list of file names

    Returns:
        list: list of file names till midnight of that day.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        files_to_query_in_current_execution = []
        for file in file_names_list:
            if file.isnumeric() and int(file) < int(one_hour_ago.timestamp()):
                files_to_query_in_current_execution.append(file)
        applogger.info(
            "{}(method={}) : {} : Found {} failed Indicators' File.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                len(files_to_query_in_current_execution),
            )
        )
        return files_to_query_in_current_execution
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Error in returning which files to process, Error : {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                error,
            )
        )
        raise CofenseIntelligenceException()


def list_checkpoint_files(parent_dir):
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
        applogger.error(
            "{}(method={}) : {} : No Failed Indicators File Found.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.RETRY_FAILED_INDICATORS
            )
        )
        return None
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : error while getting list of checkpoint files, Error : {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                error,
            )
        )
        raise CofenseIntelligenceException()


def delete_file_from_file_share(file_name, parent_dir):
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
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                file_name,
            )
        )
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : error while deleting checkpoint file, Error : {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                error,
            )
        )
        raise CofenseIntelligenceException()


def get_failed_indicators(file_name):
    """Get Failed indicators list from checkpoint."""
    __method_name = inspect.currentframe().f_code.co_name
    try:
        state_manager_obj = StateManager(consts.CONNECTION_STRING, file_path=file_name)
        checkpoint_data = state_manager_obj.get(consts.RETRY_FAILED_INDICATORS)
        if checkpoint_data is None or checkpoint_data == "":
            return None
        else:
            json_checkpoint = json.loads(checkpoint_data)
            return json_checkpoint
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : error while getting checkpoint data for failed indicators, Error : {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                error,
            )
        )
        raise CofenseIntelligenceException()


async def post_failed_indicators(indicators_data):
    """Create the asynchronous tasks for failed indicators ingestion to Microsoft Sentinel Threat Intelligence.

    Args:
        indicators_data (dict): Failed Indicators Data

    Returns:
        dict: Dictionary containing the success_count and failure_count
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        failed_indicators = []
        microsoft_sentinel_obj = MicrosoftSentinel()
        tasks = []
        async with aiohttp.ClientSession() as session:
            for indicator in indicators_data:
                tasks.append(
                    asyncio.create_task(
                        microsoft_sentinel_obj.create_indicator(indicator, session)
                    )
                )
            results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = 0
        failed_count = 0
        for i in results:
            if i is None:
                success_count += 1
            else:
                failed_count += 1
                failed_indicators.append(i)
        applogger.info(
            "{}(method={}) : {} : Total_Invocations: {}, Successful Indicators Posting: {},\
                Failed Indicators Posting: {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                len(results),
                success_count,
                failed_count,
            )
        )
        return {
            "success_count": success_count,
            "failure_count": failed_count,
            "failed_indicators": failed_indicators,
        }
    except CofenseIntelligenceException:
        applogger.error(
            "{}(method={}) : {} : Indicator Creation Failed after retrying.".format(
                consts.LOGS_STARTS_WITH, __method_name, consts.RETRY_FAILED_INDICATORS
            )
        )
        raise CofenseIntelligenceException()
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Indicator Creation Failed after retrying, Error : {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                error,
            )
        )
        raise CofenseIntelligenceException()


async def get_failed_indicators_and_retry():
    """Get failed indicators data from checkpoint and try creating them again."""
    __method_name = inspect.currentframe().f_code.co_name
    try:
        total_retry_indicators = 0
        retry_success = 0
        retry_failure = 0
        parent_dir = ShareDirectoryClient.from_connection_string(
            conn_str=consts.CONNECTION_STRING,
            share_name=consts.MS_SHARE_NAME,
            directory_path="",
        )
        failed_files = list_checkpoint_files(parent_dir)
        if not failed_files:
            applogger.info(
                "{}(method={}) : {} : No files found.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.RETRY_FAILED_INDICATORS,
                )
            )
            return
        file_names_to_query = return_file_names_to_query_in_the_current_execution(
            failed_files
        )
        if not file_names_to_query:
            applogger.info(
                "{}(method={}) : {} : No previously failed indicators found.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.RETRY_FAILED_INDICATORS,
                )
            )
            return
        for file in file_names_to_query:
            failed_indicators = get_failed_indicators(file)
            if not failed_indicators:
                applogger.info(
                    "{}(method={}) : {} : No Failed indicators found in the file-{}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.RETRY_FAILED_INDICATORS,
                        file,
                    )
                )
                continue

            result = await post_failed_indicators(failed_indicators)
            if result["failure_count"] > 0:
                post_data(
                    body=json.dumps(result["failed_indicators"]),
                    log_type=consts.FAILED_INDICATORS_TABLE_NAME,
                )
                applogger.info(
                    "{}(method={}) : {} : Posted {} failed indicators to log analytics.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.RETRY_FAILED_INDICATORS,
                        len(result["failed_indicators"]),
                    )
                )
            total_retry_indicators += len(failed_indicators)
            retry_success += result["success_count"]
            retry_failure += result["failure_count"]
            delete_file_from_file_share(file, parent_dir)
            applogger.info(
                "{}(method={}) : {} : Succesfully deleted the file, filename : {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.RETRY_FAILED_INDICATORS,
                    file,
                )
            )
        applogger.info(
            "{}(method={}) : {} : Total collected Failed Indicators : {}, "
            "posted indicators into sentinel: {}, "
            "failed indicators while posting : {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                total_retry_indicators,
                retry_success,
                retry_failure,
            )
        )
    except CofenseIntelligenceException:
        applogger.error(
            "{}(method={}) : {} : Retrying Failed Indicators incurred an error.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
            )
        )
        raise CofenseIntelligenceException()
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Retrying Failed Indicators incurred an error, Error: {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.RETRY_FAILED_INDICATORS,
                error,
            )
        )
        raise CofenseIntelligenceException()
