"""Get Mimecast TTP Attachment Data and Ingest into Sentinel."""

from SharedCode.utils import Utils
from SharedCode.logger import applogger
from SharedCode import consts
from SharedCode.mimecast_exception import MimecastException, MimecastTimeoutException
from SharedCode.state_manager import StateManager
from SharedCode.sentinel import post_data
import inspect
import json
import datetime
import time
from tenacity import RetryError


file_path = "mimecastttpattachment"


class MimecastTTPAttachment(Utils):
    """Mimecast TTP Attachment Class."""

    def __init__(self, start_time) -> None:
        """Initialize the MimecastTTPAttachment class.

        Args:
            start(int): The starting time for the timer trigger.
        """
        super().__init__(consts.TTP_ATTACHMENT_FUNCTION_NAME)
        self.check_environment_var_exist(
            [
                {"File_Share_Name": consts.FILE_SHARE_NAME},
                {"Base_Url": consts.BASE_URL},
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY},
                {"Mimecast_Client_ID": consts.MIMECAST_CLIENT_ID},
                {"Mimecast_Client_Secret": consts.MIMECAST_CLIENT_SECRET},
            ]
        )
        self.authenticate_mimecast_api()
        self.start = start_time
        self.checkpoint_obj = StateManager(
            consts.CONN_STRING, file_path, consts.FILE_SHARE_NAME
        )

    def get_mimecast_ttp_attachment_data_in_sentinel(self):
        """Get the TTP Attachment Data from Mimecast."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            # Get from date, to date and page token from checkpoint files at start of execution
            from_date, to_date, page_token = self.get_from_date_to_date_page_token(
                self.checkpoint_obj
            )
            while (
                self.iso_to_epoch_int(to_date) - self.iso_to_epoch_int(from_date)
                >= consts.TIME_DIFFERENCE
            ):
                if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
                    raise MimecastTimeoutException()
                # Entry point of starting to get and ingest data to sentinel
                from_date, to_date = self.get_and_ingest_data_to_sentinel(
                    from_date, to_date, page_token
                )
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "From and To time difference is less than 15 min, Stop execution.",
                )
            )
        except MimecastTimeoutException:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Mimecast: 9:30 mins executed hence breaking.",
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

    def get_and_ingest_data_to_sentinel(self, from_date, to_date, page_token):
        """Iterate through from and to dates and get mimecast data and ingest data to sentinel.

        Args:
            from_date (str): The start date for data retrieval.
            to_date (str): The end date for data retrieval.
            page_token (str): The token for paginating through the data.

        Returns:
            Tuple[str, str]: A tuple containing the updated start and end dates after data ingestion.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            temp_from = from_date
            temp_to = to_date
            checkpoint_data_to_post = {
                "from_date": from_date,
                "to_date": to_date,
                "page_token": page_token,
            }
            page = 1
            total_ingested_data_count = 0
            while True:
                if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
                    raise MimecastTimeoutException()
                payload = {
                    "meta": {
                        "pagination": {
                            "pageSize": consts.PAGE_SIZE,
                            "pageToken": "" if not page_token else page_token,
                        }
                    },
                    "data": [{"from": from_date, "oldestFirst": True, "to": to_date}],
                }
                applogger.debug(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Request body = {}".format(payload),
                    )
                )
                url = "{}{}".format(consts.BASE_URL, consts.ENDPOINTS["TTP_ATTACHMENT"])
                response = self.make_rest_call("POST", url, json=payload)

                pagination_details = response.get("meta").get("pagination")
                page_token = pagination_details.get("next", "")
                total_count = pagination_details.get("totalCount")
                data_to_ingest = response.get("data")[0].get("attachmentLogs")
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Data count to ingest = {}".format(len(data_to_ingest)),
                    )
                )
                total_ingested_data_count += len(data_to_ingest)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Next Page token = {}, Total count = {}, Total ingested data count = {}, Page = {}".format(
                            page_token,
                            total_count,
                            total_ingested_data_count,
                            page,
                        ),
                    )
                )
                if len(data_to_ingest) > 0:
                    post_data(
                        json.dumps(data_to_ingest),
                        consts.TABLE_NAME["TTP_ATTACHMENT"],
                    )

                checkpoint_data_to_post.update({"page_token": page_token})
                if not page_token:
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "No next page token found, Breaking the loop",
                        )
                    )
                    from_date = to_date
                    to_date = datetime.datetime.now(datetime.timezone.utc).strftime(
                        consts.DATE_TIME_FORMAT
                    )
                    checkpoint_data_to_post = {
                        "from_date": from_date,
                        "to_date": to_date,
                        "page_token": page_token,
                    }
                    self.post_checkpoint_data(
                        self.checkpoint_obj, checkpoint_data_to_post
                    )
                    break
                self.post_checkpoint_data(self.checkpoint_obj, checkpoint_data_to_post)
                page += 1
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Data ingested from = {}, to = {}, Total ingested count = {}".format(
                        temp_from, temp_to, total_ingested_data_count
                    ),
                )
            )
            return from_date, to_date
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
        except ValueError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.VALUE_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()
        except TypeError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.TYPE_ERROR_MSG.format(err),
                )
            )
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
