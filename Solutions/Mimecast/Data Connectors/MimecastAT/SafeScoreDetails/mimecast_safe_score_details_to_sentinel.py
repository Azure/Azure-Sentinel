"""Get Mimecast Awareness Training SafeScore data and ingest into sentinel."""

import inspect
from ..SharedCode import consts
from ..SharedCode.mimecast_exception import MimecastException, MimecastTimeoutException
from ..SharedCode.logger import applogger
from ..SharedCode.state_manager import StateManager
from ..SharedCode.utils import Utils
import time
import datetime
from tenacity import RetryError


class MimecastAwarenessSafeScore(Utils):
    """Class for Mimecast Awareness Training SafeScore Details."""

    def __init__(self, start_time) -> None:
        """Initialize utility methods and variables.

        Args:
            start_time (str): azure function starting time.
        """
        super().__init__(consts.AWARENESS_SAFESCORE_FUNCTION_NAME)
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
        self.state_manager_obj = StateManager(
            consts.CONN_STRING, consts.SAFESCORE_CHECKPOINT_FILE, consts.FILE_SHARE_NAME
        )
        self.hash_file_state_manager_obj = StateManager(
            consts.CONN_STRING, consts.SAFESCORE_HASH_FILE, consts.FILE_SHARE_NAME
        )
        self.safe_score_details_url = (
            consts.BASE_URL + consts.ENDPOINTS["SAFE_SCORE_DETAILS"]
        )
        self.function_start_time = start_time

    def get_request_body_and_checkpoint(self):
        """Get the request body and checkpoint data for pagination.

        Returns:
            tuple: A dictionary containing the request body and the checkpoint data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            request_body = {"meta": {"pagination": {"pageSize": consts.MAX_PAGE_SIZE}}}
            checkpoint = self.get_checkpoint_data(self.state_manager_obj)
            if checkpoint:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Page checkpoint found.",
                    )
                )
                pageToken = checkpoint.get("pageToken")
                request_body["meta"]["pagination"]["pageToken"] = pageToken
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Page checkpoint data : {}.".format(checkpoint),
                    )
                )
            else:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Page checkpoint not found.",
                    )
                )
            return request_body, checkpoint
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

    def get_awareness_safe_score_details_data_in_sentinel(self):
        """Get Mimecast awareness training safe_score details data and ingest to sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            request_body, checkpoint_data = self.get_request_body_and_checkpoint()
            next_page = True
            while next_page:
                if (
                    int(time.time())
                    >= self.function_start_time + consts.FUNCTION_APP_TIMEOUT_SECONDS
                ):
                    raise MimecastTimeoutException()
                safe_score_details_response = self.make_rest_call(
                    method="POST", url=self.safe_score_details_url, json=request_body
                )
                safe_score_details_data = safe_score_details_response["data"]
                if len(safe_score_details_data) > 0:
                    next_page_token = safe_score_details_response["meta"][
                        "pagination"
                    ].get("next", "")
                    next_page_token_flag = False
                    if next_page_token:
                        next_page_token_flag = True
                    checkpoint_token_updated = self.filter_unique_data_and_post(
                        safe_score_details_data,
                        self.hash_file_state_manager_obj,
                        consts.TABLE_NAME["SAFE_SCORE_DETAILS"],
                        checkpoint_data,
                        self.state_manager_obj,
                        next_page_token_flag,
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
                                "Posting page checkpoint : {}.".format(next_page_token),
                            )
                        )
                        checkpoint_data = {
                            "pageToken": next_page_token,
                            "date": datetime.datetime.utcnow().isoformat(),
                        }
                        self.post_checkpoint_data(
                            self.state_manager_obj, checkpoint_data
                        )
                    else:
                        if checkpoint_token_updated:
                            del request_body["meta"]["pagination"]["pageToken"]
                            checkpoint_data = {}
                        else:
                            next_page = False
                            hash_data_to_save = self.convert_to_hash(
                                safe_score_details_data
                            )
                            applogger.info(
                                self.log_format.format(
                                    consts.LOGS_STARTS_WITH,
                                    __method_name,
                                    self.azure_function_name,
                                    "Posting hash checkpoint.",
                                )
                            )
                            self.post_checkpoint_data(
                                self.hash_file_state_manager_obj,
                                hash_data_to_save,
                                True,
                            )
                            applogger.info(
                                self.log_format.format(
                                    consts.LOGS_STARTS_WITH,
                                    __method_name,
                                    self.azure_function_name,
                                    "End of data.",
                                )
                            )
                else:
                    next_page = False
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "No data found.",
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
