"""This file contains implementation of alert, graph, and statistics endpoint."""
import requests
import base64
import os
import hashlib
import json
import ast
from datetime import datetime
from ..SharedCode.logger import applogger
from .bitsight_constants import ENDPOINT_DISPATHCER
from ..SharedCode.azure_sentinel import AzureSentinel
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.state_manager import StateManager

# fetch data from os environment
api_token = os.environ.get("API_token")
connection_string = os.environ["AzureWebJobsStorage"]
diligence_statistics_table = os.environ.get("Diligence_Statistics_Table_Name")
industrial_statistics_table = os.environ.get("Industrial_Statistics_Table_Name")
observation_statistics_table = os.environ.get("Observation_Statistics_Table_Name")
diligence_historical_statistics_table = os.environ.get("Diligence_Historical_Statistics_Table_Name")
graph_data_table = os.environ.get("Graph_Table_Name")
alerts_data_table = os.environ.get("Alerts_Table_Name")

# in companies variable user need to pass slash separated names of companies
# for example: "Actors Films/Goliath Investments LLC/HCL Group/Saperix, Inc."
companies_str = os.environ.get("Companies")


class BitSight:
    """Implementation of data ingestion."""

    def __init__(self) -> None:
        """Contains class variable."""
        self.headers = None
        self.check_env_var = True
        self.state = None
        self.check_environment_var_exist()
        self.generate_auth_token()
        self.date_format = "%Y-%m-%d"
        self.azuresentinel = AzureSentinel()
        self.base_url = ENDPOINT_DISPATHCER['base_url']
        self.portfolio_path = ENDPOINT_DISPATHCER['portfolio_path']
        self.diligence_statistics_path = ENDPOINT_DISPATHCER['diligence_statistics_url']
        self.industrial_statistics_path = ENDPOINT_DISPATHCER['industries_statistics_url']
        self.observation_statistics_path = ENDPOINT_DISPATHCER['observations_statistics_url']
        self.diligence_historical_statistics_path = ENDPOINT_DISPATHCER['diligence_historical-statistics_url']
        self.graph_data_path = ENDPOINT_DISPATHCER['graph_data_url']
        self.alerts_details_path = ENDPOINT_DISPATHCER['alerts_url']

    def check_environment_var_exist(self):
        """Stop execution if os environment is not set.

        Raises:
            BitSightException: will raise if there is any unset variable which is used in this function.
        """
        env_var = [{"api_token": api_token},
                   {"diligence_statistics_table_name": diligence_statistics_table},
                   {"industrial_statistics_table_name": industrial_statistics_table},
                   {"observation_statistics_table_name": observation_statistics_table},
                   {"diligence_historical_statistics_table_name": diligence_historical_statistics_table},
                   {"graph_data_table_name": graph_data_table},
                   {"alerts_data_table_name": alerts_data_table},
                   {"companies_list": companies_str}]
        try:
            applogger.debug("BitSight: started checking existence of all custom environment variable")
            for var in env_var:
                key, val = next(iter(var.items()))
                if (val is None):
                    self.check_env_var = False
                    raise BitSightException(
                        "BitSight: ENVIRONMENT VARIABLE {} is not set in the function app environment.".format(key)
                        )
            applogger.debug("BitSight: All custom environment variable is exist.")
        except BitSightException as error:
            applogger.exception(error)
            raise BitSightException()
        except Exception as error:
            applogger.exception("BitSight: ENVIRONMENT VARIABLE {}".format(error))
            raise BitSightException()

    def generate_auth_token(self):
        """Initialize Authentication parameter."""
        try:
            applogger.info("BitSight: Started generating auth header to authenticate BitSight APIs.")
            api = [api_token, api_token]
            connector = ":"
            api = connector.join(api)
            user_and_pass = base64.b64encode(api.encode()).decode("ascii")
            headers = {
                'Accept': 'application/json',
                'X-BITSIGHT-CONNECTOR-NAME-VERSION': 'Microsoft Sentinel Data Connector 1.0.0',
                'X-BITSIGHT-CALLING-PLATFORM-VERSION': 'Microsoft-Sentinel'
                }
            headers['Authorization'] = 'Basic %s' % user_and_pass
            self.headers = headers
            applogger.info("BitSight: Successfully generated the authentication header.")
        except Exception as error:
            applogger.exception("BitSight: GENERATE AUTH TOKEN {}".format(error))
            raise BitSightException()

    def get_last_data(self):
        """Fetch last data from checkpoint file.

        Returns:
            None/json: last_data
        """
        try:
            self.state = StateManager(connection_string=connection_string, file_path="alerts-graph-statistics-details")
            last_data = self.state.get()
            if last_data is not None:
                last_data = json.loads(last_data)
            return last_data
        except Exception as err:
            applogger.exception("BitSight: GET LAST DATA {}".format(err))
            raise BitSightException()

    def save_checkpoint(self, data, endpoint, checkpoint_key, value):
        """Post checkpoint into sentinel.

        Args:
            endpoint (str): endpoint for which user want to save checkpoint
            checkpoint_key (str): checkpoint key
            value (str): value to be set in checkpoint key
        """
        try:
            if data is None:
                data = {}
                data[endpoint] = {}
            elif endpoint not in data:
                data[endpoint] = {}
            data[endpoint][checkpoint_key] = value
            self.state.post(json.dumps(data))
            applogger.info(
                "BitSight: save_checkpoint: {} -> {} successfully posted data.".format(
                    endpoint, checkpoint_key
                    )
                )
            applogger.debug(
                "BitSight: save_checkpoint: {}: {}: Posted Data: {}".format(
                    endpoint, checkpoint_key, data[endpoint][checkpoint_key]
                    )
                )
        except Exception as err:
            applogger.exception("BitSight: SAVE CHECKPOINT: {}".format(err))
            raise BitSightException()

    def get_bitsight_data(self, endpoint_path, query_parameter=None):
        """Fetch data from BitSight APIs.

        Args:
            endpoint_path (str): endpoint path for which user want to call the API.
            query_parameter (json, optional): Defaults to None.

        Returns:
            json: response of the API.
        """
        try:
            url = self.base_url + endpoint_path
            resp = requests.get(url=url, headers=self.headers, params=query_parameter)
            if(resp.status_code == 200):
                response = resp.json()
                applogger.debug(
                    "BitSight: get_bitsight_data: Successfully got response for endpoint_path: {}".format(
                        endpoint_path
                        )
                    )
                return response
            else:
                raise BitSightException(
                    "BitSight API( {} ):  Response code: {} \nError: {}".format(
                        url, resp.status_code, resp.text
                    )
                )
        except BitSightException as error:
            applogger.exception(error)
            raise BitSightException()
        except requests.exceptions.Timeout as err:
            applogger.exception("BitSight: Request Timeout for {}: {}".format(endpoint_path, err))
            raise BitSightException()
        except requests.exceptions.RequestException as err:
            applogger.exception("BitSight: Request exception for {}: {}".format(endpoint_path, err))
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET BITSIGHT DATA FOR {}: {}".format(endpoint_path, err))
            raise BitSightException()

    def get_endpoint_last_data(self, last_data, endpoint, company_guid):
        """Fetch value of checkpoint for particular checkpoint key.

        Args:
            endpoint (str): endpoint name
            company_guid (str): this will use as checkpoint key

        Returns:
            list: last checkpoint data for particular checkpoint
        """
        try:
            checkpoint_key = "{}".format(company_guid)
            if last_data is not None:
                if(last_data.get(endpoint)):
                    endpoint_last_data = last_data.get(endpoint)
                    if(endpoint_last_data.get(checkpoint_key)):
                        last_data = endpoint_last_data.get(checkpoint_key)
                        if (endpoint in ["diligence_statistics",
                                         "industries_statistics",
                                         "observations_statistics",
                                         "diligence_historical-statistics"]):
                            last_data = ast.literal_eval(last_data)
                        applogger.debug(
                            "BitSight: get_endpoint_last_data: {}: {}: Data: {}".format(
                                endpoint, checkpoint_key, last_data
                                )
                            )
                    else:
                        last_data = []
                        applogger.debug(
                            "BitSight: get_endpoint_last_data: No checkpoint data for {} -> {}".format(
                                endpoint, checkpoint_key
                                )
                            )
                else:
                    last_data = []
                    applogger.debug(
                        "BitSight: get_endpoint_last_data: No checkpoint data for {} endpoint".format(
                            endpoint)
                        )
            else:
                last_data = []
                applogger.debug("BitSight: get_endpoint_last_data: No checkpoint file created")
            return last_data
        except KeyError as err:
            applogger.exception("BitSight: GET ENDPOINT LAST DATA: {}".format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET ENDPOINT LAST DATA: {}".format(err))
            raise BitSightException()

    def send_data_to_sentinel(self, data, data_table, endpoint, company_name, is_alert_exist=True):
        """To post the data into sentinel.

        Args:
            data (dict): data to post in sentinel
            data_table (str): log type
            endpoint (str): endpoint
            company_name (str): company name
        """
        try:
            if data:
                body = json.dumps(data)
                post_data_status_code = self.azuresentinel.post_data(body, data_table)
                if(post_data_status_code >= 200 and post_data_status_code <= 299):
                    applogger.info(
                        "BitSight: [status code {}] Successfully posted the {} data of {} company.".format(
                            post_data_status_code, endpoint, company_name
                            )
                        )
                else:
                    applogger.error(
                        "BitSight: [status code {}] The {} data of {} company is not posted".format(
                            post_data_status_code, endpoint, company_name
                            )
                        )
                    raise BitSightException()
            else:
                if is_alert_exist is True:
                    applogger.info(
                        "BitSight: The data of {} for {} company is already exist.".format(
                            endpoint, company_name
                            )
                        )
                else:
                    applogger.info(
                        "BitSight: No alert data found for {} company from BitSight.".format(
                            company_name
                            )
                        )
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: SEND DATA TO SENTINEL: {}".format(err))
            raise BitSightException()

    def get_risk_vector_data(self, endpoint, endpoint_path, company_name, company_guid, table_name):
        """Post the data of diligence/industries/observation_statistics.

        Args:
            endpoint (str): diligence/industries/observation_statistics
            endpoint_path (str): endpoint path
            company_name (str): company name
            company_guid (str): company guid
            table_name (str): name of table to store data
        """
        try:
            data_to_post = []
            risk_vector_data = []
            checkpoint_key = "{}".format(company_guid)
            checkpoint_data = self.get_last_data()
            last_data = self.get_endpoint_last_data(checkpoint_data, endpoint, company_guid)
            res_list = self.get_bitsight_data(endpoint_path)
            if(res_list.get("risk_vectors")):
                risk_data = res_list.get("risk_vectors")
                risk_vectors = risk_data.keys()
                for risk_vector in risk_vectors:
                    j = risk_data.get(risk_vector)
                    j['risk_vector'] = risk_vector
                    j['Company_name'] = company_name
                    i = json.dumps(j, sort_keys=True)
                    result = hashlib.sha512(i.encode())
                    result_hash = result.hexdigest()
                    if last_data:
                        if (result_hash not in last_data):
                            risk_vector_data.append(j)
                        data_to_post.append(result_hash)
                    else:
                        risk_vector_data.append(j)
                        data_to_post.append(result_hash)
                self.send_data_to_sentinel(risk_vector_data, table_name, endpoint, company_name)
            data_to_post = str(data_to_post)
            self.save_checkpoint(checkpoint_data, endpoint, checkpoint_key, data_to_post)
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET RISK VECTOR: {}".format(err))
            raise BitSightException()

    def get_graph_data(self, company_name, company_guid):
        """Fetch and post the graph data.

        Args:
            company_name (str): company name
            company_guid (str): company guid
        """
        try:
            data_to_post = []
            post_data = []
            last_rating = None
            current_rating = None
            rating_diff = None
            last_date = None
            checkpoint_key = "{}".format(company_guid)
            checkpoint_data = self.get_last_data()
            last_data = self.get_endpoint_last_data(checkpoint_data, "graph_data", company_guid)
            if last_data:
                last_date = datetime.strptime(last_data[0], self.date_format)
                last_rating = last_data[1]
            endpoint_path = self.graph_data_path.format(company_guid)
            response = self.get_bitsight_data(endpoint_path)
            if(response.get("ratings")):
                rating_data = response["ratings"]
                sorted_ratings = sorted(rating_data, key=lambda i: i['x'])
                count = 0
                # get rating of every date from response
                for rating in sorted_ratings:
                    rating['Rating_Date'] = rating.pop('x')
                    rating['Rating'] = rating.pop('y')
                    rating['Company_name'] = company_name
                    rating['Rating_differance'] = None
                    date_in_object = datetime.strptime(rating['Rating_Date'], self.date_format)
                    if last_data:
                        if(date_in_object.date() > last_date.date()):
                            current_rating = rating['Rating']
                            rating_diff = int(current_rating) - int(last_rating)
                            rating['Rating_differance'] = rating_diff
                            last_rating = current_rating
                            post_data.append(rating)
                            data_to_post = [rating['Rating_Date'], rating['Rating']]
                        else:
                            data_to_post = [str(last_date.date()), rating['Rating']]
                    else:
                        if count == 0:
                            last_rating = rating['Rating']
                            rating['Rating_differance'] = rating_diff
                        else:
                            current_rating = rating['Rating']
                            rating_diff = int(current_rating) - int(last_rating)
                            rating['Rating_differance'] = rating_diff
                            last_rating = current_rating
                        post_data.append(rating)
                        data_to_post = [rating['Rating_Date'], rating['Rating']]
                        count += 1
            self.send_data_to_sentinel(post_data, graph_data_table, "graph", company_name)
            self.save_checkpoint(checkpoint_data, "graph_data", checkpoint_key, data_to_post)
        except BitSightException:
            raise BitSightException()
        except KeyError as err:
            applogger.exception("bitSight: GET GRAPH DATA: {}".format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET GRAPH DATA: {}".format(err))
            raise BitSightException()

    def get_alerts_details(self, company_name, company_guid):
        """Fetch and post the alert data.

        Args:
            company_name (str): company name
            company_guid (str): company guid
        """
        try:
            data_to_post = None
            checkpoint_key = "{}".format(company_guid)
            checkpoint_data = self.get_last_data()
            last_date = self.get_endpoint_last_data(checkpoint_data, "alerts", company_guid)
            if last_date:
                last_date = datetime.strptime(last_date, self.date_format).date()
            query_parameter = {
                'limit': 1000,
                'sort': 'alert_date'
            }
            endpoint_path = self.alerts_details_path.format(company_guid)
            response = self.get_bitsight_data(endpoint_path, query_parameter)
            next_link = (response.get('links').get('next'))
            alert = []
            query_parameter['offset'] = 1000
            c_data = {}
            while next_link:
                c_data['next1'] = self.get_bitsight_data(endpoint_path, query_parameter)
                next_link = (c_data['next1'].get('links').get('next'))
                response.get('results').extend(c_data['next1'].get('results'))
                query_parameter['offset'] = query_parameter['offset'] + 1000
            is_alert_exist = False
            for i in response["results"]:
                current_date = i['alert_date']
                if last_date:
                    if i['company_name'].lower() == company_name.lower():
                        is_alert_exist = True
                        current_date = datetime.strptime(current_date, self.date_format).date()
                        if(current_date > last_date):
                            data_to_post = i['alert_date']
                            alert.append(i)
                        else:
                            data_to_post = str(last_date)
                else:
                    if i['company_name'].lower() == company_name.lower():
                        is_alert_exist = True
                        data_to_post = i['alert_date']
                        alert.append(i)
            self.send_data_to_sentinel(alert, alerts_data_table, "alert", company_name, is_alert_exist)
            self.save_checkpoint(checkpoint_data, "alerts", checkpoint_key, data_to_post)
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET ALERT DATA: {}".format(err))
            raise BitSightException()

    def get_results_hash(self, data, p_data, company_name):
        """Encode the data to maintain checkpoint.

        Args:
            data (dict): inner data
            p_data (dict): outer data
            company_name (str): company name

        Returns:
            str: digestSHA512 hexdigest of data
        """
        try:
            data['date'] = p_data.get("date")
            data['grade'] = p_data.get("grade")
            data['company_name'] = company_name
            data = json.dumps(data, sort_keys=True)
            result = hashlib.sha512(data.encode())
            result_hash = result.hexdigest()
            return result_hash
        except Exception as error:
            applogger.exception("BitSight: GET RESULTS HASH: {}".format(error))
            raise BitSightException()

    def get_diligence_historical_statistics_details(self, company_name, company_guid):
        """Fetch and post the diligence historical statistics data.

        Args:
            company_name (str): company name
            company_guid (str): company guid
        """
        try:
            checkpoint_data_to_post = []
            post_data = []
            checkpoint_key = "{}".format(company_guid)
            checkpoint_data = self.get_last_data()
            last_data = self.get_endpoint_last_data(checkpoint_data, "diligence_historical-statistics", company_guid)
            endpoint_path = self.diligence_historical_statistics_path.format(company_guid)
            res_list = self.get_bitsight_data(endpoint_path)
            if(res_list.get("results")):
                data = res_list.get("results")
                for i in data:
                    if(i.get("counts")):
                        data2 = i.get("counts")
                        for j in data2:
                            result_hash = self.get_results_hash(j, i, company_name)
                            if (last_data and result_hash not in last_data) or not last_data:
                                j['grade'] = i['grade']
                                j['date'] = i['date']
                                post_data.append(j)
                                checkpoint_data_to_post.append(result_hash)
                            else:
                                checkpoint_data_to_post.append(result_hash)
                self.send_data_to_sentinel(
                    post_data,
                    diligence_historical_statistics_table,
                    "diligence historical statistics",
                    company_name)
            checkpoint_data_to_post = str(checkpoint_data_to_post)
            self.save_checkpoint(checkpoint_data, "diligence_historical-statistics", checkpoint_key, checkpoint_data_to_post)
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET DILIGENCE HISTORICAL STATISTICS: {}".format(err))
            raise BitSightException()

    def get_bitsight_data_into_sentinel(self):
        """Implement API of portfolio, fetch guid of companies."""
        try:
            applogger.info("BitSight: Started fetching companies from portfolio endpoint.")
            if self.check_env_var is True:
                if (companies_str.strip()).lower() == "all":
                    all_companies = True
                    company_list = []
                else:
                    all_companies = False
                    company_list = companies_str.split("/")
                    company_list = [(company_name.lower()).strip() for company_name in company_list]
                endpoint_path = self.portfolio_path
                response = self.get_bitsight_data(endpoint_path)
                companies = response['results']
                count_companies = 0
                for company in companies:
                    if (company['name'].lower() in company_list) or all_companies is True:
                        applogger.info("BitSight: Started fetching data for {} company.".format(company['name']))
                        endpoint_path = self.diligence_statistics_path.format(company['guid'])
                        self.get_risk_vector_data(
                            endpoint="diligence_statistics",
                            endpoint_path=endpoint_path,
                            company_name=company['name'],
                            company_guid=company['guid'],
                            table_name=diligence_statistics_table)
                        endpoint_path = self.industrial_statistics_path.format(company['guid'])
                        self.get_risk_vector_data(
                            endpoint="industries_statistics",
                            endpoint_path=endpoint_path,
                            company_name=company['name'],
                            company_guid=company['guid'],
                            table_name=industrial_statistics_table)
                        endpoint_path = self.observation_statistics_path.format(company['guid'])
                        self.get_risk_vector_data(
                            endpoint="observations_statistics",
                            endpoint_path=endpoint_path,
                            company_name=company['name'],
                            company_guid=company['guid'],
                            table_name=observation_statistics_table)
                        self.get_diligence_historical_statistics_details(company_name=company['name'], company_guid=company['guid'])
                        self.get_graph_data(company_name=company['name'], company_guid=company['guid'])
                        self.get_alerts_details(company_name=company['name'], company_guid=company['guid'])
                        count_companies += 1
                        applogger.info("BitSight: Completed fetching of data for {} company.".format(company['name']))
                if(count_companies == 0):
                    applogger.info("BitSight: No valid company name provided.")
                    applogger.info("BitSight: Please provide valid company names or pass all to fetch data of all the companies.")
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET COMPANY: {}".format(err))
            raise BitSightException()
