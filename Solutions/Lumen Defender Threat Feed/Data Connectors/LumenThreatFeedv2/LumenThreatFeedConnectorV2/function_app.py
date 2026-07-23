"""Lumen Threat Feed Connector V2 - Azure Functions V2 Programming Model.

This module provides the Azure Functions timer trigger using the V2 programming
model (decorators).
"""

import azure.functions as func
import logging
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    MSALSetup,
    SentinelUploader,
    LumenClientV2,
    LumenAPIError,
    chunks,
    CHUNK_SIZE,
    MAX_PAGES,
    DEFAULT_CONFIDENCE_THRESHOLD,
    POLL_INTERVAL,
    POLL_TIMEOUT,
)

# Create the Function App
app = func.FunctionApp()

logger = logging.getLogger(__name__)


def _parse_bool(value: str) -> bool:
    """Parse string 'true'/'false' to boolean."""
    return value.lower() == 'true'


def _get_confidence(indicator: dict) -> int:
    """Safely extract confidence value as integer.

    API v3 may return confidence as string (e.g., "75") or integer.
    Returns 0 if confidence is missing, invalid, or cannot be converted.
    """
    confidence = indicator.get('confidence')
    if confidence is None:
        return 0
    try:
        return int(confidence)
    except (ValueError, TypeError):
        return 0


def _filter_by_type(indicator: dict, enable_ipv4: bool, enable_domain: bool) -> bool:
    """Check if indicator type is enabled based on its pattern."""
    pattern = indicator.get('pattern', '')
    if 'ipv4-addr' in pattern:
        return enable_ipv4
    elif 'domain-name' in pattern:
        return enable_domain
    return True


def run_sync(
    lumen_client: LumenClientV2,
    uploader: SentinelUploader,
    confidence_threshold: int,
    enable_ipv4: bool,
    enable_domain: bool,
    poll_interval: int,
    poll_timeout: int
) -> dict:
    """Execute the synchronization workflow."""
    logger.info("Starting Lumen Threat Feed sync")

    # Step 1: Initiate query
    logger.info("Step 1: Initiating query")
    cache_id = lumen_client.initiate_query()
    logger.info("Query initiated, cache_id: %s", cache_id[:20] + "...")

    # Step 2: Poll for completion
    logger.info("Step 2: Polling for completion")
    token_id, inline_results = lumen_client.poll_status(cache_id, poll_interval, poll_timeout)

    # Handle case where API returns empty results inline (no pagination needed)
    if token_id is None:
        if inline_results is not None:
            if len(inline_results) == 0:
                logger.info("Query completed with no results - nothing to process")
                return {
                    'total_fetched': 0,
                    'total_filtered': 0,
                    'total_uploaded': 0,
                    'upload_errors': 0,
                    'page_count': 0
                }
            else:
                # Unexpected: inline results with data - process them directly
                logger.warning("Processing %d inline results (unexpected)", len(inline_results))
                # Filter and upload inline results
                filtered = [
                    ind for ind in inline_results
                    if _get_confidence(ind) >= confidence_threshold
                ]
                filtered = [
                    ind for ind in filtered
                    if _filter_by_type(ind, enable_ipv4, enable_domain)
                ]
                total_uploaded = 0
                upload_errors = 0
                for batch in chunks(filtered, CHUNK_SIZE):
                    result = uploader.upload_indicators(batch)
                    total_uploaded += result.get('uploaded_count', 0)
                    upload_errors += result.get('error_count', 0)
                return {
                    'total_fetched': len(inline_results),
                    'total_filtered': len(filtered),
                    'total_uploaded': total_uploaded,
                    'upload_errors': upload_errors,
                    'page_count': 0
                }
        else:
            logger.info("Query completed with no token_id and no results")
            return {
                'total_fetched': 0,
                'total_filtered': 0,
                'total_uploaded': 0,
                'upload_errors': 0,
                'page_count': 0
            }

    logger.info("Query completed, token_id: %s", token_id[:20] + "...")

    # Step 3: Process pages
    logger.info("Step 3: Processing pages")
    total_fetched = 0
    total_filtered = 0
    total_uploaded = 0
    upload_errors = 0
    page_count = 0
    current_token = token_id

    while current_token and page_count < MAX_PAGES:
        page_count += 1
        logger.info("Processing page %d", page_count)

        indicators, next_token = lumen_client.retrieve_page(current_token)
        total_fetched += len(indicators)

        if not indicators:
            logger.info("Page %d: No indicators", page_count)
            current_token = next_token
            continue

        # Filter by confidence (API v3 may return confidence as string)
        filtered = [
            ind for ind in indicators
            if _get_confidence(ind) >= confidence_threshold
        ]

        # Filter by type
        filtered = [
            ind for ind in filtered
            if _filter_by_type(ind, enable_ipv4, enable_domain)
        ]

        total_filtered += len(filtered)
        logger.info("Page %d: %d fetched, %d after filtering",
                   page_count, len(indicators), len(filtered))

        # Upload in batches
        for batch in chunks(filtered, CHUNK_SIZE):
            result = uploader.upload_indicators(batch)
            total_uploaded += result.get('uploaded_count', 0)
            upload_errors += result.get('error_count', 0)

        current_token = next_token

    if page_count >= MAX_PAGES and current_token:
        logger.warning("Reached max pages limit (%d)", MAX_PAGES)

    stats = {
        'total_fetched': total_fetched,
        'total_filtered': total_filtered,
        'total_uploaded': total_uploaded,
        'upload_errors': upload_errors,
        'page_count': page_count
    }

    logger.info("Sync complete: %s", stats)
    return stats


