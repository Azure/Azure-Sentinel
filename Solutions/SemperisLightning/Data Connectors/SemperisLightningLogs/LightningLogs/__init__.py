import subprocess
import sys
import requests
import json
import os
import logging
import warnings
import sys
import shutil
from typing import Optional
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

# Ensure parent directory is in sys.path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Add current directory to path for local testing
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Try relative imports first (for Azure Functions), fallback to absolute (for local)
from semperis_ioe_execution_results import SemperisIOEExecutionResults
from semperis_ioe_metadata import SemperisIOEMetadata
from semperis_tier0_attackers import SemperisTier0Attackers
from semperis_attack_paths import SemperisAttackPaths
from semperis_ioe_executions import SemperisIOEExecutions
from semperis_tier0_nodes import SemperisTier0Nodes


# Ensure parent directory is in sys.path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO), force=True)


# Get a module/function-specific logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, log_level, logging.INFO))


# Only for local/manual runs
if os.path.exists("local.settings.json"):
    with open("local.settings.json") as f:
        settings = json.load(f)
        for k, v in settings.get("Values", {}).items():
            os.environ.setdefault(k, v)

# Semperis Configuration
SEMPERIS_ZONE = os.environ.get("SEMPERIS_ZONE", "na")

# Semperis API Endpoints (with zone placeholder)
SEMPERIS_AUTH_ENDPOINT = os.environ.get("SEMPERIS_AUTH_ENDPOINT", f"https://lightning.{SEMPERIS_ZONE}.cloud.semperis.com/api/external/v1/auth/token").replace("{SEMPERIS_ZONE}", SEMPERIS_ZONE)
SEMPERIS_API_KEY = os.environ.get("SEMPERIS_API_KEY")

SEMPERIS_INDICATOR_EXECUTIONS_ENDPOINT = os.environ.get("SEMPERIS_INDICATOR_EXECUTIONS_ENDPOINT",
                                                         f"https://lightning.{SEMPERIS_ZONE}.cloud.semperis.com/api/external/v1/indicatorExecutions").replace("{SEMPERIS_ZONE}", SEMPERIS_ZONE)
SEMPERIS_TIER_0_NODE_ENDPOINT = os.environ.get("SEMPERIS_TIER_0_NODE_ENDPOINT", 
                                               f"https://lightning.{SEMPERIS_ZONE}.cloud.semperis.com/idg/api/v1/QueryGraph").replace("{SEMPERIS_ZONE}", SEMPERIS_ZONE)
SEMPERIS_ATTACK_PATHS_ENDPOINT = os.environ.get("SEMPERIS_ATTACK_PATHS_ENDPOINT", 
                                                f"https://lightning.{SEMPERIS_ZONE}.cloud.semperis.com/idg/api/v1/DetermineAttackPaths").replace("{SEMPERIS_ZONE}", SEMPERIS_ZONE)
SEMPERIS_TIER_0_ATTACKERS_ENDPOINT = os.environ.get("SEMPERIS_TIER_0_ATTACKERS_ENDPOINT",
                                                     f"https://lightning.{SEMPERIS_ZONE}.cloud.semperis.com/idg/api/v1/GetZoneAccessObjects").replace("{SEMPERIS_ZONE}", SEMPERIS_ZONE)
SEMPERIS_INDICATOR_METADATA_ENDPOINT = os.environ.get("SEMPERIS_INDICATOR_METADATA_ENDPOINT", 
                                                      f"https://lightning.{SEMPERIS_ZONE}.cloud.semperis.com/api/external/v1/ioesMetadata").replace("{SEMPERIS_ZONE}", SEMPERIS_ZONE)
SEMPERIS_INDICATOR_RESULTS_ENDPOINT = os.environ.get("SEMPERIS_INDICATOR_RESULTS_ENDPOINT", 
                                                     f"https://lightning.{SEMPERIS_ZONE}.cloud.semperis.com/api/external/v1/indicatorExecutions").replace("{SEMPERIS_ZONE}", SEMPERIS_ZONE)

# Azure DCE Configuration
DCE_ENDPOINT = os.environ["DCE_ENDPOINT"]
DCE_IMMUTABLE_ID = os.environ["DCR_IMMUTABLE_ID"]

# DCR Stream Mappings
DCR_MAPPINGS = {
    "tier0_nodes": {
        "stream_name": os.environ.get("T0_NODES_STREAM_NAME", "Custom-LightningTier0Nodes_CL"),
    },
    "indicator_executions": {
        "stream_name": os.environ.get("INDICATOR_EXECUTIONS_STREAM_NAME", "Custom-LightningIndicatorExecutions_CL"),
    },
    "attack_paths": {
        "stream_name": os.environ.get("ATTACK_PATHS_STREAM_NAME", "Custom-LightningAttackPaths_CL"),
    },
    "attack_path_links": {
        "stream_name": os.environ.get("ATTACK_PATH_LINKS_STREAM_NAME", "Custom-LightningAttackPathLinks_CL"),
    },
    "tier0_attackers": {
        "stream_name": os.environ.get("TIER_0_ATTACKERS_STREAM_NAME", "Custom-LightningTier0Attackers_CL"),
    },
    "indicator_metadata": {
        "stream_name": os.environ.get("INDICATOR_METADATA_STREAM_NAME", "Custom-LightningIOEsMetadata_CL"),
    },
    "indicator_results": {
        "stream_name": os.environ.get("INDICATOR_RESULTS_STREAM_NAME", "Custom-LightningIOEResults_CL"),
    },
}


