"""Module for fetching BitSight Alert, Graph and Statistics details and posting to Sentinel."""

import hashlib
import json
import time
from datetime import datetime
import inspect

from .bitsight_client import BitSight
from .bitsight_exception import BitSightException, BitSightTimeOutException
from .consts import *
from .get_logs_data import get_logs_data
from .logger import applogger
from .utils import CheckpointManager


class BitSightStatistics(BitSight):
    """Class for fetching BitSight Alert, Graph and Statistics details and posting it to Sentinel."""

    def __init__(self, start_time, statistics_type) -> None:
        """Initialize BitSightStatistics object.

        Args:
            start_time (float): The start time for data fetching.
            statistics_type (str): Type of statistics to fetch.
        """
        super().__init__(start_time)
        self.start_time = start_time
        self.statistics_type = statistics_type
        self.check_env_var = self.check_environment_var_exist(
            [
                {"api_token": API_TOKEN},
                {"companies_list": COMPANIES},
                {f"{self.statistics_type}_table_name".lower(): globals()[f"{self.statistics_type.upper()}_TABLE"]},
            ]
        )
        self.checkpoint_obj = CheckpointManager(
            connection_string=CONN_STRING,
            table_name=globals()[f"{self.statistics_type.upper()}_CHECKPOINT_TABLE"]
        )
        self.date_format = "%Y-%m-%d"
        self.statistics_path = ENDPOINTS[f"{self.statistics_type}_url"]
        self.companies_str = COMPANIES
        self.generate_auth_token()
    
    def get_risk_vector_data(self, endpoint, endpoint_path, company_name, company_guid, table_name):
        """Fetch risk vector data for a specific endpoint and post it to Sentinel.

        Args:
            endpoint (str): Name of the endpoint.
            endpoint_path (str): Path of the endpoint.
            company_name (str): Name of the company.
            company_guid (str): GUID of the company.
            table_name (str): Name of the table.

        Raises:
            BitSightException: Raises exception if any error occurs.
        """
        try:
            data_to_post = []
            risk_vector_data = []
            checkpoint_key = "{}".format(company_guid)

            checkpoint_value = self.checkpoint_obj.get_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key
            )
            last_data = json.loads(checkpoint_value) if checkpoint_value else []

            url = self.base_url + endpoint_path
            res_list = self.get_bitsight_data(url)
            if not res_list:
                return
            if res_list.get("risk_vectors"):
                risk_data = res_list.get("risk_vectors")
                risk_vectors = risk_data.keys()
                for risk_vector in risk_vectors:
                    self.check_timeout()
                    risk_vector_detail = risk_data.get(risk_vector)
                    risk_vector_detail["risk_vector"] = risk_vector
                    risk_vector_detail["Company_name"] = company_name
                    data = json.dumps(risk_vector_detail, sort_keys=True)
                    result = hashlib.sha512(data.encode("utf-8"))
                    result_hash = result.hexdigest()
                    if last_data:
                        if result_hash not in last_data:
                            risk_vector_data.append(risk_vector_detail)
                        data_to_post.append(result_hash)
                    else:
                        risk_vector_data.append(risk_vector_detail)
                        data_to_post.append(result_hash)
                self.send_data_to_sentinel(risk_vector_data, table_name, company_name, endpoint)
            self.checkpoint_obj.set_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key,
                value=json.dumps(data_to_post)
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error getting risk vector: {}".format(
                    self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, err
                )
            )
            raise BitSightException()

    def get_results_hash(self, data, p_data, company_name):
        """Generate a hash value for BitSight statistics results.

        Args:
            data (dict): The data to be included in the hash.
            p_data (dict): Additional data, such as date and grade, to be included in the hash.
            company_name (str): The name of the company associated with the data.

        Raises:
            BitSightException: If an error occurs during the hashing process.

        Returns:
            str: The SHA-512 hash value generated for the combined data.
        """
        try:
            data["date"] = p_data.get("date")
            data["grade"] = p_data.get("grade")
            data["company_name"] = company_name
            data = json.dumps(data, sort_keys=True)
            result = hashlib.sha512(data.encode())
            result_hash = result.hexdigest()
            return result_hash
        except Exception as error:
            applogger.exception(
                "{} {} Error in hashing: {}".format(self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, error)
            )
            raise BitSightException()

    def get_diligence_historical_statistics_details(self, company_name, company_guid):
        """Fetch and process diligence historical statistics for a specific company.

        Args:
            company_name (str): The name of the company.
            company_guid (str): The GUID of the company.

        Raises:
            BitSightException: If an error occurs during the process.
        """
        try:
            checkpoint_data_to_post = []
            post_data = []
            checkpoint_key = "{}".format(company_guid)
            checkpoint_value = self.checkpoint_obj.get_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key
            )
            last_data = json.loads(checkpoint_value) if checkpoint_value else []
            url = self.base_url + self.statistics_path.format(company_guid)
            response = self.get_bitsight_data(url)
            if not response:
                return
            if response.get("results"):
                results_data = response.get("results")
                for data in results_data:
                    self.check_timeout()
                    if data.get("counts"):
                        count_data = data.get("counts")
                        for count_category in count_data:
                            self.check_timeout()
                            result_hash = self.get_results_hash(count_category, data, company_name)
                            if (last_data and result_hash not in last_data) or not last_data:
                                count_category["grade"] = data["grade"]
                                count_category["parsed_date"] = data["date"]
                                post_data.append(count_category)
                                checkpoint_data_to_post.append(result_hash)
                            else:
                                checkpoint_data_to_post.append(result_hash)
                self.send_data_to_sentinel(
                    post_data,
                    DILIGENCE_HISTORICAL_STATISTICS_TABLE,
                    company_name,
                    "diligence_historical_statistics",
                )
            self.checkpoint_obj.set_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key,
                value=json.dumps(checkpoint_data_to_post)
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error in getting diligence historical statistics: {}".format(
                    self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, err
                )
            )
            raise BitSightException()

    def get_graph_data(self, company_name, company_guid):
        """Fetch and process graph data for a specific company.

        Args:
            company_name (str): The name of the company.
            company_guid (str): The GUID of the company.

        Raises:
            BitSightException: If an error occurs during the process.
        """
        try:
            data_to_post = []
            post_data = []
            last_rating = None
            current_rating = None
            rating_diff = None
            last_date = None
            checkpoint_key = "{}".format(company_guid)
            checkpoint_value = self.checkpoint_obj.get_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key
            )
            last_data = json.loads(checkpoint_value) if checkpoint_value else []
            if last_data:
                last_date = datetime.strptime(last_data[0], self.date_format)
                last_rating = last_data[1]
            url = self.base_url + self.statistics_path.format(company_guid)
            response = self.get_bitsight_data(url)
            if not response:
                return
            if response.get("ratings"):
                rating_data = response["ratings"]
                sorted_ratings = sorted(rating_data, key=lambda i: i["x"])
                count = 0
                # get rating of every date from response
                for rating in sorted_ratings:
                    self.check_timeout()
                    rating["Rating_Date"] = rating.pop("x")
                    rating["Rating"] = rating.pop("y")
                    rating["Company_name"] = company_name
                    rating["Rating_differance"] = None
                    date_in_object = datetime.strptime(rating["Rating_Date"], self.date_format)
                    if last_data:
                        if date_in_object.date() > last_date.date():
                            current_rating = rating["Rating"]
                            rating_diff = int(current_rating) - int(last_rating)
                            rating["Rating_differance"] = rating_diff
                            last_rating = current_rating
                            post_data.append(rating)
                            data_to_post = [rating["Rating_Date"], rating["Rating"]]
                        else:
                            data_to_post = [str(last_date.date()), rating["Rating"]]
                    else:
                        if count == 0:
                            last_rating = rating["Rating"]
                            rating["Rating_differance"] = rating_diff
                        else:
                            current_rating = rating["Rating"]
                            rating_diff = int(current_rating) - int(last_rating)
                            rating["Rating_differance"] = rating_diff
                            last_rating = current_rating
                        post_data.append(rating)
                        data_to_post = [rating["Rating_Date"], rating["Rating"]]
                        count += 1
            self.send_data_to_sentinel(post_data, GRAPH_DATA_TABLE, company_name, "graph")
            self.checkpoint_obj.set_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key,
                value=json.dumps(data_to_post)
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except KeyError as err:
            applogger.error("{} {} KeyError: {}".format(self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, err))
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "{} {} Error in getting graph data: {}".format(
                    self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, err
                )
            )
            raise BitSightException()

    def get_alerts_details(self, company_name, company_guid):
        """Fetch and process alerts details for a specific company.

        Args:
            company_name (str): The name of the company.
            company_guid (str): The GUID of the company.

        Raises:
            BitSightException: If an error occurs during the process.
        """
        try:
            data_to_post = None
            checkpoint_key = "{}".format(company_guid)
            last_date = self.checkpoint_obj.get_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key
            )
            if last_date:
                last_date = datetime.strptime(last_date, self.date_format).date()
            query_parameter = {"limit": ALERTS_PAGE_SIZE, "sort": "alert_date"}
            url = self.base_url + self.statistics_path.format(company_guid)
            response = self.get_bitsight_data(url, query_parameter)
            if not response:
                return
            next_link = response.get("links").get("next")
            alerts_data = []
            c_data = {}
            query_parameter["offset"] = 0
            while next_link:
                self.check_timeout()
                query_parameter["offset"] += query_parameter.get("limit")
                c_data["next1"] = self.get_bitsight_data(url, query_parameter)
                next_link = c_data["next1"].get("links").get("next")
                response.get("results").extend(c_data["next1"].get("results"))
            is_alert_exist = False
            for alert in response["results"]:
                self.check_timeout()
                current_date = alert["alert_date"]
                if last_date:
                    if alert["company_name"].lower() == company_name.lower():
                        is_alert_exist = True
                        current_date = datetime.strptime(current_date, self.date_format).date()
                        if current_date > last_date:
                            data_to_post = alert["alert_date"]
                            alerts_data.append(alert)
                        else:
                            data_to_post = str(last_date)
                else:
                    if alert["company_name"].lower() == company_name.lower():
                        is_alert_exist = True
                        data_to_post = alert["alert_date"]
                        alerts_data.append(alert)
            if alerts_data:
                self.send_data_to_sentinel(alerts_data, ALERTS_DATA_TABLE, company_name, "alerts_data")
            else:
                if is_alert_exist:
                    applogger.info(
                        "{} {} The data of alerts for {} company is already exist.".format(
                            self.logs_starts_with,
                            ALERT_GRAPH_STATISTICS_FUNC_NAME,
                            company_name,
                        )
                    )
                else:
                    applogger.info(
                        "{} {} No alert data found for {} company from BitSight.".format(
                            self.logs_starts_with,
                            ALERT_GRAPH_STATISTICS_FUNC_NAME,
                            company_name,
                        )
                    )
            self.checkpoint_obj.set_checkpoint(
                partition_key=DATA_CHECKPOINT_PARTITION_KEY,
                row_key=checkpoint_key,
                value=data_to_post
            )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("{} {} Error: {}".format(self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, err))
            raise BitSightException()

    def get_all_companies_alerts_graph_statistics_detailsnRuleName(self, logs_data, company_names):
        """Fetch alerts, graph, and statistics details for all companies.

        Args:
            logs_data (list): List of log data.
            company_names (list): List of company names.
        """
        fetching_index = self.get_last_data_index(
            company_names,
            self.checkpoint_obj,
        )
        try:
            for company_index in range(fetching_index + 1, len(logs_data)):
                self.check_timeout()
                company_name = logs_data[company_index].get("name")
                company_guid = logs_data[company_index].get("guid")
                self.get_company_alerts_graph_statistics_details(company_name, company_guid)
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
            applogger.exception("{} {} Error: {}".format(self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, err))
            raise BitSightException()

    def get_specified_companies_alerts_graph_statistics_details(self, logs_data, company_names):
        """Fetch alerts, graph, and statistics details for specified companies.

        Args:
            logs_data (list): List of log data.
            company_names (list): List of company names.
        """
        applogger.debug(
            "{} {} Fetching data for specified company names.".format(
                self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME
            )
        )
        try:
            companies_to_get = self.get_specified_companies_list(company_names, self.companies_str)
            company_names = list(map(str.lower, company_names))
            for company in companies_to_get:
                self.check_timeout()
                index = company_names.index(company)
                company_name = logs_data[index].get("name")
                company_guid = logs_data[index].get("guid")
                self.get_company_alerts_graph_statistics_details(company_name, company_guid)
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("{} {} Error: {}".format(self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, err))
            raise BitSightException()

    def get_company_alerts_graph_statistics_details(self, company_name, company_guid):
        """Fetch alerts, graph, and statistics details for a specific company.

        Args:
            company_name (str): Name of the company.
            company_guid (str): GUID of the company.
        """
        try:
            if self.statistics_type in [
                DILIGENCE_STATISTICS_TYPE,
                INDUSTRIES_STATISTICS_TYPE,
                OBSERVATIONS_STATISTICS_TYPE,
            ]:
                self.get_risk_vector_data(
                    endpoint=self.statistics_type,
                    endpoint_path=self.statistics_path.format(company_guid),
                    company_name=company_name,
                    company_guid=company_guid,
                    table_name=globals()[f"{self.statistics_type.upper()}_TABLE"],
                )
            elif self.statistics_type == DILIGENCE_HISTORICAL_STATISTICS_TYPE:
                self.get_diligence_historical_statistics_details(company_name, company_guid)
            elif self.statistics_type == GRAPH_DATA_TYPE:
                self.get_graph_data(company_name, company_guid)
            elif self.statistics_type == ALERTS_DATA_TYPE:
                self.get_alerts_details(company_name, company_guid)
            else:
                raise BitSightException(
                    "{} {} Invalid statistics type : {}".format(
                        self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, self.statistics_type
                    )
                )
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("{} {} Error: {}".format(self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, err))
            raise BitSightException()

    def get_bitsight_data_into_sentinel(self):
        """Fetch data from BitSight and post it to Sentinel."""
        try:
            if not self.check_env_var:
                raise BitSightException(
                    "{} {} Some Environment variables are not set hence exiting the app.".format(
                        self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME
                    )
                )

            applogger.info(
                "{} {} Fetching companies from companies table.".format(
                    self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME
                )
            )
            logs_data, flag = get_logs_data()
            if not flag:
                applogger.info(
                    "{} {} Companies are not available yet.".format(
                        self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME
                    )
                )
                return
            applogger.info(
                "{} {} Fetched companies from companies table.".format(
                    self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME
                )
            )
            logs_data = sorted(logs_data, key=lambda x: x["name"])
            company_names = [data["name"] for data in logs_data]
            if (self.companies_str.strip()).lower() == "all":
                self.get_all_companies_alerts_graph_statistics_detailsnRuleName(logs_data, company_names)
            else:
                self.get_specified_companies_alerts_graph_statistics_details(logs_data, company_names)
        except BitSightTimeOutException:
            applogger.error(
                "{} {} 9:00 mins executed hence stopping the function app.".format(
                    self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME
                )
            )
            return
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("{} {} Error: {}".format(self.logs_starts_with, ALERT_GRAPH_STATISTICS_FUNC_NAME, err))
            raise BitSightException()
