import logging
import requests
import hmac
import hashlib
import base64
from urllib.parse import urljoin, urlparse, urlencode, parse_qs
import datetime
import json

class BloodhoundManager:
    """
    Manages interactions with the BloodHound Enterprise API and Azure Monitor for
    audit logs, finding trends, posture history, posture statistics, and attack paths.
    """

    DEFAULT_LOOKBACK_DAYS = 1
    
    def _send_to_azure_monitor(self, log_entry, bearer_token, dce_uri, dcr_immutable_id, table_name):
        """
        Helper to send a log entry to Azure Monitor via Data Collection Endpoint (DCE).
        Handles POST request, error handling, and logging.
        """
        api_url = f"{dce_uri}/dataCollectionRules/{dcr_immutable_id}/streams/Custom-{table_name}?api-version=2023-01-01"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            api_url, headers=headers, data=json.dumps([log_entry])
        )
        
        if response.status_code >= 400:
            self._log_error(
                f"[Send Error] Failed to send log entry to Azure Monitor: HTTP {response.status_code}. Response: {response.text}"
            )
            return {"status": "error", "message": f"HTTP Error {response.status_code}"}

        response_content = (
            response.json()
            if response.content
            else {"status": "success", "message": "No content in response"}
        )
        return {"status": "success", "response": response_content}

    def __init__(
        self, tenant_domain: str, token_id: str, token_key: str, logger: logging.Logger
    ):
        """
        Initializes the BloodhoundManager with tenant credentials and logger.

        Args:
            tenant_domain (str): The base URL/domain of the BloodHound Enterprise instance.
            token_id (str): The token ID used for authentication.
            token_key (str): The token secret key used to generate HMAC signatures.
            logger (logging.Logger): Logger instance for logging errors and info.
        """
        self.tenant_domain = tenant_domain
        self.__token_id = token_id
        # Ensure token_key is encoded for HMAC operations consistently
        self.__token_key = (
            token_key.encode("utf-8") if isinstance(token_key, str) else token_key
        )
        self.logger = logger

        # Azure Monitor configuration attributes, to be set by set_azure_monitor_config
        self.tenant_id = None
        self.app_id = None
        self.app_secret = None
        self.dce_uri = None
        self.dcr_immutable_id = None
        self.table_name = (
            None  # This will store the *current* table name for send operations
        )

    def set_azure_monitor_config(
        self,
        tenant_id: str,
        app_id: str,
        app_secret: str,
        dce_uri: str,
        dcr_immutable_id: str,
        table_name: str,
    ):
        """
        Sets the Azure Monitor configuration for sending logs.
        This allows a single BloodhoundManager instance to be configured for a specific
        Log Analytics table/stream before calling send methods.
        """
        self.tenant_id = tenant_id
        self.app_id = app_id
        self.app_secret = app_secret
        self.dce_uri = dce_uri
        self.dcr_immutable_id = dcr_immutable_id
        self.table_name = table_name
        self.logger.info(f"Azure Monitor config set for table: {self.table_name}")

    def _get_headers(self, method: str, uri: str, payload: str = None) -> dict:
        """Generate authentication headers for API requests"""
        # Use self.__token_key directly as it's already bytes
        digester = hmac.new(self.__token_key, None, hashlib.sha256)
        digester.update(f"{method}{uri}".encode())
        digester = hmac.new(digester.digest(), None, hashlib.sha256)
        datetime_formatted = datetime.datetime.now().astimezone().isoformat("T")
        digester.update(datetime_formatted[:13].encode())
        digester = hmac.new(digester.digest(), None, hashlib.sha256)

        # Process body if it exists separately and is a POST request
        # Ensure the body is *only* included for the final hash for POST requests
        if method == "POST" and payload:
            digester.update(payload.encode())

        headers = {
            "User-Agent": "BloodHound Enterprise - Azure Functions Integration",
            "Authorization": f"bhesignature {self.__token_id}",
            "RequestDate": datetime_formatted,
            "Signature": base64.b64encode(digester.digest()).decode(),
            "Content-Type": "application/json",
        }
        return headers

    def _validate_response(
        self, response: requests.Response, error_msg: str = "An error occurred"
    ) -> bool:
        """
        Validates the HTTP response and logs errors if any.
        """
        if response.status_code >= 400:
            self._log_error(
                f"{error_msg}: HTTP Error - Status Code: {response.status_code} - Response: {response.text}"
            )
            return False
        return True

    def _api_request(
        self, uri, return_json: bool = True, method: str = "GET", payload=None
    ):
        """
        Centralized function to handle API requests and error handling.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint_key (str): Key in ENDPOINTS dictionary
            return_json (bool): Whether to return JSON response or raw response
            **kwargs: Includes parameters for URL path formatting, query parameters, and post body.

        Returns:
            Response data or None if request fails.
        """
        full_url: str = f"{self.tenant_domain}{uri}"

        headers = self._get_headers(method, uri, payload)
        if headers is None:
            self.logger.error("Failed to generate headers for API request.")
            return None

        self.logger.info(f"Making {method} request to {full_url}")
        response = requests.request(method, full_url, headers=headers, data=payload)
        self.logger.info(f"Response status code: {response.status_code}")

        if not self._validate_response(
            response, f"API request to {full_url} failed"
        ):
            return None

        # For text-based endpoints (like .md files), we return raw text, not JSON
        if full_url.__contains__(".md") and return_json is False:
            return response

        return response.json() if return_json else response

    def test_connection(self) -> requests.Response | None:
        """
        Tests the connection to the BloodHound Enterprise API.

        Returns:
            Response object: Raw HTTP response from the test connection endpoint, or None on failure.
        """
        self.logger.info("Testing connection to BloodHound API...")
        response = self._api_request("/api/v2/available-domains")
        if response:
            self.logger.info(f"BloodHound API connection successful.")
        return response

    def get_available_domains(self) -> dict | None:
        """
        Fetches available domains from the BloodHound Enterprise API.
        """
        self.logger.info("Fetching available domains from BloodHound API...")
        response = self._api_request("/api/v2/available-domains", return_json=True)
        
        if isinstance(response, dict):
            self.logger.info(
                f"Successfully fetched domains. Found {len(response.get('data', []))} entries."
            )
            return response
        else:
            self._log_error(f"Expected dict from API, got {type(response)}: {response}")
            return {}

    def get_audit_logs(self, after = "") -> list[dict] :
        """
        Fetches audit logs from the BloodHound Enterprise API.
        Returns:
            dict: Dictionary containing audit log entries, or None on failure.
        """
        audit_logs_list: list = []
        skip: int = 0
        limit = 1000
        while True:

            if after is not None and after != "":
                uri: str = f"/api/v2/audit?skip={skip}&limit={limit}&after={after}"
            else:
                two_days_ago_midnight = (
                    (datetime.datetime.now() - datetime.timedelta(days=self.DEFAULT_LOOKBACK_DAYS))
                    .replace(hour=0, minute=0, second=0, microsecond=0)
                    .strftime('%Y-%m-%dT%H:%M:%SZ')
                )
                uri: str = f"/api/v2/audit?skip={skip}&limit={limit}&after={two_days_ago_midnight}"

            audit_logs_response = self._api_request(uri)
            total_audit_logs_fetched: int = len(
                audit_logs_response.get("data", {}).get("logs", [])
                if audit_logs_response
                else []
            )
            if audit_logs_response:
                self.logger.info(
                    f"Successfully fetched audit logs. Found {total_audit_logs_fetched} entries."
                )

            if total_audit_logs_fetched == 0:
                break

            if not audit_logs_response:
                self.logger.error("Failed to fetch audit logs: Empty or unauthorized response")
                break

            logs = audit_logs_response.get("data", {}).get("logs", [])

            audit_logs_list.extend(logs)
            skip += total_audit_logs_fetched

        return audit_logs_list
    
    def get_finding_trends(self, environment_id: str, start_date: str) -> dict | None:
        """
        Fetches finding trends from the BloodHound Enterprise API.
        This matches the URL: /api/v2/attack-paths/finding-trends?environments=ID1&start=DATE

        Args:
            environment_id (str): The ID of the environment to query.
            start_date (str): The start date in RFC3339 format.

        Returns:
            dict: JSON response containing finding trends or None if request fails.
        """

        uri: str = f"/api/v2/attack-paths/finding-trends?environments={environment_id}&start={start_date}"
        self.logger.info(f"Fetching finding trends for environment ID: {environment_id} starting from {start_date}")
        return self._api_request(uri)

    def get_posture_history(self, data_type: str, environment_id=None, start = "") -> dict | None:
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
        if environment_id:
            params["environments"] = environment_id

        self.logger.info(
            f"Fetching posture history for type '{data_type}' with params: {params}"
        )

        if start is not None and start != "":
            uri: str = f"/api/v2/posture-history/{data_type}?environments={environment_id}&start={start}"
        else:
            two_days_ago_midnight = (
                (datetime.datetime.now() - datetime.timedelta(days=self.DEFAULT_LOOKBACK_DAYS))
                .replace(hour=0, minute=0, second=0, microsecond=0)
                .strftime('%Y-%m-%dT%H:%M:%SZ')
            )
            uri: str = f"/api/v2/posture-history/{data_type}?environments={environment_id}&start={two_days_ago_midnight}"

        return self._api_request(uri)

    def get_posture_stats(self):
        """
        Fetches posture statistics from the BloodHound Enterprise API.

        Returns:
            dict: Posture statistics for the specified domain, or None if an error occurs.
        """
        uri: str = "/api/v2/posture-stats"
        return self._api_request(uri)

    def get_available_types_for_domain(self, domain_id: str) -> list:
        """
        Fetch available finding types for a single domain.

        Args:
            domain_id (str): The ID of the domain to fetch available types for.

        Returns:
            list: List of available types data, or empty list if failed.
        """
        self.logger.info(f"Fetching available types for domain ID: {domain_id}")
        uri: str = f"/api/v2/domains/{domain_id}/available-types"
        # No change needed here, as domain_id is a path param, and no query params
        response = self._api_request(uri)
        if response:
            self.logger.info(
                f"Found {len(response.get('data', []))} available types for domain ID: {domain_id}"
            )
            return response.get("data", [])
        else:
            self._log_error(
                f"Received empty response or request failed for available types for domain ID: {domain_id}."
            )
            return []

    def get_attack_path_details(self, domain_id: str, finding_type: str) -> list:
        """
        Fetch attack path details for a specific domain and finding type with automatic pagination.

        Args:
            domain_id (str): ID of the domain.
            finding_type (str): The attack type (like 'T0GenericAll').

        Returns:
            list: All attack path details across all pages, or empty list on error.
        """
        self.logger.info(
            f"Fetching attack path details for domain ID: {domain_id}, finding type: {finding_type}"
        )
        all_attack_paths = []
        skip = 0
        page_size = 10  # Default page size for this endpoint if not specified

        while True:
            # Fetch a page of attack path details
            # domain_id is a path parameter
            # 'finding' and 'skip' are query parameters

            page_data = self._api_request(
                f"/api/v2/domains/{domain_id}/details?finding={finding_type}&skip={skip}"
            )

            if not page_data or not page_data.get("data"):
                break  # No more data or error occurred

            current_page_items = page_data.get("data", [])
            all_attack_paths.extend(current_page_items)

            self.logger.debug(
                f"Fetched {len(current_page_items)} items for skip={skip}, total={len(all_attack_paths)}"
            )

            # Check if this was the last page
            if len(current_page_items) < page_size:  # If fetched fewer than max, must be last page
                break

            # Increment skip for the next page
            skip += len(current_page_items)

        self.logger.info(
            f"Finished fetching attack path details for domain ID: {domain_id}, finding type: {finding_type}. Total items: {len(all_attack_paths)}"
        )
        return all_attack_paths

    def get_attack_path_sparkline_timeline(
        self, domain_id: str, finding_type: str, start_from = ""
    ) -> list:
        """
        Fetches the attack path timeline (sparkline data) for a specific domain and finding type.

        Args:
            domain_id (str): ID of the domain.
            finding_type (str): The attack type (like 'T0GenericAll').

        Returns:
            list: List of attack path timelines, or empty list on error.
        """
        self.logger.info(
            f"Fetching attack path timeline for domain {domain_id} and finding type {finding_type}."
        )
        if start_from is not None and start_from != "":
            uri: str = f"/api/v2/domains/{domain_id}/sparkline?finding={finding_type}&from={start_from}"
        else:
            two_days_ago_midnight = (
                (datetime.datetime.now() - datetime.timedelta(days=self.DEFAULT_LOOKBACK_DAYS))
                .replace(hour=0, minute=0, second=0, microsecond=0)
                .strftime('%Y-%m-%dT%H:%M:%SZ')
            )
            uri: str = f"/api/v2/domains/{domain_id}/sparkline?finding={finding_type}&from={two_days_ago_midnight}"

        page_data = self._api_request(
            uri
        )

        # The API response for sparkline might sometimes just be the list directly,
        # or wrapped in 'data'. Handle both.
        if isinstance(page_data, dict) and "data" in page_data:
            return page_data.get("data", [])
        elif isinstance(page_data, list):
            return page_data
        else:
            self._log_error(
                f"Unexpected response format for attack path timeline for {domain_id} with type {finding_type}: {page_data}"
            )
            return []

    # NEW METHOD: get_path_asset_text_details (helper for markdown content)
    def get_path_asset_text_details(self, uri) -> str:
        """
        Fetches text details (title, short_description, short_remediation, long_remediation)
        for a given finding type.

        Returns:
            str: The text content, or an empty string if fetching fails.
        """
        # No change needed here, finding_type is a path param, no query params
        response = self._api_request(uri, return_json=False)
        if response and response.status_code == 200:
            return response.text
        else:
            self._log_error(
                f"Failed to fetch data. Status: {response.status_code if response else 'No response'}"
            )
            return ""

    # NEW METHOD: get_all_path_asset_details_for_finding_types
    def get_all_path_asset_details_for_finding_types(self, domains_data: list) -> dict:
        """
        Fetches all asset details (title, descriptions, remediations) for all unique
        finding types present across the given domains.

        Args:
            domains_data (list): List of domain data dictionaries, each containing
                                 'available_types' key.

        Returns:
            dict: A dictionary where keys are finding types (or f'{finding_type}_{detail_type}')
                  and values are the corresponding text details.
                  Example: {'T0GenericAll': 'Title Text', 'T0GenericAll_short_description': 'Desc Text'}
        """

        unique_finding_types = set()
        for domain in domains_data:
            for attack_type in domain.get("available_types", []):
                unique_finding_types.add(attack_type)

        all_asset_details = {}
        for finding_type in unique_finding_types:
            self.logger.info(
                f"Collecting asset details for finding type: {finding_type}"
            )
            all_asset_details[finding_type] = self.get_path_asset_text_details(
                f"/api/v2/assets/findings/{finding_type}/title.md"
            )
            all_asset_details[f"{finding_type}_short_description"] = (
                self.get_path_asset_text_details(
                    f"/api/v2/assets/findings/{finding_type}/short_description.md"
                )
            )
            all_asset_details[f"{finding_type}_short_remediation"] = (
                self.get_path_asset_text_details(
                    f"/api/v2/assets/findings/{finding_type}/short_remediation.md"
                )
            )
            all_asset_details[f"{finding_type}_long_remediation"] = (
                self.get_path_asset_text_details(
                    f"/api/v2/assets/findings/{finding_type}/long_remediation.md"
                )
            )

        self.logger.info(
            f"Collected asset details for {len(unique_finding_types)} unique finding types."
        )
        return all_asset_details

    def _log_error(self, message: str):
        """
        Logs the provided error message using the logger.
        """
        self.logger.error(message)

    def get_bearer_token(self) -> str | None:
        """
        Fetches a Bearer token for Azure Monitor API using client credentials.
        Requires `tenant_id`, `app_id`, `app_secret` to be set in the manager via set_azure_monitor_config.
        """
        if not all([self.tenant_id, self.app_id, self.app_secret]):
            self._log_error(
                "Azure AD credentials (tenant_id, app_id, app_secret) not set for token retrieval."
            )
            return None

        token_url = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = f"client_id={self.app_id}&scope=https%3A%2F%2Fmonitor.azure.com%2F%2F.default&client_secret={self.app_secret}&grant_type=client_credentials"

        self.logger.info("Attempting to obtain Bearer token for Azure Monitor.")

        response = requests.post(token_url, headers=headers, data=body)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        if access_token:
            self.logger.info("Bearer token obtained successfully.")
        else:
            self._log_error(f"Bearer token not found in response: {response.text}")
        return access_token

    def send_audit_logs_data(self, data: dict, bearer_token: str) -> dict:
        """
        Sends a single audit log entry to Azure Monitor via Data Collection Endpoint (DCE).
        Requires `dce_uri`, `dcr_immutable_id`, `table_name` to be set via set_azure_monitor_config.
        """
        if not all([self.dce_uri, self.dcr_immutable_id, self.table_name]):
            self._log_error(
                "Azure Monitor configuration (DCE URI, DCR ID, Table Name) not set for sending audit logs."
            )
            return {
                "status": "error",
                "message": "Azure Monitor configuration missing.",
            }

        # Transform data to the expected schema for Azure Monitor for audit logs
        log_entry = {
            "action": data.get("action", ""),
            "actor_email": data.get("actor_email", ""),
            "actor_id": data.get("actor_id", ""),
            "actor_name": data.get("actor_name", ""),
            "commit_id": data.get("commit_id", ""),
            "created_at": data.get("created_at", ""),
            "fields": json.dumps(
                data.get("fields", {})
            ),  # fields should be a string in Log Analytics
            "id": data.get("id", ""),
            "request_id": data.get("request_id", ""),
            "source_ip_address": data.get("source_ip_address", ""),
            "status": data.get("status", ""),
            "tenant_url": self.tenant_domain,  # Use the tenant_domain from the manager
        }

        self.logger.info(
            f"Preparing to send audit log entry with ID: {log_entry.get('id')} to {self.table_name}"
        )
        return self._send_to_azure_monitor(
            log_entry, bearer_token, self.dce_uri, self.dcr_immutable_id, self.table_name
        )

    def send_finding_trends_logs(
        self,
        data: dict,  # This is the 'finding' dictionary from BHE response
        bearer_token: str,
        # Passed explicitly as it's part of the log data, not manager's fixed config
        tenant_domain: str,
        domains_data: list = None,  # Passed explicitly for domain name lookup
        environment_id: str = None,  # Passed explicitly as it's tied to the finding
        start_date: str = None,  # Passed explicitly
        end_date: str = None,  # Passed explicitly
        period: str = None,  # Passed explicitly as it's part of the finding data
    ) -> dict:
        """
        Sends attack data (finding trends) to Azure Monitor via Data Collection Endpoint (DCE).
        Requires `dce_uri`, `dcr_immutable_id`, `table_name` to be set via set_azure_monitor_config.
        """
        if not all([self.dce_uri, self.dcr_immutable_id, self.table_name]):
            self._log_error(
                "Azure Monitor configuration (DCE URI, DCR ID, Table Name) not set for sending finding trends."
            )
            return {
                "status": "error",
                "message": "Azure Monitor configuration missing.",
            }

        env_id = environment_id
        domain_name = (
            next(
                (
                    domain["name"]
                    for domain in domains_data
                    if domain.get("id") == env_id
                ),
                None,
            )
            if domains_data
            else None
        )

        log_entry = {
            "composite_risk": str(round(float(data.get("composite_risk", "")), 2)),
            "display_title": str(data.get("display_title", "")),
            "display_type": str(data.get("display_type", "")),
            "environment_id": env_id,
            "exposure_count": int(data.get("exposure_count", 0)),
            "finding": str(data.get("finding", "")),
            "finding_count_decrease": int(data.get("finding_count_decrease", 0)),
            "finding_count_end": int(data.get("finding_count_end", 0)),
            "finding_count_increase": int(data.get("finding_count_increase", 0)),
            "finding_count_start": int(data.get("finding_count_start", 0)),
            "impact_count": int(data.get("impact_count", 0)),
            "tenant_url": tenant_domain,
            "domain_name": domain_name,
            "start_date": start_date if start_date else "",
            "end_date": end_date if end_date else "",
            "period": period if period else "",
        }

        self.logger.info(
            f"Preparing to send finding trends log entry for finding: {log_entry.get('finding')} to {self.table_name}"
        )
        return self._send_to_azure_monitor(
            log_entry, bearer_token, self.dce_uri, self.dcr_immutable_id, self.table_name
        )

    def send_posture_history_logs(
        self,
        # This is the posture history item (e.g., from 'data' list)
        data: dict,
        bearer_token: str,
        tenant_domain: str,
        domains_data: list = None,
    ) -> dict:
        """
        Sends posture history data to Azure Monitor via Data Collection Endpoint (DCE).
        Requires `dce_uri`, `dcr_immutable_id`, `table_name` to be set via set_azure_monitor_config.
        """
        if not all([self.dce_uri, self.dcr_immutable_id, self.table_name]):
            self._log_error(
                "Azure Monitor configuration (DCE URI, DCR ID, Table Name) not set for sending posture history logs."
            )
            return {
                "status": "error",
                "message": "Azure Monitor configuration missing.",
            }

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

        log_entry = {
            "metric_date": data.get("date", ""),
            "value": str(data.get("value", "")),
            "start_time": data.get("start_date", ""),
            "end_time": data.get("end_date", ""),
            "domain_id": domain_id,
            # 'type' field is added in the processor
            "data_type": data.get("type", ""),
            "domain_name": domain_name,
            "tenant_url": tenant_domain,
        }

        self.logger.info(
            f"Preparing to send posture history log entry for type '{log_entry.get('data_type')}' in domain '{domain_name}' to {self.table_name}"
        )
        return self._send_to_azure_monitor(
            log_entry, bearer_token, self.dce_uri, self.dcr_immutable_id, self.table_name
        )

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
        return self._send_to_azure_monitor(
            log_entry, bearer_token, dce_uri, dcr_immutable_id, table_name
        )

    # NEW METHOD: send attack data
    def send_attack_data(
        self,
        attack_data: dict,
        bearer_token: str,
        # Contains pre-fetched titles, descriptions, remediations
        unique_finding_types_data: dict,
        tenant_domain: str,
        domains_data: list,  # Used to lookup domain_name by DomainSID
    ) -> dict:
        """
        Sends attack path data to Azure Monitor via Data Collection Endpoint (DCE),
        using the schema format specified for BloodHoundAttackPaths_CL table.
        Requires `dce_uri`, `dcr_immutable_id`, `table_name` to be set via set_azure_monitor_config.
        """
        if not all([self.dce_uri, self.dcr_immutable_id, self.table_name]):
            self._log_error(
                "Azure Monitor configuration (DCE URI, DCR ID, Table Name) not set for sending attack paths."
            )
            return {
                "status": "error",
                "message": "Azure Monitor configuration missing.",
            }

        domain_name = ""
        for domain in domains_data:
            if domain.get("id") == attack_data.get(
                "DomainSID"
            ):  # DomainSID here seems to be the domain ID
                domain_name = domain.get("name", "")
                break

        finding_type = attack_data.get("Finding", "")

        # Get enriched data from unique_finding_types_data
        path_title = unique_finding_types_data.get(finding_type, "")
        short_description = unique_finding_types_data.get(
            f"{finding_type}_short_description", ""
        )
        short_remediation = unique_finding_types_data.get(
            f"{finding_type}_short_remediation", ""
        )
        long_remediation = unique_finding_types_data.get(
            f"{finding_type}_long_remediation", ""
        )

        log_entry = {
            "Accepted": attack_data.get("Accepted", False),
            "AcceptedUntil": attack_data.get("AcceptedUntil", ""),
            "ComboGraphRelationID": str(
                attack_data.get("ComboGraphRelationID", "")
            ),  # Convert to string
            "created_at": attack_data.get("created_at", ""),
            "deleted_at": json.dumps(
                attack_data.get("deleted_at", {})
            ),  # Convert dict to JSON string
            "DomainSID": attack_data.get("DomainSID", ""),
            "Environment": attack_data.get("Environment", ""),
            "ExposureCount": attack_data.get("ExposureCount", 0),
            "ExposurePercentage": str(
                round(float(attack_data.get("ExposurePercentage", "0")) * 100, 2)
            ),
            "Finding": attack_data.get("Finding", ""),
            "NonTierZeroPrincipalEnvironment": attack_data.get("FromEnvironment", ""),
            "NonTierZeroPrincipalEnvironmentID": attack_data.get(
                "FromEnvironmentID", ""
            ),
            "NonTierZeroPrincipal": attack_data.get("FromPrincipal", ""),
            "NonTierZeroPrincipalKind": attack_data.get("FromPrincipalKind", ""),
            "NonTierZeroPrincipalName": attack_data.get("FromPrincipalName", ""),
            "NonTierZeroPrincipalProps": json.dumps(
                attack_data.get("FromPrincipalProps", {})
            ),  # Convert dict to JSON string
            "id": int(attack_data.get("id", 0)),
            "ImpactCount": attack_data.get("ImpactCount", 0),
            "ImpactPercentage": str(
                round(float(attack_data.get("ImpactPercentage", "0")) * 100, 2)
            ),
            # Convert to string
            "IsInherited": str(attack_data.get("IsInherited", "")),
            "Principal": attack_data.get("ToPrincipal", ""),
            "PrincipalHash": attack_data.get("PrincipalHash", ""),
            "PrincipalKind": attack_data.get("ToPrincipalKind", ""),
            "PrincipalName": attack_data.get("ToPrincipalName", ""),
            "RelProps": json.dumps(
                attack_data.get("RelProps", {})
            ),  # Convert dict to JSON string
            "Severity": attack_data.get("Severity", ""),
            "ImpactedPrincipalEnvironment": attack_data.get(
                "ToEnvironment", attack_data.get("Environment")
            ),
            "ImpactedPrincipalEnvironmentID": attack_data.get("ToEnvironmentID", ""),
            "ImpactedPrincipal": attack_data.get(
                "ToPrincipal", attack_data.get("Principal")
            ),
            "ImpactedPrincipalKind": attack_data.get(
                "ToPrincipalKind", attack_data.get("PrincipalKind")
            ),
            "ImpactedPrincipalName": attack_data.get(
                "ToPrincipalName", attack_data.get("PrincipalName")
            ),
            "ImpactedPrincipalProps": json.dumps(
                attack_data.get("ToPrincipalProps", attack_data.get("Props"))
            ),  # Convert dict to JSON string
            "updated_at": attack_data.get("updated_at", ""),
            "PathTitle": path_title,
            "ShortDescription": short_description,
            "ShortRemediation": short_remediation,
            "LongRemediation": long_remediation,
            "tenant_url": tenant_domain,
            "domain_name": domain_name,
            # Construct URL
            "Remediation": f"{tenant_domain}ui/remediation?findingType={finding_type}",
        }

        self.logger.info(
            f"Preparing to send attack path ID: {log_entry.get('id')} (Finding: {finding_type}, Domain: {domain_name}) to {self.table_name}"
        )
        return self._send_to_azure_monitor(
            log_entry, bearer_token, self.dce_uri, self.dcr_immutable_id, self.table_name
        )

    def send_attack_path_timeline_data(
        self,
        attack_data: dict,
        bearer_token: str,
        unique_finding_types_data: dict,
        domains_data: list,
    ) -> dict:
        """
        Sends attack data to Azure Monitor via Data Collection Endpoint (DCE),
        using the schema format specified for BloodHoundAttackPaths_CL table.
        Uses configuration set via set_azure_monitor_config.

        Args:
            attack_data (dict): Dictionary containing the attack path data.
            bearer_token (str): Azure Monitor API Bearer token.
            unique_finding_types_data (dict): Dictionary containing finding type details.
            domains_data (list): List of domain data dictionaries for domain name lookup.

        Returns:
            dict: Status of the send operation.
        """
        if not all([self.dce_uri, self.dcr_immutable_id, self.table_name]):
            self._log_error(
                "Azure Monitor configuration for sending data is incomplete. Cannot send attack data."
            )
            return {
                "status": "error",
                "message": "Azure Monitor configuration missing.",
            }

        domain_name = ""
        # Find the domain name from the domains_data based on DomainSID
        for domain in domains_data:
            if domain.get("id") == attack_data.get("DomainSID"):
                domain_name = domain.get("name", "")
                break

        finding_type = attack_data.get("Finding", "")
        path_title = unique_finding_types_data.get(finding_type, "")

        log_entry = {
            "CompositeRisk": str(round(float(attack_data.get("CompositeRisk")), 2)),
            "FindingCount": attack_data.get("FindingCount"),
            "ExposureCount": attack_data.get("ExposureCount"),
            "ImpactCount": attack_data.get("ImpactCount"),
            "ImpactedAssetCount": attack_data.get("ImpactedAssetCount"),
            "DomainSID": attack_data.get("DomainSID"),
            "Finding": attack_data.get("Finding"),
            "id": attack_data.get("id"),
            "created_at": attack_data.get("created_at"),
            "updated_at": attack_data.get("updated_at"),
            "deleted_at": attack_data.get("deleted_at"),
            "tenant_url": self.tenant_domain,
            "domain_name": domain_name,
            "path_title": path_title,
            "finding_type": finding_type,
            "TimeGenerated": datetime.datetime.now(datetime.timezone.utc).isoformat(
                timespec="milliseconds"
            )
            + "Z",  # Add TimeGenerated for Azure Monitor
        }

        self.logger.debug(f"Preparing to send log entry: {json.dumps(log_entry)}")
        return self._send_to_azure_monitor(
            log_entry, bearer_token, self.dce_uri, self.dcr_immutable_id, self.table_name
        )
            
    # Tier Zero Assets Functions

    def extract_domain_name(
        self, node_data: dict, properties: dict, name: str, domains_data: list = None
    ) -> str:
        """
        Helper function to extract domain name from various sources.
        Prioritizes domain property, then objectId mapping, then name/distinguishedName parsing.
        """
        # 1. Try 'domain' property directly
        if "domain" in properties:
            return properties["domain"]

        # 2. Try to map 'objectId' or 'owner_objectid' to known domain SIDs/IDs from domains_data
        target_object_id = (
            node_data.get("objectId")
            or properties.get("objectid")
            or properties.get("owner_objectid")
        )
        if target_object_id and domains_data:
            domain_name = next(
                (
                    domain["name"]
                    for domain in domains_data
                    if domain.get("id")
                    == target_object_id  # Assuming 'id' in domains_data matches 'objectId' in some cases
                ),
                None,
            )
            if domain_name:
                return domain_name

        # 3. Parse from 'name' (especially for Azure entities like users/groups)
        if "@" in name:
            return name.split("@")[-1]

        # 4. Parse from 'distinguishedname' for AD entities
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

        # 5. Fallback if no specific domain can be found
        return "UNKNOWN_DOMAIN"

    def extract_name(self, node_data: dict, properties: dict, node_id: str) -> str:
        """
        Helper function to extract a primary name for the asset.
        Prioritizes 'name' property, then 'label', then 'objectid'/node_id.
        """
        # 1. Try 'name' from properties
        if "name" in properties:
            return properties["name"]
        # 2. Try 'label' from node_data
        elif "label" in node_data:
            return node_data["label"]
        # 3. Fallback to 'objectId' or node_id if no better name found
        return str(node_data.get("objectId", node_id))

    def fetch_tier_zero_assets(self) -> dict:
        """
        Posts a Cypher query to the BloodHound Enterprise API to fetch Tier Zero assets.
        """
        cypher_query = "match (n) where (n:Tag_Tier_Zero) or coalesce(n.system_tags,'') contains('admin_tier_0') return n"
        payload = json.dumps(
            {
                "query": cypher_query,
                "include_properties": True,
            }
        )
        self.logger.info("Executing Cypher query to fetch Tier Zero assets...")
        return self._api_request(
            "/api/v2/graphs/cypher", method="POST", payload=payload
        )

    def send_tier_zero_assets_data(
        self,
        node_data: dict,
        bearer_token: str,
        domains_data: list,
    ) -> dict:
        """
        Sends Tier Zero asset data to Azure Monitor via Data Collection Endpoint (DCE),
        using the schema format specified for the custom table.
        Uses configuration set via set_azure_monitor_config.

        Args:
            node_data (dict): Dictionary containing the Tier Zero asset node data.
            bearer_token (str): Azure Monitor API Bearer token.
            domains_data (list): List of domain data dictionaries for domain name lookup.

        Returns:
            dict: Status of the send operation.
        """
        if not all([self.dce_uri, self.dcr_immutable_id, self.table_name]):
            self._log_error(
                "Azure Monitor configuration for sending data is incomplete. Cannot send Tier Zero assets data."
            )
            return {
                "status": "error",
                "message": "Azure Monitor configuration missing.",
            }

        properties = node_data.get("properties", {})
        node_id = node_data.get("nodeId", "")
        name = self.extract_name(node_data, properties, node_id)
        domain_name = self.extract_domain_name(
            node_data, properties, name, domains_data
        )

        # Initialize base log entry with common fields
        log_entry = {
            "nodeId": node_id,
            "label": node_data.get("label", ""),
            "kindType": node_data.get("kind", ""),
            "objectId": node_data.get(
                "objectId", properties.get("owner_objectid", "")
            ),  # Prioritize nodeId's objectId, then properties
            "isTierZero": node_data.get("isTierZero", False),
            "isOwnedObject": node_data.get("isOwnedObject", False),
            "lastSeen": node_data.get("lastSeen", ""),
            "tenant_url": self.tenant_domain,
            "domain_name": domain_name.upper(),  # Ensure domain name is uppercase
            "name": name,
            "TimeGenerated": datetime.datetime.now(datetime.timezone.utc).isoformat(
                timespec="milliseconds"
            )
            + "Z",  # Standard Azure Monitor timestamp
        }

        # Dynamically add all properties from the node
        for prop_key, prop_value in properties.items():
            # Flatten some common nested properties or rename for clarity if needed
            if prop_key == "date":  # Example of specific mapping if desired
                log_entry["Date"] = prop_value
            elif prop_key == "title":
                log_entry["Title"] = prop_value
            else:
                # Add all other properties as is
                log_entry[prop_key] = prop_value

        self.logger.debug(
            f"Preparing to send log entry for node {node_id}: {json.dumps(log_entry)}"
        )
        return self._send_to_azure_monitor(
            log_entry, bearer_token, self.dce_uri, self.dcr_immutable_id, self.table_name
        )