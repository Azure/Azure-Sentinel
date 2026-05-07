"""Configuration constants for Google SecOps Detection Alerts connector.

This module defines all environment variables, defaults, and tuning parameters
for the two-function pipeline that fetches detections from Google SecOps
and ingests them into Microsoft Sentinel.

Pipeline Overview:
  1. GoogleSecOpsToStorage: Polls SecOps API → saves to Azure File Share
  2. AzureStorageToSentinel: Monitors share → posts to Sentinel via DCR API
"""

import os

# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION METADATA
# ═══════════════════════════════════════════════════════════════════════════════
# Used for logging and identification across both functions

LOG_PREFIX = "GoogleSecOpsDetectionAlerts"  # Prefix for all log messages
LOG_LEVEL = os.environ.get("LogLevel", "INFO")  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "{}(method = {}) : {} : {}"  # Format: PREFIX(method) : FUNCTION : MESSAGE

FUNCTION_NAME_FETCHER = "GoogleSecOpsToStorage"  # First function (SecOps → Storage)
FUNCTION_NAME_INGESTER = (
    "AzureStorageToSentinel"  # Second function (Storage → Sentinel)
)

# ═══════════════════════════════════════════════════════════════════════════════
#  GOOGLE SECOPS API CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
# Required: Set via ARM template or environment variables
# These connect to your Google SecOps instance

GOOGLE_SECOPS_PROJECT_ID = os.environ.get("GoogleSecopsProjectId", "")
GOOGLE_SECOPS_REGION = os.environ.get("GoogleSecopsRegion", "us")  # us, europe, asia-southeast1
GOOGLE_SECOPS_INSTANCE_ID = os.environ.get("GoogleSecopsInstanceId", "")
SERVICE_ACCOUNT_JSON = os.environ.get("GoogleSecopsServiceAccountJson", "")

# Google OAuth configuration for Google SecOps API authentication
OAUTH_SCOPE = os.environ.get(
    "OAuthScope", "https://www.googleapis.com/auth/cloud-platform"
)
TOKEN_EXPIRY_BUFFER_SECONDS = 60  # Refresh token 60s before expiry


# ═══════════════════════════════════════════════════════════════════════════════
# AZURE STORAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
# File shares for checkpoint tracking and raw data storage

CONN_STRING = os.environ.get(
    "AzureWebJobsStorage", ""
)  # Storage account connection string

# State management (checkpoint tracking)
FILE_SHARE_NAME = os.environ.get("FileShareName", "google-secops-state")
CHECKPOINT_FILE_NAME = os.environ.get("CheckpointFileName", "google_secops_checkpoint")

# Raw detection data (buffering between functions)
FILE_SHARE_NAME_DATA = os.environ.get("FileShareNameData", "google-secops-data")
FILE_NAME_PREFIX = "google_secops_raw"  # Files named: {PREFIX}_{epoch}_{index}

# ═══════════════════════════════════════════════════════════════════════════════
# AZURE MONITOR INGESTION (SENTINEL DCR)
# ═══════════════════════════════════════════════════════════════════════════════
# Data Collection Rule (DCR) endpoint for posting detections to Sentinel
# Required: Set via ARM template

DCE_ENDPOINT = os.environ.get("AZURE_DATA_COLLECTION_ENDPOINT", "")
DCR_IMMUTABLE_ID = os.environ.get("DCR_RULE_ID", "")
DCR_STREAM_NAME = os.environ.get("DcrStreamName", "")

# Azure Authentication (optional: explicit credentials)
# If provided, uses ClientSecretCredential; otherwise falls back to DefaultAzureCredential
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")


# ═══════════════════════════════════════════════════════════════════════════════
# DETECTION FETCHING PARAMETERS
# ═══════════════════════════════════════════════════════════════════════════════
# Control how many detections are fetched from Google SecOps in each operation

LOOKBACK_DAYS = int(os.environ.get("LookbackDays", "1"))  # Default: 1 day back
MAX_LOOKBACK_DAYS = 7  # Safety limit: never go back more than 7 days

DETECTION_BATCH_SIZE = int(os.environ.get("DetectionBatchSize", "1000"))
# How many detections per Google SecOps API page (Google SecOps pagination)

MAX_DETECTIONS = int(os.environ.get("MaxDetections", "1000"))
# How many detections to fetch before stopping (per run)
# Prevents runaway fetches; use smaller values in testing


# ═══════════════════════════════════════════════════════════════════════════════
# DATA PIPELINE SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
# Control file handling and batching through the pipeline

# File age before ingester picks it up (seconds)
# Prevents race condition: gives fetcher time to finish writing before ingester reads
MAX_FILE_AGE_FOR_INGESTION = 120  # 2 minutes


# ═══════════════════════════════════════════════════════════════════════════════
# RESILIENCE & TIMEOUT SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
# Error handling and timeouts for API calls

# Google SecOps API streaming timeout
API_TIMEOUT_SECONDS = 300  # 5 minutes — per-read httpx timeout
# Google SecOps server sends heartbeat every ~15 seconds
# 300s timeout is safe for detecting truly dead connections

# Maximum wall-clock seconds to spend streaming a single API call.
# When there are no detections the server streams heartbeats for the entire
# window duration (potentially hours). We stop after this many seconds and
# use the most recent heartbeat nextPageStartTime to advance the checkpoint.
# Must be well under the Azure Function timeout (600 s).
STREAM_MAX_SECONDS = int(os.environ.get("StreamMaxSeconds", "300"))  # 5 minutes

# Retry behavior for transient errors
RETRY_BASE_DELAY_SECONDS = 2  # Initial backoff delay: 2 seconds
MAX_CONSECUTIVE_FAILURES = 3  # Give up after 3 consecutive errors
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}  # HTTP codes to retry on
