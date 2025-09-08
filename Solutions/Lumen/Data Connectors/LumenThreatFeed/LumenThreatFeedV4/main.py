import json
import logging
import os
import requests
import time
import uuid
import ijson
from io import BytesIO
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from msal import ConfidentialClientApplication
from azure.storage.blob import BlobServiceClient

# Configuration for indicator types and environment-based filtering
INDICATOR_TYPES = {
    'ipv4': os.environ.get('LUMEN_ENABLE_IPV4', 'true').lower() == 'true',
    'domain': os.environ.get('LUMEN_ENABLE_DOMAIN', 'true').lower() == 'true'
}

# Filter to only enabled types
INDICATOR_TYPES = {k: v for k, v in INDICATOR_TYPES.items() if v}

# Testing limits (0 = no limit)
MAX_INDICATORS_PER_TYPE = int(os.environ.get('LUMEN_MAX_INDICATORS_PER_TYPE', '0'))
MAX_TOTAL_INDICATORS = int(os.environ.get('LUMEN_MAX_TOTAL_INDICATORS', '0'))

class LumenSetup:
    """Configuration for Lumen API access."""
    
    def __init__(self, api_key: str, base_url: str, max_retries: int = 3):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        
        # Debug logging to verify environment variables
        logging.debug(f"LUMEN_API_KEY loaded: {'***' + self.api_key[-4:] if self.api_key and len(self.api_key) > 4 else 'NOT SET'}")
        logging.debug(f"LUMEN_BASE_URL loaded: {self.base_url}")
        
        if not self.api_key:
            raise ValueError("LUMEN_API_KEY environment variable is required")
        if not self.base_url:
            raise ValueError("LUMEN_BASE_URL environment variable is required")

class MSALSetup:
    """Configuration for Microsoft Authentication Library."""
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, workspace_id: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.workspace_id = workspace_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["https://management.azure.com/.default"]
        
        # Validate required parameters
        required_vars = {
            'TENANT_ID': tenant_id,
            'CLIENT_ID': client_id,
            'CLIENT_SECRET': client_secret,
            'WORKSPACE_ID': workspace_id
        }
        
        for var_name, value in required_vars.items():
            if not value:
                raise ValueError(f"{var_name} environment variable is required")