@app.timer_trigger(schedule="0 */15 * * * *", arg_name="timer", run_on_startup=False)
def timer_function(timer: func.TimerRequest) -> None:
    """Timer trigger function for Lumen Threat Feed sync."""
    logger.info("Lumen Threat Feed V2 timer triggered")

    if timer.past_due:
        logger.warning("Timer is past due")

    try:
        # Load required environment variables
        api_key = os.environ.get('LUMEN_API_KEY')
        workspace_id = os.environ.get('WORKSPACE_ID')
        tenant_id = os.environ.get('TENANT_ID')
        client_id = os.environ.get('CLIENT_ID')
        client_secret = os.environ.get('CLIENT_SECRET')

        # Validate required variables
        missing = []
        if not api_key:
            missing.append('LUMEN_API_KEY')
        if not workspace_id:
            missing.append('WORKSPACE_ID')
        if not tenant_id:
            missing.append('TENANT_ID')
        if not client_id:
            missing.append('CLIENT_ID')
        if not client_secret:
            missing.append('CLIENT_SECRET')

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        # Load optional environment variables
        base_url = os.environ.get(
            'LUMEN_BASE_URL',
            'https://microsoft-sentinel-api.us1.mss.lumen.com'
        )
        confidence_threshold = int(os.environ.get(
            'LUMEN_CONFIDENCE_THRESHOLD',
            str(DEFAULT_CONFIDENCE_THRESHOLD)
        ))
        enable_ipv4 = _parse_bool(os.environ.get('LUMEN_ENABLE_IPV4', 'true'))
        enable_domain = _parse_bool(os.environ.get('LUMEN_ENABLE_DOMAIN', 'true'))
        poll_interval = int(os.environ.get('LUMEN_POLL_INTERVAL', str(POLL_INTERVAL)))
        poll_timeout = int(os.environ.get('LUMEN_POLL_TIMEOUT', str(POLL_TIMEOUT)))

        # Initialize clients
        lumen_client = LumenClientV2(api_key, base_url)
        msal_setup = MSALSetup(tenant_id, client_id, client_secret, workspace_id)
        uploader = SentinelUploader(msal_setup)

        # Run sync
        stats = run_sync(
            lumen_client=lumen_client,
            uploader=uploader,
            confidence_threshold=confidence_threshold,
            enable_ipv4=enable_ipv4,
            enable_domain=enable_domain,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout
        )

        logger.info("Lumen Threat Feed V2 sync completed successfully: %s", stats)

    except LumenAPIError as e:
        logger.error("Lumen API error: %s", str(e))
        raise
    except TimeoutError as e:
        logger.error("Timeout error: %s", str(e))
        raise
    except ValueError as e:
        logger.error("Configuration error: %s", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        raise
