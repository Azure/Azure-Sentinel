"""Utils module for Google Threat Intelligence connector.

Provides the Utils base class with checkpoint management and date helper utilities.
"""

import inspect
import json
import datetime
from json.decoder import JSONDecodeError

from SharedCode.state_manager import StateManager
from SharedCode.exceptions import GTIRelevanceSystemAlertsException
from SharedCode.logger import applogger
from SharedCode import consts


class Utils:
    """Base utility class for the GTI connector.

    Provides checkpoint management and date helper methods
    shared across GTI connector functions.
    """

    def __init__(self, azure_function_name: str) -> None:
        """Initialise the Utils base class.

        Args:
            azure_function_name (str): Name of the Azure Function using this class.
        """
        self.azure_function_name = azure_function_name
        self.log_format = consts.LOG_FORMAT

    def get_checkpoint_data(self, checkpoint_obj: StateManager):
        """Get checkpoint data from a StateManager object.

        Args:
            checkpoint_obj (StateManager): The StateManager object to retrieve checkpoint data from.

        Returns:
            dict or None: The retrieved checkpoint data parsed as JSON, or None if no checkpoint exists.

        Raises:
            GTIRelevanceSystemAlertsException: If there is an error reading or parsing checkpoint data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Fetching checkpoint data",
                )
            )
            checkpoint_data = checkpoint_obj.get()
            if checkpoint_data:
                checkpoint_data = json.loads(checkpoint_data)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Checkpoint data = {}".format(checkpoint_data),
                )
            )
            return checkpoint_data
        except JSONDecodeError as json_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.JSON_DECODE_ERROR_MSG.format(json_error),
                )
            )
            raise GTIRelevanceSystemAlertsException(
                "JSON decode error reading checkpoint: {}".format(json_error)
            )
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise GTIRelevanceSystemAlertsException(
                "Unexpected error reading checkpoint: {}".format(err)
            )

    def post_checkpoint_data(self, checkpoint_obj: StateManager, data):
        """Post checkpoint data to a StateManager object.

        Args:
            checkpoint_obj (StateManager): The StateManager object to post data to.
            data (dict): The data to be JSON-serialised and posted.

        Raises:
            GTIRelevanceSystemAlertsException: If there is an error writing checkpoint data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Posting checkpoint data = {}".format(data),
                )
            )
            checkpoint_obj.post(json.dumps(data))
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Checkpoint data posted to Azure Storage",
                )
            )
        except TypeError as type_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.TYPE_ERROR_MSG.format(type_error),
                )
            )
            raise GTIRelevanceSystemAlertsException(
                "Type error posting checkpoint: {}".format(type_error)
            )
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise GTIRelevanceSystemAlertsException(
                "Unexpected error posting checkpoint: {}".format(err)
            )

    def get_start_date_of_data_fetching(self):
        """Retrieve the start date for data fetching.

        If no start date is configured via StartDate environment variable, calculates
        a default lookback window of DEFAULT_LOOKUP_DAYS days from now.
        If a start date is provided but is invalid or in the future, raises an exception.

        Accepts full datetime format: 2026-05-20T15:43:51.16Z (fractional seconds optional).

        Returns:
            str: The start date for data fetching in DATE_TIME_FORMAT.

        Raises:
            GTIRelevanceSystemAlertsException: If the start date is invalid or in the future.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if not consts.START_DATE:
                start_date = (
                    datetime.datetime.now(datetime.timezone.utc)
                    - datetime.timedelta(days=consts.DEFAULT_LOOKUP_DAYS)
                ).strftime(consts.DATE_TIME_FORMAT)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "No StartDate configured, defaulting to {} days lookback: {}".format(
                            consts.DEFAULT_LOOKUP_DAYS, start_date
                        ),
                    )
                )
                return start_date
            try:
                # Strip trailing Z and parse; fromisoformat handles optional fractional seconds
                dt = datetime.datetime.fromisoformat(consts.START_DATE.rstrip("Z"))
                start_date = dt.strftime(consts.DATE_TIME_FORMAT)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Start date configured by user: {}".format(start_date),
                    )
                )
                if start_date > datetime.datetime.now(datetime.timezone.utc).strftime(consts.DATE_TIME_FORMAT):
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Configured StartDate is a future date: {}".format(start_date),
                        )
                    )
                    raise GTIRelevanceSystemAlertsException(
                        "StartDate '{}' is in the future".format(start_date)
                    )
                return start_date
            except ValueError:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "StartDate '{}' is not a valid datetime in yyyy-mm-ddTHH:MM:SS[.fff]Z format".format(
                            consts.START_DATE
                        ),
                    )
                )
                raise GTIRelevanceSystemAlertsException(
                    "StartDate '{}' is not a valid datetime in yyyy-mm-ddTHH:MM:SS[.fff]Z format".format(
                        consts.START_DATE
                    )
                )
        except GTIRelevanceSystemAlertsException:
            raise
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise GTIRelevanceSystemAlertsException(
                "Unexpected error determining start date: {}".format(err)
            )
