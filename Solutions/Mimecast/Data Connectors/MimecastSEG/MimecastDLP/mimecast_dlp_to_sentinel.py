"""Get mimecast data and ingest to custom table in sentinel."""

import inspect
import datetime
import json
import time
from ..SharedCode import consts
from ..SharedCode.mimecast_exception import MimecastException, MimecastTimeoutException
from ..SharedCode.logger import applogger
from ..SharedCode.state_manager import StateManager
from ..SharedCode.utils import Utils
from ..SharedCode.sentinel import post_data
from tenacity import RetryError


class MimecastDLPToSentinel(Utils):
    """Class for ingest dlp the data from mimecast to sentinel."""

    def __init__(self, start_time) -> None:
        """Initialize MimecastDLPToSentinel object."""
        super().__init__(consts.SEG_DLP_FUNCTION_NAME)
        self.check_environment_var_exist(
            [
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
            consts.CONN_STRING, "Checkpoint-SEG-DLP", consts.FILE_SHARE_NAME
        )

    def get_mimecast_dlp_data_in_sentinel(self):
        """Get mimecast data and ingest data to sentinel, initialization method."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            # Get from date, to date and page token from checkpoint files at start of execution
            from_date, to_date, page_token = self.get_from_date_to_date_page_token()
            while (
                self.iso_to_epoch_int(to_date) - self.iso_to_epoch_int(from_date)
                >= consts.TIME_DIFFERENCE
            ):
                if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
                    raise MimecastTimeoutException()
                # Entry point of starting to get and ingest data to sentinel
                from_date, to_date, page_token = self.get_and_ingest_data_to_sentinel(
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
                    "Mimecast: 9:00 mins executed hence breaking.",
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

    def get_from_date_to_date_page_token(self):
        """Get the from date, to date, and page token from the checkpoint data.

        If data is not available in checkpoint file, then get the start date from user input.
        If user input is not available or invalid then set from date's default value.

        Returns:
            Tuple[str, str, str]: A tuple containing the from date, to date, and page token.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            checkpoint_data = self.get_checkpoint_data(self.checkpoint_obj)

            if not checkpoint_data:
                from_date = self.get_start_date_of_data_fetching()
                page_token = ""
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Checkpoint data is not available, Start fetching data from = {}".format(
                            from_date
                        ),
                    )
                )
                to_date = datetime.datetime.now(datetime.timezone.utc).strftime(
                    consts.DATE_TIME_FORMAT
                )
            else:
                from_date = checkpoint_data.get("from_date")
                page_token = checkpoint_data.get("page_token")
                to_date = checkpoint_data.get("to_date")

                if (not page_token and from_date) or (not to_date):
                    to_date = datetime.datetime.now(datetime.timezone.utc).strftime(
                        consts.DATE_TIME_FORMAT
                    )

                if not from_date:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "From date is not available in checkpoint, User has manually changed checkpoint",
                        )
                    )
                    raise MimecastException()
            return from_date, to_date, page_token
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

    def get_start_date_of_data_fetching(self):
        """Retrieve the start date for data fetching.

        If no start date is provided, it calculates the start date based on a default lookup day.
        If the provided start date is invalid, it will fail and raise an exception.

        Returns:
            str: The start date for data fetching in the format specified by consts.DATE_TIME_FORMAT.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if not consts.START_DATE:
                start_date = (
                    datetime.datetime.utcnow()
                    - datetime.timedelta(days=consts.DEFAULT_LOOKUP_DAY)
                ).strftime(consts.DATE_TIME_FORMAT)
                return start_date
            try:
                start_date = datetime.datetime.strptime(
                    consts.START_DATE, "%Y-%m-%d"
                ).strftime(consts.DATE_TIME_FORMAT)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Start date given by user is {}".format(start_date),
                    )
                )
                # * if start date is future date, raise exception
                if start_date > datetime.datetime.utcnow().strftime(
                    consts.DATE_TIME_FORMAT
                ):
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Start date given by user is future date",
                        )
                    )
                    raise MimecastException()
                return start_date
            except ValueError:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Start date given by user is not valid",
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

    def get_and_ingest_data_to_sentinel(self, from_date, to_date, page_token):
        """Iterate through from and to dates and get mimecast data and ingest data to sentinel.

        Args:
            from_date (str): The start date for data retrieval.
            to_date (str): The end date for data retrieval.
            page_token (str): The token for paginating through the data.

        Returns:
            Tuple[str, str, str]: A tuple containing the updated start, end dates and token after data ingestion.
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
                url = "{}{}".format(consts.BASE_URL, consts.ENDPOINTS["SEG_DLP"])
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Fetching data for 'From datetime' = {},  'To datetime' = {}".format(
                            from_date, to_date
                        ),
                    )
                )
                response = self.make_rest_call("POST", url, json=payload)

                pagination_details = response.get("meta").get("pagination")
                page_token = pagination_details.get("next", "")
                total_count = pagination_details.get("totalCount")
                data_to_ingest = response.get("data")[0].get("dlpLogs")
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
                    post_data(json.dumps(data_to_ingest), consts.TABLE_NAME["SEG_DLP"])

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
            return from_date, to_date, page_token
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
