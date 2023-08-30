"""This file contains implementation of cofense indicator fetching and creating microsoft indicator."""
import time
import inspect
from ..SharedCode.consts import (
    LOGS_STARTS_WITH,
    COFENSE_TO_SENTINEL,
    COFENSE_429_SLEEP,
)
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_exception import CofenseException
from ..SharedCode.utils import (
    make_rest_call,
    auth_cofense,
    create_proxy,
)


class CofenseTriage:
    """This class contains methods to pull the data from cofense apis and transform it to create TI indicator."""

    def __init__(self):
        """Initialize instance variable for class."""
        self.access_token = auth_cofense(COFENSE_TO_SENTINEL)
        self.proxy = create_proxy()
        self.headers = {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": "Bearer " + self.access_token,
        }

    def get_indicators_from_cofense(self, url, params):
        """Pull the cofense indicators from REST APIs of Cofense."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            retry_count_429 = 0
            retry_count_401 = 0
            while retry_count_429 <= 1 and retry_count_401 <= 1:
                indicators_data = make_rest_call(
                    url=url,
                    method="GET",
                    azure_function_name=COFENSE_TO_SENTINEL,
                    params=params,
                    headers=self.headers,
                    proxies=self.proxy,
                )
                indicators_data_status_code = indicators_data.status_code
                if (
                    indicators_data_status_code >= 200
                    and indicators_data_status_code <= 299
                ):
                    indicator_json = indicators_data.json()
                    return indicator_json
                elif indicators_data_status_code == 401:
                    applogger.error(
                        "{}(method={}) : {} : trying again error 401.".format(
                            LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                        )
                    )
                    self.access_token = auth_cofense(COFENSE_TO_SENTINEL)
                    self.headers["Authorization"] = "Bearer " + self.access_token
                    retry_count_401 += 1
                elif indicators_data_status_code == 429:
                    applogger.error(
                        "{}(method={}) : {} : trying again error 429.".format(
                            LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                        )
                    )
                    retry_count_429 += 1
                    time.sleep(COFENSE_429_SLEEP)
                else:
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {} : error"
                        " while pulling indicator data.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            COFENSE_TO_SENTINEL,
                            url,
                            indicators_data_status_code,
                        )
                    )
                    raise CofenseException()
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded for fetching data.".format(
                    LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                )
            )
            raise CofenseException()
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : error while pulling data of indicator : {}".format(
                    LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL, error
                )
            )
            raise CofenseException()
