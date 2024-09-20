"""Module containing the BitSightBreaches class for fetching BitSight breaches data and posting it to Sentinel."""
import time

from ..SharedCode import consts
from ..SharedCode.bitsight_client import BitSight
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.get_logs_data import get_logs_data
from ..SharedCode.logger import applogger
from ..SharedCode.utils import CheckpointManager


class BitSightBreaches(BitSight):
    """Class for fetching BitSight breaches data and posting it to Sentinel."""

    def __init__(self, start_time) -> None:
        """Initialize BitSightBreaches object.

        Args:
            start_time (float): The start time for data fetching.
        """
        super().__init__()
        self.start_time = start_time
        self.check_env_var = self.check_environment_var_exist(
            [
                {"api_token": consts.API_TOKEN},
                {"Portfolio_Companies_table_name": consts.COMPANY_DETAIL_TABLE_NAME},
                {"Breaches_Table_Name": consts.BREACHES_TABLE_NAME},
                {"companies_list": consts.COMPANIES},
            ]
        )
        self.checkpoint_obj = CheckpointManager()
        self.breach_company_state = self.checkpoint_obj.get_state("breaches_company")
        self.breaches_details_state = self.checkpoint_obj.get_state("breaches_details")
        self.generate_auth_token()

    def get_breaches_data_into_sentinel(self) -> None:
        """Fetch breaches data for all companies or specified companies and post it to Sentinel."""
        if not self.check_env_var:
            raise BitSightException(
                "{} {} Some Environment variables are not set hence exiting the app.".format(
                    self.logs_starts_with, consts.BREACHES_FUNC_NAME
                )
            )

        applogger.info(
            "{} {} Fetching companies from companies table.".format(
                self.logs_starts_with, consts.BREACHES_FUNC_NAME
            )
        )
        logs_data, flag = get_logs_data()
        if not flag:
            applogger.info(
                "{} {} Companies are not available yet.".format(
                    self.logs_starts_with, consts.BREACHES_FUNC_NAME
                )
            )
            return

        applogger.info(
            "{} {} Fetched companies from companies table.".format(
                self.logs_starts_with, consts.BREACHES_FUNC_NAME
            )
        )
        logs_data = sorted(logs_data, key=lambda x: x["name_s"])
        company_names = [data["name_s"] for data in logs_data]

        if consts.COMPANIES.strip().lower() == "all":
            self.get_all_companies_breaches_details(company_names, logs_data)
        else:
            self.get_specific_company_breaches_details(company_names, logs_data)

    def get_all_companies_breaches_details(self, company_names, logs_data):
        """Fetch breaches data for all companies and post it to Sentinel.

        Args:
            company_names (list): List of company names.
            logs_data (list): List of log data.
        """
        count_companies = 0
        fetching_index = self.get_last_data_index(
            company_names, self.checkpoint_obj, self.breach_company_state
        )
        for company_index in range(fetching_index + 1, len(logs_data)):
            company_name = logs_data[company_index].get("name_s")
            if int(time.time()) >= self.start_time + 540:
                applogger.info(
                    "{} {} 9:00 mins executed hence breaking. In next iteration, start fetching from {}.".format(
                        self.logs_starts_with,
                        consts.BREACHES_FUNC_NAME,
                        company_name,
                    )
                )
                break
            company_guid = logs_data[company_index].get("guid_g")
            self.get_breaches_data(company_name, company_guid)
            count_companies += 1
            self.checkpoint_obj.save_checkpoint(
                self.breach_company_state,
                company_name,
                "breaches",
                company_name_flag=True,
            )
        applogger.info(
            "{} {} Posted {} companies data.".format(
                self.logs_starts_with, consts.BREACHES_FUNC_NAME, count_companies
            )
        )

    def get_specific_company_breaches_details(self, company_names, logs_data):
        """Fetch breaches data for specified companies and post it to Sentinel.

        Args:
            company_names (list): List of company names.
            logs_data (list): List of log data.
        """
        applogger.debug(
            "{} {} Fetching data for specified company names.".format(
                self.logs_starts_with, consts.BREACHES_FUNC_NAME
            )
        )
        count_companies = 0
        companies_to_get = self.get_specified_companies_list(
            company_names, consts.COMPANIES
        )
        company_names = list(map(str.lower, company_names))

        for company in companies_to_get:
            if int(time.time()) >= self.start_time + 540:
                applogger.info(
                    "{} {} 9:00 mins executed hence breaking. In next iteration, start fetching after {}".format(
                        self.logs_starts_with, consts.BREACHES_FUNC_NAME, company
                    )
                )
                break

            index = company_names.index(company)
            company_name = logs_data[index].get("name_s")
            company_guid = logs_data[index].get("guid_g")
            self.get_breaches_data(company_name, company_guid)
            count_companies += 1
        applogger.info(
            "{} {} Posted {} companies data.".format(
                self.logs_starts_with, consts.BREACHES_FUNC_NAME, count_companies
            )
        )

    def get_breaches_data(self, company_name, company_guid):
        """Fetch breaches data for a specific company and post it to Sentinel.

        Args:
            company_name (str): Name of the company.
            company_guid (str): GUID of the company.

        Raises:
            BitSightException: Raises exception if any error occurs.
        """
        try:
            checkpoint_key = "{}".format(company_guid)
            breaches_endpoint = consts.ENDPOINTS["breaches_endpoint_path"].format(
                company_guid
            )
            breaches_url = self.base_url + breaches_endpoint
            breaches_response = self.get_bitsight_data(breaches_url)
            if not breaches_response:
                return
            breaches_results = breaches_response.get("results", [])
            if not breaches_results:
                applogger.info(
                    "{} {} No new data found.".format(
                        self.logs_starts_with, consts.BREACHES_FUNC_NAME
                    )
                )
                return
            last_data = self.checkpoint_obj.get_last_data(self.breaches_details_state)
            last_checkpoint_company = self.checkpoint_obj.get_endpoint_last_data(
                last_data, "breaches", company_guid
            )
            max_date = (
                last_checkpoint_company if last_checkpoint_company else "0000-01-01"
            )
            body, checkpoint_date = self.create_breaches_data(
                breaches_results, company_name, company_guid, max_date
            )
            self.send_data_to_sentinel(
                body, consts.BREACHES_TABLE_NAME, company_name, breaches_endpoint
            )
            self.checkpoint_obj.save_checkpoint(
                self.breaches_details_state,
                last_data,
                "breaches",
                checkpoint_key,
                checkpoint_date,
            )

            # delete rating field after post.
            del breaches_response["results"]
        except BitSightException:
            applogger.error(
                "{} {} Exception occurred in get_breaches_data method.".format(
                    self.logs_starts_with, consts.BREACHES_FUNC_NAME
                )
            )
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error: {}".format(
                    self.logs_starts_with, consts.BREACHES_FUNC_NAME, err
                )
            )
            raise BitSightException()

    def create_breaches_data(
        self, breaches_results, company_name, company_guid, max_date
    ):
        """Create breaches data for a specific company.

        Args:
            breaches_results (list): List of breaches data.
            company_name (str): Name of the company.
            company_guid (str): GUID of the company.
            max_date (str): Maximum date of breaches data.

        Returns:
            body (list): List of breaches data.
            max_date (str): Maximum date of breaches data.
        """
        body = []
        if max_date == "0000-01-01":
            for breach in breaches_results:
                date_created = breach.get("date_created", "")
                if date_created and date_created > max_date:
                    max_date = date_created
                breach["company_name"] = company_name
                breach["company_guid"] = company_guid
                body.append(breach)
        else:
            for breach in breaches_results:
                date_created = breach.get("date_created", "")
                if date_created and date_created > max_date:
                    max_date = date_created
                    breach["company_name"] = company_name
                    breach["company_guid"] = company_guid
                    body.append(breach)
        return body, max_date
