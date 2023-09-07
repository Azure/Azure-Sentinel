"""This file contains methods for creating microsoft indicator and custom log table."""
import time
import json
import inspect
import requests
from ..shared_code.logger import applogger
from ..shared_code.dataminrpulse_exception import DataminrPulseException
from ..shared_code import consts


class MicrosoftSentinel:
    """This class contains methods to create indicator into Microsoft Sentinel."""

    def __init__(self):
        """Initialize instance variable for class."""
        self.bearer_token = self.auth_sentinel()

    def auth_sentinel(self):
        """
        Authenticate with microsoft sentinel.

        Raises:
            DataminrPulseException: Custom cofense Exception

        Returns:
            String: Bearer token
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                "{}(method={}) : {}: generating microsoft sentinel access token.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.RETRY_FAILED_INDICATORS,
                )
            )
            azure_auth_url = consts.AZURE_AUTHENTICATION_URL.format(
                consts.AZURE_TENANT_ID
            )
            body = {
                "client_id": consts.AZURE_CLIENT_ID,
                "client_secret": consts.AZURE_CLIENT_SECRET,
                "grant_type": "client_credentials",
                "resource": "https://management.azure.com",
            }
            response = requests.post(url=azure_auth_url, data=body, timeout=10)
            if response.status_code >= 200 and response.status_code <= 299:
                json_response = response.json()
                if "access_token" not in json_response:
                    applogger.error(
                        "{}(method={}) : {}: Access token not found in sentinel api call.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.RETRY_FAILED_INDICATORS,
                        )
                    )
                    raise DataminrPulseException()
                else:
                    bearer_token = json_response.get("access_token")
                    applogger.info(
                        "{}(method={}) : {}: Microsoft sentinel access token generated successfully.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.RETRY_FAILED_INDICATORS,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) :{}: url:{}, Status Code :{}: Microsoft Sentinel access token generated.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.RETRY_FAILED_INDICATORS,
                            azure_auth_url,
                            response.status_code,
                        )
                    )
                    return bearer_token
            else:
                applogger.error(
                    "{}(method={}) :{}: url:{}, Status Code :{}: Error while creating microsoft sentinel access_token."
                    " Error Reason: {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.RETRY_FAILED_INDICATORS,
                        azure_auth_url,
                        response.status_code,
                        response.reason,
                    )
                )
                raise DataminrPulseException()
        except DataminrPulseException as error:
            applogger.error(
                "{}(method={}) : Error generated while getting sentinel access token :{}".format(
                    consts.LOGS_STARTS_WITH, __method_name, error
                )
            )
            raise DataminrPulseException()

    async def create_indicator(self, indicators_data, session):
        """To create indicator into Microsoft Sentinel.

        Args:
            indicators_data (dict): Indicator data
            session (session object): aiohttp session object

        Raises:
            DataminrPulseException: DataminrPulseException
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            display_name = indicators_data.get('properties').get('displayName')
            index_value = display_name.split(':')[-1]
            retry_count_429 = 0
            retry_count_401 = 0
            while retry_count_429 <= 3 and retry_count_401 <= 1:
                create_indicator_url = consts.CREATE_SENTINEL_INDICATORS_URL.format(
                    subscriptionId=consts.AZURE_SUBSCRIPTION_ID,
                    resourceGroupName=consts.AZURE_RESOURCE_GROUP,
                    workspaceName=consts.AZURE_WORKSPACE_NAME,
                )
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(self.bearer_token),
                }
                response = await session.post(
                    url=create_indicator_url,
                    headers=headers,
                    data=json.dumps(indicators_data),
                )
                if response.status >= 200 and response.status <= 299:
                    applogger.info(
                        "{}(method={}) : {} : Created the indicator with status_code: {}, Index-{}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.RETRY_FAILED_INDICATORS,
                            response.status,
                            index_value
                        )
                    )
                    return None
                elif response.status == 400:
                    json_response = await response.json()
                    applogger.warning(
                        "{}(method={}) : {} : url: {}, Status Code : {}: Error while\
                             creating Indicator, Error:{}, Index-{}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.RETRY_FAILED_INDICATORS,
                            create_indicator_url,
                            response.status,
                            json_response,
                            index_value
                        )
                    )
                    return indicators_data
                elif response.status == 429:
                    applogger.error(
                        "{}(method={}) : {} : trying again error 429.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.RETRY_FAILED_INDICATORS,
                        )
                    )
                    retry_count_429 += 1
                    time.sleep(consts.SENTINEL_429_SLEEP)
                elif response.status == 401:
                    applogger.error(
                        "{}(method={}) : {} : Unauthorized, Invalid Credentials, trying again error-401.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.RETRY_FAILED_INDICATORS,
                        )
                    )
                    self.bearer_token = self.auth_sentinel()
                    headers["Authorization"] = "Bearer {}".format(self.bearer_token)
                    retry_count_401 += 1
                else:
                    json_response = await response.json()
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}: Error while\
                             creating Indicator Error:{}, Index-{}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.RETRY_FAILED_INDICATORS,
                            create_indicator_url,
                            response.status,
                            json_response,
                            index_value
                        )
                    )
                    raise DataminrPulseException()
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded for microsoft sentinel.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.RETRY_FAILED_INDICATORS,
                )
            )
            raise DataminrPulseException()
        except DataminrPulseException:
            applogger.error(
                "{}(method={}) : {} : Error generated while Creating Indicator. Index-{}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.RETRY_FAILED_INDICATORS,
                    index_value
                )
            )
            return indicators_data

        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error generated while Creating Indicator, Error-{}, Index-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.RETRY_FAILED_INDICATORS,
                    error,
                    index_value
                )
            )
            return indicators_data
