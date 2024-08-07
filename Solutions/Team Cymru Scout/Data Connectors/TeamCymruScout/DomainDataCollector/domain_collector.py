"""This file includes functions to collect domain details from Team Cymru Scout API for domain provided by user and send it to Sentinel."""

import inspect

from SharedCode.logger import applogger
from SharedCode.teamcymruscout_exception import TeamCymruScoutException
from SharedCode import consts
from SharedCode.utils import TeamCymruScoutUtility
from SharedCode.teamcymruscout_client import TeamCymruScout
from SharedCode.checkpoint_manager import CheckpointManager


class DomainDataCollector:
    """Class for fetching Domain data from Team Cymru Scout and posting it to Log Analytics Workspace."""

    def __init__(self) -> None:
        """Initialize the object of DomainDataCollector."""
        self.logs_starts_with = consts.LOGS_STARTS_WITH + " DomainDataCollector:"
        self.input_domain_values = []
        self.watchlist_domain_values = []
        self.utility_obj = TeamCymruScoutUtility(indicator_type="domain")
        self.utility_obj.validate_params()
        self.rest_helper_obj = TeamCymruScout()
        self.checkpoint_obj = CheckpointManager(file_path="domain")

    def get_domain_data_into_sentinel(self):
        """To retrieve domain data from input/watchlist, fetch details from Team Cymru Scout and post it to Sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        applogger.debug(
            "{}(method={}) Getting domain values from input and fetch data from Team Cymru Scout.".format(
                self.logs_starts_with, __method_name
            )
        )
        self.input_domain_values = self.utility_obj.get_data_from_input(
            indicator_type="domain"
        )
        if len(self.input_domain_values) > 0:
            self.get_domain_details_from_team_cymru_scout_send_to_sentinel(
                self.input_domain_values
            )
        self.watchlist_domain_values = self.utility_obj.get_data_from_watchlists(
            indicator_type="domain"
        )
        if len(self.watchlist_domain_values) > 0:
            self.get_domain_details_from_team_cymru_scout_send_to_sentinel(
                self.watchlist_domain_values, watchlist_flag=True
            )

    def get_domain_details_from_team_cymru_scout_send_to_sentinel(
        self, domains_list, watchlist_flag=False
    ):
        """
        To retrieve domain details using Team Cymru Scout API for a list of domains and sends the domain details to Sentinel.

        Args:
            domains_list (list): A list of domains to retrieve details from.
            watchlist_flag (bool, optional): A flag indicating whether the domains are from a watchlist.
                                            Defaults to False.

        Raises:
            TeamCymruScoutException: If an error occurs while retrieving or sending the domain data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            domain_details = []
            domain_indicator_list = []
            for domain in domains_list:
                parsed_domain = domain.replace("[", "").replace("]", "")
                if not self.utility_obj.validate_ip_domain(
                    indicator=parsed_domain,
                    regex_pattern=consts.DOMAIN_REGEX,
                    indicator_type="domain",
                ):
                    continue
                domain_data = self.rest_helper_obj.make_rest_call(
                    endpoint=consts.SEARCH_ENDPOINT, params={"query": parsed_domain}
                )
                parse_data = self.parse_domain_data(domain_data)
                applogger.debug(
                    "{}(method={}) ip associated with domain {} are {}".format(
                        self.logs_starts_with, __method_name, domain, len(parse_data)
                    )
                )
                domain_details += [domain_ip for domain_ip in parse_data]
                domain_indicator_list.append(domain)
                if len(domain_details) >= consts.POST_CHUNK_SIZE:
                    applogger.debug(
                        "{}(method={}) Total data to post: {}".format(
                            self.logs_starts_with, __method_name, len(domain_details)
                        )
                    )
                    self.rest_helper_obj.send_data_to_sentinel(
                        domain_details, consts.DOMAIN_TABLE_NAME, indicator_value=domain_indicator_list
                    )
                    if watchlist_flag:
                        self.checkpoint_obj.save_checkpoint(
                            domain, indicator_type="domain"
                        )
                    domain_details = []
                    domain_indicator_list = []
            if len(domain_details) > 0:
                applogger.debug(
                    "{}(method={}) Total data to post: {}".format(
                        self.logs_starts_with, __method_name, len(domain_details)
                    )
                )
                self.rest_helper_obj.send_data_to_sentinel(
                    domain_details, consts.DOMAIN_TABLE_NAME, indicator_value=domain_indicator_list
                )
                if watchlist_flag:
                    self.checkpoint_obj.save_checkpoint(domain, indicator_type="domain")
        except Exception as err:
            applogger.error(
                "{}(method={}) {}".format(self.logs_starts_with, __method_name, err)
            )
            raise TeamCymruScoutException()

    def parse_domain_data(self, domain_data):
        """
        To parse the domain data and updates the IPs with additional information.

        Args:
            domain_data (dict): A dictionary containing the domain data.

        Returns:
            list or None: If there are no IPs in the domain data.

        Raises:
            TeamCymruScoutException: If an error occurs during the parsing process.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            domain_ips = domain_data.get("ips")
            query = domain_data.get("query")
            start_date = domain_data.get("start_date")
            end_date = domain_data.get("end_date")
            if domain_ips:
                for ip in domain_ips:
                    ip.update(
                        {"query": query, "start_date": start_date, "end_date": end_date}
                    )
                    ip_tags = ip.get("tags", [])
                    if ip_tags:
                        tags_ids, tags_names = (
                            self.utility_obj.extract_ids_and_names_of_tags(ip_tags)
                        )
                        ip.update({"tags_id": tags_ids, "tags_name": tags_names})
            else:
                domain_ips = {
                    "query": query,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            return domain_ips
        except Exception as err:
            applogger.error(
                "{}(method={}) {}".format(self.logs_starts_with, __method_name, err)
            )
            raise TeamCymruScoutException()
