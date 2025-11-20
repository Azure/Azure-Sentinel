"""
Lumen Threat Intelligence Connector for Microsoft Sentinel
Version: 1.1 (Delta Sync)

This connector integrates Lumen threat intelligence feeds with Microsoft Sentinel.

V1.1 Changes (Delta Sync):
- Migrated from daily full sync to 15-minute delta sync
- New API flow: POST /reputation-query → Poll GET /reputation-query/{cache_id} → Download results
- Combined indicator types (ipv4 + domain) in single endpoint
- Polling: 1-second intervals, 5-minute timeout
- Enhanced statistics tracking (poll attempts, query times)

Architecture:
1. Timer Function (every 15 min): Initiates delta query, downloads results to blob storage
2. Orchestrator: Coordinates parallel upload activities with rate limit handling
3. Activity Functions: Upload indicators from blobs to Sentinel in chunks of 100

Environment Variables:
- LUMEN_API_KEY: API key for Lumen authentication
- LUMEN_BASE_URL: Base URL for delta API endpoint
- LUMEN_CONFIDENCE_THRESHOLD: Minimum confidence score (default: 80)
- LUMEN_MAX_INDICATORS_PER_TYPE: Testing limit per type (0 = no limit)
- LUMEN_MAX_TOTAL_INDICATORS: Testing limit total (0 = no limit)
- TENANT_ID, CLIENT_ID, CLIENT_SECRET, WORKSPACE_ID: Azure/Sentinel credentials
- LUMEN_BLOB_CONNECTION_STRING: Azure Blob Storage connection
- LUMEN_BLOB_CONTAINER: Blob container name (default: lumenthreatfeed)
"""

import json
import logging
import os
import requests
import time
import uuid
import ijson
import tempfile
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

