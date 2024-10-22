"""This file includes functions to collect account usage details from Team Cymru Scout API and send it to Sentinel."""

import inspect
import requests
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.utils import TeamCymruScoutUtility
from ..SharedCode.teamcymruscout_client import TeamCymruScout
from ..SharedCode.teamcymruscout_exception import TeamCymruScoutException


class AccountUsageDataCollector:
    """Fetches the account usage information."""

    def __init__(self) -> None:
        """Initialize the object of AccountUsageDataCollector."""
        self.logs_starts_with = consts.LOGS_STARTS_WITH + " AccountUsageDataCollector:"
        self.rest_helper_obj = TeamCymruScout()
        self.utility_obj = TeamCymruScoutUtility()
        self.utility_obj.validate_params()

    def get_account_usage_data(self):
        """
        Fetch account usage data from Team Cymru Scout.

        To retrieve account usage data, fetch details from Team Cymru Scout
        and post it to Sentinel.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug("{}(method={}) fetch account usages data from Cymru Scout.".format(self.logs_starts_with, __method_name))
            account_data = self.rest_helper_obj.make_rest_call(endpoint=consts.ACCOUNT_USAGE_ENDPOINT, params={})
            self.rest_helper_obj.send_data_to_sentinel(account_data, consts.ACCOUNT_USAGE_TABLE_NAME)
        except requests.exceptions.Timeout as error:
            applogger.error(
                self.error_logs.format(
                    self.logs_starts_with,
                    __method_name,
                    consts.TIME_OUT_ERROR_MSG.format(error),
                )
            )
            raise requests.exceptions.Timeout()
        except Exception as err:
            applogger.error("{}(method={}) {}".format(self.logs_starts_with, __method_name, err))
            raise TeamCymruScoutException()
