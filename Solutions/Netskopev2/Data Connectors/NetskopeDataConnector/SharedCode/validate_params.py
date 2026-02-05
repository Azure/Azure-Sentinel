"""Validate the parameters from consts."""
import inspect
from . import consts
from .logger import applogger
from .netskope_exception import NetskopeException


def validate_parameters(azure_function_name):
    """Validate the user input parameters.

    Args:
        azure_function_name (str): The name of the caller azure function for logging.

    Raises:
        NetskopeException: Netskope Custom Exception
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        required_params = {
            "LogLevel": consts.LOG_LEVEL,
            "ConnectionString": consts.CONNECTION_STRING,
            "ShareName": consts.SHARE_NAME,
            "NetskopeHostname": consts.NETSKOPE_HOSTNAME,
            "NetskopeToken": consts.NETSKOPE_TOKEN,
        }
        applogger.debug(
            "{}(method={}) : Checking if all the environment variables exist or not.".format(
                consts.LOGS_STARTS_WITH, __method_name
            )
        )
        missing_required_field = False
        for label, params in required_params.items():
            if not params or params == "":
                missing_required_field = True
                applogger.error(
                    '{}(method={}) : {} : "{}" field is not set in the environment please set '
                    "the environment variable and run the app.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        azure_function_name,
                        label,
                    )
                )
        if missing_required_field:
            raise NetskopeException()
    except NetskopeException:
        applogger.error(
            "{}(method={}) : {} : Error while validating environment variables.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                azure_function_name,
            )
        )
        raise NetskopeException()
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Error while validating environment variables. Error-{}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                azure_function_name,
                error,
            )
        )
        raise NetskopeException()
