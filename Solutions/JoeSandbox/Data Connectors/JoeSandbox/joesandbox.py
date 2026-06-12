"""
JoeSandbox Helper Class
"""

from jbxapi import ConnectionError as JoeConnErr
from jbxapi import InvalidApiKeyError, InvalidParameterError
from jbxapi import JoeSandbox as JoeAPI
from jbxapi import PermissionError as JoePermErr
from jbxapi import ServerOfflineError
from requests import ConnectionError as HttpConnErr
from requests import HTTPError, RequestException, post

from .const import joe_config


class JoeSandbox:
    """
    Wrapper class for JoeSandboxRESTAPI modules and functions.
    Import this class to submit samples and retrieve reports.from_time
    """

    def __init__(self, log: any):
        """
        Initialize, authenticate the JoeSandbox instance,
        use JoeSandboxConfig as configuration
        :param log: logger instance
        :return void
        """
        self.api = None
        self.log = log

        self.authenticate()

    def authenticate(self):
        """
        Authenticate and verify the JoeSandbox REST API connection.
        :raises: Various exceptions if connection or config is invalid.
        """
        try:
            self.api = JoeAPI(
                apiurl=joe_config.API_URL,
                apikey=joe_config.API_KEY,
                verify_ssl=True,
                user_agent=joe_config.CONNECTOR_NAME,
                accept_tac=True,
                retries=joe_config.RETRIES,
            )
            self.api.server_online()
            self.log.info(
                "Successfully authenticated and verified JoeSandbox API",
            )
        except InvalidApiKeyError as inerr:
            self.log.error("Invalid API key for JoeSandbox: %s", inerr)
            raise
        except JoePermErr as perr:
            self.log.error("The user does not have the required permissions: %s", perr)
            raise
        except JoeConnErr as cerr:
            self.log.error("Failed to connect to JoeSandbox server: %s", cerr)
            raise
        except ServerOfflineError as serr:
            self.log.error("Joe Sandbox is offline: %s", serr)
            raise
        except Exception as err:
            self.log.error("Unexpected error during JoeSandbox authentication: %s", err)
            raise

    def download_analysis(self, web_id: str, download_type: str) -> tuple:
        """
        Download the analysis associated with web id from JoeSandbox.

        Args:
            web_id (str): web id of analysis
            download_type: the report type, e.g. 'html', 'bins', irjsonfixed

        Returns:
            listJoe_Config or None: A list of analysis metadata matching the hash value, or None
            if no analysis is available or the operation fails.
        """
        try:
            response = self.api.analysis_download(web_id, type=download_type)
            if response:
                return response
        except InvalidParameterError as inperr:
            self.log.error("An API parameter is invalid.. Error: %s", inperr)
        except JoeConnErr as cerr:
            self.log.error("Failed to connect to JoeSandbox server.. Error: %s", cerr)
        except Exception as err:
            self.log.error(
                "Unexpected error while retrieving analysis for %s: %s", web_id, err
            )

        return "", {}

    def get_analysis_info(self, web_id: str) -> dict | None:
        """
        Fetch the analysis associated with a particular web_id from JoeSandbox.

        Args:
            web_id (str): The web id of the analysis.
        Returns:
            dict or None: A dictionary containing the analysis result if found, or None
            if no analysis is available or the operation fails.
        """
        try:
            response = self.api.analysis_info(web_id)
            if response:
                return response
        except InvalidParameterError as inperr:
            self.log.error("An API parameter is invalid... Error: %s", inperr)
        except JoeConnErr as cerr:
            self.log.error(
                "Failed to connect to JoeSandbox server while fetching analysis info.. Error: %s",
                cerr,
            )
        except Exception as err:
            self.log.error("Unexpected error while retrieving analysis: %s", err)

        return None

    def get_analysis_list(self, initial_fetch: str, detections: list):
        """
        Fetches a list of analyses from JoeSandbox filtered by detection type and after-date.

        Args:
            initial_fetch (str): The date string (e.g. "2024-01-01") to filter results after.
            detections (list): List of detection types (e.g. ["malicious", "suspicious"]).

        Returns:
            list: A list of analysis entries, or None in case of failure.
        """
        analysis_list = []

        for detection in detections:
            pagination_next = None

            while True:
                try:
                    payload = {
                        "apikey": joe_config.API_KEY,
                        "pagination": "1",
                        "after-date": initial_fetch,
                        "detection": detection.lower(),
                    }

                    if pagination_next:
                        payload["pagination_next"] = pagination_next

                    response = post(
                        url=f"{joe_config.API_URL}/v2/analysis/list",
                        data=payload,
                        timeout=joe_config.TIMEOUT,
                    )
                    if response:
                        response.raise_for_status()
                        data = response.json()

                        analysis_list.extend(data.get("data", []))

                        pagination_next = data.get("pagination", {}).get("next")
                        if not pagination_next:
                            break

                except HTTPError as http_err:
                    try:
                        if http_err.response:
                            error_msg = (
                                http_err.response.json()
                                .get("errors", [{}])[0]
                                .get("message", "Unknown HTTP error")
                            )
                            self.log.error(
                                f"HTTP error while fetching analysis list: {error_msg}"
                            )
                    except Exception:
                        error_msg = str(http_err)
                        self.log.error(
                            f"HTTP error while fetching analysis list: {error_msg}"
                        )
                    return None

                except HttpConnErr as conn_err:
                    self.log.error(
                        f"Connection error during analysis list fetch: {conn_err}"
                    )
                    return None

                except RequestException as req_err:
                    self.log.error(
                        f"Request error during analysis list fetch: {req_err}"
                    )
                    return None

                except Exception as err:
                    self.log.error(
                        f"Unexpected error during analysis list fetch: {err}"
                    )
                    return None

        return analysis_list
