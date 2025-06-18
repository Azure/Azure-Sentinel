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
DCR_IMMUTABLE_ID = "dcr-6b87c97982ec42f38880b4bf43d1ba12"
TABLE_NAME = "BloodHoundPostureStats_CL"

ENDPOINTS = {
    "test_connection": "/api/v2/available-domains",
    "posture_stats": "/api/v2/posture-stats",
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
            # Construct URL and URI path
            url = self._get_full_url(endpoint_key, **kwargs)
            uri_path = ENDPOINTS[endpoint_key].format(**kwargs)

            # Prepare headers
            headers = self._get_headers(method, uri_path)

            if headers is None:
                self._log_error("Failed to generate headers")
                return None

            # Extract query params and payload
            params = kwargs.get("params", None)
            data = kwargs.get("data", None)

            # Make the request
            response = requests.request(
                method, url, headers=headers, params=params, data=data
            )

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

    def get_posture_stats(self, domain_id):
        """
        Fetches posture statistics from the BloodHound Enterprise API.

        Args:
            domain_id (str): The ID of the domain for which to fetch posture statistics.
        Returns:
            dict: Posture statistics for the specified domain, or None if an error occurs.
        """
        try:
            return self._api_request(
                "posture_stats",
                domain_id=domain_id,
            )
        except Exception as e:
            self._log_error(f"Error fetching attack path details for {domain_id}: {e}")
            return None

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

    def send_posture_stat_data(
        self,
        data,
        bearer_token,
        dce_uri,
        dcr_immutable_id,
        table_name,
        tenant_domain="",
    ):
        """
        Sends attack data to Azure Monitor via Data Collection Endpoint (DCE),
        using the schema format specified for BloodHoundAttackPaths_CL table.
        """
        print(f"Sending data to DCE: {tenant_domain}")

        log_entry = {
            "created_at": data.get("created_at", ""),
            "critical_risk_count": int(data.get("critical_risk_count", 0)),
            "deleted_at": data.get("deleted_at", {}),
            "domain_name": data.get("domain_name", ""),
            "domain_sid": data.get("domain_sid", ""),
            "exposure_index": str(data.get("exposure_index", "")),
            "id": int(data.get("id", 0)),
            "tier_zero_count": int(data.get("tier_zero_count", 0)),
            "updated_at": data.get("updated_at", ""),
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
        print(f"Found {domains_data} domains")

        filtered_domains = [
            domain for domain in domains_data if domain.get("collected") == True
        ]

        if not filtered_domains:
            print("No collected domains found. Exiting.")
            return
        print(f"Collected Domains:{filtered_domains}")

        consolidated_posture_data = []

        for domain in filtered_domains:
            print(f"Processing domain: {domain.get('name')}")
            domain_id = domain.get("id")
            domain_name = domain.get("name")

            # Fetch posture stats for the domain
            posture_stats = bloodhound_manager.get_posture_stats(domain_id)

            posture_stats_data = posture_stats.get("data", {})

            for data in posture_stats_data:
                # Add domain name to each posture stats entry
                data["domain_name"] = domain_name

            # Consolidate posture stats data
            consolidated_posture_data.append(posture_stats_data)
            # print(f"Consolidated posture stats for {domain_name}: {consolidated_posture_data}")

        print(f"Consolidated posture stats for all domains:{consolidated_posture_data}")
        flattened_posture_data = [
            consolidated_posture_data
            for sublist in consolidated_posture_data
            for consolidated_posture_data in sublist
        ]
        # Add available_types field to each domain

        print(f"Flattened posture stats data: {flattened_posture_data}")

        # Now send the attack data to Data Collection Endpoint (DCE)

        token = bloodhound_manager.get_bearer_token(TENANT_ID, APP_ID, APP_SECRET)
        if not token:
            print("Failed to obtain Bearer token. Exiting.")
            return
        print("Bearer token obtained successfully.")
        results = []

        # Iterate through the flattened attack paths and send each one to the DCE

        for i, data in enumerate(flattened_posture_data, 1):
            print(
                f"Sending attack data {i}/{len(flattened_posture_data)}: ID {data.get('id')}"
            )
            try:
                res = bloodhound_manager.send_posture_stat_data(
                    data, token, DCE_URI, DCR_IMMUTABLE_ID, TABLE_NAME, tenant_domain
                )
                results.append(
                    {"id": data.get("id"), "status": "success", "response": res}
                )
            except Exception as e:
                results.append(
                    {"id": data.get("id"), "status": "error", "message": str(e)}
                )
            time.sleep(0.1)  # Avoid rate limiting

        print("results:", results)
        print("All attack data sent to DCE successfully.")

    else:
        print("Connection test failed - check logs for details")


if __name__ == "__main__":
    main()
