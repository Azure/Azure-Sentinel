"""Module with BitSightFindingsSummary for fetching findings summary data and posting to Sentinel."""
import hashlib
import json
import time

from ..SharedCode import consts
from ..SharedCode.bitsight_client import BitSight
from ..SharedCode.bitsight_exception import BitSightException, BitSightTimeOutException
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
        super().__init__(start_time)
        self.start_time = start_time
        self.check_env_var = self.check_environment_var_exist(
            [
                {"api_token": consts.API_TOKEN},
                {"Portfolio_Companies_table_name": consts.COMPANY_DETAIL_TABLE_NAME},
                {"Findings_Summary_Table_Name": consts.FINDINGS_SUMMARY_TABLE_NAME},
                {"companies_list": consts.COMPANIES},
            ]
        )
        self.checkpoint_obj = CheckpointManager(
            connection_string=consts.CONN_STRING,
            table_name=consts.FINDINGS_SUMMARY_CHECKPOINT_TABLE
        )
        self.generate_auth_token()

    def get_findings_summary_data_into_sentinel(self):
        """Fetch findings summary data and post it to Sentinel."""
        try:
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
            logs_data = sorted(logs_data, key=lambda x: x["name"])
            company_names = [data["name"] for data in logs_data]

            if consts.COMPANIES.strip().lower() == "all":
                self.get_all_companies_findings_summary_details(company_names, logs_data)
            else:
                self.get_specific_company_findings_summary_details(company_names, logs_data)
        except BitSightTimeOutException:
            applogger.error(
                "{} {} 9:00 mins executed hence stopping the function app.".format(
                    self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME
                )
            )
            return
        except BitSightException as err:
            raise BitSightException(err)
        except KeyError as err:
            applogger.error(
                "BitSight: KeyError while getting company details: {}".format(err)
            )
            raise BitSightException()
        except Exception as err:
            applogger.error("BitSight: Exception: {}".format(err))
            raise BitSightException(err)

    def get_all_companies_findings_summary_details(self, company_names, logs_data):
        """Fetch findings summary details for all companies and post them to Sentinel.

        Args:
            company_names (list): List of company names.
            logs_data (list): List of log data.
        """
        try:
            count_companies = 0
            fetching_index = self.get_last_data_index(
                company_names, self.checkpoint_obj
            )
            for company_index in range(fetching_index + 1, len(logs_data)):
                company_name = logs_data[company_index].get("name")
                self.check_timeout()
                company_guid = logs_data[company_index].get("guid")
                self.get_findings_summary_data(company_name, company_guid)
                count_companies += 1
                self.checkpoint_obj.set_checkpoint(
                    partition_key=consts.COMPANY_CHECKPOINT_PARTITION_KEY,
                    row_key=consts.COMPANY_CHECKPOINT_ROW_KEY,
                    value=company_name
                )
            applogger.info(
                "{} {} Posted {} companies data.".format(
                    self.logs_starts_with,
                    consts.FINDINGS_SUMMARY_FUNC_NAME,
                    count_companies,
                )
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.error("BitSight: GET FINDING SUMMARY DETAILS ERROR: {}".format(err))
            raise BitSightException()

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
        try:
            count_companies = 0
            companies_to_get = self.get_specified_companies_list(
                company_names, consts.COMPANIES
            )
            company_names = list(map(str.lower, company_names))

            for company in companies_to_get:
                self.check_timeout()
                index = company_names.index(company)
                company_name = logs_data[index].get("name")
                company_guid = logs_data[index].get("guid")
                self.get_findings_summary_data(company_name, company_guid)
                count_companies += 1
            applogger.info(
                "{} {} Posted {} companies data.".format(
                    self.logs_starts_with,
                    consts.FINDINGS_SUMMARY_FUNC_NAME,
                    count_companies,
                )
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.error("BitSight: GET FINDING SUMMARY DETAILS ERROR: {}".format(err))
            raise BitSightException()

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
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
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
        try:
            checkpoint_key = "{}".format(company_guid)
            checkpoint_value = self.checkpoint_obj.get_checkpoint(
                partition_key=consts.DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key
            )
            last_checkpoint_company = json.loads(checkpoint_value) if checkpoint_value else []
            last_checkpoint_company = (
                last_checkpoint_company if last_checkpoint_company else []
            )
            findings_summary_endpoint = consts.ENDPOINTS[
                "findings_summary_endpoint_path"
            ].format(company_guid)
            end_date = findings_summary_data.get("end_date")
            start_date = findings_summary_data.get("start_date")
            stats = findings_summary_data.get("stats", [])

            for stat in stats:
                self.check_timeout()
                for vulnerability in vulnerabilities_response:
                    self.check_timeout()
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
            self.checkpoint_obj.set_checkpoint(
                partition_key=consts.DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key,
                value=json.dumps(last_checkpoint_company)
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error: {}".format(
                    self.logs_starts_with, consts.FINDINGS_SUMMARY_FUNC_NAME, err
                )
            )
            raise BitSightException()
