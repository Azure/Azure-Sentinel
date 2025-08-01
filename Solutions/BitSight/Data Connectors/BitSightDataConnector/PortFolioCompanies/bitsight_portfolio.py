import inspect
import time

from ..SharedCode.bitsight_client import BitSight
from ..SharedCode.bitsight_exception import BitSightException, BitSightTimeOutException
from ..SharedCode.consts import (
    API_TOKEN,
    COMPANIES_TABLE_NAME,
    ENDPOINTS,
    LOGS_STARTS_WITH,
    PORTFOLIO_PAGE_SIZE
)
from ..SharedCode.get_logs_data import get_logs_data
from ..SharedCode.logger import applogger


class BitSightPortFolio(BitSight):
    """Implementation of data ingestion."""

    def __init__(self, start_time) -> None:
        """Contains class variable."""
        super().__init__(start_time)
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
                self.check_timeout()
                name = company["name"]
                if name in post_data:
                    data_to_post.append(company)
            return data_to_post
        except BitSightTimeOutException:
            raise BitSightTimeOutException()
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
                companies_table_data = set([data["name"] for data in logs_data])
                applogger.debug(
                    "{}(method={})Total {} Companies are retrieved from table.".format(
                        self.logs_starts_with, __method_name, len(companies_table_data)
                    )
                )
            page_size = PORTFOLIO_PAGE_SIZE
            offset = 0
            params = {"limit": page_size, "offset": offset, "fields": "name,guid"}
            while True:
                self.check_timeout()
                response = self.get_bitsight_data(self.portfolio_url, params)
                companies = response.get("results", [])
                companies_api = [data["name"] for data in companies]
                companies_post_data = self.get_companies_to_post(
                    companies_table_data, companies_api
                )
                if companies_post_data:
                    data_to_post = self.preapre_data(companies_post_data, companies)
                    self.send_data_to_sentinel(data_to_post, COMPANIES_TABLE_NAME)
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
        except BitSightTimeOutException:
            applogger.error(
                "{} {} 9:00 mins executed hence stopping the function app.".format(
                    self.logs_starts_with, __method_name
                )
            )
            return
        except BitSightException as err:
            raise BitSightException(err)
        except Exception as err:
            applogger.exception(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise BitSightException()
