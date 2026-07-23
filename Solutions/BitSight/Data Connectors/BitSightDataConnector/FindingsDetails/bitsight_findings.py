"""This file contains implementation of findings endpoint."""
import inspect
import time
import datetime
from ..SharedCode.logger import applogger
from ..SharedCode.bitsight_client import BitSight
from ..SharedCode.bitsight_exception import BitSightException, BitSightTimeOutException
from ..SharedCode.get_logs_data import get_logs_data
from ..SharedCode.utils import CheckpointManager
from ..SharedCode.consts import (
    API_TOKEN,
    FINDINGS_PAGE_SIZE,
    FINDINGS_TABLE_NAME,
    COMPANIES,
    ENDPOINTS,
    CONN_STRING,
    FINDINGS_CHECKPOINT_TABLE,
    COMPANY_CHECKPOINT_PARTITION_KEY,
    COMPANY_CHECKPOINT_ROW_KEY,
    DATA_CHECKPOINT_PARTITION_KEY,
    FINDINGS_FUNC_NAME
)


class BitSightFindings(BitSight):
    """Implementation of data ingestion."""

    def __init__(self, start_time) -> None:
        super().__init__(start_time)
        self.start_time = start_time
        self.companies_str = COMPANIES
        self.check_env_var = self.check_environment_var_exist(
            [
                {"api_token": API_TOKEN},
                {"findings_table_name": FINDINGS_TABLE_NAME},
                {"companies_list": self.companies_str},
            ]
        )
        self.checkpoint_obj = CheckpointManager(
            connection_string=CONN_STRING,
            table_name=FINDINGS_CHECKPOINT_TABLE
        )
        self.generate_auth_token()
        self.limit = FINDINGS_PAGE_SIZE
        self.findings_endpoint_path = ENDPOINTS["findings_endpoint_path"]

    def get_all_copmanies_findings_details(self, logs_data, company_names):
        try:
            count_companies = 0
            fetching_index = self.get_last_data_index(
                company_names, self.checkpoint_obj
            )
            for company_index in range(fetching_index + 1, len(logs_data)):
                company_name = logs_data[company_index].get("name")
                self.check_timeout()
                applogger.info(
                    "Fetching Index: {}, company name: {}".format(
                        company_index, company_name
                    )
                )
                company_guid = logs_data[company_index].get("guid")
                self.get_findings_details(company_name, company_guid)
                count_companies += 1
                self.checkpoint_obj.set_checkpoint(
                    partition_key=COMPANY_CHECKPOINT_PARTITION_KEY,
                    row_key=COMPANY_CHECKPOINT_ROW_KEY,
                    value=company_name
                )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.error("BitSight: GET FINDING DETAILS ERROR: {}".format(err))
            raise BitSightException()

    def get_specified_companies_findings_details(self, logs_data, company_names):
        try:
            count_companies = 0
            companies_to_get = self.get_specified_companies_list(
                company_names, self.companies_str
            )
            company_names = list(map(str.lower, company_names))
            for company in companies_to_get:
                self.check_timeout()
                index = company_names.index(company)
                company_name = logs_data[index].get("name")
                company_guid = logs_data[index].get("guid")
                self.get_findings_details(company_name, company_guid)
                count_companies += 1
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.error("BitSight: GET FINDING DETAILS ERROR: {}".format(err))
            raise BitSightException()

    def prepare_data_to_post(self, results, company_name):
        """Post data into sentinel.

        Args:
            results (dict): object to post
            company_name (str): company name
            risk (str): risk type
            checkpoint_key (str): checkpoint key
            data_to_post (str): last_see date
        """
        try:
            results = results.get("results")
            for result in results:
                self.check_timeout()
                details = []
                details.append(result["details"])
                result["details"] = details
                result["company_name"] = company_name
            return results
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: SEND DATA TO SENTINEL: {}".format(err))
            raise BitSightException()

    def get_findings_details(self, company_name, company_guid):
        """Post the data of findings details.

        Args:
            company_name (str): company name
            company_guid (str): company guid
        """
        try:
            data_to_post = None
            risk_categories = [
                {"risk_category": "Diligence"},
                {"risk_category": "Compromised Systems"},
                {"risk_category": "User Behavior"},
            ]
            findings_url = self.base_url + self.findings_endpoint_path.format(
                company_guid
            )
            for params in risk_categories:
                self.check_timeout()
                risk = params["risk_category"]
                checkpoint_key = "{}_{}".format(risk, company_guid)
                last_date = self.checkpoint_obj.get_checkpoint(
                    partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                    row_key=checkpoint_key
                )
                params["sort"] = "last_seen"
                params["limit"] = self.limit
                params["expand"] = "attributed_companies"
                params["offset"] = 0
                params["last_seen_gte"] = last_date if last_date is not None else ""
                results = self.get_bitsight_data(findings_url, params)
                if not results or len(results.get("results")) == 0:
                    applogger.info(
                        'BitSight: No new findings found for "{}" ({})'.format(
                            risk, company_name
                        )
                    )
                    continue
                results["id"] = risk
                results["Company_name"] = company_name
                next_link = results.get("links").get("next")
                index = len(results.get("results")) - 1
                data_to_post = results.get("results")[index].get("last_seen")
                formatted_data = self.prepare_data_to_post(results, company_name)
                data_to_post = datetime.datetime.strptime(data_to_post, "%Y-%m-%d")
                data_to_post += datetime.timedelta(days=1)
                self.send_data_to_sentinel(
                    formatted_data,
                    FINDINGS_TABLE_NAME,
                    company_name,
                    "findings details",
                )
                self.checkpoint_obj.set_checkpoint(
                    partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                    row_key=checkpoint_key,
                    value=str(data_to_post.date())
                )
                c_data = {}
                params["offset"] += self.limit
                page = 0
                while next_link:
                    self.check_timeout()
                    page += 1
                    applogger.info(
                        "BitSight: Findings: Page {} of {} ({})".format(
                            page, company_name, risk
                        )
                    )
                    c_data["next1"] = self.get_bitsight_data(findings_url, params)
                    next_link = c_data["next1"].get("links").get("next")
                    length_results = len(c_data.get("next1").get("results"))
                    if length_results == 0:
                        applogger.info(
                            'BitSight: No new findings found for {} on page {} ({})'.format(
                                company_name, page, risk
                            )
                        )
                        break
                    applogger.info(
                        "BitSight: Got {} findings for {} on page {}".format(
                            length_results, company_name, page
                        )
                    )
                    c_data["next1"]["id"] = risk
                    c_data["next1"]["Company_name"] = company_name
                    index = length_results - 1
                    data_to_post = (
                        c_data["next1"].get("results")[index].get("last_seen")
                    )
                    data_to_post = datetime.datetime.strptime(data_to_post, "%Y-%m-%d")
                    data_to_post += datetime.timedelta(days=1)
                    formatted_data = self.prepare_data_to_post(
                        c_data["next1"], company_name
                    )
                    self.send_data_to_sentinel(
                        formatted_data,
                        FINDINGS_TABLE_NAME,
                        company_name,
                        "findings details",
                    )
                    self.checkpoint_obj.set_checkpoint(
                        partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                        row_key=checkpoint_key,
                        value=str(data_to_post.date())
                    )
                    params["offset"] += self.limit
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.error("BitSight: GET FINDINGS DETAILS: {}".format(err))
            raise BitSightException()

    def get_bitsight_data_into_sentinel(self):
        try:
            applogger.info("BitSight: Started fetching findings data.")
            if not self.check_env_var:
                raise BitSightException(
                    "Some Environment variables are not set so exiting the app."
                )
            logs_data, flag = get_logs_data()
            if not flag:
                applogger.warning("Portfolio Companies are not available yet.")
                return
            logs_data = sorted(logs_data, key=lambda x: x["name"])
            company_names = [data["name"] for data in logs_data]
            if (self.companies_str.strip()).lower() == "all":
                self.get_all_copmanies_findings_details(logs_data, company_names)
            else:
                self.get_specified_companies_findings_details(logs_data, company_names)
        except BitSightTimeOutException:
            applogger.error(
                "{} {} 9:00 mins executed hence stopping the function app.".format(
                    self.logs_starts_with, FINDINGS_FUNC_NAME
                )
            )
            return
        except BitSightException as err:
            raise BitSightException(err)
        except KeyError as err:
            applogger.error(
                "BitSight: KeyError while getting portfolios: {}".format(err)
            )
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET COMPANY: {}".format(err))
            raise BitSightException()
