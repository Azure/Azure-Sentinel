"""This module contains Microsoft Defender class for authentication."""
import inspect
from ..SharedCode.logger import applogger
from ..SharedCode import consts
from ..SharedCode.utils import Utils
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException
import json
import time


class MicrosoftDefender:
    """This class is for MS Defender authentication and posting indicator to defender."""

    def __init__(self) -> None:
        """Initialize instance variable for class."""
        self.bearer_token = self.auth_defender(
            azure_function_name=consts.SENTINEL_TO_DEFENDER
        )

    def auth_defender(self, azure_function_name):
        """To authenticate with microsoft defender."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                "{}(method={}) : {}: generating MS Defender access token.".format(
                    consts.LOGS_STARTS_WITH, __method_name, azure_function_name
                )
            )
            azure_auth_url = consts.AZURE_AUTHENTICATION_URL.format(
                consts.AZURE_TENANT_ID
            )
            # Creating body for Microsoft Defender authentication API
            body = {
                "client_id": consts.AZURE_CLIENT_ID,
                "client_secret": consts.AZURE_CLIENT_SECRET,
                "grant_type": "client_credentials",
                "resource": "https://api.securitycenter.microsoft.com/",
            }
            utils_obj = Utils(azure_function_name=consts.SENTINEL_TO_DEFENDER)
            response = utils_obj.make_http_request(
                url=azure_auth_url,
                method="POST",
                body=body,
            )
            if response.status_code >= 200 and response.status_code <= 299:
                json_response = response.json()
                if "access_token" not in json_response:
                    applogger.error(
                        "{}(method={}) : {}: Access token not found in MS Defender api call.".format(
                            consts.LOGS_STARTS_WITH, __method_name, azure_function_name
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                        "Access token not found in MS Defender authentication api call.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            azure_function_name,
                            azure_auth_url,
                            response.status_code,
                            response.reason,
                            response.text,
                        )
                    )
                    raise CofenseIntelligenceException()
                else:
                    bearer_token = json_response.get("access_token")
                    applogger.info(
                        "{}(method={}) : {}: MS Defender access token generated successfully.".format(
                            consts.LOGS_STARTS_WITH, __method_name, azure_function_name
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}: Microsoft Defender access "
                        "token generated.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            azure_function_name,
                            azure_auth_url,
                            response.status_code,
                        )
                    )
                    return bearer_token
            else:
                applogger.error(
                    "{}(method={}) : {}: url: {}, Status Code : {}: Error while creating MS "
                    "Defender access_token. Error Reason: {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        azure_function_name,
                        azure_auth_url,
                        response.status_code,
                        response.reason,
                    )
                )
                applogger.debug(
                    "{}(method={}) : {}: url: {}, Status Code : {}, Response: {} : "
                    "Error while creating MS Defender access token. Error Reason: {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        azure_function_name,
                        azure_auth_url,
                        response.status_code,
                        response.text,
                        response.reason,
                    )
                )
                raise CofenseIntelligenceException()
        except CofenseIntelligenceException as error:
            applogger.error(
                "{}(method={}) : Error generated while getting MS Defender access token : {}".format(
                    consts.LOGS_STARTS_WITH, __method_name, error
                )
            )
            raise CofenseIntelligenceException()

    def create_defender_indicator(self, indicator_data):
        """To create indicator into Microsoft Sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            retry_count_429 = 0
            retry_count_401 = 0
            while retry_count_429 <= 3 and retry_count_401 <= 1:
                create_indicator_url = consts.DEFENDER_POST_INDICATOR_URL
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(self.bearer_token),
                }
                payload = json.dumps(indicator_data)
                utils_obj = Utils(azure_function_name=consts.SENTINEL_TO_DEFENDER)
                response = utils_obj.make_http_request(
                    url=create_indicator_url,
                    method="POST",
                    body=payload,
                    headers=headers,
                )
                if response.status_code >= 200 and response.status_code <= 299:
                    response_json = response.json()
                    applogger.debug(
                        "{}(method={}) : {} : Created the indicator into the MS Defender with status code {} "
                        "and got the response {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            response.status_code,
                            response_json,
                        )
                    )
                    return response.status_code
                elif response.status_code == 429:
                    retry_count_429 += 1
                    applogger.error(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "Getting 429 from defender api call. Retrying again after {} seconds.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            create_indicator_url,
                            response.status_code,
                            consts.DEFENDER_429_SLEEP,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                        "Getting 429 from MS Defender api call. Retry count: {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            create_indicator_url,
                            response.status_code,
                            response.reason,
                            response.text,
                            retry_count_429,
                        )
                    )
                    time.sleep(consts.DEFENDER_429_SLEEP)
                elif response.status_code == 401:
                    retry_count_401 += 1
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}:  Error Reason: {}: "
                        "MS Defender access token expired, generating new access token. Retry count: {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            create_indicator_url,
                            response.status_code,
                            response.reason,
                            retry_count_401,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {} : url: {}, Status Code : {}, Error Reason: {}, Response: {} : "
                        "Defender access token expired, generating new access token. Retry count: {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            create_indicator_url,
                            response.status_code,
                            response.reason,
                            response.text,
                            retry_count_401,
                        )
                    )
                    self.bearer_token = self.auth_defender(consts.SENTINEL_TO_DEFENDER)
                    headers["Authorization"] = ("Bearer {}".format(self.bearer_token),)

                elif response.status_code == 400:
                    applogger.error(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "Getting 400 from MS Defender api call. Sentinel Indicator Title: {}, "
                        "Reason : {}, Response : {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            create_indicator_url,
                            response.status_code,
                            indicator_data.get("title", "None"),
                            response.reason,
                            response.text,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "Getting 400 from MS Defender api call. Error Reason : {}, Response : {},"
                        " Payload : {}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            create_indicator_url,
                            response.status_code,
                            response.reason,
                            response.text,
                            payload,
                        )
                    )
                    return response.status_code
                elif response.status_code == 403:
                    # If permissions is not provided to AAD application.
                    applogger.error(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "May be necessary roles are not provided to Azure Active directory "
                        "application to create indicator into MS Defender. "
                        "Response: {}, Error Reason: {}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            create_indicator_url,
                            response.status_code,
                            response.text,
                            response.reason,
                        )
                    )
                    raise CofenseIntelligenceException()
                else:
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}:  Error generated while creating "
                        "indicator in MS Defender. Error Reason: {}, Response : {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            create_indicator_url,
                            response.status_code,
                            response.reason,
                            response.text,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {} : url: {}, Status Code : {}:  Error generated while creating "
                        "indicator in MS Defender. Error Reason: {}, Response : {}, Payload: {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.SENTINEL_TO_DEFENDER,
                            create_indicator_url,
                            response.status_code,
                            response.reason,
                            response.text,
                            payload,
                        )
                    )
                    raise CofenseIntelligenceException()
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded for microsoft defender.".format(
                    consts.LOGS_STARTS_WITH, __method_name, consts.SENTINEL_TO_DEFENDER
                )
            )
            raise CofenseIntelligenceException()
        except CofenseIntelligenceException as error:
            applogger.error(
                "{}(method={}) : {} : Error generated while creating indicator in MS Defender : {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.SENTINEL_TO_DEFENDER,
                    error,
                )
            )
            raise CofenseIntelligenceException()
