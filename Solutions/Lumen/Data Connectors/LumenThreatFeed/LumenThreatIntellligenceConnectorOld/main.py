import datetime
import json
import logging
import os
import sys
import time
import re
from collections import namedtuple
from typing import List, Dict, Any

import azure.functions as func
import msal
import requests
from requests.adapters import HTTPAdapter
from requests_ratelimiter import LimiterSession
from urllib3.util import Retry


# Required environment variables for the Lumen-Sentinel integration
# These must be configured in the Azure Function App settings
REQUIRED_ENVIRONMENT_VARIABLES = [
    "LUMEN_API_KEY",        # API key for Lumen threat intelligence service
    "LUMEN_BASE_URL",       # Base URL for Lumen API endpoints 
    "CLIENT_ID",            # Azure AD application (client) ID
    "CLIENT_SECRET",        # Azure AD application client secret
    "TENANT_ID",            # Azure AD tenant ID
    "WORKSPACE_ID",         # Microsoft Sentinel workspace ID
]

# Indicator types to process (both IPv4 and domain indicators)
INDICATOR_TYPES = ["ipv4"]

# Configuration containers for cleaner parameter passing
LumenSetup = namedtuple("LumenSetup", ["api_key", "base_url", "tries"])
MSALSetup = namedtuple("MSALSetup", ["tenant_id", "client_id", "client_secret", "workspace_id"])

