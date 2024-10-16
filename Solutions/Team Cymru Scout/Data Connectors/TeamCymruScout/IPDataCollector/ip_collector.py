"""This file includes functions to collect IP details from Team Cymru Scout API for IP address provided by user and send it to Sentinel."""

import inspect
import requests

from SharedCode.logger import applogger
from SharedCode.teamcymruscout_exception import TeamCymruScoutException
from SharedCode import consts
from SharedCode.utils import TeamCymruScoutUtility
from SharedCode.teamcymruscout_client import TeamCymruScout
from SharedCode.checkpoint_manager import CheckpointManager


class IPDataCollector:
    """Class for fetching IP data from Team Cymru Scout and ingest it into Log Analytics Workspace."""

    def __init__(self) -> None:
        """Initialize the object of IPDataCollector."""
        self.logs_starts_with = consts.LOGS_STARTS_WITH + " IPDataCollector:"
        self.input_ip_values = []
        self.watchlist_ip_values = []
        self.utility_obj = TeamCymruScoutUtility(indicator_type="ip")
        self.utility_obj.validate_params()
        self.rest_helper_obj = TeamCymruScout()
        self.checkpoint_obj = CheckpointManager(file_path="ip")
        self.error_logs = "{}(method={}) {}"

    def divide_chunks(self, ip_list):
        """
        To divide list of IP addresses into chunks.

        Args:
            ip_list (list): List of IP addresses.

        Yields:
            list: A chunk of IP addresses from the input list.
        """
        chunk_size = consts.FOUNDATION_CHUNK_SIZE
        for i in range(0, len(ip_list), chunk_size):
            yield ip_list[i: i + chunk_size]

    def get_ip_data_into_sentinel(self):
        """To retrieve IP data from input/watchlist, fetch details from Team Cymru Scout and post it to Sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                "{}(method={}) Getting IP values from input and fetch data from Team Cymru Scout.".format(
                    self.logs_starts_with, __method_name
                )
            )
            self.input_ip_values = self.utility_obj.get_data_from_input(indicator_type="ip")
            if len(self.input_ip_values) > 0:
                input_ip_values_list = list(self.input_ip_values)
                self.get_ip_data_from_api_type(input_ip_values_list)
            applogger.debug(
                "{}(method={}) Getting IP values from watchlist and fetch data from Team Cymru Scout.".format(
                    self.logs_starts_with, __method_name
                )
            )
            self.watchlist_ip_values = self.utility_obj.get_data_from_watchlists(indicator_type="ip")
            if len(self.watchlist_ip_values) > 0:
                self.get_ip_data_from_api_type(self.watchlist_ip_values, watchlist_flag=True)
        except Exception as err:
            applogger.error(self.error_logs.format(self.logs_starts_with, __method_name, err))
            raise TeamCymruScoutException()

    def get_ip_data_from_api_type(self, ip_list, watchlist_flag=False):
        """
        To get IP data from Team Cymru Scout API based on user selected API.

        Args:
            ip_list (list): A list of IPs to retrieve details from.
            watchlist_flag (bool, optional): A flag indicating whether the IPs are from a watchlist.
                                            Defaults to False.
        """
        if consts.API_TYPE.lower() == "foundation":
            self.get_ip_data_from_foundation_api(ip_list, watchlist_flag)
        else:
            self.get_ip_data_from_details_api(ip_list, watchlist_flag)

    def validate_ip_values(self, ip_list):
        """
        To validate IP data before making API call.

        Args:
            ip_list (list): A list of IPs to validate.

        Returns:
            list: A list of valid IPs.
        """
        valid_ip_values = []
        for ip in ip_list:
            parsed_ip = ip.replace("[", "").replace("]", "")
            if not self.utility_obj.validate_ip_domain(
                indicator=parsed_ip,
                indicator_type="ip",
            ):
                continue
            valid_ip_values.append(parsed_ip)
        return valid_ip_values

    def add_tags(self, ip_details):
        """
        Add Tags ID and Tags Name to the IP data.

        Args:
            ip_details (dict): The IP data to add tags to.
        """
        if ip_details.get("tags", []):
            tags_ids, tags_names = self.utility_obj.extract_ids_and_names_of_tags(ip_details.get("tags", []))
            ip_details["tags_id"] = tags_ids
            ip_details["tags_name"] = tags_names

    def get_ip_data_from_foundation_api(self, ip_list, watchlist_flag=False):
        """To get IP data from Foundation API.

        Args:
            ip_list (list): A list of IPs to retrieve details from foundation API.
            watchlist_flag (bool, optional): A flag indicating whether the IPs are from a watchlist.
                                            Defaults to False.
        Raises:
            TeamCymruScoutException: If an error occurs while retrieving or sending the IP data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug("{}(method={}) Getting data from Foundation API.".format(self.logs_starts_with, __method_name))
            ip_chunks = self.divide_chunks(ip_list)
            for list_indicator in ip_chunks:
                valid_ip_values = self.validate_ip_values(list_indicator)
                if len(valid_ip_values) > 0:
                    foundation_response = self.rest_helper_obj.make_rest_call(
                        endpoint=consts.IP_FOUNDATION_ENDPOINT,
                        params={"ips": ",".join(ips for ips in valid_ip_values)},
                    )
                    foundation_data = foundation_response.get("data", [])
                    if len(foundation_data) == 0:
                        applogger.info(
                            "{}(method={}) No Foundation data found for {} IPs.".format(
                                self.logs_starts_with, __method_name, valid_ip_values
                            )
                        )
                        continue
                    for ip_details in foundation_data:
                        self.add_tags(ip_details)
                    self.rest_helper_obj.send_data_to_sentinel(
                        foundation_data,
                        "{}_{}".format(consts.IP_TABLE_NAME, "Foundation"),
                        indicator_value=valid_ip_values,
                    )
                if watchlist_flag:
                    self.checkpoint_obj.save_checkpoint(data=list_indicator[-1], indicator_type="ip")
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
            applogger.error(self.error_logs.format(self.logs_starts_with, __method_name, err))
            raise TeamCymruScoutException()

    def get_ip_data_from_details_api(self, ip_list, watchlist_flag=False):
        """
        To get IP data from Details API.

        Args:
            ip_list (list): A list of IPs to retrieve details from details API.
            watchlist_flag (bool, optional): A flag indicating whether the IPs are from a watchlist.
                                            Defaults to False.
        Raises:
            TeamCymruScoutException: If an error occurs while retrieving or sending the IP data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug("{}(method={}) Getting data from Details API.".format(self.logs_starts_with, __method_name))
            valid_ip_count = 0
            for ip in ip_list:
                parsed_ip = ip.replace("[", "").replace("]", "")
                if self.utility_obj.validate_ip_domain(indicator=parsed_ip, indicator_type="ip"):
                    valid_ip_count += 1
                    ip_data = self.rest_helper_obj.make_rest_call(endpoint=consts.IP_DETAILS_ENDPOINT.format(parsed_ip))
                    self.parse_ip_data_and_ingest_into_sentinel(ip_data=ip_data, indicator_value=ip)
                if watchlist_flag:
                    self.checkpoint_obj.save_checkpoint(data=ip, indicator_type="ip")
            applogger.debug("{}(method={}) Total data ingested for {} IPs.".format(self.logs_starts_with, __method_name, valid_ip_count))
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
            applogger.error(self.error_logs.format(self.logs_starts_with, __method_name, err))
            raise TeamCymruScoutException()

    def process_ip_data(self, ip_data, parent_key, child_key, table_name, indicator_value):
        """
        To extract and ingest the IP data into different tables in Log Analytics workspace.

        Args:
            ip_data (dict): A dictionary containing the ip address data.
            parent_key (str): The key of the parent data to extract.
            child_key (str): The key of the child data to extract.
            table_name (str): The name of the table.

        Returns:
            dict: A updated dictionary after extraction.

        Raises:
            TeamCymruScoutException: If an error occurs during the extracting or ingesting the IP data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                "{}(method={}) Extracting IP data from Details API for IP: {}.".format(
                    self.logs_starts_with, __method_name, indicator_value
                )
            )
            parent_data = ip_data.get(parent_key, {})
            if parent_data:
                child_data = parent_data.get(child_key, [])
                if child_data:
                    if "ip" not in child_data:
                        for item in child_data:
                            item["ip"] = ip_data.get("ip")
                            item["start_date"] = ip_data.get("start_date")
                            item["end_date"] = ip_data.get("end_date")
                    self.rest_helper_obj.send_data_to_sentinel(
                        child_data,
                        "{}_{}".format(consts.IP_TABLE_NAME, table_name),
                        indicator_value=indicator_value,
                    )
                    parent_data.pop(child_key)
            return parent_data
        except Exception as err:
            applogger.error(self.error_logs.format(self.logs_starts_with, __method_name, err))
            raise TeamCymruScoutException()

    def parse_ip_data_and_ingest_into_sentinel(self, ip_data, indicator_value):
        """
        To parse the IP address data and divide information into different tables.

        Args:
            ip_data (dict): A dictionary containing the ip address data.

        Raises:
            TeamCymruScoutException: If an error occurs during the parsing process.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                "{}(method={}) Parsing and Ingesting IP data from Details API into different tables for IP: {}.".format(
                    self.logs_starts_with, __method_name, indicator_value
                )
            )
            communications = self.process_ip_data(
                ip_data,
                "communications",
                "peers",
                "Communications",
                indicator_value=indicator_value,
            )
            pdns = self.process_ip_data(ip_data, "pdns", "pdns", "PDNS", indicator_value=indicator_value)
            fingerprints = self.process_ip_data(
                ip_data,
                "fingerprints",
                "fingerprints",
                "Fingerprints",
                indicator_value=indicator_value,
            )
            openports = self.process_ip_data(
                ip_data,
                "open_ports",
                "open_ports",
                "OpenPorts",
                indicator_value=indicator_value,
            )
            x509 = self.process_ip_data(ip_data, "x509", "x509", "x509", indicator_value=indicator_value)

            summary_details = ip_data.get("summary", {})
            summary_tags = summary_details.get("tags", [])
            if summary_details:
                ip_data.pop("summary")
            ip_data.pop("request_id")
            ip_data.pop("sections")
            ip_data["communications"] = communications
            ip_data["pdns"] = pdns
            ip_data["fingerprints"] = fingerprints
            ip_data["open_ports"] = openports
            ip_data["x509"] = x509
            self.rest_helper_obj.send_data_to_sentinel(
                ip_data,
                "{}_{}".format(consts.IP_TABLE_NAME, "Details"),
                indicator_value=indicator_value,
            )
            if summary_details:
                summary_pdns = self.process_ip_data(
                    summary_details,
                    "pdns",
                    "top_pdns",
                    "Summary_PDNS",
                    indicator_value=indicator_value,
                )
                summary_openports = self.process_ip_data(
                    summary_details,
                    "open_ports",
                    "top_open_ports",
                    "Summary_OpenPorts",
                    indicator_value=indicator_value,
                )
                summary_certs = self.process_ip_data(
                    summary_details,
                    "certs",
                    "top_certs",
                    "Summary_Certs",
                    indicator_value=indicator_value,
                )
                summary_fingerprints = self.process_ip_data(
                    summary_details,
                    "fingerprints",
                    "top_fingerprints",
                    "Summary_Fingerprints",
                    indicator_value=indicator_value,
                )
                if summary_tags:
                    summary_tags_ids, summary_tags_names = self.utility_obj.extract_ids_and_names_of_tags(summary_tags)
                    summary_details["tags_id"] = summary_tags_ids
                    summary_details["tags_name"] = summary_tags_names
                summary_details["pdns"] = summary_pdns
                summary_details["open_ports"] = summary_openports
                summary_details["certs"] = summary_certs
                summary_details["fingerprints"] = summary_fingerprints
                self.rest_helper_obj.send_data_to_sentinel(
                    summary_details,
                    "{}_{}".format(consts.IP_TABLE_NAME, "Summary_Details"),
                    indicator_value=indicator_value,
                )
        except Exception as err:
            applogger.error(self.error_logs.format(self.logs_starts_with, __method_name, err))
            raise TeamCymruScoutException()
