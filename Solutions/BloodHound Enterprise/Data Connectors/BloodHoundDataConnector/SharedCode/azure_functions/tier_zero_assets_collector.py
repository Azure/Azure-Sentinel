import logging
import time
import datetime
import json
from azure.core.exceptions import ResourceNotFoundError

from ..utility.utils import (
    load_environment_configs, get_azure_batch_size
)
from ..utility.bloodhound_manager import BloodhoundManager


def send_tier_zero_assets_to_azure_monitor(
    nodes_array,
    bloodhound_manager,
    azure_monitor_token,
    current_tenant_domain,
    filtered_domains_by_env,
):
    """
    Sends tier zero assets data to Azure Monitor in batches of 100 and returns the count of successful and failed submissions.
    """
    successful_submissions = 0
    failed_submissions = 0

    if not nodes_array:
        logging.info("No Tier Zero Assets data to send to Azure Monitor for this environment.")
        return successful_submissions, failed_submissions

    batch_size = get_azure_batch_size()
    logging.info(f"Sending {len(nodes_array)} Tier Zero Assets to Azure Monitor in batches of {batch_size}.")
    
    # Process in batches
    for batch_start in range(0, len(nodes_array), batch_size):
        batch_end = min(batch_start + batch_size, len(nodes_array))
        batch = nodes_array[batch_start:batch_end]
        
        # Transform batch entries to the expected schema for Azure Monitor
        log_entries = []
        for node_data in batch:
            properties = node_data.get("properties", {})
            node_id = node_data.get("nodeId", "")
            name = bloodhound_manager.extract_name(node_data, properties, node_id)
            domain_name = bloodhound_manager.extract_domain_name(
                node_data, properties, name, filtered_domains_by_env
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
                "tenant_url": current_tenant_domain,
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
            
            log_entries.append(log_entry)
        
        logging.info(f"Sending batch {batch_start//batch_size + 1} ({len(log_entries)} entries): IDs {[log.get('nodeId', 'unknown') for log in log_entries[:5]]}...")
        
        # Send batch to Azure Monitor
        result = bloodhound_manager._send_to_azure_monitor(
            log_entries,
            azure_monitor_token,
            bloodhound_manager.dce_uri,
            bloodhound_manager.dcr_immutable_id,
            bloodhound_manager.table_name
        )
        
        if result and result.get("status") == "success":
            entries_sent = result.get("entries_sent", len(log_entries))
            successful_submissions += entries_sent
            logging.info(f"Successfully sent batch of {entries_sent} Tier Zero Assets")
        else:
            failed_submissions += len(log_entries)
            logging.error(f"Failed to send batch: {result.get('message', 'Unknown error') if result else 'No response'}")
        
        # Rate limiting is handled automatically by azure_monitor_rate_limiter in _send_to_azure_monitor()

    logging.info(
        f"Tier Zero Asset processing for '{current_tenant_domain}' complete. "
        f"Successful: {successful_submissions}, Failed: {failed_submissions}."
    )
    return successful_submissions, failed_submissions


def fetch_tier_zero_nodes(bloodhound_manager, filtered_domains_by_env):
    """
    Fetch and transform Tier Zero assets into a list of node dictionaries.
    """
    cypher_response = bloodhound_manager.fetch_tier_zero_assets()

    if not cypher_response or "data" not in cypher_response or "nodes" not in cypher_response["data"]:
        logging.error("Failed to fetch Tier Zero assets or received unexpected response structure.")
        return []

    nodes_array = []
    for node_id, node_data in cypher_response["data"]["nodes"].items():
        if node_data.get("kind") == "Meta":
            continue

        properties = node_data.get("properties", {})
        name = bloodhound_manager.extract_name(node_data, properties, node_id)
        domain_name = bloodhound_manager.extract_domain_name(
            node_data, properties, name, filtered_domains_by_env
        )

        combined_node_data = {
            "nodeId": node_id,
            "domain_name": domain_name,
            "name": name,
            **node_data,
        }
        nodes_array.append(combined_node_data)

    return nodes_array


def process_tier_zero_for_environment(
    current_tenant_domain, current_token_id, current_token_key, azure_config
) -> bool:
    """
    Process Tier Zero Assets collection for a single environment.
    """
    logging.info(f"\n--- Starting Tier Zero Assets collection for '{current_tenant_domain}' ---")

    # Initialize BloodhoundManager
    bloodhound_manager = BloodhoundManager(
        current_tenant_domain, current_token_id, current_token_key, logger=logging
    )
    bloodhound_manager.set_azure_monitor_config(
        azure_config.tenant_id,
        azure_config.app_id,
        azure_config.app_secret,
        azure_config.dce_uri,
        azure_config.dcr_immutable_id,
        azure_config.table_name,
    )

    # Test connection
    if not bloodhound_manager.test_connection():
        logging.error(f"BloodHound API connection failed for '{current_tenant_domain}'. Skipping.")
        return False

    logging.info("Connection test passed. Fetching domains...")

    # Fetch available domains
    res_domains = bloodhound_manager.get_available_domains()
    if not res_domains:
        logging.error("Failed to fetch available domains. Skipping this environment.")
        return False

    all_domains_data = res_domains.get("data", [])
    filtered_domains_by_env = [d for d in all_domains_data if d.get("collected") is True]

    if not filtered_domains_by_env:
        logging.info("No collected domains available. Skipping.")
        return True

    logging.info(f"Filtered {len(filtered_domains_by_env)} domains for Tier Zero Assets collection.")

    # Fetch Tier Zero Assets
    nodes_array = fetch_tier_zero_nodes(bloodhound_manager, filtered_domains_by_env)
    logging.info(f"Found {len(nodes_array)} Tier Zero Assets to process.")

    if not nodes_array:
        return True

    # Get Bearer Token
    azure_monitor_token = bloodhound_manager.get_bearer_token()
    if not azure_monitor_token:
        logging.error("Failed to obtain Bearer token. Skipping submission.")
        return False

    successful, failed = send_tier_zero_assets_to_azure_monitor(
        nodes_array,
        bloodhound_manager,
        azure_monitor_token,
        current_tenant_domain,
        filtered_domains_by_env,
    )

    logging.info(f"Successful submissions: {successful}, Failed: {failed}")
    return successful > 0


def run_tier_zero_assets_collection_process() -> bool:
    """
    Orchestrates the entire Tier Zero Assets collection process across all environments.
    """
    logging.info("Starting BloodHound Tier Zero Assets collection process.")

    # Load Azure + BloodHound configuration
    env_configs, azure_config = load_environment_configs("TIER_ZERO_ASSETS_TABLE_NAME")

    success = True
    for env_config in env_configs:
        if not process_tier_zero_for_environment(
            env_config.tenant_domain, env_config.token_id, env_config.token_key, azure_config
        ):
            success = False

    logging.info("Tier Zero Assets collection process completed for all environments.")
    return success