# Upload chunk size (aligns with Sentinel API limit)
CHUNK_SIZE = 100

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
            'User-Agent': 'LumenSentinelConnector/1.1',
            'Accept': 'application/json'
        })
        
        # Configure confidence threshold
        self.confidence_threshold = int(os.environ.get('LUMEN_CONFIDENCE_THRESHOLD', '80'))
        
        # Statistics tracking
        self.stats = {
            'run_id': None,
            'start_time': None,
            'indicators_processed': 0,
            'indicators_uploaded': 0,
            'errors': 0,
            'rate_limit_events': 0,
            'processing_time': 0,
            'delta_query_time': 0,
            'poll_attempts': 0,
            'cache_query_time': 0
        }

    def log_config(self):
        """Log current configuration for debugging."""
        enabled_types = [k for k, v in INDICATOR_TYPES.items() if v]
        
        logging.debug("=== LUMEN CONNECTOR V1.1 (DELTA SYNC) ===")
        logging.debug(f"Mode: Delta sync (15-minute intervals)")
        logging.debug(f"Enabled indicator types: {enabled_types if enabled_types else 'All types (combined endpoint)'}")
        logging.debug(f"Confidence threshold: {self.confidence_threshold}")
        logging.debug(f"Max indicators per type: {MAX_INDICATORS_PER_TYPE if MAX_INDICATORS_PER_TYPE > 0 else 'No limit'}")
        logging.debug(f"Max total indicators: {MAX_TOTAL_INDICATORS if MAX_TOTAL_INDICATORS > 0 else 'No limit'}")
        logging.debug(f"Lumen API base URL: {self.lumen_setup.base_url}")
        logging.debug(f"Workspace ID: {self.msal_setup.workspace_id}")
        logging.debug("=========================================")

    def _get_access_token(self) -> str:
        """Get or refresh Microsoft access token for Sentinel API."""
        now = datetime.utcnow()
        
        # Check if we have a valid token
        if self.access_token and self.token_expiry and now < self.token_expiry:
            return self.access_token
        
        logging.debug("Obtaining new access token...")
        
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
                logging.debug("✓ Access token obtained successfully")
                return self.access_token
            else:
                error_msg = result.get("error_description", result.get("error", "Unknown error"))
                raise Exception(f"Failed to obtain access token: {error_msg}")
                
        except Exception as e:
            logging.error(f"Token acquisition error: {e}")
            raise

    def initiate_delta_query(self) -> str:
        """POST to /reputation-query endpoint to initiate delta query.
        
        Returns:
            cache_id (str): The cache ID to use for polling
            
        Raises:
            Exception: If POST fails or response doesn't contain cache_id
        """
        headers = {
            'Authorization': self.lumen_setup.api_key,
            'Content-Type': 'application/json'
        }
        
        url = self.lumen_setup.base_url
        
        for attempt in range(self.lumen_setup.max_retries):
            try:
                logging.info(f"Initiating delta query (attempt {attempt + 1})")
                
                response = self.session.post(url, headers=headers, json={}, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                cache_id = data.get('cache_id')
                
                if cache_id:
                    logging.debug(f"✓ Delta query initiated, cache_id: {cache_id}")
                    return cache_id
                else:
                    raise ValueError("No 'cache_id' field in POST response")
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.lumen_setup.max_retries - 1:
                    logging.error(f"✗ Failed to initiate delta query: {e}")
                    raise
                else:
                    logging.warning(f"Retry {attempt + 1} for delta query initiation: {e}")
                    time.sleep(2 ** attempt)

    def poll_query_status(self, cache_id: str, timeout: int = 300, poll_interval: int = 1) -> Dict[str, Any]:
        """Poll GET /reputation-query/{cache_id} until status is COMPLETED or timeout.
        
        Args:
            cache_id: The cache ID from initiate_delta_query
            timeout: Maximum time to wait in seconds (default 300 = 5 minutes)
            poll_interval: Time between polls in seconds (default 1 second)
            
        Returns:
            dict: Response containing 'status' and 'results' (presigned URL)
            
        Raises:
            TimeoutError: If polling exceeds timeout
            Exception: If polling fails
        """
        headers = {
            'Authorization': self.lumen_setup.api_key,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.lumen_setup.base_url}/{cache_id}"
        start_time = time.time()
        poll_count = 0
        
        logging.info(f"Polling for query completion (timeout: {timeout}s, interval: {poll_interval}s)")
        
        while True:
            poll_count += 1
            elapsed = time.time() - start_time
            
            if elapsed > timeout:
                error_msg = f"Polling timeout after {elapsed:.1f}s ({poll_count} attempts)"
                logging.error(f"✗ {error_msg}")
                raise TimeoutError(error_msg)
            
            try:
                response = self.session.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                status = data.get('status', '').upper()
                
                if response.status_code == 200 and status == 'COMPLETED':
                    results_url = data.get('results')
                    if not results_url:
                        raise ValueError("COMPLETED response missing 'results' field")
                    
                    self.stats['poll_attempts'] = poll_count
                    self.stats['cache_query_time'] = elapsed
                    
                    logging.info(f"✓ Query completed after {elapsed:.1f}s ({poll_count} polls)")
                    logging.debug(f"Results URL obtained: {results_url[:80]}...")
                    return data
                    
                elif response.status_code == 202:
                    # Still processing
                    if poll_count % 10 == 0:  # Log every 10 polls to reduce noise
                        logging.info(f"Poll #{poll_count}: Status {status} (elapsed: {elapsed:.1f}s)")
                    time.sleep(poll_interval)
                    continue
                    
                else:
                    raise ValueError(f"Unexpected response: status_code={response.status_code}, status={status}")
                    
            except requests.exceptions.RequestException as e:
                logging.warning(f"Poll attempt {poll_count} failed: {e}")
                time.sleep(poll_interval)
                continue

    def get_delta_results_url(self) -> str:
        """Orchestrate the full delta query flow: POST → Poll → Extract presigned URL.
        
        Returns:
            str: Presigned URL for downloading delta results
            
        Raises:
            Exception: If any step fails
        """
        start_time = time.time()
        
        logging.info("=== STARTING DELTA QUERY FLOW ===")
        
        # Step 1: Initiate query
        cache_id = self.initiate_delta_query()
        
        # Step 2: Poll until completed
        response = self.poll_query_status(cache_id)
        
        # Step 3: Extract results URL
        results_url = response.get('results')
        
        total_time = time.time() - start_time
        self.stats['delta_query_time'] = total_time
        
        logging.info(f"=== DELTA QUERY COMPLETE ({total_time:.1f}s) ===")
        
        return results_url

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

    def stream_and_filter_to_blob(self, container_client, indicator_type: str, presigned_url: str, run_id: str, max_remaining: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Stream threat data from Lumen and write filtered indicators into chunked JSONL blobs of size CHUNK_SIZE.
        Returns a list of chunk descriptors: [{ indicator_type, blob_name, filtered_count, ... }]
        If max_remaining is provided (>0), stop accepting new indicators once that budget is exhausted.
        """
        start_time = time.time()
        blob_name = f"{run_id}-{indicator_type}-{uuid.uuid4().hex[:8]}.jsonl"

        logging.debug(f"Streaming {indicator_type} data to blob: {blob_name}")

        total_downloaded = 0
        filtered_total = 0
        # How many indicators we can still accept globally for this call; None means unlimited
        remaining_budget = max_remaining if (isinstance(max_remaining, int) and max_remaining > 0) else None
        chunks: List[Dict[str, Any]] = []
        chunk_index = 0
        chunk_count = 0
        tmp = None
        tmp_path = None
        
        def start_new_chunk():
            nonlocal tmp, tmp_path, chunk_index, chunk_count, blob_name
            if tmp is not None:
                try:
                    tmp.close()
                except Exception:
                    pass
            chunk_index += 1
            chunk_count = 0
            # Name per chunk
            blob_name = f"{run_id}-{indicator_type}-{uuid.uuid4().hex[:8]}-part-{chunk_index:05d}.jsonl"
            tmp = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False)
            tmp_path = tmp.name

        def finalize_current_chunk():
            nonlocal tmp, tmp_path, chunk_count, filtered_total
            if tmp is None:
                return None
            try:
                tmp.flush()
                os.fsync(tmp.fileno())
            except Exception:
                pass
            finally:
                try:
                    tmp.close()
                except Exception:
                    pass
            # Upload if wrote anything
            if chunk_count > 0 and tmp_path and os.path.exists(tmp_path):
                try:
                    blob_client_local = container_client.get_blob_client(blob_name)
                    with open(tmp_path, 'rb') as f:
                        blob_client_local.upload_blob(f, overwrite=True)
                    chunks.append({
                        'indicator_type': indicator_type,
                        'blob_name': blob_name,
                        'filtered_count': chunk_count,
                        'confidence_threshold': self.confidence_threshold
                    })
                    filtered_total += chunk_count
                finally:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

        # Begin first chunk
        start_new_chunk()
        
        try:
            try:
                # Stream response
                response = self.session.get(presigned_url, stream=True, timeout=(10, 300))
                logging.debug(
                    "Presigned GET status=%s, content-type=%s, length=%s",
                    response.status_code,
                    response.headers.get('Content-Type'),
                    response.headers.get('Content-Length')
                )
                response.raise_for_status()

                # Check if response is empty
                if not response.content and response.status_code == 200:
                    logging.warning(f"Empty response from presigned URL for {indicator_type}")
                    logging.info(f"Response headers: {dict(response.headers)}")
                    return chunks  # Return empty chunks list

                # For small responses or debugging, try reading as text first
                response_text = response.text
                
                if not response_text or len(response_text.strip()) == 0:
                    logging.warning(f"Empty or whitespace-only response for {indicator_type}")
                    return chunks

                logging.debug(f"Response size: {len(response_text)} bytes")
                logging.debug(f"Response preview (first 500 chars): {response_text[:500]}")

                parsed_any = False

                def handle_obj(obj: Dict[str, Any]):
                    nonlocal total_downloaded, chunk_count, remaining_budget
                    total_downloaded += 1
                    confidence = obj.get('confidence', 0)
                    if confidence >= self.confidence_threshold:
                        # Enforce global remaining budget if provided
                        if remaining_budget is not None and remaining_budget <= 0:
                            return True  # signal to stop
                        tmp.write(json.dumps(obj))
                        tmp.write('\n')
                        chunk_count += 1
                        if remaining_budget is not None:
                            remaining_budget -= 1
                        # Rotate per-chunk
                        if chunk_count >= CHUNK_SIZE:
                            finalize_current_chunk()
                            start_new_chunk()
                        # Per-type limit (for testing)
                        if MAX_INDICATORS_PER_TYPE > 0 and (filtered_total + chunk_count) >= MAX_INDICATORS_PER_TYPE:
                            return True  # signal to stop
                    return False

                # Parse the JSON response
                try:
                    data = json.loads(response_text)
                    logging.debug(f"Successfully parsed JSON. Type: {type(data)}")
                    
                    if isinstance(data, dict):
                        if 'stixobjects' in data:
                            stix_objects = data['stixobjects']
                            logging.debug(f"Found 'stixobjects' array with {len(stix_objects)} items")
                            for obj in stix_objects:
                                parsed_any = True
                                if handle_obj(obj):
                                    break
                        else:
                            logging.warning(f"Response is a dict but missing 'stixobjects' key. Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        logging.debug(f"Response is a list with {len(data)} items")
                        for obj in data:
                            parsed_any = True
                            if handle_obj(obj):
                                break
                    else:
                        raise ValueError(f"Unexpected response type: {type(data)}")
                    
                    if not parsed_any:
                        logging.warning(f"No indicators were parsed from response")
                        
                except json.JSONDecodeError as jde:
                    logging.error(f"JSON decode error for {indicator_type}: {jde}")
                    logging.error(f"Response text (first 1000 chars): {response_text[:1000]}")
                    raise

            except Exception as e:
                logging.error(f"Error streaming {indicator_type} to blob: {e}")
                raise
            finally:
                # finalize last partial chunk
                finalize_current_chunk()

        except Exception:
            # Ensure any open temp file is removed
            try:
                if tmp is not None:
                    tmp.close()
            except Exception:
                pass
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            raise

        processing_time = time.time() - start_time
        filter_rate = (filtered_total / total_downloaded * 100) if total_downloaded > 0 else 0
        logging.debug(f"   • Confidence ≥{self.confidence_threshold}: {filtered_total:,} objects ({filter_rate:.1f}%)")
        logging.debug(f"   • Processing time: {processing_time:.1f}s")
        logging.debug(f"   • Chunks created: {len(chunks)}")
        logging.info(f"📊 SUMMARY: {filtered_total:,} of {total_downloaded:,} {indicator_type} indicators passed filtering in {len(chunks)} chunk(s)")

        return chunks

    def upload_indicators_to_sentinel(self, stix_objects: List[Dict], batch_info: str = "", external_backoff: bool = False) -> Dict[str, Any]:
        """Upload STIX indicators to Microsoft Sentinel with enhanced error handling."""
        if not stix_objects:
            return {'uploaded_count': 0, 'error_count': 0, 'throttle_events': 0}

        access_token = self._get_access_token()

        # Prepare upload URL and headers
        upload_url = (
            f"https://api.ti.sentinel.azure.com/workspaces/{self.msal_setup.workspace_id}/"
            "threat-intelligence-stix-objects:upload"
        )

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'LumenSentinelConnector/1.1'
        }

        params = {'api-version': '2024-02-01-preview'}

        # Process in chunks of 100 (Sentinel API limit)
        chunk_size = CHUNK_SIZE
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
            
            # Log a sample indicator to verify format
            if chunk_num == 1 and len(chunk) > 0:
                logging.debug(f"Sample indicator being sent: {json.dumps(chunk[0], indent=2)[:500]}")

            max_retries = 3
            retry_delay = 0.5

            for attempt in range(max_retries):
                try:
                    logging.info(
                        f"Uploading chunk {chunk_num}/{total_chunks} {batch_info} "
                        f"({len(chunk)} indicators, attempt {attempt + 1})"
                    )

                    response = self.session.post(
                        upload_url, json=payload, headers=headers, params=params, timeout=60
                    )

                    # Log the response details
                    logging.info(f"Sentinel API Response - Status: {response.status_code}")
                    logging.debug(f"Sentinel API Response - Headers: {dict(response.headers)}")
                    
                    # ALWAYS log the response body for 200s to see what Sentinel says
                    if response.status_code == 200:
                        logging.debug(f"Sentinel API Response Body: {response.text[:1000]}")
                    else:
                        logging.warning(
                            f"Sentinel API Error {response.status_code}: {response.text[:200]}..."
                        )

                    if response.status_code == 200:
                        uploaded_count += len(chunk)
                        logging.info(
                            f"✓ Chunk {chunk_num} uploaded successfully {batch_info} - {len(chunk)} indicators"
                        )
                        break
                    elif response.status_code == 429:
                        # Rate limiting
                        throttle_events += 1
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logging.warning(f"Rate limited on chunk {chunk_num} {batch_info}")
                        if external_backoff:
                            # Let the orchestrator manage backoff deterministically
                            return {
                                'uploaded_count': uploaded_count,
                                'error_count': error_count,
                                'throttle_events': throttle_events,
                                'throttled': True,
                                'retry_after': retry_after
                            }
                        else:
                            logging.warning(
                                f"Sleeping {retry_after}s inside activity (internal backoff)"
                            )
                            time.sleep(retry_after)
                            continue
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                        if attempt == max_retries - 1:
                            logging.error(
                                f"✗ Chunk {chunk_num} failed {batch_info}: {error_msg}"
                            )
                            error_count += len(chunk)
                        else:
                            logging.warning(
                                f"Retry chunk {chunk_num} {batch_info}: {error_msg}"
                            )
                            time.sleep(retry_delay)
                            retry_delay *= 2

                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        logging.error(
                            f"✗ Chunk {chunk_num} network error {batch_info}: {e}"
                        )
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
