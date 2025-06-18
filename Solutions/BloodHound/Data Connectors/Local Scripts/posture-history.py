import requests
import hmac
import hashlib
import base64
from urllib.parse import urljoin
from urllib.parse import urlparse
import datetime

import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# from datetime import datetime, timezone

# Azure AD authentication configuration
TENANT_ID = os.getenv("TENANT_ID")
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# Azure Monitor configuration
DCE_URI = (
    "https://dce-bloodhound-attackpaths-krhl.centralindia-1.ingest.monitor.azure.com"
)
DCR_IMMUTABLE_ID = "dcr-698fbb9e80c6483e804bc52d1174a626"
TABLE_NAME = "BloodHoundPostureHistory_CL"

ENDPOINTS = {
    "test_connection": "/api/v2/available-domains",
    "available_domain": "/api/v2/available-domains",
    "finding_trends": "/api/v2/attack-paths/finding-trends",
    "posture_history": "/api/v2/posture-history/{data_type}",
}


class BloodhoundManager:
    def __init__(self, tenant_domain, token_id, token_key, logger=None):
        """
        Initializes the BloodhoundManager with tenant credentials and optional logger.

        Args:
            tenant_domain (str): The base URL/domain of the BloodHound Enterprise instance.
            token_id (str): The token ID used for authentication.
            token_key (str): The token secret key used to generate HMAC signatures.
            logger (logging.Logger, optional): Logger instance for logging errors and info.
        """
        self.tenant_domain = tenant_domain
        self.__token_id = token_id
        self.__token_key = token_key
        self.logger = logger

    def _get_full_url(self, url_key, **kwargs) -> str:
        """Construct full URL from endpoint key and parameters"""
        return urljoin(self.tenant_domain, ENDPOINTS[url_key].format(**kwargs))

    def _get_headers(self, method: str, uri: str) -> dict:
        """Generate authentication headers for API requests"""
        try:
            digester = hmac.new(self.__token_key.encode(), None, hashlib.sha256)
            digester.update(f"{method}{uri}".encode())
            digester = hmac.new(digester.digest(), None, hashlib.sha256)
            datetime_formatted = datetime.datetime.now().astimezone().isoformat("T")
            digester.update(datetime_formatted[:13].encode())
            digester = hmac.new(digester.digest(), None, hashlib.sha256)

            headers = {
                "User-Agent": f"BloodHound Enterprise - Google SecOps Integration",
                "Authorization": f"bhesignature {self.__token_id}",
                "RequestDate": datetime_formatted,
                "Signature": base64.b64encode(digester.digest()).decode(),
                "Content-Type": "application/json",
            }

            return headers
        except Exception as e:
            error_msg: str = f"Error generating headers: {e}"
            self._log_error(error_msg)
            return None

    def _validate_response(self, response, error_msg="An error occurred"):
        """
        Validates the HTTP response and logs errors if any
        """
        try:
            response.raise_for_status()
            return True
        except requests.HTTPError as error:
            self._log_error(
                f"{error_msg}: {error} - Status Code: {response.status_code}"
            )
            return False

    def _api_request(
        self, endpoint_key: str, return_json=True, method: str = "GET", **kwargs
    ):
        """
        Centralized function to handle API requests and error handling
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint_key: Key in ENDPOINTS dictionary
            return_json: Whether to return JSON response or raw response
            **kwargs: Includes format params, query params, post body, etc.
        Returns:
            Response data or None if request fails
        """
        try:
            # Extract query params and payload
            params = kwargs.get("params", None)
            data = kwargs.get("data", None)

            # Construct full URL
            url = self._get_full_url(endpoint_key, **kwargs)
            parsed_url = urlparse(url)

            # Build uri_path for HMAC — MUST match the request
            uri_path = parsed_url.path
            if params:
                # Handle multiple values for the same parameter (like environments)
                query_parts = []
                for k, v in params.items():
                    if isinstance(v, list):
                        # For multiple values of same key, add each as separate parameter
                        for val in v:
                            query_parts.append(f"{k}={val}")
                    else:
                        query_parts.append(f"{k}={v}")
                query_string = "&".join(query_parts)
                uri_path = f"{uri_path}?{query_string}"

            # Prepare headers with correct uri_path
            headers = self._get_headers(method, uri_path)
            if headers is None:
                self._log_error("Failed to generate headers")
                return None

            # Make the request
            print(
                f"Making {method} request to {url} with headers: {headers} and params: {params} and data: {data}"
            )
            response = requests.request(
                method, url, headers=headers, params=params, data=data
            )
            print(f"Response status code: {response.status_code}")

            if not self._validate_response(
                response, f"API request to {endpoint_key} failed"
            ):
                return None

            return response.json() if return_json else response

        except Exception as e:
            self._log_error(f"Exception in _api_request: {e}")
            return None

    def test_connection(self):
        """
        Tests the connection to the BloodHound Enterprise API.

        Returns:
            Response object: Raw HTTP response from the test connection endpoint.
        """
        return self._api_request("test_connection", return_json=False)

    def get_finding_trends(self, environment_ids=None):
        """
        Fetches finding trends from the BloodHound Enterprise API.
        This matches the URL: /api/v2/attack-paths/finding-trends?environments=ID1&environments=ID2

        Args:
            environment_ids (list, optional): List of environment IDs to filter trends.
                                            Each ID will be added as a separate 'environments' parameter.

        Returns:
            dict: JSON response containing finding trends or None if request fails.
        """
        params = {}
        if environment_ids:
            # Create multiple 'environments' parameters - one for each ID
            params["environments"] = environment_ids

        return self._api_request("finding_trends", params=params)

    def get_posture_history(self, data_type, environment_ids=None):
        """
        Fetches posture history data from the BloodHound Enterprise API for a specific data_type.
        This matches the URL: /api/v2/posture-history/{data_type}?environments=ID1&environments=ID2

        Args:
            data_type (str): Type of data to fetch (e.g., 'findings', 'risks', 'exposures', 'assets').
            environment_ids (list, optional): List of environment IDs to filter data.
                                            Each ID will be added as a separate 'environments' parameter.

        Returns:
            dict: JSON response containing posture history data or None if request fails.
        """
        params = {}
        if environment_ids:
            # Create multiple 'environments' parameters - one for each ID
            params["environments"] = environment_ids

        return self._api_request("posture_history", params=params, data_type=data_type)

    def _log_error(self, message):
        """ "
        Logs the provided error message using the logger if available, else prints it.

        Args:
            message (str): Error message to be logged or printed.
        """
        if self.logger:
            self.logger.error(message)
        else:
            print(f"[ERROR] {message}")

    # methods for posting the data to our Data Collection Endpoint (DCE)

    def get_bearer_token(self, tenant_id, app_id, app_secret):
        """
        Fetches a Bearer token for Azure Monitor API using client credentials.
        """
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = f"client_id={app_id}&scope=https%3A%2F%2Fmonitor.azure.com%2F%2F.default&client_secret={app_secret}&grant_type=client_credentials"

        try:
            response = requests.post(token_url, headers=headers, data=body)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.RequestException as e:
            self._log_error(f"[Token Error] {e}")
            return None

    def send_finding_trends_logs(
        self,
        data,
        bearer_token,
        dce_uri,
        dcr_immutable_id,
        table_name,
        tenant_domain="",
        domains_data=None,
    ):
        """
        Sends attack data to Azure Monitor via Data Collection Endpoint (DCE),
        using the schema format specified for BloodHoundAttackPaths_CL table.
        """

        domain_id = data.get("domain_id", "")

        domain_name = (
            next(
                (
                    domain["name"]
                    for domain in domains_data
                    if domain.get("id") == domain_id
                ),
                None,
            )
            if domains_data
            else None
        )

        print(f"Domain Name: {domain_name}, Environment ID: {domain_id}")

        log_entry = {
            "metric_date": data.get("date", ""),
            "value": int(data.get("value", 0)),
            "start_time": data.get("start_date", ""),
            "end_time": data.get("end_date", ""),
            "domain_id": data.get("domain_id", ""),
            "data_type": data.get("type", ""),
            "domain_name": domain_name,
            "tenant_url": tenant_domain,
        }

        api_url = f"{dce_uri}/dataCollectionRules/{dcr_immutable_id}/streams/Custom-{table_name}?api-version=2023-01-01"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                api_url, headers=headers, data=json.dumps([log_entry])
            )
            response.raise_for_status()
            return response.json() if response.content else {"status": "success"}
        except requests.RequestException as e:
            self._log_error(f"[Send Error] {e}")
            return {"status": "error", "message": str(e)}


