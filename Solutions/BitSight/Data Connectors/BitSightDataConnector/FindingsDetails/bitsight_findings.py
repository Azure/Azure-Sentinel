"""This file contains implementation of findings endpoint."""
import requests
import base64
import os
import json
from ..SharedCode.logger import applogger
import datetime
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.azure_sentinel import AzureSentinel
from ..SharedCode.state_manager import StateManager

# fetch data from os environment
api_token = os.environ.get("API_token")
findings_table_name = os.environ.get("Findings_Table_Name")
connection_string = os.environ["AzureWebJobsStorage"]

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
        self.limit = 3000
        self.offset = 3000
        self.base_url = "https://api.bitsighttech.com"
        self.findings_endpoint_path = "/ratings/v1/companies/{}/findings"

    def check_environment_var_exist(self):
        """Stop execution if os environment is not set.

        Raises:
            BitSightException: will raise if there is any unset variable which is used in this function.
        """
        env_var = [{"api_token": api_token},
                   {"findings_table_name": findings_table_name},
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
            raise BitSightException()

    def get_last_data(self):
        """Fetch last data from checkpoint file.

        Returns:
            None/json: last_data
        """
        try:
            self.state = StateManager(connection_string=connection_string, file_path="findings_details")
            self.last_data = self.state.get()
            if self.last_data is not None:
                self.last_data = json.loads(self.last_data)
        except Exception as err:
            applogger.exception("BitSight: GET LAST DATA: {}".format(err))
            raise BitSightException()

    def save_checkpoint(self, endpoint, checkpoint_key, value):
        """Post checkpoint into sentinel.

        Args:
            endpoint (str): endpoint for which user want to save checkpoint
            checkpoint_key (str): checkpoint key
            value (str): value to be set in checkpoint key
        """
        try:
            if self.last_data is None:
                self.last_data = {}
                self.last_data[endpoint] = {}
            elif endpoint not in self.last_data:
                self.last_data[endpoint] = {}
            self.last_data[endpoint][checkpoint_key] = value
            self.state.post(json.dumps(self.last_data))
            applogger.info(
                "BitSight: save_checkpoint: {} -> {} successfully posted data.".format(
                    endpoint, checkpoint_key
                    )
                )
            applogger.debug(
                "BitSight: save_checkpoint: {}: {}: Posted Data: {}".format(
                    endpoint, checkpoint_key, self.last_data[endpoint][checkpoint_key]
                    )
                )
        except Exception as err:
            applogger.exception("BitSight: SAVE CHECKPOINT: {}".format(err))
            raise BitSightException()

    def get_endpoint_last_data(self, endpoint, company_guid):
        """Fetch value of checkpoint for particular checkpoint key.

        Args:
            endpoint (str): endpoint name
            company_guid (str): this will use as checkpoint key

        Returns:
            list: last checkpoint data for particular checkpoint
        """
        try:
            checkpoint_key = "{}".format(company_guid)
            if self.last_data is not None:
                if type(self.last_data) != dict:
                    last_data = json.loads(self.last_data)
                else:
                    last_data = self.last_data
                if (last_data.get(endpoint)):
                    endpoint_last_data = last_data.get(endpoint)
                    if (endpoint_last_data.get(checkpoint_key)):
                        last_data = endpoint_last_data.get(checkpoint_key)
                        applogger.debug("BitSight: get_endpoint_last_data: {}: {}: Data: {}".format(endpoint, checkpoint_key, last_data))
                    else:
                        last_data = ""
                        applogger.debug("BitSight: get_endpoint_last_data: No checkpoint data for {} -> {}".format(endpoint, checkpoint_key))
                else:
                    last_data = ""
                    applogger.debug("BitSight: get_endpoint_last_data: No checkpoint data for {} endpoint".format(endpoint))
            else:
                last_data = ""
                applogger.debug("BitSight: get_endpoint_last_data: No checkpoint file created")
            return last_data
        except KeyError as err:
            applogger.exception("BitSight: GET ENDPOINT LAST DATA: {}".format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET ENDPOINT LAST DATA: {}".format(err))
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
            get_data_exception = "BitSight: GET DATA FOR {}: {}"
            url = self.base_url + endpoint_path
            resp = requests.get(url=url, headers=self.headers, params=query_parameter)
            if (resp.status_code == 200):
                response = resp.json()
                applogger.debug(
                    "BitSight: get_bitsight_data: Successfully got response for endpoint_path: {}".format(
                        endpoint_path
                        )
                    )
                return response
            else:
                raise BitSightException(
                    "BitSight: API( {} ):  Response code: {} \nError: {}".format(
                        url, resp.status_code, resp.text
                    )
                )
        except BitSightException as error:
            applogger.error(error)
            raise BitSightException()
        except requests.exceptions.Timeout as err:
            applogger.exception(get_data_exception.format(endpoint_path, err))
            raise BitSightException()
        except requests.exceptions.RequestException as err:
            applogger.exception(get_data_exception.format(endpoint_path, err))
            raise BitSightException()
        except Exception as err:
            applogger.exception(get_data_exception.format(endpoint_path, err))
            raise BitSightException()

    def send_data_to_sentinel(self, results, company_name, risk, checkpoint_key, data_to_post):
        """Post data into sentinel.

        Args:
            results (dict): object to post
            company_name (str): company name
            risk (str): risk type
            checkpoint_key (str): checkpoint key
            data_to_post (str): last_see date
        """
        try:
            results = results.get('results')
            for result in results:
                details = []
                details.append(result['details'])
                result['details'] = details
                result['company_name'] = company_name
            data_to_post = datetime.datetime.strptime(data_to_post, "%Y-%m-%d")
            data_to_post += datetime.timedelta(days=1)
            body = json.dumps(results)
            post_data_status_code = self.azuresentinel.post_data(body, findings_table_name)
            if (post_data_status_code >= 200 and post_data_status_code <= 299):
                applogger.info(
                    "BitSight: [status code {}] Successfully posted the findings details of risk {} for {} company.".format(
                        post_data_status_code, risk, company_name
                        )
                    )
                self.save_checkpoint("findings", checkpoint_key, str(data_to_post.date()))
            else:
                applogger.error(
                    "BitSight: [status code {}] The findings details of {} company is not posted".format(
                        post_data_status_code, company_name
                        )
                    )
                raise BitSightException()
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
            ls = [{'risk_category': 'Diligence'}, {'risk_category': "Compromised Systems"}, {'risk_category': 'User Behavior'}]
            for i in ls:
                risk = i['risk_category']
                checkpoint_key = "{}_{}".format(risk, company_guid)
                last_date = self.get_endpoint_last_data("findings", checkpoint_key)
                i['sort'] = "last_seen"
                i['limit'] = self.limit
                i['expand'] = 'attributed_companies'
                i['offset'] = 0
                i['last_seen_gte'] = last_date
                endpoint_path = self.findings_endpoint_path.format(company_guid)
                results = self.get_bitsight_data(endpoint_path, i)
                if results:
                    if len(results.get('results')) == 0:
                        applogger.info(
                            'BitSight: No new findings found for "{}" ({})'.format(
                                risk,
                                company_name
                            ))
                        continue
                else:
                    applogger.error(
                        'BitSight: No new findings data found for "{}" ({})'.format(
                            risk, company_name
                        )
                    )
                    continue
                results['id'] = risk
                results['Company_name'] = company_name
                next_link = results.get('links').get('next')
                index = len(results.get("results")) - 1
                data_to_post = results.get("results")[index].get("last_seen")
                self.send_data_to_sentinel(
                    results,
                    company_name,
                    risk,
                    checkpoint_key,
                    data_to_post)
                c_data = {}
                i['offset'] = self.offset
                pg = 0
                while next_link:
                    pg += 1
                    applogger.info("BitSight: Findings: Page {} of {} ({})".format(pg, company_name, risk))
                    c_data['next1'] = self.get_bitsight_data(endpoint_path, i)
                    next_link = (c_data['next1'].get('links').get('next'))
                    length_results = len(c_data.get('next1').get('results'))
                    applogger.info("BitSight: Got {} findings for {} on page {}".format(
                        length_results, company_name, pg))
                    c_data['next1']['id'] = risk
                    c_data['next1']['Company_name'] = company_name
                    index = length_results - 1
                    data_to_post = c_data['next1'].get('results')[index].get("last_seen")
                    self.send_data_to_sentinel(c_data['next1'], company_name, risk, checkpoint_key, data_to_post)
                    i['offset'] += 3000
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: GET FINDINGS DETAILS: {}".format(err))
            raise BitSightException()

    def get_data_of_companies(self, companies, company_list, all_companies):
        """Get data of companies."""
        try:
            count_companies = 0
            for company in companies:
                if (company['name'].lower() in company_list) or all_companies is True:
                    applogger.info("BitSight: Started fetching data for {} company.".format(company['name']))
                    self.get_findings_details(company['name'], company['guid'])
                    count_companies += 1
                    applogger.info("BitSight: Checkpoint successfully posted for {} company".format(company['name']))
                    applogger.info("BitSight: Completed fetching of data for {} company.".format(company['name']))
            if (count_companies == 0):
                applogger.info("BitSight: No valid company name provided.")
                applogger.info("BitSight: Please provide valid company names or pass all to fetch data of all the companies.")
        except BitSightException:
            raise BitSightException()
        except Exception:
            applogger.exception("BitSight: GET DATA OF COMPANIES: {}".format(err))
            raise BitSightException()

    def get_bitsight_data_into_sentinel(self):
        """Implement API of portfolio, fetch guid of companies."""
        try:
            company_exception = "BitSight: GET COMPANY: {}"
            applogger.info("BitSight: Started fetching companies from portfolio endpoint.")
            if self.check_env_var is True:
                if (companies_str.strip()).lower() == "all":
                    all_companies = True
                    company_list = []
                else:
                    all_companies = False
                    company_list = companies_str.split("/")
                    company_list = [(company_name.lower()).strip() for company_name in company_list]
                url = "{}/ratings/v2/portfolio".format(self.base_url)
                resp = requests.get(url=url, headers=self.headers)
                if (resp.status_code == 200):
                    response = resp.json()
                    companies = response['results']
                    self.get_data_of_companies(companies, company_list, all_companies)
                else:
                    raise BitSightException(
                        "BitSight: API( {} ):  Response code: {} \nError: {}".format(
                            url, resp.status_code, resp.text
                        )
                    )
        except BitSightException as error:
            applogger.exception(error)
            raise BitSightException()
        except requests.exceptions.Timeout as err:
            applogger.exception(company_exception.format(err))
            raise BitSightException()
        except requests.exceptions.RequestException as err:
            applogger.exception(company_exception.format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception(company_exception.format(err))
            raise BitSightException()
