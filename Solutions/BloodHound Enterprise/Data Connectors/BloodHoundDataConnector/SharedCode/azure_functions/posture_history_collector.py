import logging
import time
from typing import Dict, List, Any, Optional
from ..utility.utils import load_environment_configs, get_token_lists
from ..utility.bloodhound_manager import BloodhoundManager


# Set up logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_posture_history_collection_process(last_posture_history_timestamps: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Orchestrates the entire BloodHound posture history collection and Azure Monitor submission process
    for multiple environments, handling each sequentially.
    """
    logging.info("Starting BloodHound posture history collection process.")
    last_posture_history_timestamps = last_posture_history_timestamps or {}

    # Load all configurations in a structured way using the dedicated utility function
    env_configs, azure_config = load_environment_configs("POSTURE_HISTORY_TABLE_NAME")
    logging.info(f"Successfully loaded configurations for {len(env_configs)} BloodHound environments.")

    # Process each configured environment
    for i, env_config in enumerate(env_configs):
        current_tenant_domain = env_config.tenant_domain
        logging.info(f"\n--- Starting posture history collection for environment '{current_tenant_domain}' ---")

        # Initialize BloodhoundManager with environment-specific and Azure configurations
        bloodhound_manager = BloodhoundManager(
            tenant_domain=env_config.tenant_domain,
            token_id=env_config.token_id,
            token_key=env_config.token_key,
            logger=logging
        )
        bloodhound_manager.set_azure_monitor_config(
            tenant_id=azure_config.tenant_id,
            app_id=azure_config.app_id,
            app_secret=azure_config.app_secret,
            dce_uri=azure_config.dce_uri,
            dcr_immutable_id=azure_config.dcr_immutable_id,
            table_name=azure_config.table_name
        )

        # Test BloodHound API connection
        if not bloodhound_manager.test_connection():
            logging.error(f"BloodHound API connection test failed for '{current_tenant_domain}'. Skipping this environment.")
            continue

        # Get and filter available domains
        res_domains = bloodhound_manager.get_available_domains()
        if not res_domains:
            logging.error(f"Failed to fetch available domains for '{current_tenant_domain}'. Skipping this environment.")
            continue
        
        domains_data = res_domains.get("data", [])
        selected_environments = env_config.selected_environments
        
        filtered_domains_by_env = filter_domains_by_environment(domains_data, selected_environments)

        if not filtered_domains_by_env:
            logging.info(f"No collected or selected environments found for '{current_tenant_domain}'. Skipping.")
            continue

        environment_ids = [domain["id"] for domain in filtered_domains_by_env if domain.get("id")]
        if not environment_ids:
            logging.info(f"No environment IDs found for '{current_tenant_domain}'. Skipping this environment.")
            continue
        
        # Get Azure Monitor Bearer Token
        azure_monitor_token = bloodhound_manager.get_bearer_token()
        if not azure_monitor_token:
            logging.error(f"Failed to obtain Bearer token for Azure Monitor for '{current_tenant_domain}'. Skipping.")
            continue

        # Fetch, process, and send posture history
        data_types_to_fetch = ["findings", "exposure", "assets", "attack-paths"]
        all_collected_data = []

        for env_id in environment_ids:
            collected_data = collect_posture_history(
                bloodhound_manager, env_id, data_types_to_fetch, 
                current_tenant_domain, last_posture_history_timestamps
            )

            all_collected_data.extend(collected_data)

        successful_submissions, failed_submissions = send_posture_history_to_azure_monitor(
            all_collected_data, bloodhound_manager, azure_monitor_token, 
            current_tenant_domain, domains_data
        )

        logging.info(f"Posture history collection for '{current_tenant_domain}' completed. Successful submissions: {successful_submissions}, Failed submissions: {failed_submissions}.")

    # End of processing all environments
    logging.info("BloodHound posture history collection process finished for all environments.")
    return last_posture_history_timestamps

# The following functions remain unchanged as they are already well-defined helpers.
# You just need to ensure they are available in the module.

def prepare_tokens(token_id, token_key, key_vault_url, token_ids_secret_name, token_keys_secret_name):
    """
    Prepares token lists either from environment variables or key vault.
    This function's logic is now encapsulated within the `load_environment_configs` function from utils.
    """
    if token_id is not None and token_key is not None:
        return [tid.strip() for tid in token_id.split(',')], [tkey.strip() for tkey in token_key.split(',')]
    
    return get_token_lists(
        key_vault_url=key_vault_url,
        token_ids_secret_name=token_ids_secret_name,
        token_keys_secret_name=token_keys_secret_name
    )

def filter_domains_by_environment(domains_data, selected_bhe_environments):
    """
    Filters domains based on selected environments configuration.
    """
    if selected_bhe_environments.strip().lower() == "all":
        return [domain for domain in domains_data if domain.get("collected") is True]
    
    domain_names_to_include = [name.strip() for name in selected_bhe_environments.split(",")]
    return [
        domain
        for domain in domains_data
        if domain.get("collected") is True
        and domain.get("name").strip() in domain_names_to_include
    ]

def collect_posture_history(bloodhound_manager, env_id, data_types, current_tenant_domain, last_posture_history_timestamps):
    """
    Collects posture history data for a specific environment ID.
    """
    all_collected_data = []
    timestamps = last_posture_history_timestamps.get(current_tenant_domain, {}).get(env_id, {})

    for data_type in data_types:
        last_timestamp = timestamps.get(data_type, "")
        posture_history_response = bloodhound_manager.get_posture_history(
            data_type, environment_id=env_id, start=last_timestamp
        )

        if posture_history_response and "data" in posture_history_response and posture_history_response["data"]:
            response_data = posture_history_response["data"]

            for data_item in response_data:
                data_item["start_date"] = posture_history_response.get("start", "")
                data_item["end_date"] = posture_history_response.get("end", "")
                data_item["domain_id"] = env_id
                data_item["type"] = data_type
                data_item["tenant_domain"] = current_tenant_domain
                all_collected_data.append(data_item)

            # Update timestamps
            latest_timestamp = max(item.get("date", "") for item in response_data)
            last_posture_history_timestamps.setdefault(current_tenant_domain, {}).setdefault(env_id, {})[data_type] = latest_timestamp

    return all_collected_data

def send_posture_history_to_azure_monitor(posture_history_data, bloodhound_manager, azure_monitor_token, current_tenant_domain, domains_data):
    """
    Sends posture history data to Azure Monitor and returns the count of successful and failed submissions.
    """
    successful_submissions = 0
    failed_submissions = 0
    
    if not posture_history_data:
        logging.info("No posture history data was collected to send to Azure Monitor for this environment.")
        return successful_submissions, failed_submissions

    logging.info(f"Sending {len(posture_history_data)} posture history records to Azure Monitor.")
    
    for i, data_item in enumerate(posture_history_data, 1):
        result = bloodhound_manager.send_posture_history_logs(
            data_item, azure_monitor_token, current_tenant_domain, domains_data
        )
        logging.info(f"Processing posture history entry {i}/{len(posture_history_data)}: {data_item}")
        logging.info(f"Result of sending posture history is {result}")
        
        if result.get("status") == "success":
            successful_submissions += 1
        else:
            failed_submissions += 1
            logging.error(f"Failed to send posture history for date '{data_item.get('value')}': {result.get('message', 'Unknown error')}")
        
        time.sleep(0.1)
    
    logging.info(f"Posture history processing complete for '{current_tenant_domain}'. Successful submissions: {successful_submissions}, Failed submissions: {failed_submissions}.")
    return successful_submissions, failed_submissions