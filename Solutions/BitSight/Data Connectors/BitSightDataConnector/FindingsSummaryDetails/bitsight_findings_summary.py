"""Module with BitSightFindingsSummary for fetching findings summary data and posting to Sentinel."""
import hashlib
import json
import time

from ..SharedCode import consts
from ..SharedCode.bitsight_client import BitSight
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.get_logs_data import get_logs_data
from ..SharedCode.logger import applogger
from ..SharedCode.utils import CheckpointManager


class BitSightFindingsSummary(BitSight):
    """Class for fetching BitSight findings summary data and posting it to Sentinel."""

    def __init__(self, start_time) -> None:
        """Initialize BitSightFindingsSummary object.

        Args:
            start_time (float): The start time for data fetching.
        """
        super().__init__()
        self.start_time = start_time
        self.check_env_var = self.check_environment_var_exist(
            [
                {"api_token": consts.API_TOKEN},
                {"Portfolio_Companies_table_name": consts.COMPANY_DETAIL_TABLE_NAME},
                {"Findings_Summary_Table_Name": consts.FINDINGS_SUMMARY_TABLE_NAME},
                {"companies_list": consts.COMPANIES},
            ]
        )
        self.checkpoint_obj = CheckpointManager()
        self.findings_summary_company_state = self.checkpoint_obj.get_state(
            "findings_summary_company"
        )
        self.findings_summary_details_state = self.checkpoint_obj.get_state(
            "findings_summary_details"
        )
        self.generate_auth_token()

    def get_findings_summary_data_into_sentinel(self):
        """Fetch findings summary data and post it to Sentinel."""
        if not self.check_env_var:
            raise BitSightException(
                "{} {} Some Environment variables are not set hence exiting the app.".format(
                    self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME
                )
            )
        applogger.info(
            "{} {} Fetching companies from companies table.".format(
                self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME
            )
        )
        logs_data, flag = get_logs_data()
        if not flag:
            applogger.info(
                "{} {} Companies are not available yet.".format(
                    self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME
                )
            )
            return

        applogger.info(
            "{} {} Fetched companies from companies table.".format(
                self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME
            )
        )
        logs_data = sorted(logs_data, key=lambda x: x["name_s"])
        company_names = [data["name_s"] for data in logs_data]

        if consts.COMPANIES.strip().lower() == "all":
            self.get_all_companies_findings_summary_details(company_names, logs_data)
        else:
            self.get_specific_company_findings_summary_details(company_names, logs_data)

    def get_all_companies_findings_summary_details(self, company_names, logs_data):
        """Fetch findings summary details for all companies and post them to Sentinel.

        Args:
            company_names (list): List of company names.
            logs_data (list): List of log data.
        """
        count_companies = 0
        fetching_index = self.get_last_data_index(
            company_names, self.checkpoint_obj, self.findings_summary_company_state
        )
        for company_index in range(fetching_index + 1, len(logs_data)):
            company_name = logs_data[company_index].get("name_s")
            if int(time.time()) >= self.start_time + 540:
                applogger.info(
                    "{} {} 9:00 mins executed hence breaking. In next iteration, start fetching from {}.".format(
                        self.logs_starts_with,
                        consts.FINDINGS_SUMMARY_FUNC_NAME,
                        company_name,
                    )
                )
                break
            company_guid = logs_data[company_index].get("guid_g")
            self.get_findings_summary_data(company_name, company_guid)
            count_companies += 1
            self.checkpoint_obj.save_checkpoint(
                self.findings_summary_company_state,
                company_name,
                "findings_summary",
                company_name_flag=True,
            )
        applogger.info(
            "{} {} Posted {} companies data.".format(
                self.logs_starts_with,
                consts.FINDINGS_SUMMARY_FUNC_NAME,
                count_companies,
            )
        )

    def get_specific_company_findings_summary_details(self, company_names, logs_data):
        """Fetch findings summary details for specified companies and post them to Sentinel.

        Args:
            company_names (list): List of company names.
            logs_data (list): List of log data.
        """
        applogger.debug(
            "{} {} Fetching data for specified company names.".format(
                self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME
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
                        self.logs_starts_with,
                        consts.FINDINGS_SUMMARY_FUNC_NAME,
                        company,
                    )
                )
                break
            index = company_names.index(company)
            company_name = logs_data[index].get("name_s")
            company_guid = logs_data[index].get("guid_g")
            self.get_findings_summary_data(company_name, company_guid)
            count_companies += 1
        applogger.info(
            "{} {} Posted {} companies data.".format(
                self.logs_starts_with,
                consts.FINDINGS_SUMMARY_FUNC_NAME,
                count_companies,
            )
        )

    def get_findings_summary_data(self, company_name, company_guid):
        """Fetch findings summary data for a specific company and post it to Sentinel.

        Args:
            company_name (str): Name of the company.
            company_guid (str): GUID of the company.

        Raises:
            BitSightException: Raised when invalid findings summary data is received.
        """
        try:
            findings_summary_endpoint = consts.ENDPOINTS[
                "findings_summary_endpoint_path"
            ].format(company_guid)
            findings_summary_url = self.base_url + findings_summary_endpoint
            findings_summary_results = self.get_bitsight_data(findings_summary_url)
            if not (findings_summary_results and findings_summary_results[-1]):
                applogger.info(
                    "{} {} No new data found.".format(
                        self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME
                    )
                )
                return

            req_params = {}
            req_params["fields"] = "name,display_name,description,severity"
            vulnerabilities_response = self.get_bitsight_data(
                consts.VULNERABILITIES_URL, query_parameter=req_params
            )

            if not vulnerabilities_response:
                applogger.info(
                    "{} {} No vulnerabilities data found.".format(
                        self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME
                    )
                )
                return

            self.create_findings_summary_data(
                findings_summary_results[-1],
                vulnerabilities_response,
                company_name,
                company_guid,
            )

            # delete rating field after post.
            del findings_summary_results
        except BitSightException:
            applogger.error(
                "{} {} Exception occurred in get_findings_summary_data method.".format(
                    self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME
                )
            )
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error: {}".format(
                    self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME, err
                )
            )
            raise BitSightException()

    def create_findings_summary_data(
        self,
        findings_summary_data,
        vulnerabilities_response,
        company_name,
        company_guid,
    ):
        """Create findings summary data and post it to Sentinel.

        Args:
            findings_summary_data (dict): Findings summary data.
            vulnerabilities_response (list): Vulnerabilities response data.
            company_name (str): Name of the company.
            company_guid (str): GUID of the company.
        """
        last_data = self.checkpoint_obj.get_last_data(
            self.findings_summary_details_state
        )
        last_checkpoint_company = self.checkpoint_obj.get_endpoint_last_data(
            last_data, "findings_summary", company_guid
        )
        last_checkpoint_company = (
            last_checkpoint_company if last_checkpoint_company else []
        )
        findings_summary_endpoint = consts.ENDPOINTS[
            "findings_summary_endpoint_path"
        ].format(company_guid)
        checkpoint_key = "{}".format(company_guid)
        end_date = findings_summary_data.get("end_date")
        start_date = findings_summary_data.get("start_date")
        stats = findings_summary_data.get("stats", [])

        for stat in stats:
            for vulnerability in vulnerabilities_response:
                if stat.get("name") == vulnerability.get("display_name"):
                    stat["description"] = vulnerability.get("description")
                    stat["severity"] = vulnerability.get("severity")
                    stat["end_date"] = end_date
                    stat["start_date"] = start_date
                    stat["Company"] = company_name

                    body = json.dumps(stat, sort_keys=True)
                    data_hash = hashlib.sha512(body.encode())
                    result_hash = data_hash.hexdigest()
                    if (
                        last_checkpoint_company
                        and result_hash not in last_checkpoint_company
                    ) or not last_checkpoint_company:
                        last_checkpoint_company.append(result_hash)
                        self.send_data_to_sentinel(
                            stat,
                            consts.FINDINGS_SUMMARY_TABLE_NAME,
                            company_name,
                            findings_summary_endpoint,
                        )

        self.checkpoint_obj.save_checkpoint(
            self.findings_summary_details_state,
            last_data,
            "findings_summary",
            checkpoint_key,
            last_checkpoint_company,
        )
