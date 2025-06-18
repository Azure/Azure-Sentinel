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
DCR_IMMUTABLE_ID = "dcr-4d013aa9faa64537909486976870b9d1"
TABLE_NAME = "BloodHoundAttackPathsDetails_CL"

ENDPOINTS = {
    "test_connection": "/api/v2/available-domains",
    "available_domain": "/api/v2/available-domains",
    "domain_available_types": "/api/v2/domains/{domain}/available-types",
    "path_title": "/api/v2/assets/findings/{finding_type}/title.md",
    "attack_path_details": "/api/v2/domains/{domain_id}/details?finding={finding_type}&skip={skip}",
    "short_description": "/api/v2/assets/findings/{finding_type}/short_description.md",
    "short_remediation": "/api/v2/assets/findings/{finding_type}/short_remediation.md",
    "long_remediation": "/api/v2/assets/findings/{finding_type}/long_remediation.md",
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

    def get_available_types_for_domain(self, domain: str):
        """
        Fetch available types for a single domain.

        Args:
            domain (str): The domain to fetch available types for.

        Returns:
            list: List of available types data, or empty list if failed.
        """
        try:
            response = self._api_request("domain_available_types", domain=domain)
            if response:
                return response.get("data", [])
            else:
                self._log_error("Received empty response or request failed.")
                return []
        except Exception as e:
            self._log_error(
                f"Exception occurred while fetching attack path types for domain {domain}: {e}"
            )
            return []

    def get_attack_path_details(self, domain_id: str, finding_type: str):
        """
        Fetch attack path details for a specific domain and finding type with automatic pagination.

        Args:
            domain_id (str): ID of the domain.
            finding_type (str): The attack type (like 'T0GenericAll').

        Returns:
            list: All attack path details across all pages, or empty list on error
        """
        try:
            all_attack_paths = []
            skip = 0

            while True:
                # Fetch a page of attack path details
                page_data = self._api_request(
                    "attack_path_details",
                    domain_id=domain_id,
                    finding_type=finding_type,
                    skip=skip,
                ).get("data", [])

                # If no data returned or empty page, we're done
                if not page_data:
                    break

                all_attack_paths.extend(page_data)

                # Move to next page
                skip += len(page_data)

                # If we got fewer results than expected, we've reached the end
                if len(page_data) < 10:
                    break

            return all_attack_paths

        except Exception as e:
            self._log_error(
                f"Error fetching attack path details for {domain_id} with type {finding_type}: {e}"
            )
            return []

    def get_path_title_details(self, domains_data):
        """
        Fetches the path title details for each domain in the provided data.

        Args:
            domains_data (list): List of domain data dictionaries.

        Returns:
            dict: A dictionary mapping domain IDs to their path titles.
        """
        unique_finding_types = set()
        array_of_domains_and_available_types_and_path_title = []
        for domain in domains_data:
            available_types = domain.get("available_types", [])
            array_of_domains_and_available_types_and_path_title.append(
                {
                    "domain_id": domain.get("id"),
                    "domain_name": domain.get("name"),
                    "available_types": available_types,
                }
            )
            for attack_type in available_types:
                unique_finding_types.add(attack_type)
        path_titles = {}
        path_types_and_titles = []
        for finding_type in unique_finding_types:
            try:
                path_title_response = self._api_request(
                    "path_title", return_json=False, finding_type=finding_type
                )
                path_types_and_titles.append(
                    {
                        "finding_type": finding_type,
                        "path_title": (
                            path_title_response.text if path_title_response else ""
                        ),
                    }
                )
                short_description_response = self._api_request(
                    "short_description", return_json=False, finding_type=finding_type
                )
                short_remediation_response = self._api_request(
                    "short_remediation", return_json=False, finding_type=finding_type
                )
                long_remediation_response = self._api_request(
                    "long_remediation", return_json=False, finding_type=finding_type
                )

                if path_title_response and path_title_response.status_code == 200:
                    path_titles[finding_type] = path_title_response.text
                    print(
                        f"Fetched path title for {finding_type}: {path_titles[finding_type]}"
                    )
                if (
                    short_description_response
                    and short_description_response.status_code == 200
                ):
                    path_titles[finding_type + "_short_description"] = (
                        short_description_response.text
                    )
                    print(
                        f"Fetched short description for {finding_type}: {path_titles[finding_type + '_short_description']}"
                    )
                if (
                    short_remediation_response
                    and short_remediation_response.status_code == 200
                ):
                    path_titles[finding_type + "_short_remediation"] = (
                        short_remediation_response.text
                    )
                    print(
                        f"Fetched short remediation for {finding_type}: {path_titles[finding_type + '_short_remediation']}"
                    )
                if (
                    long_remediation_response
                    and long_remediation_response.status_code == 200
                ):
                    path_titles[finding_type + "_long_remediation"] = (
                        long_remediation_response.text
                    )
                    print(
                        f"Fetched long remediation for {finding_type}: {path_titles[finding_type + '_long_remediation']}"
                    )
                else:
                    self._log_error(f"Failed to fetch path title for {finding_type}")
            except Exception as e:
                self._log_error(f"Error fetching path title for {finding_type}: {e}")
                path_titles[finding_type] = ""

        print(f"Fetched path titles: {path_types_and_titles}")
        return path_titles

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

    def send_attack_data(
        self,
        attack_data,
        bearer_token,
        unique_finding_types_data,
        dce_uri,
        dcr_immutable_id,
        table_name,
        tenant_domain,
        domains_data,
    ):
        """
        Sends attack data to Azure Monitor via Data Collection Endpoint (DCE),
        using the schema format specified for BloodHoundAttackPaths_CL table.
        """

        domain_name = ""
        for domain in domains_data:
            if domain.get("id") == attack_data.get("DomainSID"):
                domain_name = domain.get("name", "")
                break
        # print(f"Domain Name: {domain_name}")

        finding_type = attack_data.get("Finding", "")

        path_title = unique_finding_types_data.get(finding_type, "")
        # print(f"Path Title for {finding_type}: {path_title}")
        short_description = unique_finding_types_data.get(
            f"{finding_type}_short_description", ""
        )
        # print(f"Short Description for {finding_type}: {short_description}")
        short_remediation = unique_finding_types_data.get(
            f"{finding_type}_short_remediation", ""
        )
        # print(f"Short Remediation for {finding_type}: {short_remediation}")
        long_remediation = unique_finding_types_data.get(
            f"{finding_type}_long_remediation", ""
        )
        # print(f"Long Remediation for {finding_type}: {long_remediation}")

        print(f"attack_data: {attack_data}")
        print(
            f"percentages: {attack_data.get('ExposurePercentage', '')}, {attack_data.get('ImpactPercentage', '')}"
        )

        log_entry = {
            "Accepted": attack_data.get("Accepted", False),
            "AcceptedUntil": attack_data.get("AcceptedUntil", ""),
            "ComboGraphRelationID": str(attack_data.get("ComboGraphRelationID", "")),
            "created_at": attack_data.get("created_at", ""),
            "deleted_at": attack_data.get("deleted_at", {}),
            "DomainSID": attack_data.get("DomainSID", ""),
            "Environment": attack_data.get("Environment", ""),
            "ExposureCount": attack_data.get("ExposureCount", 0),
            "ExposurePercentage": attack_data.get("ExposurePercentage", 0),
            "Finding": attack_data.get("Finding", ""),
            "NonTierZeroPrincipalEnvironment": attack_data.get("FromEnvironment", ""),
            "NonTierZeroPrincipalEnvironmentID": attack_data.get(
                "FromEnvironmentID", ""
            ),
            "NonTierZeroPrincipal": attack_data.get("FromPrincipal", ""),
            "NonTierZeroPrincipalKind": attack_data.get("FromPrincipalKind", ""),
            "NonTierZeroPrincipalName": attack_data.get("FromPrincipalName", ""),
            "NonTierZeroPrincipalProps": attack_data.get("FromPrincipalProps", {}),
            "id": int(attack_data.get("id", 0)),
            "ImpactCount": attack_data.get("ImpactCount", 0),
            "ImpactPercentage": attack_data.get("ImpactPercentage", 0),
            "IsInherited": str(attack_data.get("IsInherited", "")),
            "Principal": attack_data.get("ToPrincipal", ""),
            "PrincipalHash": attack_data.get("PrincipalHash", ""),
            "PrincipalKind": attack_data.get("ToPrincipalKind", ""),
            "PrincipalName": attack_data.get("ToPrincipalName", ""),
            "RelProps": attack_data.get("RelProps", {}),
            "Severity": attack_data.get("Severity", ""),
            "ImpactedPrincipalEnvironment": attack_data.get("ToEnvironment", ""),
            "ImpactedPrincipalEnvironmentID": attack_data.get("ToEnvironmentID", ""),
            "ImpactedPrincipal": attack_data.get("ToPrincipal", ""),
            "ImpactedPrincipalKind": attack_data.get("ToPrincipalKind", ""),
            "ImpactedPrincipalName": attack_data.get("ToPrincipalName", ""),
            "ImpactedPrincipalProps": attack_data.get("ToPrincipalProps", {}),
            "updated_at": attack_data.get("updated_at", ""),
            "PathTitle": path_title,
            "ShortDescription": short_description,
            "ShortRemediation": short_remediation,
            "LongRemediation": long_remediation,
            "tenant_url": tenant_domain,
            "domain_name": domain_name,
            "Remediation": f"{tenant_domain}/ui/remediation?findingType={finding_type}",
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

        domains_data = [
            domain for domain in domains_data if domain.get("collected") == True
        ]

        # Add available_types field to each domain
        for domain in domains_data:
            # Fetch available types for this domain
            available_types = bloodhound_manager.get_available_types_for_domain(
                domain.get("id")
            )

            # Add the available_types field to the domain dictionary
            domain["available_types"] = available_types

        # Print the complete updated domains_data
        print(f"Total Domains with available types: {domains_data}")

        unique_finding_types_data = bloodhound_manager.get_path_title_details(
            domains_data
        )

        consolidated_attack_paths_details = []

        for domain in domains_data:
            domain_id = domain.get("id")
            domain_name = domain.get("name")
            available_types = domain.get("available_types", [])

            if not available_types:
                print(f"[SKIPPED] No available types for domain {domain_name}")
                continue

            for attack_type in available_types:
                print(f"Fetching attack path for {domain_name} [{attack_type}]...")
                attack_details = bloodhound_manager.get_attack_path_details(
                    domain_id, attack_type
                )

                if attack_details:
                    consolidated_attack_paths_details.append(attack_details)
                    print(f"Fetched {len(attack_details)} findings for {attack_type}.")
                else:
                    consolidated_attack_paths_details.append([])
                    print(
                        f"Failed to fetch attack path for {attack_type} in domain {domain_name}"
                    )

        flattened_attack_paths_details = [
            item for sublist in consolidated_attack_paths_details for item in sublist
        ]
        print(f"CONSOLIDATED ATTACK PATHS DETAILS:{flattened_attack_paths_details}")

        # Now send the attack data to Data Collection Endpoint (DCE)

        token = bloodhound_manager.get_bearer_token(TENANT_ID, APP_ID, APP_SECRET)
        if not token:
            print("Failed to obtain Bearer token. Exiting.")
            return
        print("Bearer token obtained successfully.")
        results = []

        # Iterate through the flattened attack paths and send each one to the DCE

        for i, attack in enumerate(flattened_attack_paths_details, 1):
            print(
                f"Sending attack data {i}/{len(flattened_attack_paths_details)}: ID {attack.get('id')}"
            )
            try:
                res = bloodhound_manager.send_attack_data(
                    attack,
                    token,
                    unique_finding_types_data,
                    DCE_URI,
                    DCR_IMMUTABLE_ID,
                    TABLE_NAME,
                    tenant_domain,
                    domains_data,
                )
                results.append(
                    {"id": attack.get("id"), "status": "success", "response": res}
                )
            except Exception as e:
                results.append(
                    {"id": attack.get("id"), "status": "error", "message": str(e)}
                )
            time.sleep(0.2)  # Avoid rate limiting

        print("results:", results)
        print("All attack data sent to DCE successfully.")

    else:
        print("Connection test failed - check logs for details")


if __name__ == "__main__":
    main()
