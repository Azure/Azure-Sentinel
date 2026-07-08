"""Google service account OAuth2 token provider."""

import inspect

from google.oauth2 import service_account
import json

from . import consts
from .exceptions import GoogleSecOpsAuthError
from .logger import applogger


class GoogleServiceAccountAuth:
    """Manage Google OAuth2 tokens from service account credentials."""

    def __init__(self, service_account_json: str = consts.SERVICE_ACCOUNT_JSON):
        """Load and validate service account credentials."""
        self._validate_and_load(service_account_json)

    def _validate_and_load(self, service_account_json: str) -> None:
        __method_name = inspect.currentframe().f_code.co_name

        if not service_account_json:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleServiceAccountAuth",
                "GoogleSecopsServiceAccountJson not configured",
            )
            applogger.error(error_msg)
            raise GoogleSecOpsAuthError(error_msg)

        try:
            sa_dict = json.loads(service_account_json)
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    "GoogleServiceAccountAuth",
                    "Successfully parsed service account JSON",
                )
            )
        except json.JSONDecodeError as exc:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleServiceAccountAuth",
                f"GoogleSecopsServiceAccountJson invalid JSON: {exc}",
            )
            applogger.error(error_msg)
            raise GoogleSecOpsAuthError(error_msg) from exc

        missing = [k for k in ("client_email", "private_key") if not sa_dict.get(k)]
        if missing:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleServiceAccountAuth",
                f"Missing required fields in service account: {missing}",
            )
            applogger.error(error_msg)
            raise GoogleSecOpsAuthError(error_msg)

        try:
            self._creds = service_account.Credentials.from_service_account_info(
                sa_dict, scopes=[consts.OAUTH_SCOPE]
            )
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    "GoogleServiceAccountAuth",
                    "Successfully created service account credentials",
                )
            )
        except Exception as exc:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "GoogleServiceAccountAuth",
                f"Failed to create credentials: {exc}",
            )
            applogger.error(error_msg)
            raise GoogleSecOpsAuthError(error_msg) from exc

    def get_credentials(self):
        """Return the underlying service account credentials."""
        return self._creds