def main():
    print("This script is designed to fetch attack paths in a system.")

    # Your credentials
    token_id = os.getenv("MAPLESYRUP_TOKEN_ID")
    token_key = os.getenv("MAPLESYRUP_TOKEN_KEY")
    tenant_domain = os.getenv("MAPLESYRUP_URL")

    # token_id = os.getenv("DEMO_TOKEN_ID")
    # token_key = os.getenv("DEMO_TOKEN_KEY")
    # tenant_domain = os.getenv("DEMO_TENANT_DOMAIN")

    # Create an instance of BloodhoundManager class
    bloodhound_manager = BloodhoundManager(tenant_domain, token_id, token_key)

    # Test the connection
    response = bloodhound_manager.test_connection()
    if response:
        print("Connection test successful!")
        res_domains = response.json()
        domains_data = res_domains.get("data", [])
        print(f"Found {len(domains_data)} domains")
        print(f"domains_data is {domains_data}")

        domains_data = [
            domain for domain in domains_data if domain.get("collected") == True
        ]

        environment_ids = []
        for domain in domains_data:
            if isinstance(domain, dict) and domain.get("id"):
                environment_ids.append(domain["id"])
            elif isinstance(domain, str):
                environment_ids.append(domain)

        print(f"Environment IDs: {environment_ids}")

        if environment_ids:
            data_types = ["findings", "exposure", "assets"]
            all_collected_data = []

            for env_id in environment_ids:
                print(f"\n--- Processing Environment ID: {env_id} ---")
                for data_type in data_types:
                    print(f"Fetching {data_type} for environment ID: {env_id}")
                    # Call get_posture_history with a single environment_id
                    posture_history_response = bloodhound_manager.get_posture_history(
                        data_type, environment_ids=[env_id]
                    )

                    if posture_history_response and "data" in posture_history_response:

                        type_specific_data = []

                        if len(posture_history_response["data"]) >= 3:
                            first_element = posture_history_response["data"][0]
                            middlle_element = posture_history_response["data"][
                                len(posture_history_response["data"]) // 2
                            ]
                            last_element = posture_history_response["data"][-1]
                            type_specific_data = [
                                first_element,
                                middlle_element,
                                last_element,
                            ]

                        # type_specific_data = posture_history_response.get("data", [])
                        for data in type_specific_data:
                            data["start_date"] = posture_history_response.get(
                                "start", ""
                            )
                            data["end_date"] = posture_history_response.get("end", "")
                            data["domain_id"] = posture_history_response.get(
                                "environments", []
                            )[0]

                        print(
                            f"Found {len(type_specific_data)} {data_type} entries for environment ID {env_id}"
                        )

                        # Add the 'type' field to each event
                        for item in type_specific_data:
                            item["type"] = data_type
                        all_collected_data.extend(type_specific_data)
                    else:
                        print(
                            f"No {data_type} data found or an error occurred for environment ID {env_id}."
                        )

            print("\n--- Consolidated Data ---")
            print(
                f"Total collected data points across all types and environments: {len(all_collected_data)}"
            )
            print(f"data is {all_collected_data}")

            print(
                json.dumps(all_collected_data, indent=2)
            )  # Uncomment to see the consolidated data

            # Example of how you might proceed with sending to Azure Monitor
            if all_collected_data:
                token = bloodhound_manager.get_bearer_token(
                    TENANT_ID, APP_ID, APP_SECRET
                )
                if not token:
                    print("Failed to obtain Bearer token. Exiting.")
                    return

                print(
                    "Bearer token obtained successfully. Sending consolidated data to DCE."
                )
                for i, data_item in enumerate(all_collected_data):
                    # You might need to adapt the send_finding_trends_logs function
                    # to handle the consolidated data structure, or create a new one.
                    # For demonstration, let's assume send_finding_trends_logs can take a single item.
                    # Note: The current send_finding_trends_logs uses 'environment_ids' and 'domains_data'
                    # which might need to be adjusted based on the consolidated item's structure.
                    print(f"Sending item {i+1}/{len(all_collected_data)}")
                    res = bloodhound_manager.send_finding_trends_logs(
                        data_item,
                        token,
                        DCE_URI,
                        DCR_IMMUTABLE_ID,
                        TABLE_NAME,
                        tenant_domain,
                        domains_data,
                    )
                    print(f"Send result: {res}")
                    time.sleep(0.1)  # Avoid rate limiting
                print("All consolidated data sent to DCE successfully.")
        else:
            print("No environment IDs found to query posture history.")
    else:
        print("Connection test failed - check logs for details.")


if __name__ == "__main__":
    main()