class LumenSentinelUpdater:
    """Enhanced Lumen threat intelligence connector with blob storage support."""
    
    def __init__(self, lumen_setup: LumenSetup, msal_setup: MSALSetup):
        self.lumen_setup = lumen_setup
        self.msal_setup = msal_setup
        self.access_token = None
        self.token_expiry = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LumenSentinelConnector/4.0',
            'Accept': 'application/json'
        })
        
        # Configure confidence threshold
        self.confidence_threshold = int(os.environ.get('LUMEN_CONFIDENCE_THRESHOLD', '60'))
        
        # Statistics tracking
        self.stats = {
            'run_id': None,
            'start_time': None,
            'indicators_processed': 0,
            'indicators_uploaded': 0,
            'errors': 0,
            'rate_limit_events': 0,
            'processing_time': 0
        }

    def log_config(self):
        """Log current configuration for debugging."""
        enabled_types = [k for k, v in INDICATOR_TYPES.items() if v]
        
        logging.info("=== LUMEN CONNECTOR V4 CONFIGURATION ===")
        logging.info(f"Enabled indicator types: {enabled_types}")
        logging.info(f"Confidence threshold: {self.confidence_threshold}")
        logging.info(f"Max indicators per type: {MAX_INDICATORS_PER_TYPE if MAX_INDICATORS_PER_TYPE > 0 else 'No limit'}")
        logging.info(f"Max total indicators: {MAX_TOTAL_INDICATORS if MAX_TOTAL_INDICATORS > 0 else 'No limit'}")
        logging.info(f"Lumen API base URL: {self.lumen_setup.base_url}")
        logging.info(f"Workspace ID: {self.msal_setup.workspace_id}")
        logging.info("========================================")

    def _get_access_token(self) -> str:
        """Get or refresh Microsoft access token for Sentinel API."""
        now = datetime.utcnow()
        
        # Check if we have a valid token
        if self.access_token and self.token_expiry and now < self.token_expiry:
            return self.access_token
        
        logging.info("Obtaining new access token...")
        
        try:
            app = ConfidentialClientApplication(
                client_id=self.msal_setup.client_id,
                client_credential=self.msal_setup.client_secret,
                authority=self.msal_setup.authority
            )
            
            result = app.acquire_token_for_client(scopes=self.msal_setup.scope)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                # Set expiry to 50 minutes from now (tokens typically last 60 minutes)
                self.token_expiry = now + timedelta(minutes=50)
                logging.info("✓ Access token obtained successfully")
                return self.access_token
            else:
                error_msg = result.get("error_description", result.get("error", "Unknown error"))
                raise Exception(f"Failed to obtain access token: {error_msg}")
                
        except Exception as e:
            logging.error(f"Token acquisition error: {e}")
            raise

    def get_lumen_presigned_urls(self, indicator_types: Dict[str, bool]) -> Dict[str, str]:
        """Get presigned URLs from Lumen API for enabled indicator types."""
        headers = {
            'Authorization': self.lumen_setup.api_key,
            'Content-Type': 'application/json'
        }
        presigned_urls = {}
        
        for indicator_type, enabled in indicator_types.items():
            if not enabled:
                continue
                
            url = f"{self.lumen_setup.base_url}/{indicator_type}"
            
            for attempt in range(self.lumen_setup.max_retries):
                try:
                    logging.info(f"Getting presigned URL for {indicator_type} (attempt {attempt + 1})")
                    
                    response = self.session.get(url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    presigned_url = data.get('url')
                    
                    if presigned_url:
                        presigned_urls[indicator_type] = presigned_url
                        logging.info(f"✓ Got presigned URL for {indicator_type}")
                        break
                    else:
                        raise ValueError(f"No 'url' field in response for {indicator_type}")
                        
                except requests.exceptions.RequestException as e:
                    if attempt == self.lumen_setup.max_retries - 1:
                        logging.error(f"✗ Failed to get presigned URL for {indicator_type}: {e}")
                    else:
                        logging.warning(f"Retry {attempt + 1} for {indicator_type}: {e}")
                        time.sleep(2 ** attempt)
                        
        return presigned_urls

    def stream_and_filter_to_blob(self, container_client, indicator_type: str, presigned_url: str, run_id: str) -> Dict[str, Any]:
        """Stream threat data from Lumen and filter to blob storage."""
        start_time = time.time()
        blob_name = f"{run_id}-{indicator_type}-{uuid.uuid4().hex[:8]}.jsonl"
        
        logging.info(f"Streaming {indicator_type} data to blob: {blob_name}")
        
        # Create blob for writing
        blob_client = container_client.get_blob_client(blob_name)
        
        # Stream and filter data
        filtered_objects = []
        total_downloaded = 0
        filtered_count = 0
        
        try:
            # Download data (simplified approach like V3)
            response = self.session.get(presigned_url, timeout=300)
            response.raise_for_status()
            
            data = response.json()
            logging.info(f"Downloaded {indicator_type} data: {len(str(data))} characters")
            
            # Extract STIX objects from the Lumen response
            if isinstance(data, dict) and 'stixobjects' in data:
                objects_list = data['stixobjects']
                logging.info(f"📊 FILTERING STATS for {indicator_type.upper()}:")
                logging.info(f"   • Total downloaded: {len(objects_list):,} objects")
            else:
                logging.error(f"Unexpected data structure for {indicator_type}: {type(data)}")
                return {
                    'indicator_type': indicator_type,
                    'blob_name': blob_name,
                    'total_downloaded': 0,
                    'filtered_count': 0,
                    'processing_time': time.time() - start_time,
                    'error': 'Unexpected data structure'
                }
            
            for obj in objects_list:
                total_downloaded += 1
                
                # Apply confidence filtering
                confidence = obj.get('confidence', 0)
                if confidence >= self.confidence_threshold:
                    filtered_objects.append(json.dumps(obj) + '\n')
                    filtered_count += 1
                    
                    # Check per-type limit
                    if MAX_INDICATORS_PER_TYPE > 0 and filtered_count >= MAX_INDICATORS_PER_TYPE:
                        logging.info(f"Reached per-type limit for {indicator_type}: {MAX_INDICATORS_PER_TYPE}")
                        break
                    
                    # Upload in chunks to avoid memory issues
                    if len(filtered_objects) >= 1000:
                        chunk_data = ''.join(filtered_objects)
                        if filtered_count == len(filtered_objects):  # First chunk
                            blob_client.upload_blob(chunk_data, overwrite=True)
                        else:  # Append to existing blob
                            existing_data = blob_client.download_blob().readall().decode('utf-8')
                            blob_client.upload_blob(existing_data + chunk_data, overwrite=True)
                        filtered_objects = []
            
            # Upload remaining objects
            if filtered_objects:
                chunk_data = ''.join(filtered_objects)
                if filtered_count == len(filtered_objects):  # Only chunk
                    blob_client.upload_blob(chunk_data, overwrite=True)
                else:  # Append to existing blob
                    existing_data = blob_client.download_blob().readall().decode('utf-8')
                    blob_client.upload_blob(existing_data + chunk_data, overwrite=True)
            
            processing_time = time.time() - start_time
            
            result = {
                'indicator_type': indicator_type,
                'blob_name': blob_name,
                'total_downloaded': total_downloaded,
                'filtered_count': filtered_count,
                'confidence_threshold': self.confidence_threshold,
                'processing_time': processing_time
            }
            
            # Enhanced filtering summary
            filter_rate = (filtered_count / total_downloaded * 100) if total_downloaded > 0 else 0
            logging.info(f"   • Confidence ≥{self.confidence_threshold}: {filtered_count:,} objects ({filter_rate:.1f}%)")
            logging.info(f"   • Processing time: {processing_time:.1f}s")
            logging.info(f"   • Blob created: {blob_name}")
            logging.info(f"📊 SUMMARY: {filtered_count:,} of {total_downloaded:,} {indicator_type} indicators passed filtering")
            
            return result
            
        except Exception as e:
            logging.error(f"Error streaming {indicator_type} to blob: {e}")
            # Try to cleanup partial blob
            try:
                blob_client.delete_blob()
            except:
                pass
            raise

    def upload_indicators_to_sentinel(self, stix_objects: List[Dict], batch_info: str = "") -> Dict[str, int]:
        """Upload STIX indicators to Microsoft Sentinel with enhanced error handling."""
        if not stix_objects:
            return {'uploaded_count': 0, 'error_count': 0, 'throttle_events': 0}
        
        access_token = self._get_access_token()
        
        # Prepare upload URL and headers
        upload_url = f"https://api.ti.sentinel.azure.com/workspaces/{self.msal_setup.workspace_id}/threat-intelligence-stix-objects:upload"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'LumenSentinelConnector/4.0'
        }
        
        params = {'api-version': '2024-02-01-preview'}
        
        # Process in chunks of 100 (Sentinel API limit)
        chunk_size = 100
        uploaded_count = 0
        error_count = 0
        throttle_events = 0
        
        for i in range(0, len(stix_objects), chunk_size):
            chunk = stix_objects[i:i + chunk_size]
            chunk_num = (i // chunk_size) + 1
            total_chunks = (len(stix_objects) + chunk_size - 1) // chunk_size
            
            payload = {
                'sourcesystem': 'Lumen',
                'stixobjects': chunk
            }
            
            max_retries = 3
            retry_delay = 0.5
            
            for attempt in range(max_retries):
                try:
                    logging.debug(f"Uploading chunk {chunk_num}/{total_chunks} {batch_info} "
                                f"({len(chunk)} indicators, attempt {attempt + 1})")
                    
                    response = self.session.post(upload_url, json=payload, headers=headers, params=params, timeout=60)
                    
                    # Log the response details (debug level to reduce noise)
                    logging.debug(f"Sentinel API Response - Status: {response.status_code}")
                    logging.debug(f"Sentinel API Response - Headers: {dict(response.headers)}")
                    if response.status_code != 200:
                        logging.warning(f"Sentinel API Error {response.status_code}: {response.text[:200]}...")
                    else:
                        logging.debug(f"Sentinel API Response - Body: {response.text[:500]}...")
                    
                    if response.status_code == 200:
                        uploaded_count += len(chunk)
                        logging.info(f"✓ Chunk {chunk_num} uploaded successfully {batch_info} - {len(chunk)} indicators")
                        break
                    elif response.status_code == 429:
                        # Rate limiting
                        throttle_events += 1
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logging.warning(f"Rate limited on chunk {chunk_num} {batch_info}, "
                                      f"waiting {retry_after}s")
                        time.sleep(retry_after)
                        continue
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                        if attempt == max_retries - 1:
                            logging.error(f"✗ Chunk {chunk_num} failed {batch_info}: {error_msg}")
                            error_count += len(chunk)
                        else:
                            logging.warning(f"Retry chunk {chunk_num} {batch_info}: {error_msg}")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        logging.error(f"✗ Chunk {chunk_num} network error {batch_info}: {e}")
                        error_count += len(chunk)
                    else:
                        logging.warning(f"Retry chunk {chunk_num} {batch_info}: {e}")
                        time.sleep(retry_delay)
                        retry_delay *= 2
        
        return {
            'uploaded_count': uploaded_count,
            'error_count': error_count,
            'throttle_events': throttle_events
        }
