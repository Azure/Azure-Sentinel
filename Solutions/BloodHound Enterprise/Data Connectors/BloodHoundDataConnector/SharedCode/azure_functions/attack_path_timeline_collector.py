import logging
import time
import datetime
from ..utility.utils import load_environment_configs, get_azure_batch_size
from ..utility.bloodhound_manager import BloodhoundManager


def initialize_bloodhound_manager(tenant_domain, token_id, token_key, tenant_id, app_id, app_secret, dce_uri, dcr_immutable_id, table_name):
    """Initialize and configure BloodHoundManager instance."""
    logging.info(f"Initializing BloodHound manager for {tenant_domain}")
    bloodhound_manager = BloodhoundManager(
        tenant_domain, token_id, token_key, logger=logging
    )
    bloodhound_manager.set_azure_monitor_config(
        tenant_id, app_id, app_secret, dce_uri, dcr_immutable_id, table_name
    )
    
    connection_response = bloodhound_manager.test_connection()
    if not connection_response:
        logging.error(f"BloodHound API connection test failed for '{tenant_domain}'")
        return None
        
    logging.info(f"BloodHound API connection test passed for '{tenant_domain}'")
    return bloodhound_manager


def filter_domains_by_environment(all_domains_data, selected_bhe_environments):
    """Filter domains based on environment selection."""
    if selected_bhe_environments.strip().lower() == "all":
        return [domain for domain in all_domains_data if domain.get("collected") is True]
    
    domain_names_to_include = [name.strip() for name in selected_bhe_environments.split(",")]
    return [
        domain
        for domain in all_domains_data
        if domain.get("collected") is True
        and domain.get("name").strip() in domain_names_to_include
    ]


def filter_domains_by_finding_types(bloodhound_manager, domains, selected_finding_types):
    """Filter domains based on available finding types."""
    selected_finding_types_list = (
        [t.strip() for t in selected_finding_types.split(",")]
        if selected_finding_types.strip().lower() != "all"
        else []
    )
    
    final_domains = []
    for domain in domains:
        domain_id = domain.get("id")
        domain_name = domain.get("name")
        available_types = bloodhound_manager.get_available_types_for_domain(domain_id)
        
        filtered_domain_types = (
            [_type for _type in available_types if _type in selected_finding_types_list]
            if selected_finding_types_list
            else available_types
        )
        
        if filtered_domain_types:
            domain["available_types"] = filtered_domain_types
            final_domains.append(domain)
            logging.info(f"Domain '{domain_name}' has {len(filtered_domain_types)} relevant finding types after filtering.")
        else:
            logging.info(f"Domain '{domain_name}' has no relevant finding types after filtering. Skipping.")
    
    return final_domains


def collect_attack_path_timeline(bloodhound_manager, domain, last_timestamps):
    """Collect attack path timeline data for a specific domain."""
    domain_id = domain.get("id")
    domain_name = domain.get("name")
    available_types = domain.get("available_types", [])
    
    if not available_types:
        logging.warning(f"No available types for domain {domain_name} after filtering. Skipping.")
        return []
    
    domain_attack_path_entries = []
    last_timestamp = last_timestamps.get(domain_name, "")
    
    for attack_type in available_types:
        logging.info(f"Fetching attack path timeline for {domain_name} [{attack_type}]...")
        attack_path_timeline = bloodhound_manager.get_attack_path_sparkline_timeline(
            domain_id, attack_type, start_from=last_timestamp
        )
        
        if attack_path_timeline:
            domain_attack_path_entries.extend(attack_path_timeline)
            logging.info(f"Fetched {len(attack_path_timeline)} entries for {attack_type} in domain {domain_name}.")
        else:
            logging.warning(f"No data returned for {attack_type} in domain {domain_name}.")
    
    return domain_attack_path_entries


def update_timestamps(domain_entries, current_tenant_domain, domain_name, last_timestamps):
    """Update timestamps for a domain based on collected entries."""
    if domain_entries:
        latest_timestamp = max(
            [ap.get("updated_at", "") for ap in domain_entries if ap.get("updated_at")],
            default=None
        )
        if latest_timestamp:
            if current_tenant_domain not in last_timestamps:
                last_timestamps[current_tenant_domain] = {}
            last_timestamps[current_tenant_domain][domain_name] = latest_timestamp
            logging.info(f"Updated last_attack_path_timeline_timestamps for {current_tenant_domain}/{domain_name} to {latest_timestamp}")


def _prepare_attack_path_timeline_log_entry(attack_data: dict, unique_finding_types_data: dict, 
                                             tenant_domain: str, domains_data: list) -> dict:
    """Helper function to prepare a single attack path timeline log entry."""
    domain_name = ""
    # Find the domain name from the domains_data based on DomainSID
    for domain in domains_data:
        if domain.get("id") == attack_data.get("DomainSID"):
            domain_name = domain.get("name", "")
            break

    finding_type = attack_data.get("Finding", "")
    path_title = unique_finding_types_data.get(finding_type, "")

    return {
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
        "tenant_url": tenant_domain,
        "domain_name": domain_name,
        "path_title": path_title,
        "finding_type": finding_type,
        "TimeGenerated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds") + "Z",
    }


