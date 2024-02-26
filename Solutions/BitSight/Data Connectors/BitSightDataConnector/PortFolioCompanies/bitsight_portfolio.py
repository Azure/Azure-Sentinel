import inspect
import json
import time

from ..SharedCode.bitsight_client import BitSight
from ..SharedCode.bitsight_exception import BitSightException
from ..SharedCode.consts import (
    API_TOKEN,
    COMPANIES_TABLE_NAME,
    ENDPOINTS,
    LOGS_STARTS_WITH,
    PORTFOLIO_PAGE_SIZE,
)
from ..SharedCode.get_logs_data import get_logs_data
from ..SharedCode.logger import applogger


class BitSightPortFolio(BitSight):
    """Implementation of data ingestion."""

    def __init__(self, start_time) -> None:
        """Contains class variable."""
        super().__init__()
        self._start_time = start_time
        self.portfolio_url = self.base_url + ENDPOINTS["portfolio_path"]
        self.headers = None
        self.check_env_var = self.check_environment_var_exist(
            [{"api_token": API_TOKEN}, {"company_table_name": COMPANIES_TABLE_NAME}]
        )
        self.logs_starts_with = LOGS_STARTS_WITH
        self.error_logs = "{}(method={}) {}"
        self.generate_auth_token()

    def preapre_data(self, post_data, companies):
        __method_name = inspect.currentframe().f_code.co_name
        data_to_post = []
        try:
            for company in companies:
                name = company["name"]
                if name in post_data:
                    data_to_post.append(company)
            return data_to_post
        except BitSightException as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise BitSightException(err)
        except Exception as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise BitSightException(err)

    def get_companies_to_post(self, companies_table_data, companies_api_data):
        return list(set(companies_api_data) - set(companies_table_data))

    def get_companies_data_from_portfolio(self):
        __method_name = inspect.currentframe().f_code.co_name
        try:
            companies_table_data = set()
            logs_data, flag = get_logs_data()
            if flag:
                companies_table_data = set([data["name_s"] for data in logs_data])
                applogger.debug(
                    "{}(method={})Total {} Companies are retrieved from table.".format(
                        self.logs_starts_with, __method_name, len(companies_table_data)
                    )
                )
            page_size = PORTFOLIO_PAGE_SIZE
            offset = 0
            params = {"limit": page_size, "offset": offset, "fields": "name,guid"}
            while True:
                if int(time.time()) >= self._start_time + 540:
                    applogger.info(
                        "{}(method={}) : 9:00 mins executed hence breaking.".format(
                            self.logs_starts_with, __method_name
                        )
                    )
                    break
                response = self.get_bitsight_data(self.portfolio_url, params)
                companies = response.get("results", [])
                companies_api = [data["name"] for data in companies]
                companies_post_data = self.get_companies_to_post(
                    companies_table_data, companies_api
                )
                if companies_post_data:
                    data_to_post = self.preapre_data(companies_post_data, companies)
                    self.send_portfolio_data_to_sentinel(data_to_post)
                else:
                    applogger.info(
                        "{}(method={}) No new companies found to post.".format(
                            self.logs_starts_with, __method_name
                        )
                    )
                if not response.get("links", {}).get("next", ""):
                    applogger.debug(
                        "{} Next page is not available.".format(self.logs_starts_with)
                    )
                    break
                else:
                    offset += page_size
                    params.update({"offset": offset})
        except BitSightException as err:
            raise BitSightException(err)
        except Exception as err:
            applogger.exception(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise BitSightException()

    def send_portfolio_data_to_sentinel(self, companies_post_data):
        __method_name = inspect.currentframe().f_code.co_name
        try:
            count_companies = 0
            applogger.debug(
                "{}(method={}) Found {} new companies to post.".format(
                    self.logs_starts_with, __method_name, len(companies_post_data)
                )
            )
            body = json.dumps(companies_post_data)
            post_data_status_code = self.azuresentinel.post_data(
                body, COMPANIES_TABLE_NAME
            )
            if post_data_status_code >= 200 and post_data_status_code <= 299:
                count_companies += len(companies_post_data)
                applogger.info(
                    "{}(method={}) Total {} companies data posted successfully.".format(
                        self.logs_starts_with, __method_name, count_companies
                    )
                )
            else:
                applogger.error(
                    "{}(method={}) [status code {}] Error while posting data into Sentnel.".format(
                        self.logs_starts_with, __method_name, post_data_status_code
                    )
                )
                raise BitSightException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise BitSightException()
