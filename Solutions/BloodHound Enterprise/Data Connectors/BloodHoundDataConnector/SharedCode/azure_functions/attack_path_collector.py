import logging
import time
import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from ..utility.utils import load_environment_configs, EnvironmentConfig, AzureConfig
from ..utility.bloodhound_manager import BloodhoundManager

@dataclass
class Environment:
    """Container for environment-specific data."""
    tenant_domain: str
    token_id: str
    token_key: str

def initialize_bloodhound_manager(
    tenant_domain: str,
    token_id: str,
    token_key: str,
    azure_config: Dict[str, str]
) -> Optional[BloodhoundManager]:
    """Initialize and test BloodHound manager connection."""
    bloodhound_manager = BloodhoundManager(
        tenant_domain, token_id, token_key, logger=logging
    )
    bloodhound_manager.set_azure_monitor_config(
        azure_config["tenant_id"],
        azure_config["app_id"],
        azure_config["app_secret"],
        azure_config["dce_uri"],
        azure_config["dcr_immutable_id"],
        azure_config["table_name"]
    )

    if not bloodhound_manager.test_connection():
        logging.error(f"BloodHound API connection test failed for '{tenant_domain}'.")
        return None

    logging.info(f"BloodHound API connection test passed for '{tenant_domain}'.")
    return bloodhound_manager

def fetch_and_filter_domains(
    bloodhound_manager: BloodhoundManager,
    selected_environments: str
) -> List[Dict[str, Any]]:
    """Fetch available domains and filter based on selected environments."""
    res_domains = bloodhound_manager.get_available_domains()
    if not isinstance(res_domains, dict):
        logging.error(f"Expected dict for available domains, got {type(res_domains)}: {res_domains}")
        return []

    all_domains_data = res_domains.get("data", [])
    logging.info(f"Found {len(all_domains_data)} domains from BloodHound API.")

    if selected_environments.strip().lower() == "all":
        return [domain for domain in all_domains_data if domain.get("collected") is True]
    
    domain_names_to_include = [name.strip() for name in selected_environments.split(",")]
    return [
        domain for domain in all_domains_data
        if domain.get("collected") is True
        and domain.get("name", "").strip() in domain_names_to_include
    ]

def filter_domains_by_finding_types(
    bloodhound_manager: BloodhoundManager,
    domains: List[Dict[str, Any]],
    selected_finding_types: str
) -> List[Dict[str, Any]]:
    """Filter domains based on available finding types."""
    selected_types_list = (
        [t.strip() for t in selected_finding_types.split(",")]
        if selected_finding_types.strip().lower() != "all"
        else []
    )

    final_domains = []
    for domain in domains:
        domain_id = domain.get("id")
        domain_name = domain.get("name")
        available_types = bloodhound_manager.get_available_types_for_domain(domain_id)

        if not isinstance(available_types, list):
            logging.error(f"Expected list for available types, got {type(available_types)}: {available_types}")
            continue

        filtered_types = (
            [_type for _type in available_types if _type in selected_types_list]
            if selected_types_list
            else available_types
        )

        if filtered_types:
            domain_copy = domain.copy()
            domain_copy["available_types"] = filtered_types
            final_domains.append(domain_copy)
            logging.info(f"Domain '{domain_name}' has {len(filtered_types)} relevant finding types.")
        else:
            logging.info(f"Domain '{domain_name}' has no relevant finding types after filtering.")

    return final_domains

