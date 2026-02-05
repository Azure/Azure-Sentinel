"""
VMRay API Configurations
"""

from time import sleep

from vmray.rest_api import VMRayRESTAPI, VMRayRESTAPIError

from .const import RETRY_STATUS_CODE, VMRay_CONFIG


class VMRay:
    """
    Wrapper class for VMRayRESTAPI modules and functions.
    Import this class to submit samples and retrieve reports.
    """

    def __init__(self, log):
        """
        Initialize, authenticate and healthcheck the VMRay instance,
        use VMRayConfig as configuration
        :param log: logger instance
        :return void
        """
        self.api = None
        self.log = log

        self.healthcheck()

    def healthcheck(self):
        """
        Healthcheck for VMRay REST API, uses system_info endpoint
        :raise: When healthcheck error occurred during the connection wih REST API
        :return: boolean status of VMRay REST API
        """
        method = "GET"
        url = "/rest/system_info"

        try:
            self.api = VMRayRESTAPI(
                VMRay_CONFIG.BASE_URL,
                VMRay_CONFIG.API_KEY,
                connector_name=VMRay_CONFIG.CONNECTOR_NAME,
            )
            self.api.call(method, url)
            self.log.info("VMRay Healthcheck is successfully.")
            return True
        except VMRayRESTAPIError as verr:
            self.log.error(f"Healthcheck failed due to error in VMRay: {verr.args}")
            raise
        except Exception as err:
            self.log.error(f"Healthcheck failed. Error: {err}")
            raise

    def retry_request(
        self,
        method,
        url,
        vmray_retries=VMRay_CONFIG.RETRIES,
        backoff=VMRay_CONFIG.BACKOFF,
        param=None,
    ):
        """
        Call VMRay API with retry logic for server errors and rate-limiting.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, etc.)
        url : str
            Full API URL to call.
        vmray_retries : int
            Maximum number of retry attempts.
        backoff : int
            Time in seconds between retries.
        param : dict
            Request parameters or data payload.

        Returns
        -------
        dict
            Parsed JSON response from VMRay API.

        Raises
        ------
        Exception
            If all retries fail or a non-retryable error occurs.
        """
        attempt = 0

        while attempt < vmray_retries:
            try:
                response = self.api.call(method, url, params=param)
                return response
            except VMRayRESTAPIError as err:
                status_code = getattr(err, "status_code", None)
                if status_code in RETRY_STATUS_CODE:
                    self.log.warning(
                        f"HTTP {status_code}: {getattr(err, 'message', 'No message')}"
                    )
                    self.log.info(
                        f"Retrying ({attempt + 1}/{vmray_retries}) after {backoff}s..."
                    )
                    sleep(backoff)
                    attempt += 1
                    continue
                self.log.error(f"VMRay error: {err}")
                raise

            except ValueError as verr:
                self.log.error(f"ValueError: {verr}")
                raise

            except Exception as ex:
                self.log.error(f"Unexpected error during VMRay API call: {ex}")
                raise

        self.log.error("Failed to complete VMRay request after multiple retries.")
        raise Exception("VMRay request failed after all retry attempts.")
