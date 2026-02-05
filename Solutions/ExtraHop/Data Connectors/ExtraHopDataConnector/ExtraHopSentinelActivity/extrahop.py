"""This file contains implementation to ingest ExtraHop detections data into sentinel."""

import inspect
import json

from SharedCode.consts import LOGS_STARTS_WITH, DETECTIONS_TABLE_NAME
from SharedCode.extrahop_exceptions import ExtraHopException
from SharedCode.logger import applogger
from .sentinel import MicrosoftSentinel


class ExtraHop:
    """This class contains methods to get data from request body pushed via ExtraHop webhook and ingest into Log Analytics Workspace."""
    def __init__(self) -> None:
        """Initialize instance variables for class."""
        self.logs_starts_with = LOGS_STARTS_WITH+" Activity"
        self.microsoftsentinel = MicrosoftSentinel()
        self.error_logs = "{}(method={}) {}"
        self.check_environment_var_existance()

    def check_environment_var_existance(self):
        """To verify that all required environment variables are exist.

        Raises:
            ExtraHopException: raise exception if any of the required environment variable is not set.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                "{}(method={}) Checking environment variables are exist or not.".format(
                    self.logs_starts_with, __method_name
                )
            )
            if DETECTIONS_TABLE_NAME is None:
                raise ExtraHopException(
                    "DetectionsTableName is not set in the environment please set the environment variable."
                )
            applogger.debug(
                "{}(method={}) All custom environment variable exists.".format(
                    self.logs_starts_with, __method_name
                )
            )
        except ExtraHopException as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise ExtraHopException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise ExtraHopException(err)

    def parse_data_and_send_to_sentinel(self, data):
        """Parse data and send it to sentinel.

        Args:
            data (dict): Data received from ExtraHop webhook.

        Raises:
            ExtraHopException: raises when any error occurs.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            body = json.dumps(data)
            self.microsoftsentinel.post_data(body=body, log_type=DETECTIONS_TABLE_NAME)
            applogger.info(
                "{}(method={}) Detections data is ingested into {} table of log analytics workspace.".format(
                    self.logs_starts_with, __method_name, DETECTIONS_TABLE_NAME
                )
            )
            return "Data ingetsed successfully to Microsoft Sentinel log analytics workspace."
        except ExtraHopException as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise ExtraHopException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise ExtraHopException(err)
