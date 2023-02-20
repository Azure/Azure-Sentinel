"""This file contains implementation of companies endpoint."""
import ast
import requests
import base64
import hashlib
import os
import json
from ..SharedCode.logger import applogger
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.azure_sentinel import AzureSentinel
from ..SharedCode.state_manager import StateManager

# fetch data from os environment
api_token = os.environ.get("API_token")
connection_string = os.environ["AzureWebJobsStorage"]
company_data_table_name = os.environ.get("Company_Table_Name")
company_rating_details_table_name = os.environ.get("Company_Rating_Details_Table_Name")

# in companies variable user need to pass slash separated names of companies
# for example: "Actors Films/Goliath Investments LLC/HCL Group/Saperix, Inc."
companies_str = os.environ.get("Companies")


class BitSight:
    """Implementation of data ingestion."""

    def __init__(self) -> None:
        """Contains class variable."""
        self.headers = None
        self.check_env_var = True
        self.last_data = None
        self.state = None
        self.check_environment_var_exist()
        self.generate_auth_token()
        self.get_last_data()
        self.azuresentinel = AzureSentinel()
        self.base_url = "https://api.bitsighttech.com"
        self.company_endpoint_path = "/ratings/v1/companies/{}"
        self.portfolio_path = "/ratings/v2/portfolio"

    def check_environment_var_exist(self):
        """Stop execution if os environment is not set.

        Raises:
            BitSightException: will raise if there is any unset variable which is used in this function.
        """
        env_var = [{"api_token": api_token},
                   {"company_data_table_name": company_data_table_name},
                   {"company_rating_details_table_name": company_rating_details_table_name},
                   {"companies_list": companies_str}]

        try:
            applogger.debug("BitSight: check_environment_var_exist: started checking existence of all custom environment variable")
            for i in env_var:
                key, val = next(iter(i.items()))
                if (val is None):
                    self.check_env_var = False
                    raise BitSightException("BitSight: ENVIRONMENT VARIABLE: {} is not set in the environment.".format(key))
            applogger.debug("BitSight: check_environment_var_exist: All custom environment variable is exist.")
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
                'X-BITSIGHT-CONNECTOR-NAME-VERSION': 'BitSight Security Performance Management for Microsoft Sentinel Data Connector 1.0.0',
                'X-BITSIGHT-CALLING-PLATFORM-VERSION': 'Microsoft-Sentinel'
                }
            headers['Authorization'] = 'Basic %s' % user_and_pass
            self.headers = headers
            applogger.info("BitSight: Successfully generated the authentication header.")
        except Exception as error:
            applogger.exception("BitSight: GENERATE AUTH TOKEN: {}".format(error))
            raise Exception()

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

    def get_last_data(self):
        """Fetch last data from checkpoint file.

        Returns:
            None/json: last_data
        """
        try:
            self.state = StateManager(connection_string=connection_string, file_path="companies_details")
            last_data = self.state.get()
            if last_data is not None:
                last_data = json.loads(last_data)
            return last_data
        except Exception as err:
            applogger.exception("BitSight: GET LAST DATA: {}".format(err))
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
                        applogger.debug("BitSight: get_endpoint_last_data: {}: {}: Data: {}".format(endpoint, checkpoint_key, last_data))

                    else:
                        last_data = []
                        applogger.debug(
                            "BitSight: get_endpoint_last_data: No checkpoint data for {} -> {}".format(endpoint, checkpoint_key))
                else:
                    last_data = []
                    applogger.debug("BitSight: get_endpoint_last_data: No checkpoint data for {} endpoint".format(endpoint))
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

    def send_data_to_sentinel(self, data, data_table, company_name, endpoint):
        """To post the data into sentinel.

        Args:
            data (dict): data to post in sentinel
            data_table (str): log type
            company_name (str): company name
        """
        try:
            body = json.dumps(data, sort_keys=True)
            post_data_status_code = self.azuresentinel.post_data(body, data_table)
            if(post_data_status_code >= 200 and post_data_status_code <= 299):
                applogger.info(
                    "BitSight: [status code {}] Successfully posted the {} of {} company.".format(
                        post_data_status_code, endpoint, company_name
                        )
                    )
            else:
                applogger.error(
                    "BitSight: [status code {}] The {} of {} company is not posted".format(
                        post_data_status_code, endpoint, company_name
                        )
                    )
                raise BitSightException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: SEND DATA TO SENTINEL: {}".format(err))
            raise BitSightException()

    def get_company_details(self, company_name, company_guid):
        """Post the data of company details/company ratings.

        Args:
            company_name (str): name of company for which we need to fetch details
            company_guid (str): company guid to pass it in url
        """
        try:
            data_to_post = None
            post_data_ratings = []
            checkpoint_key = "{}".format(company_guid)
            checkpoint_data = self.get_last_data()
            last_data_company_details = self.get_endpoint_last_data(checkpoint_data, "companies_details", company_guid)
            last_data_company_ratings = self.get_endpoint_last_data(checkpoint_data, "companies_ratings_details", company_guid)
            url = self.company_endpoint_path.format(company_guid)
            response = self.get_bitsight_data(url)
            if(response.get("rating_details")):
                rating_details = response.get("rating_details")
                rating = json.dumps(rating_details, sort_keys=True)
                result = hashlib.sha512(rating.encode())
                result_hash = result.hexdigest()
                if(result_hash != last_data_company_ratings):
                    ratingdetailskeys = rating_details.keys()
                    # filter out rating field from company details.
                    for rating_detail in ratingdetailskeys:
                        rating = rating_details.get(rating_detail)
                        rating['Company_name'] = company_name
                        post_data_ratings.append(rating)
                    self.send_data_to_sentinel(post_data_ratings, company_rating_details_table_name, company_name, "company rating details")
                else:
                    applogger.info("BitSight: The company rating details of {} company is already exist.".format(company_name))
                data_to_post = result_hash
                self.save_checkpoint(checkpoint_data, "companies_ratings_details", checkpoint_key, data_to_post)
                # delete rating field after post.
                del response['rating_details']
            rating = json.dumps(response, sort_keys=True)
            result = hashlib.sha512(rating.encode())
            result_hash = result.hexdigest()
            if(result_hash != last_data_company_details):
                self.send_data_to_sentinel(response, company_data_table_name, company_name, "company details")
            else:
                applogger.info("BitSight: The company details of {} company is already exist.".format(company_name))
            data_to_post = result_hash
            checkpoint_data = self.get_last_data()
            self.save_checkpoint(checkpoint_data, "companies_details", checkpoint_key, data_to_post)
        except BitSightException:
            raise BitSightException()
        except KeyError as err:
            applogger.exception("BitSight: Key Error while getting Company data: {}".format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET COMPANY DETAILS: {}".format(err))
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
                url = self.portfolio_path
                response = self.get_bitsight_data(url)
                companies = response['results']
                count_companies = 0
                for company in companies:
                    if (company['name'].lower() in company_list) or all_companies is True:
                        applogger.info("BitSight: Started fetching data for {} company.".format(company['name']))
                        self.get_company_details(company['name'], company['guid'])
                        count_companies += 1
                        applogger.info("BitSight: Completed fetching of data for {} company.".format(company['name']))
                if(count_companies == 0):
                    applogger.info("BitSight: No valid company name provided.")
                    applogger.info("BitSight: Please provide valid company names or pass all to fetch data of all the companies.")
        except BitSightException:
            raise BitSightException()
        except KeyError as err:
            applogger.exception("BitSight: KeyError while getting portfolios: {}".format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET COMPANY: {}".format(err))
            raise BitSightException()