def send_to_azure_dce(dce_data: list) -> bool:
    """Send records to Azure Data Collection Endpoint using LogsIngestionClient."""
    if not dce_data:
        logger.info("No data to send to DCE")
        return True

    try:
        # Authenticate using bearer token from Azure CLI
        
        
        logger.info("Attempting to authenticate with Azure Monitor Ingestion API...")
        credential = DefaultAzureCredential()
        client = LogsIngestionClient(endpoint=DCE_ENDPOINT, credential=credential)
        logger.info("✓ Authenticated with Azure Monitor Ingestion API")

        logger.info(f"Preparing to send data to DCE: {len(dce_data)} streams with total {sum(len(records) for _, records in dce_data)} records")

        # Send logs to DCE
        for stream_name, records in dce_data:
            if not records:
                logger.info(f"⊘ No records for stream: {stream_name}")
                continue
            logger.info(f"Uploading {len(records)} records to stream: {stream_name}")   
            client.upload(
                rule_id=DCE_IMMUTABLE_ID,
                stream_name=stream_name,
                logs=records,
            )
            logger.info(f"✓ Uploaded {len(records)} records to {stream_name}")

        return True

    except Exception as e:
        logging.error(f"✗ Failed to send data to Azure DCE: {e}")
        logging.error("Troubleshooting:")
        logging.error("  1. Ensure you are authenticated: az login")
        logging.error("  2. Verify DCR Immutable ID is correct")
        logging.error("  3. Check DCE endpoint is accessible")
        logging.error("  4. Verify role: Monitoring Metrics Publisher on DCE/DCR")
        return False


def process_tier0_nodes(token: str) -> tuple:
    """Process and return Tier0 nodes for ingestion."""
    logger.info("Processing Tier0 Nodes...")
    try:
        data = SemperisTier0Nodes.get_tier_0_nodes(token, SEMPERIS_TIER_0_NODE_ENDPOINT)
        if data:
            logger.info(f"Retrieved {len(data)} Tier0 nodes")
            return (DCR_MAPPINGS["tier0_nodes"]["stream_name"], data)
        return None
    except Exception as e:
        logging.error(f"Error processing Tier0 Nodes: {e}")
        return None


def process_indicator_executions(token: str) -> tuple:
    """Process and return indicator executions for ingestion."""
    logger.info("Processing Indicator Executions...")
    try:
        data = SemperisIOEExecutions.get_indicator_executions(token, SEMPERIS_INDICATOR_EXECUTIONS_ENDPOINT)
        if data:
            logger.info(f"Retrieved {len(data)} indicator executions")
            return (DCR_MAPPINGS["indicator_executions"]["stream_name"], data)
        return None
    except Exception as e:
        logging.error(f"Error processing Indicator Executions: {e}")
        return None


def process_attack_paths(token: str) -> list:
    """Process and return attack paths and links for ingestion."""
    logger.info("Processing Attack Paths...")
    results = []
    try:
        data = SemperisAttackPaths.get_attack_paths(token, SEMPERIS_ATTACK_PATHS_ENDPOINT)
        if data and len(data) >= 2:
            # data[0] = attack paths, data[1] = attack path links
            if data[0]:
                logger.info(f"Retrieved {len(data[0])} attack paths")
                results.append((DCR_MAPPINGS["attack_paths"]["stream_name"], data[0]))
            if data[1]:
                logger.info(f"Retrieved {len(data[1])} attack path links")
                results.append((DCR_MAPPINGS["attack_path_links"]["stream_name"], data[1]))
        return results
    except Exception as e:
        logging.error(f"Error processing Attack Paths: {e}")
        return []


def process_tier0_attackers(token: str) -> tuple:
    """Process and return Tier0 attackers for ingestion."""
    logger.info("Processing Tier0 Attackers...")
    try:
        data = SemperisTier0Attackers.get_tier_0_attackers(token, SEMPERIS_TIER_0_ATTACKERS_ENDPOINT)
        if data:
            logger.info(f"Retrieved {len(data)} Tier0 attackers")
            return (DCR_MAPPINGS["tier0_attackers"]["stream_name"], data)
        return None
    except Exception as e:
        logging.error(f"Error processing Tier0 Attackers: {e}")
        return None


