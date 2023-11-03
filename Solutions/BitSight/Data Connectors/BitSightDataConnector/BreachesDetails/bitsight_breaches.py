"""This file contains implementation of breaches endpoint."""
import requests
import base64
import os
import json
from ..SharedCode.logger import applogger
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.azure_sentinel import AzureSentinel
from ..SharedCode.state_manager import StateManager

# fetch data from os environment
api_token = os.environ.get("API_token")
breaches_table_name = os.environ.get("Breaches_Table_Name")
connection_string = os.environ["AzureWebJobsStorage"]

# in companies variable user need to pass slash separated names of companies
# for example: "Actors Films/Goliath Investments LLC/HCL Group/Saperix, Inc."
companies_str = os.environ.get("Companies")


class BitSight:
    """Implementation of data ingestion."""

    def __init__(self) -> None:
        """Contains class variable."""
        self.headers = None
        self.last_data = None
        self.state = None
        self.check_environment_var_exist()
        self.generate_auth_token()
        self.get_last_data()
        self.check_env_var = True
        self.azuresentinel = AzureSentinel()
        self.base_url = "https://api.bitsighttech.com"
        self.breaches_endpoint_path = "/v1/companies/{}/providers/breaches"

    def check_environment_var_exist(self):
        """Stop execution if os environment is not set.

        Raises:
            BitSightException: will raise if there is any unset variable which is used in this function.
        """
        env_var = [
            {"api_token": api_token},
            {"breaches_table_name": breaches_table_name},
            {"companies_list": companies_str},
        ]
        try:
            applogger.debug(
                "BitSight: check_environment_var_exist: started checking existence of all custom environment variable"
            )
            for i in env_var:
                key, val = next(iter(i.items()))
                if val is None:
                    self.check_env_var = False
                    raise BitSightException(
                        "BitSight: ENVIRONMENT VARIABLE: {} is not set in the environment.".format(
                            key
                        )
                    )
            applogger.debug(
                "BitSight: check_environment_var_exist: All custom environment variable is exist."
            )
        except BitSightException as error:
            applogger.error(error)
            raise BitSightException()
        except Exception as error:
            applogger.exception("BitSight: ENVIRONMENT VARIABLE {}".format(error))
            raise BitSightException()

    def generate_auth_token(self):
        """Initialize Authentication parameter."""
        try:
            applogger.info(
                "BitSight: Started generating auth header to authenticate BitSight APIs."
            )
            api = [api_token, api_token]
            connector = ":"
            api = connector.join(api)
            user_and_pass = base64.b64encode(api.encode()).decode("ascii")
            headers = {
                "Accept": "application/json",
                "X-BITSIGHT-CONNECTOR-NAME-VERSION": "BitSight Security Performance Management for Microsoft Sentinel Data Connector 1.0.0",
                "X-BITSIGHT-CALLING-PLATFORM-VERSION": "Microsoft-Sentinel",
            }
            headers["Authorization"] = "Basic %s" % user_and_pass
            self.headers = headers
            applogger.info(
                "BitSight: Successfully generated the authentication header."
            )
        except Exception as error:
            applogger.exception("BitSight: GENERATE AUTH TOKEN: {}".format(error))
            raise BitSightException()

    def get_last_data(self):
        """Fetch last data from checkpoint file.

        Returns:
            None/json: last_data
        """
        try:
            self.state = StateManager(
                connection_string=connection_string, file_path="breaches"
            )
            self.last_data = self.state.get()
            if self.last_data is not None:
                self.last_data = json.loads(self.last_data)
            applogger.debug("BitSight: last checkpoint : {}".format(self.last_data))
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

    def get_data_breaches(
        self,
        breaches_results,
        company_name,
        company_guid,
        body,
        max_date,
        post_data_status_code,
    ):
        """Create data to post into microsoft sentinel."""
        try:
            is_data_exist = False
            status_code = post_data_status_code
            maximum_date = max_date
            if breaches_results:
                if maximum_date == "0000-01-01":
                    for breach in breaches_results:
                        date_created = breach.get("date_created", "")
                        if date_created and date_created > maximum_date:
                            maximum_date = date_created
                        breach["company_name"] = company_name
                        breach["company_guid"] = company_guid
                        body.append(breach)
                else:
                    for breach in breaches_results:
                        date_created = breach.get("date_created", "")
                        if date_created and date_created > maximum_date:
                            maximum_date = date_created
                            breach["company_name"] = company_name
                            breach["company_guid"] = company_guid
                            body.append(breach)
                if not body:
                    is_data_exist = True
                data = json.dumps(body)
                status_code = self.azuresentinel.post_data(
                    data, breaches_table_name
                )
            return status_code, maximum_date, is_data_exist
        except Exception:
            raise BitSightException()

    def get_breaches_details(self, company_name, company_guid):
        """Post the data of breaches details.

        Args:
            company_name (str): Name of the company for which we are fetching data.
            company_guid (str): Company guid to pass it in url.
        """
        try:
            breaches_exception = "BitSight: GET BREACHES: {}"
            exception_string = (
                "BitSight: BITSIGHT API( {} ):  Response code: {} \nError: {}"
            )
            url = self.base_url + self.breaches_endpoint_path.format(company_guid)
            breaches_response = requests.get(url=url, headers=self.headers)
            is_data_exist = False
            if breaches_response.status_code == 200:
                breaches_response = breaches_response.json()
                post_data_status_code = None
                breaches_results = breaches_response.get("results", [])
                body = []
                max_date = (
                    "0000-01-01"
                    if self.last_data is None
                    else self.last_data.get("breaches", {}).get(
                        company_guid, "0000-01-01"
                    )
                )
                if not breaches_results:
                    is_data_exist = True
                    return is_data_exist
                post_data_status_code, max_date, is_data_exist = self.get_data_breaches(
                    breaches_results,
                    company_name,
                    company_guid,
                    body,
                    max_date,
                    post_data_status_code,
                )
                if post_data_status_code == 200:
                    applogger.info(
                        "BitSight: [status code {}] Successfully posted the breaches details of {} company.".format(
                            post_data_status_code, company_name
                        )
                    )
                    self.save_checkpoint("breaches", company_guid, max_date)
                elif post_data_status_code != 200 and post_data_status_code is not None:
                    applogger.error(
                        "BitSight: [status code {}] The findings details of {} company is not posted".format(
                            post_data_status_code, company_name
                            )
                        )
                    raise BitSightException()
            else:
                raise BitSightException(
                    exception_string.format(
                        url, breaches_response.status_code, breaches_response.text
                    )
                )
            return is_data_exist
        except BitSightException as error:
            applogger.error(error)
            raise BitSightException()
        except requests.exceptions.Timeout as err:
            # Maybe set up for a retry, or continue in a retry loop
            applogger.exception(breaches_exception.format(err))
            raise BitSightException()
        except requests.exceptions.RequestException as err:
            applogger.exception(breaches_exception.format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception(breaches_exception.format(err))
            raise BitSightException()

    def get_data_of_companies(self, companies, company_list, all_companies):
        """Get data of companies."""
        try:
            count_companies = 0
            for company in companies:
                if (
                    (company["name"].lower()).strip() in company_list
                ) or all_companies is True:
                    applogger.info(
                        "BitSight: Started fetching data for {} company.".format(
                            company["name"]
                        )
                    )
                    is_data_exist = self.get_breaches_details(company["name"], company["guid"])
                    if is_data_exist:
                        applogger.info("BitSight: No new data found.")
                    count_companies += 1
                    applogger.info(
                        "BitSight: Completed fetching of data for {} company.".format(
                            company["name"]
                        )
                    )
            if count_companies == 0:
                applogger.info("BitSight: No valid company name provided.")
                applogger.info(
                    "BitSight: Please provide valid company names or pass all to fetch data of all the companies."
                )
        except Exception:
            raise BitSightException()

    def get_bitsight_data_into_sentinel(self):
        """Implement API of portfolio, fetch guid of companies."""
        try:
            breaches_exception = "BitSight: GET BREACHES DETAILS: {}"
            applogger.info(
                "BitSight: Started fetching companies from portfolio endpoint."
            )
            if self.check_env_var:
                if (companies_str.strip()).lower() == "all":
                    all_companies = True
                    company_list = []
                else:
                    all_companies = False
                    company_list = companies_str.split("/")
                    company_list = [
                        company_name.lower() for company_name in company_list
                    ]
                url = "{}/ratings/v2/portfolio".format(self.base_url)
                resp = requests.get(url=url, headers=self.headers)
                if resp.status_code == 200:
                    response = resp.json()
                    companies = response["results"]
                    self.get_data_of_companies(companies, company_list, all_companies)
                else:
                    raise BitSightException(
                        "BITSIGHT API( {} ):  Response code: {} \nError: {}".format(
                            url, resp.status_code, resp.text
                        )
                    )
        except BitSightException as error:
            applogger.error(error)
            raise BitSightException()
        except requests.exceptions.Timeout as err:
            # Maybe set up for a retry, or continue in a retry loop
            applogger.exception(breaches_exception.format(err))
            raise BitSightException()
        except requests.exceptions.RequestException as err:
            applogger.exception(breaches_exception.format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception(breaches_exception.format(err))
            raise BitSightException()
