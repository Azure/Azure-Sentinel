from os import environ
from vmray.rest_api import VMRayRESTAPI, VMRayRESTAPIError

vmray_api_key = environ["vmrayAPIKey"]
vmray_base_url = environ["vmrayBaseURL"]


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
                vmray_base_url,
                vmray_api_key,
                connector_name="VMRay-MSSentinel",
            )
            self.log.info("Successfully authenticated the VMRay API")
            self.api.call(method, url)
            self.log.info("VMRay Healthcheck is successfully.")
            return True
        except VMRayRESTAPIError as verr:
            self.log.error(f"Healthcheck failed due to error in VMRay: {verr.args}")
            raise
        except Exception as err:
            self.log.error("Healthcheck failed. Error: %s" % (err))
            raise

    def check_id(self, id_to_check: int | str) -> bool:
        """Checks if parameter id_to_check is a number

        Args:
            id_to_check (int or str):

        Returns:
            bool: True if is a number, else returns error
        """
        if (
            isinstance(id_to_check, int)
            or isinstance(id_to_check, str)
            and id_to_check.isdigit()
        ):
            return True
        raise ValueError(f"Invalid ID `{id_to_check}` provided.")

    def request_vmray_api(
        self,
        method,
        url,
        param=None,
    ):
        """
        Retries the given API request in case of server errors or rate-limiting (HTTP 5xx or 429).

        :param method: HTTP method (GET, POST, etc.)
        :param url: URL to make the request to
        :param param: Data to pass with the request (if applicable, e.g., for POST requests)
        :return: Response object from the request or None if it fails after retries
        """
        try:
            response = self.api.call(method, url, params=param)
            return response
        except VMRayRESTAPIError as err:
            self.log.error(f"Error In VMRay: {err.args}")
            raise Exception("An error occurred during retry request") from err