def process_environment(bloodhound_manager, env_config, tenant_domain, last_timestamps):
    """Process a single environment for attack path timeline collection."""
    # Get and filter domains
    res_domains = bloodhound_manager.get_available_domains()
    if not res_domains:
        logging.error("Failed to fetch available domains.")
        return last_timestamps
    
    all_domains_data = res_domains.get("data", [])
    selected_environments = env_config.selected_environments if env_config.selected_environments else "all"
    filtered_domains = filter_domains_by_environment(all_domains_data, selected_environments)
    if not filtered_domains:
        logging.info("No collected or selected environments found to query attack paths.")
        return last_timestamps
    
    # Filter domains by finding types
    selected_finding_types = env_config.selected_finding_types if env_config.selected_finding_types else "all"
    final_domains = filter_domains_by_finding_types(bloodhound_manager, filtered_domains, selected_finding_types)
    if not final_domains:
        logging.info("No domains or finding types remain after filtering.")
        return last_timestamps
    
    # Get finding types details
    unique_finding_types_data = bloodhound_manager.get_all_path_asset_details_for_finding_types(final_domains)
    logging.info(f"Fetched asset text details for {len(unique_finding_types_data)} unique finding types/details combinations.")
    
    # Collect timeline data
    consolidated_timeline = []
    tenant_timestamps = last_timestamps.get(tenant_domain, {})
    
    for domain in final_domains:
        domain_entries = collect_attack_path_timeline(bloodhound_manager, domain, tenant_timestamps)
        if domain_entries:
            consolidated_timeline.extend(domain_entries)
            update_timestamps(domain_entries, tenant_domain, domain.get("name"), last_timestamps)
    
    if not consolidated_timeline:
        logging.info("No attack path timeline data to send to Azure Monitor.")
        return last_timestamps
    
    # Submit data to Azure Monitor in batches
    token = bloodhound_manager.get_bearer_token()
    if not token:
        logging.error("Failed to obtain Bearer token for Azure Monitor.")
        return last_timestamps
    
    batch_size = get_azure_batch_size()
    logging.info(f"Sending {len(consolidated_timeline)} attack path timeline records to Azure Monitor in batches of {batch_size}.")
    
    successful_submissions = 0
    failed_submissions = 0
    
    # Process in batches
    for batch_start in range(0, len(consolidated_timeline), batch_size):
        batch_end = min(batch_start + batch_size, len(consolidated_timeline))
        batch = consolidated_timeline[batch_start:batch_end]
        
        # Prepare log entries for this batch
        log_entries = []
        for attack_data in batch:
            try:
                log_entry = _prepare_attack_path_timeline_log_entry(
                    attack_data, unique_finding_types_data, tenant_domain, final_domains
                )
                log_entries.append(log_entry)
            except Exception as e:
                failed_submissions += 1
                logging.error(f"Failed to prepare attack path timeline log entry for ID {attack_data.get('id')}: {str(e)}")
        
        if not log_entries:
            continue
        
        # Send batch to Azure Monitor
        logging.info(f"Sending batch {batch_start//batch_size + 1} ({len(log_entries)} entries): IDs {[entry.get('id') for entry in log_entries[:5]]}...")
        result = bloodhound_manager._send_to_azure_monitor(
            log_entries,
            token,
            bloodhound_manager.dce_uri,
            bloodhound_manager.dcr_immutable_id,
            bloodhound_manager.table_name
        )
        
        if result and result.get("status") == "success":
            entries_sent = result.get("entries_sent", len(log_entries))
            successful_submissions += entries_sent
            logging.info(f"Successfully sent batch of {entries_sent} attack path timeline records")
        else:
            failed_submissions += len(log_entries)
            logging.error(f"Failed to send batch: {result.get('message', 'Unknown error')}")
        
        # Rate limiting is handled automatically by azure_monitor_rate_limiter in _send_to_azure_monitor()
    
    logging.info(f"Attack path timeline sending complete. Successful: {successful_submissions}, Failed: {failed_submissions}")
    return last_timestamps


def run_attack_paths_timeline_collection_process(last_attack_path_timeline_timestamps=None):
    """Orchestrates the BloodHound attack paths timeline collection process."""
    logging.info("Starting BloodHound attack paths timeline collection process.")
    last_attack_path_timeline_timestamps = last_attack_path_timeline_timestamps or {}

    # Load environment configuration
    env_configs, azure_config = load_environment_configs("ATTACK_PATHS_TIMELINE_TABLE_NAME")
    if not env_configs:
        logging.error("No valid environment configurations found.")
        return
    
    # Process each environment
    for i, env_config in enumerate(env_configs, 1):
        logging.info(f"\n--- Starting process for BloodHound Environment #{i} at '{env_config.tenant_domain}' ---")
        
        bloodhound_manager = initialize_bloodhound_manager(
            env_config.tenant_domain,
            env_config.token_id,
            env_config.token_key,
            azure_config.tenant_id,
            azure_config.app_id,
            azure_config.app_secret,
            azure_config.dce_uri,
            azure_config.dcr_immutable_id,
            azure_config.table_name
        )
        
        if bloodhound_manager:
            last_attack_path_timeline_timestamps = process_environment(
                bloodhound_manager,
                env_config,
                env_config.tenant_domain,
                last_attack_path_timeline_timestamps
            )
    
    logging.info("BloodHound attack paths timeline collection process completed.")
    logging.info(f"Final last_attack_path_timeline_timestamps state: {last_attack_path_timeline_timestamps}")
    return last_attack_path_timeline_timestamps