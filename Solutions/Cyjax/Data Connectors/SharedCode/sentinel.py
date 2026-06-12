"""This module contains methods for uploading indicators to Microsoft Sentinel."""

import inspect
import time
import json
import requests
from SharedCode import consts
from SharedCode.logger import applogger
from SharedCode.exceptions import SentinelUploadException, CyjaxAuthenticationException


class MicrosoftSentinel:
    """Microsoft Sentinel client for the Upload Indicator API.

    Handles OAuth 2.0 authentication and STIX indicator batch upload.
    """

    def __init__(self):
        """Initialize the Microsoft Sentinel client and generate OAuth token."""
        self.bearer_token = self.auth_sentinel()
        self.log_format = consts.LOG_FORMAT

    def auth_sentinel(self):
        """Authenticate with Microsoft Sentinel using OAuth 2.0 client credentials flow.

        Returns:
            str: Bearer token for Upload Indicator API.

        Raises:
            CyjaxAuthenticationException: If authentication fails.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                "{}(method={}) : {} : Generating Microsoft Sentinel access token.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                )
            )
            azure_auth_url = consts.AZURE_AUTHENTICATION_URL.format(consts.AZURE_TENANT_ID)
            body = {
                "client_id": consts.AZURE_CLIENT_ID,
                "client_secret": consts.AZURE_CLIENT_SECRET,
                "grant_type": "client_credentials",
                "scope": consts.AUTH_SCOPE,
            }
            response = requests.post(url=azure_auth_url, data=body, timeout=consts.REQUEST_TIMEOUT)
            if 200 <= response.status_code <= 299:
                json_response = response.json()
                if "access_token" not in json_response:
                    applogger.error(
                        "{}(method={}) : {} : Access token not found in Sentinel API response.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                        )
                    )
                    raise CyjaxAuthenticationException("Access token not found in Sentinel API response.")
                bearer_token = json_response.get("access_token")
                applogger.info(
                    "{}(method={}) : {} : Microsoft Sentinel access token generated successfully.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                    )
                )
                return bearer_token
            elif response.status_code == 400 or response.status_code == 401:
                # Parse error response for more details
                error_msg = "Authentication failed with status code: {}".format(response.status_code)
                try:
                    json_response = response.json()
                    error = json_response.get("error", "")
                    error_desc = json_response.get("error_description", "")
                    if response.status_code == 400:
                        error_msg = "Bad Request: {}: {}".format(error, error_desc)
                    elif response.status_code == 401:
                        error_msg = "Unauthorized: {}: {}".format(error, error_desc)
                except (ValueError, json.JSONDecodeError):
                    # If we can't parse JSON, use default error
                    error_msg = "Authentication failed: {} {}".format(response.status_code, response.text)

                applogger.error(
                    "{}(method={}) : {} : {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        error_msg,
                    )
                )
                raise CyjaxAuthenticationException(error_msg)
            else:
                applogger.error(
                    "{}(method={}) : {} : Error generating Sentinel access token. "
                    "Status Code: {}, Reason: {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        response.status_code,
                        response.reason,
                    )
                )
                raise CyjaxAuthenticationException(
                    "Error generating Sentinel access token: status code {}, reason: {}".format(
                        response.status_code, response.reason
                    )
                )
        except CyjaxAuthenticationException:
            raise
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Unexpected error while generating Sentinel access token: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    error,
                )
            )
            raise CyjaxAuthenticationException("Unexpected error during Sentinel authentication: {}".format(error))

    def upload_indicators(self, stix_objects):
        """Upload STIX indicator objects to Microsoft Sentinel via Upload Indicator API.

        Args:
            stix_objects (list): List of STIX 2.1 indicator objects (max 100 per batch).

        Returns:
            dict: Dictionary with 'success_count', 'failure_count', and 'failed_indicators'.

        Raises:
            SentinelUploadException: If the upload fails after retries.
        """
        __method_name = inspect.currentframe().f_code.co_name
        success_count = 0
        failure_count = 0
        failed_indicators = []

        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Uploading {} indicators".format(len(stix_objects)),
            )
        )

        # Upload all indicators in one call - API handles the 100-item limit internally
        result = self._upload_batch(stix_objects)
        success_count = result["success_count"]
        failure_count = result["failure_count"]
        failed_indicators = result["failed_indicators"]

        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Upload complete. Success: {}, Failed: {}".format(success_count, failure_count),
            )
        )

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "failed_indicators": failed_indicators,
        }

    def _handle_validation_errors(self, batch, json_response, status_code):
        """Handle validation errors from Sentinel API response.

        Common logic for both 200 (with errors) and 400 status codes.

        Args:
            batch (list): Original batch of indicators
            json_response (dict): Parsed JSON response from API
            status_code (int): HTTP status code (200 or 400)

        Returns:
            dict: Result with success_count, failure_count, and failed_indicators
        """
        __method_name = inspect.currentframe().f_code.co_name
        errors = json_response.get("errors", [])
        failed_indices = set()

        for error_item in errors:
            record_index = error_item.get("recordIndex")
            error_messages = error_item.get("errorMessages", [])
            applogger.warning(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    "Validation error at recordIndex {}: {}".format(record_index, error_messages),
                )
            )
            if record_index is not None and record_index < len(batch):
                failed_indices.add(record_index)

        failed = [batch[i] for i in failed_indices if i < len(batch)]
        succeeded = len(batch) - len(failed)

        if status_code == 200:
            log_msg = "IOC partial result (200 with errors): {} succeeded, {} failed validation"
        else:
            log_msg = "IOC partial result: {} succeeded, {} failed validation"

        applogger.warning(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                log_msg.format(succeeded, len(failed)),
            )
        )

        return {
            "success_count": succeeded,
            "failure_count": len(failed),
            "failed_indicators": failed,
        }

    def _upload_batch(self, batch):
        """Upload a single batch of STIX indicators to the Upload Indicator API.

        Args:
            batch (list): List of STIX indicator objects (max 100).

        Returns:
            dict: Dictionary with 'success_count', 'failure_count', and 'failed_indicators'.
        """
        __method_name = inspect.currentframe().f_code.co_name
        retry_count_429 = 0
        retry_count_401 = 0
        upload_url = consts.UPLOAD_INDICATOR_URL.format(consts.WORKSPACE_ID)
        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Uploading {} indicators with URL: {}".format(len(batch), upload_url),
            )
        )
        while retry_count_429 <= consts.MAX_RETRIES and retry_count_401 <= 1:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(self.bearer_token),
                }
                request_body = {
                    "sourcesystem": consts.STIX_SOURCE_SYSTEM,
                    "stixobjects": batch,
                }
                response = requests.post(
                    url=upload_url,
                    headers=headers,
                    data=json.dumps(request_body),
                    timeout=consts.REQUEST_TIMEOUT,
                )

                if 200 <= response.status_code <= 299:
                    # Even with 200 status, check for validation errors in response body
                    try:
                        json_response = response.json()
                        errors = json_response.get("errors", [])
                        if not errors:
                            # True success - no errors in response body
                            applogger.info(
                                self.log_format.format(
                                    consts.LOGS_STARTS_WITH,
                                    __method_name,
                                    consts.FUNCTION_NAME,
                                    "IOC uploaded successfully, status code: {}, indicators: {}".format(
                                        response.status_code, len(batch)
                                    ),
                                )
                            )
                            return {
                                "success_count": len(batch),
                                "failure_count": 0,
                                "failed_indicators": [],
                            }
                        # 200 but with validation errors - use common handler
                        return self._handle_validation_errors(batch, json_response, 200)
                    except (ValueError, json.JSONDecodeError):
                        # 200 but can't parse JSON - assume success (empty response)
                        applogger.info(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.FUNCTION_NAME,
                                "IOC uploaded successfully, status code: {}, indicators: {}".format(
                                    response.status_code, len(batch)
                                ),
                            )
                        )
                        return {
                            "success_count": len(batch),
                            "failure_count": 0,
                            "failed_indicators": [],
                        }

                elif response.status_code == 400:
                    if "Workspace Id must be a valid" in response.text:
                        applogger.error(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.FUNCTION_NAME,
                                "Invalid workspace ID: {}".format(response.text),
                            )
                        )
                        raise SentinelUploadException("Invalid workspace ID")
                    try:
                        json_response = response.json()
                        return self._handle_validation_errors(batch, json_response, 400)
                    except (ValueError, json.JSONDecodeError):
                        applogger.error(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.FUNCTION_NAME,
                                "Bad request (400) for IOC upload, could not parse error response",
                            )
                        )
                        return {
                            "success_count": 0,
                            "failure_count": len(batch),
                            "failed_indicators": batch,
                        }
                elif response.status_code == 429:
                    sleep_time = consts.SENTINEL_429_SLEEP
                    # Extract retry time from response body
                    try:
                        json_response = response.json()
                        message = json_response.get("message", "")
                        import re

                        match = re.search(r"Try again in (\d+) seconds", message)
                        if match:
                            sleep_time = int(match.group(1))
                            applogger.warning(
                                self.log_format.format(
                                    consts.LOGS_STARTS_WITH,
                                    __method_name,
                                    consts.FUNCTION_NAME,
                                    "Rate limited (429) for IOC upload, extracted retry time: {} seconds".format(
                                        sleep_time
                                    ),
                                )
                            )
                    except (ValueError, json.JSONDecodeError):
                        applogger.warning(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.FUNCTION_NAME,
                                "Rate limited (429) for IOC upload, using default retry time: {} seconds".format(
                                    sleep_time
                                ),
                            )
                        )

                    applogger.warning(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "Rate limited (429) for IOC upload, retry {}/{}, sleeping {} seconds".format(
                                retry_count_429 + 1,
                                consts.MAX_RETRIES,
                                sleep_time,
                            ),
                        )
                    )
                    time.sleep(sleep_time)
                    retry_count_429 += 1

                elif response.status_code == 401:
                    if retry_count_401 != 0:
                        # Second 401 after token refresh - fail
                        applogger.error(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.FUNCTION_NAME,
                                "Unauthorized (401) for IOC upload after token refresh. Response: {}".format(
                                    response.text
                                ),
                            )
                        )
                        raise SentinelUploadException(
                            "Unauthorized (401) after token refresh. Check Azure credentials and permissions."
                        )
                    # First 401 - attempt token refresh
                    applogger.warning(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "Unauthorized (401) for IOC upload, refreshing token (attempt 1/1)",
                        )
                    )
                    retry_count_401 += 1
                    self.bearer_token = self.auth_sentinel()
                    continue
                elif response.status_code == 404:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "Workspace not found (404) for IOC upload. Check WORKSPACE_ID. Response: {}".format(
                                response.text
                            ),
                        )
                    )
                    # Don't retry - this is a configuration error
                    raise SentinelUploadException(
                        "Workspace ID '{}' not found. Verify the WORKSPACE_ID configuration.".format(
                            consts.WORKSPACE_ID
                        )
                    )

                elif response.status_code == 500:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "Server error (500) for IOC upload. Response: {}".format(response.text),
                        )
                    )
                    # Don't retry - server errors indicate API issues
                    raise SentinelUploadException("Microsoft Sentinel server error (500). Please try again later.")

                else:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "Upload failed for IOC upload, status code: {}, response: {}".format(
                                response.status_code, response.text
                            ),
                        )
                    )
                    return {
                        "success_count": 0,
                        "failure_count": len(batch),
                        "failed_indicators": batch,
                    }

            except (CyjaxAuthenticationException, SentinelUploadException):
                raise
            except requests.exceptions.RequestException as req_err:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Request error uploading IOC: {}".format(req_err),
                    )
                )
                return {
                    "success_count": 0,
                    "failure_count": len(batch),
                    "failed_indicators": batch,
                }
            except Exception as error:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Unexpected error uploading IOC: {}".format(error),
                    )
                )
                return {
                    "success_count": 0,
                    "failure_count": len(batch),
                    "failed_indicators": batch,
                }

        if retry_count_429 > consts.MAX_RETRIES:
            error_msg = "Max retries exceeded for IOC upload due to rate limiting (429)"
        elif retry_count_401 > 1:
            error_msg = "Max retries exceeded for IOC upload due to authentication failures (401)"
        else:
            error_msg = "Max retries exceeded for IOC upload"
        applogger.error(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "{} - 429 retries: {}, 401 retries: {}".format(error_msg, retry_count_429, retry_count_401),
            )
        )
        return {
            "success_count": 0,
            "failure_count": len(batch),
            "failed_indicators": batch,
        }
