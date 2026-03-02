from io import BytesIO
from os import environ
from jbxapi import ConnectionError, InvalidApiKeyError, InvalidParameterError
from jbxapi import JoeSandbox as JoeAPI
from jbxapi import PermissionError, ServerOfflineError

joe_sandbox_api_key = environ["JoeSandboxAPIKey"]
joe_sandbox_base_url = environ["JoeSandboxBaseURL"]


class JoeSandbox:
    """
    Wrapper class for JoeSandboxRESTAPI modules and functions.
    Import this class to submit samples and retrieve reports.
    """

    def __init__(self, log):
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
                apiurl=f"{joe_sandbox_base_url}/api",
                apikey=joe_sandbox_api_key,
                verify_ssl=True,
                user_agent="JoeSandboxMSSentinel",
                accept_tac=True,
                retries=5,
                timeout=600,
            )
            self.api.server_online()
            self.log.info(
                "Successfully authenticated and verified JoeSandbox API",
            )
        except InvalidApiKeyError as inerr:
            self.log.error("Invalid API key for JoeSandbox: %s", inerr)
            raise
        except PermissionError as perr:
            self.log.error("The user does not have the required permissions: %s", perr)
            raise
        except ConnectionError as cerr:
            self.log.error("Failed to connect to JoeSandbox server: %s", cerr)
            raise
        except ServerOfflineError as serr:
            self.log.error("Joe Sandbox is offline: %s", serr)
            raise
        except Exception as err:
            self.log.error("Unexpected error during JoeSandbox authentication: %s", err)
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

    def get_analysis(self, query: str) -> list | None:
        """
        Fetch the analysis associated based on a given query (hash or url) from JoeSandbox.

        Args:
            query (str): The SHA-256 hash of the file or url for which the analysis
            is being requested.

        Returns:
            list or None: A list of analysis metadata matching the hash value, or None
            if no analysis is available or the operation fails.
        """
        try:
            response = self.api.analysis_search(query)
            if response:
                self.log.info("Analysis for %s retrieved from JoeSandbox", query)
                return response
        except InvalidParameterError as inperr:
            self.log.error("An API parameter is invalid.. Error: %s", inperr)
        except ConnectionError as cerr:
            self.log.error("Failed to connect to JoeSandbox server.. Error: %s", cerr)
        except Exception as err:
            self.log.error(
                "Unexpected error while retrieving analysis for %s: %s", query, err
            )

        return None

    def download_analysis(self, web_id: str, download_type: str) -> tuple | None:
        """
        Download the analysis associated with web id from JoeSandbox.

        Args:
            web_id (str): web id of analysis
            download_type: the report type, e.g. 'html', 'bins', irjsonfixed

        Returns:
            list or None: A list of analysis metadata matching the hash value, or None
            if no analysis is available or the operation fails.
        """
        try:
            response = self.api.analysis_download(web_id, type=download_type)
            if response:
                self.log.info("Analysis for %s retrieved from JoeSandbox", web_id)
                return response
        except InvalidParameterError as inperr:
            self.log.error("An API parameter is invalid.. Error: %s", inperr)
        except ConnectionError as cerr:
            self.log.error("Failed to connect to JoeSandbox server.. Error: %s", cerr)
        except Exception as err:
            self.log.error(
                "Unexpected error while retrieving analysis for %s: %s", web_id, err
            )

        return None

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
                self.log.info("Analysis retrieved from JoeSandbox")
                return response
        except InvalidParameterError as inperr:
            self.log.error("An API parameter is invalid... Error: %s", inperr)
        except ConnectionError as cerr:
            self.log.error(
                "Failed to connect to JoeSandbox server while fetching analysis info.. Error: %s",
                cerr,
            )
        except Exception as err:
            self.log.error("Unexpected error while retrieving analysis: %s", err)

        return None

    def submit_files_to_joesandbox(
        self, file: BytesIO, params: dict
    ) -> dict|None:
        """
        Function to submit file to JoeSandbox.

        Args:
           file: File object to submit JoeSandbox
           params: Dict of params
        Returns:
            list: A list of dictionaries containing submission details.
        """
        try:
            response = self.api.submit_sample(sample=file, params=params)
            return response
        except PermissionError as perr:
            self.log.error("Insufficient permissions for this API key: %s", perr)
        except InvalidParameterError as inperr:
            self.log.error("Invalid parameter in submission: %s", inperr)
        except ConnectionError as cerr:
            self.log.error("Connection to JoeSandbox failed: %s", cerr)
        except Exception as err:
            self.log.error("Unexpected error during submission: %s", err)

        return None

    def get_submission(self, submission_id) -> dict|None:
        """
        Get submission details using submission id
        Args:
            submission_id: submission id
        Returns:
            Dict: Submission information
        """
        try:
            response = self.api.submission_info(submission_id)
            return response
        except InvalidParameterError as inperr:
            self.log.error("An API parameter is invalid... Error: %s", inperr)
        except ConnectionError as cerr:
            self.log.error(
                "Failed to connect to JoeSandbox server while fetching submission info.. Error: %s",
                cerr,
            )
        except Exception as err:
            self.log.error("Unexpected error while retrieving submission details: %s", err)

        return None


    def submit_url(self, url: str, params: dict) -> dict|None:
        """
        Function to submit urls to JoeSandbox from AV or EDR alerts.

        Args:
            url: Url to submit.
            params: parameters.

        Returns:
            list: A list of dictionaries containing submission details.
        """
        try:
            response = self.api.submit_url(url=url, params=params)
            return response
        except PermissionError as perr:
            self.log.error(
                "Insufficient permissions for this API key to submit urls: %s",
                perr,
            )
        except InvalidParameterError as inperr:
            self.log.error(
                "An API parameter is invalid under url submission. Error: %s",
                inperr,
            )
        except ConnectionError as cerr:
            self.log.error(
                "Failed to connect to JoeSandbox server while submitting urls. Error: %s",
                cerr,
            )
        except Exception as err:
            self.log.error(err)
        return None
