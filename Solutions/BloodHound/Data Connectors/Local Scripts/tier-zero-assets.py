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

ENDPOINTS = {
    "test_connection": "/api/v2/available-domains",
    "available_domain": "/api/v2/available-domains",
    "cypher": "/api/v2/graphs/cypher",
}

# Azure AD authentication configuration
TENANT_ID = os.getenv("TENANT_ID")
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# Azure Monitor configuration
DCE_URI = (
    "https://dce-bloodhound-attackpaths-krhl.centralindia-1.ingest.monitor.azure.com"
)
DCR_IMMUTABLE_ID = "dcr-4d013aa9faa64537909486976870b9d1"
TABLE_NAME = "BloodHoundTierZeroAssetsData_CL"


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

    def _get_headers(self, method: str, uri: str, body: str = "") -> dict:
        try:
            # Start with first hash: method + uri ******** NOTE: Don't include body here **********
            digester = hmac.new(self.__token_key.encode(), None, hashlib.sha256)
            digester.update(f"{method}{uri}".encode())  # body removed
            digester = hmac.new(digester.digest(), None, hashlib.sha256)

            # Second hash: add hour-based timestamp
            datetime_formatted = datetime.datetime.now().astimezone().isoformat("T")
            digester.update(datetime_formatted[:13].encode())
            digester = hmac.new(digester.digest(), None, hashlib.sha256)

            # Process body if it exists separately
            if body:
                digester.update(body.encode())

            signature = base64.b64encode(digester.digest()).decode()

            headers = {
                "User-Agent": "BloodHound Enterprise",
                "Authorization": f"bhesignature {self.__token_id}",
                # 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDkxNTA2NzQsImp0aSI6Ijk1MyIsImlhdCI6MTc0OTEyMTg3NCwic3ViIjoiODc3NWE2ZDUtOWY3Ni00ZDg5LThkZDctYWI5ZDZkNzI4OTdhIn0.e4nf5sWdOGKX9YRtX-fZghh6zErugzkKG6parhpY7Gk',
                "RequestDate": datetime_formatted,
                "Signature": signature,
                "Content-Type": "application/json",
            }

            return headers
        except Exception as e:
            self._log_error(f"Error generating headers: {e}")
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
            uri_path = parsed_url.path

            # Add query string if any
            if params:
                query_string = "&".join(f"{k}={v}" for k, v in params.items())
                uri_path = f"{uri_path}?{query_string}"
            print(uri_path)
            # For POST method, ensure data is a string and included in HMAC
            body = data if method == "POST" and data else ""
            headers = self._get_headers(method, uri_path, body)

            if headers is None:
                self._log_error("Failed to generate headers")
                return None

            print(
                f"Making {method} request to {url} with headers: {headers} and params: {params}"
            )

            # Make the request
            response = requests.request(method, url, headers=headers, data=data)
            print(response.json())
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

    def fetch_tier_zero_assets(self):
        """
        Posts a Cypher query to the BloodHound Enterprise API using the correct endpoint.

        Args:
            query (str): The Cypher query to be executed.
            include_properties (bool): Whether to include node properties in the response.

        Returns:
            dict: JSON response from the API or None if request fails.
        """
        cypher_query = "match (n) where (n:Tag_Tier_Zero) or coalesce(n.system_tags,'''''') contains('''admin_tier_0''') return n"

        # Prepare the payload matching the curl example
        payload = json.dumps(
            {
                "query": "match (n) where (n:Tag_Tier_Zero) or coalesce(n.system_tags,'') contains('admin_tier_0') return n",
                "include_properties": True,
            }
        )

        return self._api_request("cypher", method="POST", data=payload)

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

    def send_tier_zero_assets_data(
        self,
        data,
        bearer_token,
        dce_uri,
        dcr_immutable_id,
        table_name,
        tenant_url="",
        domains_data=None,
    ):
        """
        Sends attack data to Azure Monitor via Data Collection Endpoint (DCE),
        using the schema format specified for BloodHoundAttackPaths_CL table.
        """

        log_entry = {
            "nodeId": data.get("nodeId", ""),
            "label": data.get("label", ""),
            "kindType": data.get("kind", ""),
            "objectId": data.get(
                "objectId", data.get("properties", {}).get("owner_objectid", "")
            ),
            "isTierZero": data.get("isTierZero", False),
            "isOwnedObject": data.get("isOwnedObject", False),
            "lastSeen": data.get("lastSeen", ""),
            "tenant_url": tenant_url,
            "properties": data.get("properties", {}),
            "domain_name": data.get("domain_name", ""),
            "name": data.get("name", ""),
        }

        for field_name, field_value in data.get("properties", {}).items():
            if field_name == "date":
                log_entry["Date"] = field_value
            elif field_name == "title":
                log_entry["Title"] = field_value
            else:
                log_entry[field_name] = field_value

        if log_entry.get("owner_objectid"):
            print(f"Owner objectId: {log_entry['owner_objectid']}")

        if log_entry.get("objectId") is None or log_entry.get("objectId") == "":
            log_entry["objectId"] = log_entry.get("owner_objectid", "")

        if log_entry.get("objectId"):
            print(f"Domain objectId: {log_entry['objectId']}")
        else:
            print(
                "Domain objectId not found in log entry, extracting from node data..."
            )

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

    def extract_domain_name(self, node_data, properties, name, domains_data=None):
        """
        Helper function to extract domain name from various sources
        """
        # Try domain property first
        if "domain" in properties:
            return properties["domain"]

        objectId = (
            node_data.get(
                "objectId", node_data.get("properties", {}).get("owner_objectid", "")
            ),
        )

        if objectId:
            domain_name = (
                next(
                    (
                        domain["name"]
                        for domain in domains_data
                        if domain.get("id") == objectId
                    ),
                    None,
                )
                if domains_data
                else None
            )
            return domain_name

        # Try to extract from name for Azure entities
        if "@" in name:
            return name.split("@")[-1]

        # Try to extract from distinguished name for AD entities
        if "distinguishedname" in properties:
            dn = properties["distinguishedname"]
            if "DC=" in dn.upper():
                dc_parts = []
                for part in dn.split(","):
                    part = part.strip()
                    if part.upper().startswith("DC="):
                        dc_parts.append(part.split("=")[1])
                if dc_parts:
                    return ".".join(dc_parts)

        # Try to extract from object ID patterns
        return self.extract_domain_from_object_id(node_data.get("objectId", ""))

    def extract_domain_from_object_id(self, object_id):
        """
        Helper function to extract domain from object_id patterns
        """
        if "@" in object_id:
            return object_id.split("@")[-1]
        elif object_id.startswith("S-1-5-21-"):
            # This is a SID, we might need to map it to domain name
            # For now, return a placeholder that indicates it's an AD domain
            return "AD_Domain"
        else:
            return "Unknown"

    def extract_name(self, node_data, properties, node_id):
        """
        Helper function to extract name from node data or properties
        """

        object_id = (
            node_data.get("objectId")
            or properties.get("objectid")
            or properties.get("objectId")
            or node_id
        )

        # Try to get name from properties first
        if "name" in properties:
            return properties["name"]

        # If label is present, use it as a fallback
        elif "label" in node_data:
            return node_data["label"]

        # Fallback to node_data if name is not in properties
        return str(object_id)


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
    res_domains = response.json()
    domains_data = res_domains.get("data", [])
    if response and response.status_code == 200:
        print("Connection test successful!")
        print("Response data:", response.json())

        # Now execute the Cypher query
        domains_data = [
            domain for domain in domains_data if domain.get("collected") == True
        ]

        cypher_response = bloodhound_manager.fetch_tier_zero_assets()

        nodes_array = [
            {
                "nodeId": node_id,
                "domain_name": (
                    bloodhound_manager.extract_domain_name(
                        node_data,
                        node_data.get("properties", {}),
                        node_data.get("name", ""),
                        domains_data,
                    )
                    or ""
                ).upper(),
                "name": bloodhound_manager.extract_name(
                    node_data, node_data.get("properties", {}), node_id
                ),
                **node_data,
            }
            for node_id, node_data in cypher_response["data"]["nodes"].items()
        ]

        nodes_array = [nodes for nodes in nodes_array if nodes.get("kind") != "Meta"]

        token = bloodhound_manager.get_bearer_token(TENANT_ID, APP_ID, APP_SECRET)
        if not token:
            print("Failed to obtain Bearer token. Exiting.")
            return
        print("Bearer token obtained successfully.")
        results = []

        for i, data in enumerate(nodes_array, 1):
            print(
                f"Sending attack data {i}/{len(nodes_array)}: ID {data.get('nodeId')}"
            )
            try:
                res = bloodhound_manager.send_tier_zero_assets_data(
                    data,
                    token,
                    DCE_URI,
                    DCR_IMMUTABLE_ID,
                    TABLE_NAME,
                    tenant_domain,
                    domains_data,
                )
                results.append(
                    {"id": data.get("nodeId"), "status": "success", "response": res}
                )
            except Exception as e:
                results.append(
                    {"id": data.get("nodeId"), "status": "error", "message": str(e)}
                )
                time.sleep(0.1)  # Avoid rate limiting

        print("results:", results)
        print("All attack data sent to DCE successfully.")

    else:
        print("Connection test failed - check logs for details")


if __name__ == "__main__":
    main()
