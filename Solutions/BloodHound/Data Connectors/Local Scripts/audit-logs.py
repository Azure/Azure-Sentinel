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
TENANT_ID = os.getenv("TENANT_ID")
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# Azure Monitor configuration
DCE_URI = (
    "https://dce-bloodhound-attackpaths-krhl.centralindia-1.ingest.monitor.azure.com"
)
DCR_IMMUTABLE_ID = "dcr-6b87c97982ec42f38880b4bf43d1ba12"
TABLE_NAME = "BloodHoundAuditLogs_CL"

ENDPOINTS = {
    "test_connection": "/api/v2/available-domains",
    "audit_logs": "/api/v2/audit",
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
                query_string = "&".join(f"{k}={v}" for k, v in params.items())
                uri_path = f"{uri_path}?{query_string}"

            # Prepare headers with correct uri_path
            headers = self._get_headers(method, uri_path)
            if headers is None:
                self._log_error("Failed to generate headers")
                return None

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

    def convert_to_rfc(self, days: int) -> str:
        """
        Returns the RFC-3339 UTC timestamp for 'days' ago from now.

        Args:
            days (int): Number of days in the past from now.

        Returns:
            str: Timestamp in RFC-3339 format (e.g., '2023-06-02T14:00:00Z')
        """
        target_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            days=days
        )
        return target_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_audit_logs(self, start_date=None, end_date=None, limit=1000):
        """
        Fetches audit logs from the BloodHound Enterprise API.

        Args:
            start_date (str): Start date for filtering logs in ISO format (optional).
            end_date (str): End date for filtering logs in ISO format (optional).
            limit (int): Maximum number of logs to retrieve (default is 100).

        Returns:
            list: List of audit log entries.
        """
        params = {
            # "after": start_date if start_date else self.convert_to_rfc(365),  # Default to 365 days ago
            # "before": end_date if end_date else self.convert_to_rfc(0),  # Default to now
            "skip": 0,  # Starting point for pagination
            "limit": limit,
        }
        return self._api_request("audit_logs", params=params)

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

    def send_audit_logs_data(
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
        log_entry = {
            "action": data.get("action", ""),
            "actor_email": data.get("actor_email", ""),
            "actor_id": data.get("actor_id", ""),
            "actor_name": data.get("actor_name", ""),
            "commit_id": data.get("commit_id", ""),
            "created_at": data.get("created_at", ""),
            "fields": data.get("fields", {}),
            "id": int(data.get("id", 0)),
            "request_id": data.get("request_id", ""),
            "source_ip_address": data.get("source_ip_address", ""),
            "status": data.get("status", ""),
            "tenant_url": tenant_domain,
        }

        print(f"Sending log entry: {log_entry}")

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

        domains_data = [
            domain for domain in domains_data if domain.get("collected") == True
        ]

        audit_logs_response = bloodhound_manager.get_audit_logs(limit=50)

        print("Audit logs response:", audit_logs_response)

        audit_logs_data = audit_logs_response.get("data", [])

        audit_logs = audit_logs_data.get("logs", [])

        print(f"audit logs {audit_logs}")

        # Now send the attack data to Data Collection Endpoint (DCE)

        token = bloodhound_manager.get_bearer_token(TENANT_ID, APP_ID, APP_SECRET)
        if not token:
            print("Failed to obtain Bearer token. Exiting.")
            return
        print("Bearer token obtained successfully.")
        results = []

        # Iterate through the flattened attack paths and send each one to the DCE

        for i, data in enumerate(audit_logs, 1):
            print(f"Sending attack data {i}/{len(audit_logs)}: ID {data.get('id')}")
            try:
                res = bloodhound_manager.send_audit_logs_data(
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
