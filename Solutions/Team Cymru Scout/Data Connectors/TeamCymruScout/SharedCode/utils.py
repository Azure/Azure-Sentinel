"""This file contains utility functions to be used by other modules."""

from . import consts
import inspect
import re
import ipaddress
from .logger import applogger
from .teamcymruscout_exception import TeamCymruScoutException
from .get_logs_data import get_logs_data
from .checkpoint_manager import CheckpointManager


class TeamCymruScoutUtility:
    """Class for performing various tasks."""

    def __init__(self, indicator_type=None) -> None:
        """
        Initialize the insatnce object of TeamCymruScoutUtility.

        Args:
            indicator_type (str): type of indicator.
        """
        self.logs_starts_with = consts.LOGS_STARTS_WITH
        self.constants = {"domain": consts.DOMAIN_VALUES, "ip": consts.IP_VALUES}
        self.query_constants = {"domain": consts.DOMAIN_QUERY, "ip": consts.IP_QUERY}
        self.error_logs = "{}(method={}) {}"

        if indicator_type is not None:
            self.checkpoint_obj = CheckpointManager(file_path=indicator_type)

    def validate_params(self):
        """
        To validate the required parameters for the function.

        Raises:
            TeamCymruScoutException: If any required parameter is missing or empty.
        """
        __method_name = inspect.currentframe().f_code.co_name
        required_params = {
            "CymruScoutBaseURL": consts.CYMRU_SCOUT_BASE_URL,
            "AuthenticationType": consts.AUTHENTICATION_TYPE,
            "APIType": consts.API_TYPE,
            "AZURE_CLIENT_ID": consts.AZURE_CLIENT_ID,
            "AZURE_CLIENT_SECRET": consts.AZURE_CLIENT_SECRET,
            "AZURE_TENANT_ID": consts.AZURE_TENANT_ID,
            "WorkspaceID": consts.WORKSPACE_ID,
            "WorkspaceKey": consts.WORKSPACE_KEY,
            "IPTableName": consts.IP_TABLE_NAME,
            "DomainTableName": consts.DOMAIN_TABLE_NAME,
            "AccountUsageTableName": consts.ACCOUNT_USAGE_TABLE_NAME,
        }
        if consts.AUTHENTICATION_TYPE == "API Key":
            required_params.update({"APIKey": consts.API_KEY})
        else:
            required_params.update({"Username": consts.USERNAME, "Password": consts.PASSWORD})
        applogger.debug(
            "{}(method={}) : Checking if all the environment variables exist or not.".format(self.logs_starts_with, __method_name)
        )
        missing_required_field = False
        for label, params in required_params.items():
            if not params or params == "":
                missing_required_field = True
                applogger.error(
                    '{}(method={}) : "{}" field is not set in the environment please set '
                    "the environment variable and run the app.".format(
                        self.logs_starts_with,
                        __method_name,
                        label,
                    )
                )
        if missing_required_field:
            raise TeamCymruScoutException("Error Occurred while validating params. Required fields missing.")
        applogger.info(
            "{}(method={}) : All necessary variables are present in the Configuration.".format(self.logs_starts_with, __method_name)
        )

    def validate_ip(self, indicator):
        """
        To validate if the given indicator is a valid IP.

        Args:
            indicator (str): The IP indicator to be validated.

        Returns:
            bool: True if the indicator is a valid IPv4 or IPv6, False otherwise.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            ip_obj = ipaddress.ip_address(indicator)
            if ip_obj.version == 4:
                applogger.debug("{}(method={}) : {} is a valid IPv4.".format(self.logs_starts_with, __method_name, indicator))
                return True
            elif ip_obj.version == 6:
                applogger.debug("{}(method={}) : {} is a valid IPv6.".format(self.logs_starts_with, __method_name, indicator))
                return True
        except ValueError:
            applogger.debug("{}(method={}) : {} is not a valid IP address.".format(self.logs_starts_with, __method_name, indicator))
        return False

    def validate_ip_domain(self, indicator, indicator_type):
        """
        To validate if the given indicator is a valid IP or domain.

        Args:
            indicator (str): The indicator to be validated.
            regex_pattern (str): The regular expression pattern to match the indicator.

        Returns:
            bool: True if the indicator is a valid IP or domain, False otherwise.
        """
        __method_name = inspect.currentframe().f_code.co_name
        if indicator_type == "ip":
            return self.validate_ip(indicator)
        elif re.search(consts.DOMAIN_REGEX, indicator):
            applogger.debug("{}(method={}) : {} is a valid domain.".format(self.logs_starts_with, __method_name, indicator))
            return True
        else:
            applogger.debug("{}(method={}) : {} is not a valid domain.".format(self.logs_starts_with, __method_name, indicator))
            return False

    def get_data_from_input(self, indicator_type):
        """
        To retrieve data from the input based on the given indicator type.

        Args:
            indicator_type (str): The type of the indicator.

        Returns:
            list: A list of input values.

        Raises:
            TeamCymruScoutException: If an error occurs.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if not self.constants.get(indicator_type):
                applogger.info(
                    "{} (method={}) : No {} values found in the input.".format(self.logs_starts_with, __method_name, indicator_type)
                )
                return []
            input_values = set([data.strip() for data in self.constants.get(indicator_type).split(",")])
            applogger.debug(
                "{} (method={}) : {} data to fetch for input data: {}".format(
                    self.logs_starts_with, __method_name, indicator_type, input_values
                )
            )
            return input_values
        except Exception as err:
            applogger.error(self.error_logs.format(self.logs_starts_with, __method_name, err))
            raise TeamCymruScoutException()

    def get_data_from_watchlists(self, indicator_type):
        """
        To retrieve data from watchlists based on the given indicator type.

        Args:
            indicator_type (str): The type of the indicator.

        Returns:
            list or None: A list of values from the watchlist if the indicator type is found,
                          otherwise None.

        Raises:
            TeamCymruScoutException: If an error occurs while retrieving the data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            logs_data, flag = get_logs_data(self.query_constants.get(indicator_type))
            if not flag:
                applogger.info(
                    "{} (method={}) : No {} values found in the watchlist.".format(self.logs_starts_with, __method_name, indicator_type)
                )
                return []
            watchlist_data = [data[indicator_type].strip() for data in logs_data]
            last_checkpoint_data = self.checkpoint_obj.get_checkpoint(indicator_type)
            applogger.debug("{}(method={}) Last Checkpoint Data: {}".format(self.logs_starts_with, __method_name, last_checkpoint_data))
            watchlist_values = sorted(set(watchlist_data))
            if last_checkpoint_data is not None and last_checkpoint_data != watchlist_data[-1]:
                watchlist_values = sorted(set(watchlist_data[watchlist_data.index(last_checkpoint_data) + 1: len(watchlist_data)]))
            applogger.debug(
                "{} (method={}) : {} data to fetch for watchlist data: {}".format(
                    self.logs_starts_with,
                    __method_name,
                    indicator_type,
                    watchlist_values,
                )
            )
            return watchlist_values
        except ValueError:
            applogger.info(
                "{}(method={}) Checkpoint data does not exist in watchlists data."
                " Hence considering watchlist data from initial value in ascending order.".format(self.logs_starts_with, __method_name)
            )
            self.checkpoint_obj.save_checkpoint(data="", indicator_type="domain")
            return watchlist_values
        except Exception as err:
            applogger.error(self.error_logs.format(self.logs_starts_with, __method_name, err))
            raise TeamCymruScoutException()

    def extract_ids_and_names_of_tags(self, tags):
        """
        To retrieve ids and names from tags based on the given indicator type.

        Args:
            tags (list): The tags to extract ids and names from.

        Raises:
            TeamCymruScoutException: If an error occurs while extracting tag ids and names.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            ids = []
            names = []
            for item in tags:
                ids.append(item.get("id"))
                names.append(item.get("name", ""))
                tags_children = item.get("children", {})
                if tags_children:
                    child_ids, child_names = self.extract_ids_and_names_of_tags(tags_children)
                    ids.extend(child_ids)
                    names.extend(child_names)
            return ids, names
        except Exception as err:
            applogger.error(self.error_logs.format(self.logs_starts_with, __method_name, err))
            raise TeamCymruScoutException()