def collect_attack_paths(
    bloodhound_manager: BloodhoundManager,
    domains: List[Dict[str, Any]],
    tenant_domain: str,
    last_attack_path_timestamps: Dict[str, Dict[str, str]],
    default_lookback_days: int = 1
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """Collect attack paths for each domain and finding type."""
    all_collected_paths = []
    domain_latest_timestamps = {}

    for domain in domains:
        domain_id = domain.get("id")
        domain_name = domain.get("name")
        available_types = domain.get("available_types", [])

        if not available_types:
            logging.info(f"[SKIPPED] No available types to fetch for domain {domain_name}.")
            continue

        for attack_type in available_types:
            logging.info(f"Fetching attack path details for domain: {domain_name}, type: {attack_type}")
            attack_details = bloodhound_manager.get_attack_path_details(domain_id, attack_type)

            if not isinstance(attack_details, list):
                logging.warning(f"Skipping invalid attack path details for {domain_name}, type {attack_type}")
                continue

            attack_details = [x for x in attack_details if isinstance(x, dict)]
            if not attack_details:
                logging.warning(f"No valid attack path details found for {attack_type} in domain {domain_name}.")
                continue

            for data_item in attack_details:
                item_updated_at = data_item.get("updated_at")
                last_saved_ts = last_attack_path_timestamps.get(tenant_domain, {}).get(domain_name)
                
                if not last_saved_ts:
                    last_saved_ts = (
                        (datetime.datetime.now() - datetime.timedelta(days=default_lookback_days))
                        .replace(hour=0, minute=0, second=0, microsecond=0)
                        .strftime('%Y-%m-%dT%H:%M:%SZ')
                    )

                if item_updated_at > last_saved_ts:
                    all_collected_paths.append(data_item)
                    domain_latest_timestamps[domain_name] = max(
                        domain_latest_timestamps.get(domain_name, ""),
                        item_updated_at
                    )

    return all_collected_paths, domain_latest_timestamps

def send_attack_paths_to_azure_monitor(
    attack_paths: List[Dict[str, Any]],
    bloodhound_manager: BloodhoundManager,
    azure_monitor_token: str,
    finding_types_data: List[Dict[str, Any]],
    tenant_domain: str,
    domains_data: List[Dict[str, Any]]
) -> Tuple[int, int]:
    """Send collected attack paths to Azure Monitor."""
    successful_submissions = 0
    failed_submissions = 0

    if not attack_paths:
        logging.info("No attack path details to send to Azure Monitor.")
        return successful_submissions, failed_submissions

    logging.info(f"Sending {len(attack_paths)} collected attack path details to Azure Monitor.")
    for i, data_item in enumerate(attack_paths, 1):
        result = bloodhound_manager.send_attack_data(
            data_item,
            azure_monitor_token,
            finding_types_data,
            tenant_domain,
            domains_data
        )
        logging.info(f"Processing attack path log entry {i}/{len(attack_paths)}: {data_item.get('id')}")

        if result and result.get("status") == "success":
            successful_submissions += 1
            logging.info(f"Successfully sent attack path for '{data_item.get('id')}'")
        else:
            failed_submissions += 1
            logging.error(f"Failed to send attack path for '{data_item.get('id')}': {result.get('message', 'Unknown error')}")
        
        time.sleep(0.1)  # Rate limiting between requests

    return successful_submissions, failed_submissions

def process_environment(
    env: Environment,
    azure_config: Dict[str, str],
    selected_environments: str,
    selected_finding_types: str,
    last_timestamps: Dict[str, Dict[str, str]]
) -> Optional[Dict[str, str]]:
    """Process attack paths for a single environment."""
    logging.info(f"\n--- Processing environment: {env.tenant_domain} ---")

    # Initialize BloodHound manager
    bloodhound_manager = initialize_bloodhound_manager(
        env.tenant_domain, env.token_id, env.token_key, azure_config
    )
    if not bloodhound_manager:
        return None

    # Filter domains
    filtered_domains = fetch_and_filter_domains(bloodhound_manager, selected_environments)
    if not filtered_domains:
        logging.info("No domains available after filtering.")
        return {}

    # Filter by finding types
    domains_with_types = filter_domains_by_finding_types(
        bloodhound_manager, filtered_domains, selected_finding_types
    )
    if not domains_with_types:
        logging.info("No domains with matching finding types.")
        return {}

    # Get Azure Monitor token
    azure_monitor_token = bloodhound_manager.get_bearer_token()
    if not azure_monitor_token:
        logging.error("Failed to obtain Azure Monitor token.")
        return None

    # Get finding types details
    finding_types_data = bloodhound_manager.get_all_path_asset_details_for_finding_types(domains_with_types)

    # Collect and send attack paths
    attack_paths, latest_timestamps = collect_attack_paths(
        bloodhound_manager,
        domains_with_types,
        env.tenant_domain,
        last_timestamps
    )

    logging.info(f"Collected {len(attack_paths)} attack path details to process.")

    if attack_paths:
        successful, failed = send_attack_paths_to_azure_monitor(
            attack_paths,
            bloodhound_manager,
            azure_monitor_token,
            finding_types_data,
            env.tenant_domain,
            domains_with_types
        )
        logging.info(f"Attack paths sent. Successful: {successful}, Failed: {failed}")

    return latest_timestamps

def run_attack_paths_collection_process(
    last_attack_path_timestamps: Optional[Dict[str, Dict[str, str]]] = None
) -> Optional[Dict[str, Dict[str, str]]]:
    """Main entry point for attack paths collection process."""
    logging.info("Starting BloodHound attack paths collection process.")
    last_attack_path_timestamps = last_attack_path_timestamps or {}

    # Load configurations using the utility function
    env_configs, azure_config = load_environment_configs("ATTACK_PATHS_TABLE_NAME")
    
    # Extract Azure configuration
    azure_settings = {
        "tenant_id": azure_config.tenant_id,
        "app_id": azure_config.app_id,
        "app_secret": azure_config.app_secret,
        "dce_uri": azure_config.dce_uri,
        "dcr_immutable_id": azure_config.dcr_immutable_id,
        "table_name": azure_config.table_name
    }

    # Process each environment
    updated_timestamps = last_attack_path_timestamps.copy()
    num_environments = len(env_configs)
    logging.info(f"Processing {num_environments} environments")

    for i, env_config in enumerate(env_configs, 1):
        logging.info(f"Processing environment {i}/{num_environments}: {env_config.tenant_domain}")
        
        env = Environment(
            env_config.tenant_domain, 
            env_config.token_id, 
            env_config.token_key
        )

        latest_timestamps = process_environment(
            env,
            azure_settings,
            env_config.selected_environments,
            env_config.selected_finding_types,
            updated_timestamps
        )

        if latest_timestamps is not None:
            if env_config.tenant_domain not in updated_timestamps:
                updated_timestamps[env_config.tenant_domain] = {}
            updated_timestamps[env_config.tenant_domain].update(latest_timestamps)

    logging.info("BloodHound attack paths collection process finished.")
    return updated_timestamps
