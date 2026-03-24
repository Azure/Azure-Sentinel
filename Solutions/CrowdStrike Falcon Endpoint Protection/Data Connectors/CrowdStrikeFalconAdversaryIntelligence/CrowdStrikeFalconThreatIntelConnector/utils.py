"""
Utility module for CrowdStrike Falcon Adversary Intelligence Connector.

This module provides essential utility classes and constants for integrating
CrowdStrike Falcon threat intelligence with Microsoft Sentinel. It handles
authentication, state management, data transformation mappings, and error
handling for the Azure Function-based threat intelligence connector.
"""

from datetime import datetime, timedelta, timezone
import logging
import re
import requests
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient

CONFIDENCE_MAPPING = {"high": 85, "medium": 60, "low": 30}

STIX_PATTERN_MAPPING = {
    "hash_md5": "file:hashes.MD5",
    "hash_sha256": "file:hashes.'SHA-256'",
    "hash_sha1": "file:hashes.'SHA-1'",
    "url": "url:value",
    "domain": "domain-name:value",
    "ip_address": "ipv4-addr:value",
    "mutex_name": "mutex:name",
    "password": "user-account:credential",
    "file_name": "file:name",
    "email_address": "email-addr:value",
    "username": "user-account:account_login",
    "persona_name": "user-account:display_name",
    "ip_address_block": "ipv4-addr:value",
    "coin_address": "x-wallet-addr:value",
    "bitcoin_address": "x-wallet-addr:value",
}


class ParseDurationInput:
    """Input struct for parse_duration_to_seconds function."""

    def __init__(self, duration_str):
        """
        Initialize ParseDurationInput.

        Args:
            duration_str: Duration string to parse (e.g., "30m", "2h", "7d")
        """
        self.duration_str = duration_str


def parse_duration_to_seconds(input_params):
    """
    Parse a duration string to seconds.

    Args:
        input_params: ParseDurationInput containing duration_str

    Returns:
        int: Total seconds for the duration

    Raises:
        ValueError: If the format is invalid or unit is not allowed

    Examples:
        parse_duration_to_seconds(ParseDurationInput("30m")) -> 1800
        parse_duration_to_seconds(ParseDurationInput("1h")) -> 3600
        parse_duration_to_seconds(ParseDurationInput("7d")) -> 604800
    """
    duration_str = input_params.duration_str
    if not duration_str:
        raise ValueError("Duration string cannot be empty")

    # Pattern: number followed by unit (m, h, or d)
    pattern = r'^(\d+)(m|h|d)$'
    match = re.match(pattern, duration_str.lower())

    if not match:
        raise ValueError(
            f"Invalid duration format: '{duration_str}'. "
            "Expected format: <number><unit> where unit is 'm' (minutes), "
            "'h' (hours), or 'd' (days). Examples: 30m, 2h, 7d"
        )

    value = int(match.group(1))
    unit = match.group(2)

    # Convert to seconds based on unit
    unit_to_seconds = {
        'm': 60,        # minutes
        'h': 3600,      # hours
        'd': 86400,     # days
    }

    return value * unit_to_seconds[unit]


def get_valid_until(seconds):
    """
    Calculate and return the valid_until timestamp in RFC 3339 format.

    Args:
        seconds: Number of seconds from now

    Returns:
        str: RFC 3339 formatted timestamp (e.g., "2024-01-01T12:30:00Z")

    Examples:
        If seconds=1800 and current time is 2024-01-01T12:00:00Z,
        returns "2024-01-01T12:30:00Z"
    """
    future_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    return future_time.strftime('%Y-%m-%dT%H:%M:%SZ')


class UnauthorizedTokenException(Exception):
    """Exception raised when token authorization fails."""

    def __init__(self, response):
        """
        Initialize UnauthorizedTokenException with logging.

        Args:
            response: HTTP response object from requests library
        """
        super().__init__(response.text)
        logging.error("Unauthorized Error Code: %s", response.status_code)
        logging.error("Unauthorized Error Response: %s", response.text)


class InvalidCredentialsException(Exception):
    """Exception raised when provided credentials are invalid."""

    def __init__(self, response):
        """
        Initialize InvalidCredentialsException with logging.

        Args:
            response: HTTP response object from requests library
        """
        super().__init__(response.text)
        logging.error("Invalid Credentials Error Code: %s", response.status_code)
        logging.error("Invalid Credentials Error Response: %s", response.text)


class APIError(Exception):
    """Exception raised when API calls return error responses."""

    def __init__(self, response):
        """
        Initialize APIError with logging.

        Args:
            response: HTTP response object from requests library
        """
        super().__init__(response.text)
        logging.error("API Error Code: %s", response.status_code)
        logging.error("API Error Response: %s", response.text)


