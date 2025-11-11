"""Get Mimecast Awareness Training phishing campaigns user data and ingest into sentinel."""

import inspect
from ..SharedCode import consts
from ..SharedCode.mimecast_exception import MimecastException, MimecastTimeoutException
from ..SharedCode.logger import applogger
from ..SharedCode.utils import Utils
from ..SharedCode.sentinel import post_data
import json
import time
from tenacity import RetryError


class MimecastAwarenessUserData(Utils):
    """Class for Mimecast Awareness Training phishing campaigns user data."""

    def __init__(self, start_time) -> None:
        """Initialize utility methods and variables."""
        super().__init__(consts.AWARENESS_USER_DATA_FUNCTION_NAME)
        self.check_environment_var_exist(
            [
                {"BaseURL": consts.BASE_URL},
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY},
                {"MimecastClientID": consts.MIMECAST_CLIENT_ID},
                {"MimecastClientSecret": consts.MIMECAST_CLIENT_SECRET},
                {"ConnectionString": consts.CONN_STRING},
                {"LogLevel": consts.LOG_LEVEL},
            ]
        )
        self.authenticate_mimecast_api()
        self.get_campaign_url = consts.BASE_URL + consts.ENDPOINTS["CAMPAIGN_DATA"]
        self.get_user_url = consts.BASE_URL + consts.ENDPOINTS["USER_DATA"]
        self.function_start_time = start_time

    def fetch_user_data_for_campaigns(self, campaign_id):
        """Get mimecast phishing user data from given campaign.

        Args:
            campaign (dict): campaign for which user data to be fetched.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            request_body = {
                "data": [{"id": campaign_id}],
                "meta": {"pagination": {"pageSize": consts.MAX_PAGE_SIZE}},
            }
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Fetching user data for campaign : {}.".format(campaign_id),
                )
            )
            next_page = True
            total_user_count = 0
            while next_page:
                if (
                    int(time.time())
                    >= self.function_start_time + consts.FUNCTION_APP_TIMEOUT_SECONDS
                ):
                    raise MimecastTimeoutException()
                user_data_response = self.make_rest_call(
                    method="POST", url=self.get_user_url, json=request_body
                )
                user_data = user_data_response.get("data", [])
                if len(user_data) > 0 and len(user_data[0].get("items", [])) > 0:
                    total_user_count += len(user_data[0]["items"])
                    user_data_items = user_data[0]["items"]
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Posting data to azure Sentinel log analytics, data count : {}.".format(
                                len(user_data_items)
                            ),
                        )
                    )
                    post_data(
                        json.dumps(user_data_items),
                        log_type=consts.TABLE_NAME["USER_DATA"],
                    )
                    next_page_token = user_data_response["meta"]["pagination"].get(
                        "next", ""
                    )
                    if next_page_token:
                        request_body["meta"]["pagination"][
                            "pageToken"
                        ] = next_page_token
                        applogger.info(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.azure_function_name,
                                "Found next in response : {}.".format(next_page_token),
                            )
                        )
                    else:
                        next_page = False
                        applogger.debug(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.azure_function_name,
                                "End of user data for campaign id : {}.".format(
                                    campaign_id
                                ),
                            )
                        )
                else:
                    next_page = False
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "No user data found for campaign : {}.".format(campaign_id),
                        )
                    )
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Total user count : {} for campaign : {}.".format(
                        total_user_count, campaign_id
                    ),
                )
            )
        except KeyError as key_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.KEY_ERROR_MSG.format(key_error),
                )
            )
            raise MimecastException()
        except MimecastTimeoutException:
            raise MimecastTimeoutException()
        except RetryError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.MAX_RETRY_ERROR_MSG.format(
                        error, error.last_attempt.exception()
                    ),
                )
            )
            raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def get_awareness_user_data_in_sentinel(self):
        """Get Mimecast Awareness Training phishing campaigns user data and ingest to sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            campaigns_response = self.make_rest_call(
                method="POST", url=self.get_campaign_url
            )
            campaigns_data = campaigns_response["data"]
            if len(campaigns_data) > 0:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Awareness Training Phishing User Data : Found {} Phishing Campaigns ids".format(
                            len(campaigns_data)
                        ),
                    )
                )
                for campaign in campaigns_data:
                    if (
                        int(time.time())
                        >= self.function_start_time
                        + consts.FUNCTION_APP_TIMEOUT_SECONDS
                    ):
                        raise MimecastTimeoutException()
                    self.fetch_user_data_for_campaigns(campaign["id"])
            else:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "No Phishing Campaigns found.",
                    )
                )
        except KeyError as key_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.KEY_ERROR_MSG.format(key_error),
                )
            )
            raise MimecastException()
        except MimecastTimeoutException:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "function app 9:30 mins executed hence breaking.",
                )
            )
            return
        except RetryError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.MAX_RETRY_ERROR_MSG.format(
                        error, error.last_attempt.exception()
                    ),
                )
            )
            raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()
