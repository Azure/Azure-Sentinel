"""Module for fetching BitSight companies details, ratings, and posting to Sentinel."""
import hashlib
import json
import time
import inspect

from ..SharedCode.bitsight_client import BitSight
from ..SharedCode.bitsight_exception import BitSightException, BitSightTimeOutException
from ..SharedCode.consts import (
    API_TOKEN,
    COMPANIES,
    COMPANIES_RATING_DETAILS_TABLE_NAME,
    COMPANY_DETAIL_TABLE_NAME,
    ENDPOINTS,
    COMPANY_DETAILS_FUNC_NAME,
    CONN_STRING,
    COMPANIES_CHECKPOINT_TABLE,
    RATING_CHECKPOINT_PARTITION_KEY,
    COMPANY_CHECKPOINT_PARTITION_KEY,
    COMPANY_CHECKPOINT_ROW_KEY,
    DATA_CHECKPOINT_PARTITION_KEY
)
from ..SharedCode.get_logs_data import get_logs_data
from ..SharedCode.logger import applogger
from ..SharedCode.utils import CheckpointManager


class BitSightCompanies(BitSight):
    """Class for fetching BitSight companies details and ratings data and posting it to Sentinel."""

    def __init__(self, start_time) -> None:
        """Initialize BitSightCompanies object.

        Args:
            start_time (float): The start time for data fetching.
        """
        super().__init__(start_time)
        self.start_time = start_time
        self.company_endpoint_path = ENDPOINTS["company_endpoint_path"]
        self.companies_str = COMPANIES
        self.check_env_var = self.check_environment_var_exist(
            [
                {"api_token": API_TOKEN},
                {"company_data_table_name": COMPANY_DETAIL_TABLE_NAME},
                {
                    "company_rating_details_table_name": COMPANIES_RATING_DETAILS_TABLE_NAME
                },
                {"companies_list": self.companies_str},
            ]
        )
        self.checkpoint_obj = CheckpointManager(
            connection_string=CONN_STRING,
            table_name=COMPANIES_CHECKPOINT_TABLE
        )
        self.generate_auth_token()

    def get_company_details(self, company_name, company_guid):
        """Post the data of company details/company ratings.

        Args:
            company_name (str): Name of the company for which details need to be fetched.
            company_guid (str): GUID of the company to pass in the URL.
        """
        try:
            data_to_post = None
            post_data_ratings = []
            checkpoint_key = "{}".format(company_guid)
            last_data_company_details = self.checkpoint_obj.get_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key
            )
            last_data_company_ratings = self.checkpoint_obj.get_checkpoint(
                partition_key=RATING_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key
            )
            company_detail_url = self.base_url + self.company_endpoint_path.format(
                company_guid
            )
            response = self.get_bitsight_data(company_detail_url)
            if not response:
                applogger.info(
                    "{} {} No new data found.".format(
                        self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME
                    )
                )
                return
            rating_details = response.get("rating_details", [])
            if rating_details:
                rating = json.dumps(rating_details, sort_keys=True)
                result = hashlib.sha512(rating.encode("utf-8"))
                result_hash = result.hexdigest()
                if result_hash != last_data_company_ratings:
                    ratingdetailskeys = rating_details.keys()
                    # filter out rating field from company details.
                    for rating_detail in ratingdetailskeys:
                        self.check_timeout()
                        rating = rating_details.get(rating_detail)
                        rating["Company_name"] = company_name
                        post_data_ratings.append(rating)
                    self.send_data_to_sentinel(
                        post_data_ratings,
                        COMPANIES_RATING_DETAILS_TABLE_NAME,
                        company_name,
                        "company rating details",
                    )
                else:
                    applogger.info(
                        "BitSight: The company rating details of {} company is already exist.".format(
                            company_name
                        )
                    )
                data_to_post = result_hash
                self.checkpoint_obj.set_checkpoint(
                    partition_key=RATING_CHECKPOINT_PARTITION_KEY,
                    row_key=checkpoint_key,
                    value=data_to_post
                )
                # delete rating field after post.
                del response["rating_details"]
            rating = json.dumps(response, sort_keys=True)
            result = hashlib.sha512(rating.encode("utf-8"))
            result_hash = result.hexdigest()
            if result_hash != last_data_company_details:
                self.send_data_to_sentinel(
                    response, COMPANY_DETAIL_TABLE_NAME, company_name, "company details"
                )
            else:
                applogger.info(
                    "{} {} The company details of {} company is already exist.".format(
                        self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, company_name
                    )
                )
            data_to_post = result_hash
            self.checkpoint_obj.set_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key,
                value=data_to_post
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except KeyError as err:
            applogger.error(
                "{} {} Key Error while getting Company data: {}".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, err
                )
            )
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error: {}".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, err
                )
            )
            raise BitSightException()

    def get_all_copmanies_details(self, logs_data, company_names):
        """Fetch details for all companies and post them to Sentinel.

        Args:
            logs_data (list): List of log data.
            company_names (list): List of company names.
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
                self.get_company_details(company_name, company_guid)
                count_companies += 1
                self.checkpoint_obj.set_checkpoint(
                    partition_key=COMPANY_CHECKPOINT_PARTITION_KEY,
                    row_key=COMPANY_CHECKPOINT_ROW_KEY,
                    value=company_name
                )
            applogger.info(
                "{} {} Posted {} companies data.".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, count_companies
                )
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except KeyError as err:
            applogger.error(
                "{} {} Key Error while getting Company data: {}".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, err
                )
            )
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error: {}".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, err
                )
            )
            raise BitSightException()

    def get_specified_companies_details(self, logs_data, company_names):
        """Fetch details for specified companies and post them to Sentinel.

        Args:
            logs_data (list): List of log data.
            company_names (list): List of company names.
        """
        applogger.debug(
            "{} {} Fetching data for specified company names.".format(
                self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME
            )
        )
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
                self.get_company_details(company_name, company_guid)
                count_companies += 1
            applogger.info(
                "{} {} Posted {} companies data.".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, count_companies
                )
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except KeyError as err:
            applogger.error(
                "{} {} Key Error while getting Company data: {}".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, err
                )
            )
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error: {}".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, err
                )
            )
            raise BitSightException()

    def get_bitsight_data_into_sentinel(self):
        """Fetch companies details and ratings data and post them to Sentinel."""
        try:
            if not self.check_env_var:
                raise BitSightException(
                    "{} {} Some Environment variables are not set hence exiting the app.".format(
                        self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME
                    )
                )

            applogger.info(
                "{} {} Fetching companies from companies table.".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME
                )
            )
            logs_data, flag = get_logs_data()
            if not flag:
                applogger.info(
                    "{} {} Companies are not available yet.".format(
                        self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME
                    )
                )
                return
            applogger.info(
                "{} {} Fetched companies from companies table.".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME
                )
            )
            logs_data = sorted(logs_data, key=lambda x: x["name"])
            company_names = [data["name"] for data in logs_data]
            if (self.companies_str.strip()).lower() == "all":
                self.get_all_copmanies_details(logs_data, company_names)
            else:
                self.get_specified_companies_details(logs_data, company_names)
        except BitSightTimeOutException:
            applogger.error(
                "{} {} 9:00 mins executed hence stopping the function app.".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME
                )
            )
            return
        except BitSightException:
            raise BitSightException()
        except KeyError as err:
            applogger.error(
                "{} {} KeyError while getting portfolios: {}".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, err
                )
            )
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error: {}".format(
                    self.logs_starts_with, COMPANY_DETAILS_FUNC_NAME, err
                )
            )
            raise BitSightException()
