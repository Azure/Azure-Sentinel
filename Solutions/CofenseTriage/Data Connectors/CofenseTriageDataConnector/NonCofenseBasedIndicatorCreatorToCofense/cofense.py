"""This file contains Cofense Triage class containing creating and updating indicator function."""
import time
import json
import inspect
from ..SharedCode.consts import (
    LOGS_STARTS_WITH,
    COFENSE_POST_INDICATOR_URL,
    SENTINEL_TO_COFENSE,
    COFENSE_429_SLEEP,
    COFENSE_UPDATE_INDICATOR_URL,
)
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_exception import CofenseException
from ..SharedCode.utils import make_rest_call, auth_cofense, create_proxy


class CofenseTriage:
    """This class containes methods to create indicators into Cofense Triage."""

    def __init__(self) -> None:
        """Initialize instance variable for class."""
        self.access_token = auth_cofense(SENTINEL_TO_COFENSE)

        self.accept_content_type = "application/vnd.api+json"

        self.proxy = create_proxy()

    # To do: merge post_indicators and update_indicators as common code.
    def post_indicators(
        self,
        threat_level,
        threat_type,
        threat_value,
        threat_source,
        sentinel_indicator_name,
    ):
        """To post indicators into cofense triage.

        Args:
            threat_level (String): (Required) Level of threat (Malicious, Suspicious, or Benign).
            threat_type (String): (Required) Type of threat (Hostname, URL, MD5 or SHA256).
            threat_value (String): (Required) Value corresponding to the type of threat indicated in threat_type.
            threat_source (String): (Required) Value corresponding to the source of the threat.
            sentinel_indicator_name (String): (Required) ID of sentinel indicator. Used in 422 error code.

        Raises:
            CofenseException: Custom exception raises while getting exception.

        Returns:
            post_indicator_json_response: API response to fetch the cofense indicator id.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            cofense_post_indicator_url = COFENSE_POST_INDICATOR_URL

            body = json.dumps(
                {
                    "data": {
                        "type": "threat_indicators",
                        "attributes": {
                            "threat_level": threat_level,
                            "threat_type": threat_type,
                            "threat_value": threat_value,
                            "threat_source": threat_source,
                        },
                    }
                }
            )

            headers = {
                "Accept": self.accept_content_type,
                "Content-Type": self.accept_content_type,
                "Authorization": "Bearer " + self.access_token,
            }

            retry_count_429 = 0
            retry_count_401 = 0
            while retry_count_429 <= 1 and retry_count_401 <= 1:
                post_indicator_response = make_rest_call(
                    url=cofense_post_indicator_url,
                    method="POST",
                    azure_function_name=SENTINEL_TO_COFENSE,
                    payload=body,
                    headers=headers,
                    proxies=self.proxy,
                )

                post_indicator_status_code = post_indicator_response.status_code

                # if response status code is 200-299.
                if (
                    post_indicator_status_code >= 200
                    and post_indicator_status_code <= 299
                ):
                    post_indicator_json_response = json.loads(
                        post_indicator_response.text
                    )
                    # return the json response to fetch the indicator id.
                    return post_indicator_status_code, post_indicator_json_response

                # if response status code is 401. access token expired.
                elif post_indicator_status_code == 401:
                    retry_count_401 = retry_count_401 + 1
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}:  Error Reason: {}: "
                        " Cofense access token expired, generating new access token. Retry count: {}.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_post_indicator_url,
                            post_indicator_response.status_code,
                            post_indicator_response.reason,
                            retry_count_401,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {} : url: {}, Status Code : {}, Error Reason: {}, Response: {} :"
                        " Cofense access token expired, generating new access token. Retry count: {}.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_post_indicator_url,
                            post_indicator_response.status_code,
                            post_indicator_response.reason,
                            post_indicator_response.text,
                            retry_count_401,
                        )
                    )
                    self.access_token = auth_cofense(SENTINEL_TO_COFENSE)

                # response status code is 429, to many request.
                elif post_indicator_status_code == 429:
                    applogger.error(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "Getting 429 from cofense api call. Retrying again after {} seconds.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_post_indicator_url,
                            post_indicator_response.status_code,
                            COFENSE_429_SLEEP,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                        "Getting 429 from cofense api call. Retry count: {}.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_post_indicator_url,
                            post_indicator_response.status_code,
                            post_indicator_response.reason,
                            post_indicator_response.text,
                            retry_count_429,
                        )
                    )
                    retry_count_429 += 1
                    time.sleep(COFENSE_429_SLEEP)

                # response status code is 422, If indicator already present in cofense triage.
                elif (
                    post_indicator_status_code == 422
                    and json.loads(post_indicator_response.text)
                    .get("errors", [{}])[0]
                    .get("title")
                    == "has already been taken"
                ):
                    applogger.error(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "Indicator already present in Cofense Triage. "
                        "Microsoft Sentinel Indicator name: {} .".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_post_indicator_url,
                            post_indicator_response.status_code,
                            sentinel_indicator_name,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} :"
                        "Indicator already present in Cofense Triage."
                        "Microsoft Sentinel Indicator name: {} .".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_post_indicator_url,
                            post_indicator_response.status_code,
                            post_indicator_response.reason,
                            post_indicator_response.text,
                            sentinel_indicator_name,
                        )
                    )
                    post_indicator_json_response = json.loads(
                        post_indicator_response.text
                    )
                    # return the json response to fetch the indicator id.
                    return post_indicator_status_code, post_indicator_json_response

                # if response status code is not 200-299, 401, 429 and 422(indicator already present).
                # Raise exception for this.
                else:
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}: Error while creating indicators"
                        " into cofense triage. Error Reason: {}".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_post_indicator_url,
                            post_indicator_response.status_code,
                            post_indicator_response.reason,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                        "Error while creating indicators into cofense triage.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_post_indicator_url,
                            post_indicator_response.status_code,
                            post_indicator_response.reason,
                            post_indicator_response.text,
                        )
                    )
                    raise CofenseException()
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded for posting indicators into cofense.".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE
                )
            )
            raise CofenseException()
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Error occurred while creating indicator in cofense : {}".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
                )
            )
            raise CofenseException()

    # To do: merge post_indicators and update_indicators as common code.
    def update_indicators(self, threat_level, id=""):
        """To update indicators into cofense triage.

        Args:
            threat_level (String): (Required) Level of threat (Malicious, Suspicious, or Benign).
            id (str, optional): Cofense Indicator ID for updating indicator.. Defaults to "".

        Raises:
            CofenseException: Custom exception raises while getting exception.

        Returns:
            update_indicator_json_response: API response to fetch the cofense indicator id.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            cofense_update_indicator_url = COFENSE_UPDATE_INDICATOR_URL + str(id)

            body = json.dumps(
                {
                    "data": {
                        "id": str(id),
                        "type": "threat_indicators",
                        "attributes": {
                            "threat_level": threat_level,
                        },
                    }
                }
            )

            headers = {
                "Accept": self.accept_content_type,
                "Content-Type": self.accept_content_type,
                "Authorization": "Bearer " + self.access_token,
            }

            retry_count_429 = 0
            retry_count_401 = 0
            while retry_count_429 <= 1 and retry_count_401 <= 1:
                update_indicator_response = make_rest_call(
                    url=cofense_update_indicator_url,
                    method="PUT",
                    azure_function_name=SENTINEL_TO_COFENSE,
                    payload=body,
                    headers=headers,
                    proxies=self.proxy,
                )

                update_indicator_status_code = update_indicator_response.status_code

                if (
                    update_indicator_status_code >= 200
                    and update_indicator_status_code <= 299
                ):
                    update_indicator_json_response = json.loads(
                        update_indicator_response.text
                    )
                    # return the json response to fetch the indicator id.
                    return update_indicator_json_response

                elif update_indicator_status_code == 401:
                    retry_count_401 = retry_count_401 + 1
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}:  Error Reason: {}: "
                        " Cofense access token expired, generating new access token. Retry count: {}.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_update_indicator_url,
                            update_indicator_response.status_code,
                            update_indicator_response.reason,
                            retry_count_401,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {} : url: {}, Status Code : {}, Error Reason: {}, Response: {} :"
                        " Cofense access token expired, generating new access token. Retry count: {}.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_update_indicator_url,
                            update_indicator_response.status_code,
                            update_indicator_response.reason,
                            update_indicator_response.text,
                            retry_count_401,
                        )
                    )
                    self.access_token = auth_cofense(SENTINEL_TO_COFENSE)

                elif update_indicator_status_code == 429:
                    applogger.error(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "Getting 429 from cofense api call. Retrying again after {} seconds.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_update_indicator_url,
                            update_indicator_response.status_code,
                            COFENSE_429_SLEEP,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                        "Getting 429 from cofense api call. Retry count: {}.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_update_indicator_url,
                            update_indicator_response.status_code,
                            update_indicator_response.reason,
                            update_indicator_response.text,
                            retry_count_429,
                        )
                    )
                    retry_count_429 += 1
                    time.sleep(COFENSE_429_SLEEP)

                else:
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}: Error while updating indicators"
                        " into cofense triage. Error Reason: {}".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_update_indicator_url,
                            update_indicator_response.status_code,
                            update_indicator_response.reason,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                        "Error while creating indicators into cofense triage.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            SENTINEL_TO_COFENSE,
                            cofense_update_indicator_url,
                            update_indicator_response.status_code,
                            update_indicator_response.reason,
                            update_indicator_response.text,
                        )
                    )
                    raise CofenseException()
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded for updating indicators into cofense.".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE
                )
            )
            raise CofenseException()
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Error occurred while updating indicator in cofense : {}".format(
                    LOGS_STARTS_WITH, __method_name, SENTINEL_TO_COFENSE, error
                )
            )
            raise CofenseException()