def process_indicator_metadata(token: str) -> tuple:
    """Process and return indicator metadata for ingestion."""
    logger.info("Processing Indicator Metadata...")
    try:
        data = SemperisIOEMetadata.get_indicator_metadata(token, SEMPERIS_INDICATOR_METADATA_ENDPOINT)
        if data:
            logger.info(f"Retrieved {len(data)} indicator metadata")
            return (DCR_MAPPINGS["indicator_metadata"]["stream_name"], data)
        return None
    except Exception as e:
        logging.error(f"Error processing Indicator Metadata: {e}")
        return None


def process_indicator_results(token: str) -> tuple:
    """Process and return indicator execution results for ingestion."""
    logger.info("Processing Indicator Results...")
    try:
        data = SemperisIOEExecutionResults.get_indicator_execution_results(token, SEMPERIS_INDICATOR_RESULTS_ENDPOINT)
        if data:
            logger.info(f"Retrieved {len(data)} indicator results")
            return (DCR_MAPPINGS["indicator_results"]["stream_name"], data)
        return None
    except Exception as e:
        logging.error(f"Error processing Indicator Results: {e}")
        return None

def get_semperis_token(api_key: str) -> Optional[str]:
    """Get authentication token from Semperis."""
    headers = {
        "accept": "*/*",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true",
        "User-Agent": "curl/7.64.1",
    }
    payload = {"apiKey": api_key}

    try:
        response = requests.post(
            SEMPERIS_AUTH_ENDPOINT,
            json=payload,
            headers=headers,
            verify=False,
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("Token")
        logger.info("✓ Semperis authentication successful")
        return token
    except requests.exceptions.RequestException as e:
        logging.error(f"✗ Failed to obtain Semperis token: {e}")
        return None

def get_azure_token() -> Optional[str]:
    """Get Azure Monitor authentication token using bearer token flow"""
    try:
        if shutil.which("az") is None:
            logger.info("Azure CLI not found; skipping az-based token retrieval")
            return None
        # Use managed identity to get token
        result = subprocess.run(
            ["az", "account", "get-access-token", "--resource", "https://monitor.azure.com/"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        data = json.loads(result.stdout)
        token = data.get("accessToken")
        if token:
            logger.info("Successfully obtained Azure token")
            return token
        else:
            logger.error("No access token in response")
            return None
    except Exception as e:
        logger.error(f"Error getting Azure token: {e}")
        return None

def run_pipeline() -> bool:
    """Run the Semperis to Azure DCE ingestion pipeline."""
    logger.info("=" * 70)
    logger.info("Semperis to Azure Data Collection Endpoint Pipeline")
    logger.info("=" * 70)

    # Step 1: Authenticate to Semperis
    logger.info("\nStep 1: Authenticating to Semperis...")
    semperis_token = get_semperis_token(SEMPERIS_API_KEY)
    if not semperis_token:
        logging.error("Failed to authenticate with Semperis. Exiting.")
        return False

    # Step 2: Retrieve data from all sources
    logger.info("\nStep 2: Retrieving data from Semperis...")
    dce_data = []
    sources_processed = 0
    total_records = 0

    # Process each data source
    processing_functions = [
        ("Tier0 Nodes", process_tier0_nodes),
        ("Indicator Executions", process_indicator_executions),
        ("Attack Paths & Links", process_attack_paths),
        ("Tier0 Attackers", process_tier0_attackers),
        ("Indicator Metadata", process_indicator_metadata),
        ("Indicator Results", process_indicator_results),
    ]

    for source_name, process_func in processing_functions:
        try:
            result = process_func(semperis_token)
            if result:
                if isinstance(result, list):  # attack_paths returns a list of tuples
                    for item in result:
                        dce_data.append(item)
                        total_records += len(item[1]) if item and len(item) > 1 else 0
                    sources_processed += 1
                else:  # regular tuple (stream_name, records)
                    dce_data.append(result)
                    total_records += len(result[1]) if result and len(result) > 1 else 0
                    sources_processed += 1
        except Exception as e:
            logging.error(f"Error processing {source_name}: {e}")

    if not dce_data:
        logging.warning("No data retrieved from any source")
        return False

    logger.info(f"Retrieved data from {sources_processed} sources ({total_records} total records)")

    # Step 3: Send to Azure DCE
    logger.info("\nStep 3: Sending data to Azure Data Collection Endpoint...")
    success = send_to_azure_dce(dce_data)

    if success:
        logger.info("=" * 70)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 70)
    else:
        logging.error("Pipeline encountered errors during DCE ingestion")

    return success



def main(mytimer: func.TimerRequest) -> None:
    """Timer-triggered function for Semperis Lightning data ingestion."""
    if mytimer.past_due:
        logging.warning("Timer trigger is past due")

    warnings.filterwarnings("ignore", category=Warning)
    run_pipeline()



if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=Warning)
    run_pipeline()