class LumenSentinelUpdater:
    """
    Lumen Threat Intelligence to Microsoft Sentinel STIX Objects uploader.
    
    This class handles the complete pipeline for ingesting threat intelligence data
    from Lumen's API and uploading it to Microsoft Sentinel using the STIX Objects API.
    
    Key Features:
    - Rate-limited HTTP requests to respect API quotas
    - Automatic retry logic for transient failures  
    - MSAL-based authentication for Microsoft APIs
    - Batch processing to handle large datasets
    - Comprehensive error handling and logging
    
    API Limits & Rate Limiting:
    - Sentinel STIX API: 100 requests/minute, 100 objects per request
    - Implements conservative rate limiting (95 requests/minute) for safety
    - Uses exponential backoff retry strategy for 429/5xx errors
    
    Authentication:
    - Uses MSAL (Microsoft Authentication Library) for token acquisition
    - Supports both silent token refresh and new token acquisition
    - Handles token expiry and renewal automatically
    """

    def __init__(self, lumen_setup: LumenSetup, msal_setup: MSALSetup):
        """
        Initialize the Lumen-Sentinel updater with configuration and HTTP session.
        
        Args:
            lumen_setup (LumenSetup): Lumen API configuration (key, URL, retry count)
            msal_setup (MSALSetup): Microsoft authentication configuration
        """
        super(LumenSentinelUpdater, self).__init__()

        # Store Lumen API configuration
        self.lumen_api_key = lumen_setup.api_key
        self.lumen_base_url = lumen_setup.base_url
        self.lumen_tries = lumen_setup.tries
        
        # Store Microsoft authentication configuration
        self.msal_tenant_id = msal_setup.tenant_id
        self.msal_client_id = msal_setup.client_id
        self.msal_client_secret = msal_setup.client_secret
        self.msal_workspace_id = msal_setup.workspace_id

        # Setup rate-limited HTTP session with retry strategy
        # Configured for Sentinel STIX Objects API limits: 100 requests/minute, 100 objects/request
        self.limiter_session = LimiterSession(
            per_minute=95,  # Conservative limit to avoid 429 errors
            limit_statuses=[429, 503],  # Status codes that trigger rate limiting
        )
        
        # Configure retry strategy for transient failures
        retry_strategy = Retry(
            total=3,                                          # Maximum number of retries
            status_forcelist=[429, 500, 502, 503, 504],      # HTTP status codes to retry
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"], # HTTP methods to retry
            backoff_factor=1                                  # Exponential backoff multiplier
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.limiter_session.mount("http://", adapter)
        self.limiter_session.mount("https://", adapter)

        # Authentication state - managed by acquire_token() method
        self.bearer_token = None
        self.token_expiry_seconds = None

    def get_lumen_presigned_urls(self, indicator_types: List[str]) -> Dict[str, str]:
        """
        Retrieve presigned URLs from Lumen's API for downloading threat intelligence data.
        
        This method makes GET requests to Lumen's presigned URL endpoints for each indicator type,
        which returns temporary URLs that can be used to download the latest threat intelligence data files.
        
        Args:
            indicator_types (List[str]): List of indicator types to fetch (e.g., ['ipv4', 'domain'])
        
        Returns:
            Dict[str, str]: Dictionary mapping indicator types to their presigned URLs
            
        Raises:
            requests.exceptions.RequestException: If any API request fails
            ValueError: If any response doesn't contain a valid URL
            
        """
        headers = {
            'Authorization': self.lumen_api_key,  # Changed from 'x-api-key' to 'Authorization'
            'Content-Type': 'application/json'
        }
        
        presigned_urls = {}
        
        for indicator_type in indicator_types:
            # Construct URL for each indicator type
            url = f"{self.lumen_base_url}/{indicator_type}"
            
            try:
                logging.info(f"Getting presigned URL for {indicator_type} indicators...")
                
                # Make GET request to get the presigned URL 
                response = self.limiter_session.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Parse response and extract the presigned URL
                data = response.json()
                presigned_url = data.get('url')
                
                if not presigned_url:
                    raise ValueError(f"No 'url' field found in Lumen API response for {indicator_type}")
                    
                presigned_urls[indicator_type] = presigned_url
                logging.info(f"Successfully obtained presigned URL for {indicator_type} indicators")
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Error getting presigned URL for {indicator_type} from Lumen API: {str(e)}", exc_info=True)
                raise
        
        return presigned_urls

    def get_lumen_threat_data(self, presigned_url: str) -> Dict[str, Any]:
        """
        Download threat intelligence data from Lumen using a presigned URL.
        
        This method downloads the actual threat intelligence data file from the presigned URL
        obtained from get_lumen_presigned_url().
        
        Args:
            presigned_url (str): The presigned URL from Lumen API
            
        Returns:
            Dict[str, Any]: The threat intelligence data in STIX format, typically containing
                           a 'stixobjects' key with a list of threat intelligence indicators
            
        Raises:
            requests.exceptions.RequestException: If the download request fails
            json.JSONDecodeError: If the downloaded content is not valid JSON
            
        Note:
            Uses a 5-minute timeout to accommodate large file downloads.
            The response content is logged (first 500 chars) for debugging if parsing fails.
        """
        try:
            # Download threat intelligence data with extended timeout for large files
            response = self.limiter_session.get(presigned_url, timeout=300)  # 5 min timeout
            response.raise_for_status()
            
            try:
                # Parse JSON response and log success metrics
                data = response.json()
                data_size = len(str(data))
                logging.info(f"Successfully downloaded threat data from Lumen. Data size: {data_size} characters")
                return data
            except json.JSONDecodeError as e:
                # Log parsing errors with response content for debugging
                logging.error(f"Error parsing JSON response from presigned URL: {str(e)}")
                logging.error(f"Response content (first 500 chars): {response.content[:500]}")
                raise
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading threat data from presigned URL: {str(e)}", exc_info=True)
            if 'response' in locals():
                logging.error(f"HTTP status: {response.status_code}")
                logging.error(f"Response content (first 500 chars): {response.content[:500]}")
            raise

    def acquire_token(self):
        """
        Acquire Microsoft Entra access token using MSAL for authenticating with Sentinel API.
        
        This method handles both silent token refresh (if a cached token exists) and new
        token acquisition using client credentials flow. The token is required for all
        Microsoft Sentinel API calls.
        
        Returns:
            tuple: A tuple containing (bearer_token: str, token_expiry_seconds: int)
            
        Raises:
            ValueError: If token acquisition fails or returns an error
            Exception: For other authentication-related errors
            
        Note:
            Uses the client credentials flow suitable for daemon/service applications.
            Tokens are typically valid for 60-90 minutes.
        """
        try:
            # Configure OAuth scope for Azure Management API
            scope = ["https://management.azure.com/.default"]
            
            # Create MSAL confidential client application
            context = msal.ConfidentialClientApplication(
                self.msal_client_id, 
                authority=f"https://login.microsoftonline.com/{self.msal_tenant_id}",
                client_credential=self.msal_client_secret
            )
            
            # Attempt silent token acquisition first (uses cache)
            result = context.acquire_token_silent(scopes=scope, account=None)
            if not result:
                # Fall back to new token acquisition if silent fails
                result = context.acquire_token_for_client(scopes=scope)

            # Process the authentication result
            if 'access_token' in result:
                bearer_token = result['access_token']
                token_expiry_seconds = result['expires_in']
                logging.debug("Successfully acquired Microsoft Entra access token")
                return bearer_token, token_expiry_seconds
            else:
                # Log and raise authentication errors
                error_code = result.get("error")
                error_message = result.get("error_description")
                logging.error(f"Error acquiring token: {error_code} - {error_message}")
                raise ValueError(error_message)

        except Exception as e:
            logging.error(f"Error acquiring token: {str(e)}", exc_info=True)
            raise

    def upload_stix_objects_to_sentinel(self, token: str, stix_objects: List[Dict[str, Any]]) -> requests.Response:
        """
        Upload STIX objects to Microsoft Sentinel using the STIX Objects API.
        
        This method uploads a batch of STIX threat intelligence objects to Microsoft Sentinel.
        The API has specific limits: maximum 100 objects per request, 100 requests per minute.
        
        Args:
            token (str): The Bearer authentication token for Microsoft APIs
            stix_objects (List[Dict[str, Any]]): List of STIX objects to upload (max 100)
            
        Returns:
            requests.Response: The HTTP response from the Sentinel API
            
        Raises:
            requests.exceptions.RequestException: If the HTTP request fails
            ValueError: If the API returns an error status code
            
        """
        # Sentinel STIX Objects API endpoint (preview version)
        url = f"https://api.ti.sentinel.azure.com/workspaces/{self.msal_workspace_id}/threat-intelligence-stix-objects:upload"
        
        # Configure request headers with authentication and content type
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        # API version parameter (required for Sentinel APIs)
        params = {
            'api-version': '2024-02-01-preview'
        }        # Request payload in the format expected by Sentinel STIX Objects API        
        payload = {
            'sourcesystem': 'Lumen',              # Source system identifier
            'stixobjects': stix_objects           # Array of STIX objects to upload
        }
        
        try:
            # Make POST request to upload STIX objects
            response = self.limiter_session.post(
                url, 
                headers=headers,
                params=params,
                json=payload,
                timeout=30            )
            
            # Handle successful response (200 OK)
            if response.status_code == 200:
                logging.debug(f"Successfully uploaded {len(stix_objects)} STIX objects to Sentinel")
            else:
                # Log and raise errors for non-200 status codes
                logging.error(f"Upload failed with status {response.status_code}: {response.text}")
                raise ValueError(f"Failed to upload STIX objects: {response.status_code}")
                
            return response
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error uploading STIX objects to Sentinel: {str(e)}", exc_info=True)
            raise

    def process_lumen_data(self, indicator_types: List[str]) -> int:
        """
        Main processing function to orchestrate the complete Lumen-to-Sentinel pipeline.
        
        This method coordinates the entire process:
        1. Obtains presigned URLs from Lumen API for each indicator type
        2. Downloads threat intelligence data for each type
        3. Validates and cleans STIX objects
        4. Acquires authentication token for Sentinel
        5. Uploads data in batches respecting API limits
        
        Args:
            indicator_types (List[str]): List of indicator types to process (e.g., ['ipv4', 'domain'])
        
        Returns:
            int: Total number of STIX objects successfully processed and uploaded
            
        Raises:
            Exception: For any step that fails in the pipeline
            
        Note:
            Implements batch processing (100 objects per batch) and rate limiting
            (95 requests/minute) to stay within Sentinel API quotas.
        """
        total_processed = 0
        all_stix_objects = []
        
        try:
            # Step 1: Get presigned URLs from Lumen API for each indicator type
            logging.info(f"Getting presigned URLs for indicator types: {', '.join(indicator_types)}")
            presigned_urls = self.get_lumen_presigned_urls(indicator_types)
            
            # Step 2: Download threat data from each presigned URL
            for indicator_type, presigned_url in presigned_urls.items():
                logging.info(f"Downloading threat intelligence data for {indicator_type}...")
                threat_data = self.get_lumen_threat_data(presigned_url)
                
                # Step 3: Extract and validate STIX objects from the response
                stix_objects = threat_data.get('stixobjects', [])
                if not stix_objects:
                    logging.warning(f"No STIX objects found in Lumen threat data for {indicator_type}")
                    continue
                    
                logging.info(f"Found {len(stix_objects)} STIX objects for {indicator_type}")
                all_stix_objects.extend(stix_objects)

            if not all_stix_objects:
                logging.warning("No STIX objects found in any Lumen threat data")
                return 0
                
            logging.info(f"Total STIX objects collected: {len(all_stix_objects)}")

            # Step 4: Acquire authentication token for Sentinel API
            if not self.bearer_token:
                self.bearer_token, self.token_expiry_seconds = self.acquire_token()

            # Step 5: Upload STIX objects in batches (API limit: 100 objects per request)
            batch_size = 100
            for i in range(0, len(all_stix_objects), batch_size):
                batch = all_stix_objects[i:i + batch_size]
                batch_number = i // batch_size + 1
                logging.info(f"Uploading batch {batch_number} ({len(batch)} objects)...")
                try:
                    response = self.upload_stix_objects_to_sentinel(self.bearer_token, batch)
                    if response.status_code == 200:
                        total_processed += len(batch)
                        logging.debug(f"Successfully uploaded batch {batch_number}")
                    else:
                        logging.error(f"Failed to upload batch {batch_number}: {response.status_code}")
                except Exception as e:
                    logging.error(f"Error uploading batch {batch_number}: {str(e)}")
                    continue
                time.sleep(0.7)
            logging.info(f"Processing complete. Total STIX objects processed: {total_processed}")
            return total_processed
        except Exception as e:
            logging.error(f"Error in process_lumen_data: {str(e)}", exc_info=True)
            raise


def main(mytimer: func.TimerRequest) -> None:
    """
    Azure Function main entry point for the Lumen Threat Intelligence Connector.
    
    This function is triggered by a timer and orchestrates the complete process of
    downloading threat intelligence data from Lumen and uploading it to Microsoft Sentinel.
    
    Args:
        mytimer (func.TimerRequest): Azure Functions timer trigger object
        
    Environment Variables Required:
        - LUMEN_API_KEY: API key for Lumen threat intelligence service
        - LUMEN_BASE_URL: Base URL for Lumen API endpoints
        - CLIENT_ID: Azure AD application (client) ID
        - CLIENT_SECRET: Azure AD application client secret  
        - TENANT_ID: Azure AD tenant ID
        - WORKSPACE_ID: Microsoft Sentinel workspace ID
        
    Note:
        Function will exit with status code 1 if required environment variables
        are missing or if the process fails.
    """
    # Log execution timestamp
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info(f'Lumen Threat Intelligence Connector executed at: {utc_timestamp}')

    # Validate all required environment variables are present
    missing_vars = []
    for var in REQUIRED_ENVIRONMENT_VARIABLES:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)

    try:
        # Use hardcoded indicator types (both IPv4 and domain)
        logging.info(f"Processing indicator types: {', '.join(INDICATOR_TYPES)}")
        
        # Initialize Lumen API configuration
        lumen_setup = LumenSetup(
            api_key=os.environ.get("LUMEN_API_KEY"),
            base_url=os.environ.get("LUMEN_BASE_URL"),
            tries=3
        )
        
        # Initialize Microsoft authentication configuration
        msal_setup = MSALSetup(
            tenant_id=os.environ.get("TENANT_ID"),
            client_id=os.environ.get("CLIENT_ID"),
            client_secret=os.environ.get("CLIENT_SECRET"),
            workspace_id=os.environ.get("WORKSPACE_ID")
        )

        # Initialize and run the threat intelligence updater
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)
        processed_count = updater.process_lumen_data(INDICATOR_TYPES)
        
        logging.info(f"Lumen Threat Intelligence Connector completed successfully. "
                    f"Processed {processed_count} STIX objects.")

    except Exception as e:
        logging.error(f"Lumen Threat Intelligence Connector failed: {str(e)}", exc_info=True)
        sys.exit(1)
