"""This file contains implementation of findings summary endpoint."""
import requests
import base64
import os
import json
import hashlib
from ..SharedCode.logger import applogger
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.azure_sentinel import AzureSentinel
from ..SharedCode.state_manager import StateManager

# fetch data from os environment
api_token = os.environ.get("API_token")
findings_summary_table_name = os.environ.get("Findings_Summary_Table_Name")
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
        self.findings_summary_endpoint_path = (
            "/ratings/v1/companies/{}/findings/summary"
        )
        self.vulnerabilities_url = (
            "https://service.bitsighttech.com/customer-api/v1/defaults/vulnerabilities"
        )

    def check_environment_var_exist(self):
        """Stop execution if os environment is not set.

        Raises:
            BitSightException: will raise if there is any unset variable which is used in this function.
        """
        env_var = [
            {"api_token": api_token},
            {"findings_summary_table_name": findings_summary_table_name},
            {"companies_list": companies_str},
        ]
        try:
            applogger.debug("BitSight: check_environment_var_exist: started checking existence of all custom environment variable")
            for i in env_var:
                key, val = next(iter(i.items()))
                if val is None:
                    self.check_env_var = False
                    raise BitSightException(
                        "BitSight: ENVIRONMENT VARIABLE: {} is not set in the environment.".format(
                            key
                        )
                    )
            applogger.debug("BitSight: check_environment_var_exist: All custom environment variable is exist.")
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
                connection_string=connection_string, file_path="findings_summary"
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

    def findings_summary_data(
        self, result, end_date, start_date, company_name, j, data_to_post, company_guid, flag, post_data_status_code, data_is_exist
    ):
        """Create data to post into microsoft sentinel."""
        try:
            break_flag = False
            for k in result:
                if j.get("name") == k.get("display_name"):
                    j["description"] = k.get("description")
                    j["severity"] = k.get("severity")
                    j["end_date"] = end_date
                    j["start_date"] = start_date
                    j["Company"] = company_name
                    body = json.dumps(j, sort_keys=True)
                    data_hash = hashlib.sha512(body.encode())
                    result_hash = data_hash.hexdigest()
                    data_to_post.append(result_hash)
                    if (
                        self.last_data
                        and self.last_data.get("findings_summary", {}).get(company_guid)
                        and result_hash in self.last_data["findings_summary"][company_guid]
                    ):
                        break_flag = True
                        data_is_exist = True
                        break
                    post_data_status_code = self.azuresentinel.post_data(
                        body, findings_summary_table_name
                    )
                    if post_data_status_code != 200:
                        flag = True
                        break
            return break_flag, flag, post_data_status_code, data_is_exist
        except BitSightException:
            raise BitSightException()
        except Exception as error:
            applogger.exception("BitSight: FINDINGS SUMMARY DATA {}".format(error))
            raise BitSightException()

    def get_findings_summary_details(self, company_name, company_guid):
        """Post the data of findings details.

        Args:
            company_name (str): Name of the company for which we are fetching data.
            company_guid (str): Company guid to pass it in url.
        """
        try:
            findings_summary_exception = "BitSight: GET FINDINGS SUMMARY: {}"
            url = self.base_url + self.findings_summary_endpoint_path.format(
                company_guid
            )
            res_list = requests.get(url=url, headers=self.headers)
            status_code = None
            exception_string = "BITSIGHT API( {} ):  Response code: {}"
            if res_list.json() and res_list.status_code == 200:
                res_list = res_list.json()
                stats = res_list[2].get("stats")
                req_params = {}
                req_params["fields"] = "name,display_name,description,severity"
                result = requests.get(
                    url=self.vulnerabilities_url,
                    headers=self.headers,
                    params=req_params,
                )
                status_code = result.status_code
            if status_code == 200 and stats:
                result = result.json()
                post_data_status_code = None
                data_to_post = []
                flag = False
                end_date = res_list[2].get("end_date")
                start_date = res_list[2].get("start_date")
                data_is_exist = False
                for j in stats:
                    break_flag, flag, post_data_status_code, data_is_exist = self.findings_summary_data(
                        result,
                        end_date,
                        start_date,
                        company_name,
                        j,
                        data_to_post,
                        company_guid,
                        flag,
                        post_data_status_code,
                        data_is_exist,
                    )
                    if break_flag:
                        continue
                    if flag:
                        break
                if post_data_status_code == 200:
                    applogger.info(
                        "BitSight: [status code {}] Successfully posted the findings summary details of {} company.".format(
                            post_data_status_code, company_name
                        )
                    )
                    self.save_checkpoint("findings_summary", company_guid, data_to_post)
                elif data_is_exist:
                    applogger.info("BitSight: No new data found.")
                else:
                    applogger.error(
                        "BitSight: [status code {}] Findings summary details of {} company is not posted".format(
                            post_data_status_code, company_name
                        )
                    )
                    raise BitSightException()
            elif status_code != 200 and status_code is not None:
                raise BitSightException(
                    exception_string.format(
                        self.vulnerabilities_url, status_code
                    )
                )
            elif res_list.status_code != 200:
                raise BitSightException(
                    exception_string.format(
                        url, res_list.status_code
                    )
                )
        except BitSightException as error:
            applogger.error(error)
            raise BitSightException()
        except requests.exceptions.Timeout as err:
            # Maybe set up for a retry, or continue in a retry loop
            applogger.exception(findings_summary_exception.format(err))
            raise BitSightException()
        except requests.exceptions.RequestException as err:
            applogger.exception(findings_summary_exception.format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception(findings_summary_exception.format(err))
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
                    self.get_findings_summary_details(
                        company["name"], company["guid"]
                    )
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
        except BitSightException:
            raise BitSightException()
        except Exception as error:
            applogger.exception("BitSight: GET DATA OF COMPANIES {}".format(error))
            raise BitSightException()

    def get_bitsight_data_into_sentinel(self):
        """Implement API of portfolio, fetch guid of companies."""
        try:
            findings_summary_exception = "BitSight: GET FINDINGS SUMMARY: {}"
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
            applogger.exception(findings_summary_exception.format(err))
            raise BitSightException()
        except requests.exceptions.RequestException as err:
            applogger.exception(findings_summary_exception.format(err))
            raise BitSightException()
        except Exception as err:
            applogger.exception(findings_summary_exception.format(err))
            raise BitSightException()