class StateManager:
    """
    Manages persistent state using Azure File Storage to track processing progress.

    This class handles storing and retrieving marker values that indicate the last
    processed position in the CrowdStrike API results, ensuring no data loss
    across function executions.
    """

    def __init__(self, connection_string, share_name, file_path):
        """
        Initialize the StateManager with Azure File Storage configuration.

        Args:
            connection_string: Azure Storage connection string
            share_name: Name of the file share to use
            file_path: Path to the marker file within the share
        """

        self.share_cli = ShareClient.from_connection_string(
            conn_str=connection_string, share_name=share_name
        )
        self.file_cli = ShareFileClient.from_connection_string(
            conn_str=connection_string, share_name=share_name, file_path=file_path
        )

    def post(self, marker_text: str):
        """
        Save the current processing marker to Azure File Storage.

        Args:
            marker_text: The marker value to store
        """
        try:

            self.file_cli.upload_file(marker_text)

        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self):
        """
        Retrieve the last saved processing marker from Azure File Storage.

        Returns:
            str: The last saved marker value, or None if no marker exists
        """

        try:
            logging.info("Looking for marker")
            marker = self.file_cli.download_file().readall().decode()
            logging.info("Marker found '%s'", marker)
            return marker
        except ResourceNotFoundError:
            logging.info("No marker found.")
            return None


class CrowdStrikeTokenRetriever:
    """
    Manages authentication tokens for CrowdStrike Falcon API access.

    This class handles automatic token generation and renewal for CrowdStrike API
    calls, ensuring tokens are refreshed before expiration to maintain
    uninterrupted API access.
    """

    def __init__(
        self, crowdstrike_client_id, crowdstrike_client_secret, crowdstrike_base_url
    ):
        """
        Initialize the CrowdStrike token retriever.

        Args:
            crowdstrike_client_id: Client ID for CrowdStrike authentication
            crowdstrike_client_secret: Client secret for CrowdStrike authentication
            crowdstrike_base_url: Base URL for CrowdStrike API
        """

        self.crowdstrike_base_url = crowdstrike_base_url
        self.crowdstrike_client_id = crowdstrike_client_id
        self.crowdstrike_client_secret = crowdstrike_client_secret
        self.token_exp = datetime.now()
        self.token = self.get_token()

    def get_token(self):
        """
        Retrieve or refresh the CrowdStrike authentication token.

        Automatically generates a new token if the current token is within
        60 seconds of expiring or if no token exists.

        Returns:
            str: Valid CrowdStrike API authentication token

        Raises:
            InvalidCredentialsException: If authentication fails due to invalid credentials
        """

        # if token is within 60 seconds of expiring, generate a new token.
        if (self.token_exp - datetime.now()).total_seconds() < 60:
            response = requests.post(
                f"{self.crowdstrike_base_url}/oauth2/token",
                data={"grant_type": "client_credentials"},
                auth=(self.crowdstrike_client_id, self.crowdstrike_client_secret),
            )

            if response.status_code != 201:
                raise InvalidCredentialsException(response)

            # calculate expiration date
            response_data = response.json()
            self.token_exp = datetime.now() + timedelta(
                seconds=response_data["expires_in"]
            )
            self.token = response_data["access_token"]

        return self.token


class AADTokenRetriever:
    """
    Manages authentication tokens for Azure Active Directory API access.

    This class handles automatic token generation and renewal for Azure services
    including Microsoft Sentinel, ensuring tokens are refreshed before expiration
    to maintain uninterrupted API access.
    """

    def __init__(self, tenant_id, aad_client_id, aad_client_secret):
        """
        Initialize the Azure AD token retriever.

        Args:
            tenant_id: Azure AD tenant identifier
            aad_client_id: Azure AD application client ID
            aad_client_secret: Azure AD application client secret
        """

        self.aad_client_id = aad_client_id
        self.aad_client_secret = aad_client_secret
        self.tenant_id = tenant_id
        self.token_exp = datetime.now()
        self.token = self.get_token()

    def get_token(self):
        """
        Retrieve or refresh the Azure AD authentication token.

        Automatically generates a new token if the current token is within
        60 seconds of expiring or if no token exists.

        Returns:
            str: Valid Azure AD API authentication token

        Raises:
            InvalidCredentialsException: If authentication fails due to invalid credentials
        """

        # if token is within 60 seconds of expiring, generate a new token.
        if (self.token_exp - datetime.now()).total_seconds() < 60:
            url = (
                f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            )
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.aad_client_id,
                "client_secret": self.aad_client_secret,
                "scope": "https://management.azure.com/.default",
            }
            response = requests.post(url=url, data=payload)

            if response.status_code != 200:
                raise InvalidCredentialsException(response)

            # calculate expiration date
            response_data = response.json()
            self.token_exp = datetime.now() + timedelta(
                seconds=response_data["expires_in"]
            )
            self.token = response_data["access_token"]

        return self.token
