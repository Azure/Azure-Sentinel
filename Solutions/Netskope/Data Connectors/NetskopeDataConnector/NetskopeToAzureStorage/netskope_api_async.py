"""Make API call and handle exceptions."""
import asyncio
import inspect
from random import randrange
import aiohttp
from ..SharedCode import consts
from ..SharedCode.netskope_exception import NetskopeException
from ..SharedCode.logger import applogger
from aiohttp.client_exceptions import ServerDisconnectedError


class NetskopeAPIAsync:
    """Class to handle Netskope asynchronous api calls and exception handling."""

    def __init__(self, type_of_data, sub_type) -> None:
        """Initialize NetskopeAPIAsync class.

        Args:
            type_of_data (str): The type of Netskope Data to fetch.(alerts/events)
            sub_type (str): The subtype of the data to fetch.
        """
        self.hostname = consts.NETSKOPE_HOSTNAME
        self.type_of_data = type_of_data
        self.sub_type = sub_type
        self.nskp_data_type_for_logging = self.type_of_data + "_" + self.sub_type

    def url_builder(self, iterator_name, operation) -> str:
        """Build the URL and return the built url.

        Returns:
            str: Generated url for http request
        """
        url = consts.URL[self.type_of_data].format(
            hostname=self.hostname,
            sub_type=self.sub_type,
            iterator_name=iterator_name,
            operation=operation,
        )
        return url

    async def aio_http_handler(self, url, session: aiohttp.ClientSession, server_disconnect_retry=0):
        """Make http request and handle the api call errors.

        Args:
            url (str): The url to perform the http request.
            session (aiohttp.ClientSession): The session object used to perform api calls.

        Raises:
            NetskopeException: Netskope Custom Exception

        Returns:
            dict: Response from the api
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            retry_count_429 = 0
            retry_count_409 = 0
            retry_count_500 = 0
            # Implemented retry mechanism for the status codes 409, 429 and 500.
            # Retry count for 429 is higher due to higher frequency seen in tests.
            while retry_count_429 <= 3 and retry_count_409 <= 1 and retry_count_500 <= 1:
                applogger.debug(
                    "{}(method={}) : {} ({}): Initiating the get request.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_TO_AZURE_STORAGE,
                        self.nskp_data_type_for_logging,
                    )
                )
                response = await session.get(url=url)
                applogger.info(
                    "{}(method={}) : {} ({}): The API call response status code is {}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_TO_AZURE_STORAGE,
                        self.nskp_data_type_for_logging,
                        response.status,
                    )
                )
                if response.status == 200:
                    applogger.info(
                        "{}(method={}) : {} ({}): Successfully fetched netskope data.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.NETSKOPE_TO_AZURE_STORAGE,
                            self.nskp_data_type_for_logging,
                        )
                    )
                    json_response = await response.json()
                    return json_response
                elif response.status == 403:
                    applogger.error(
                        "{}(method={}) : {} ({}): Status code 403 token issue."
                        "Check the API V2 token is associated to the valid endpoint and its not expired.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.NETSKOPE_TO_AZURE_STORAGE,
                            self.nskp_data_type_for_logging,
                        )
                    )
                    raise NetskopeException()
                elif response.status == 409:
                    applogger.error(
                        "{}(method={}) : {} ({}): Status code 409."
                        "Concurrency conflict and the request cannot be processed currently. Sleeping...".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.NETSKOPE_TO_AZURE_STORAGE,
                            self.nskp_data_type_for_logging,
                        )
                    )
                    retry_count_409 += 1
                    await asyncio.sleep(randrange(2, 10))
                elif response.status == 429:
                    retry_after = response.headers.get("RateLimit-Reset")
                    applogger.error(
                        "{}(method={}) : {} ({}): Status code 429."
                        "Too many request for the same tenant for the same endpoint. Retrying after {} seconds.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.NETSKOPE_TO_AZURE_STORAGE,
                            self.nskp_data_type_for_logging,
                            retry_after,
                        )
                    )
                    await asyncio.sleep(float(retry_after))
                    retry_count_429 += 1
                elif response.status >= 500 and response.status < 600:
                    applogger.error(
                        "{}(method={}) : {} ({}): Status code {}. Netskope is having a temporary server issue."
                        "Retrying after 5 seconds.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.NETSKOPE_TO_AZURE_STORAGE,
                            self.nskp_data_type_for_logging,
                            response.status,
                        )
                    )
                    await asyncio.sleep(randrange(5, 10))
                    retry_count_500 += 1

            applogger.error(
                "{}(method={}) : {} ({}): Max retries exceeded.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            raise NetskopeException()
        # Catching Server Disconnected Error which occurs when the amount of concurrent requests increases.
        # Hence Retrying with random sleep timer.
        except ServerDisconnectedError as server_error:
            if server_disconnect_retry < 3:
                retry_time = randrange(2, 10)
                applogger.error(
                    "{}(method={}) : {} ({}): Server Disconnect error. Error-{}. Retrying after - {} seconds.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_TO_AZURE_STORAGE,
                        self.nskp_data_type_for_logging,
                        server_error,
                        retry_time,
                    )
                )
                server_disconnect_retry += 1
                await asyncio.sleep(retry_time)
                json_response = await self.aio_http_handler(url, session, server_disconnect_retry)
                return json_response
            applogger.error(
                "{}(method={}) : {} ({}): Max retries exceeded for server disconnect error.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            raise NetskopeException()

        except NetskopeException:
            applogger.error(
                "{}(method={}) : {} ({}): Error while fetching data.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                )
            )
            raise NetskopeException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} ({}): Error while fetching data, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_TO_AZURE_STORAGE,
                    self.nskp_data_type_for_logging,
                    error,
                )
            )
            raise NetskopeException()
