from typing import Dict, List, Tuple, Optional, Any
import logging
import time
import json
from ..utility.utils import load_environment_configs, EnvironmentConfig, AzureConfig, get_azure_batch_size
from ..utility.bloodhound_manager import BloodhoundManager

def process_environment(
    env_config: EnvironmentConfig,
    azure_config: AzureConfig,
    last_timestamp: str
) -> Tuple[int, int, Optional[str]]:
    """
    Process a single BloodHound environment.
    
    Args:
        env_config: Configuration for the BloodHound environment
        azure_config: Azure-specific configuration
        last_timestamp: Last processed timestamp for this environment
    
    Returns:
        Tuple of (successful_submissions, failed_submissions, new_last_timestamp)
    """
    logging.info(f"\n--- Starting audit log collection for environment '{env_config.tenant_domain}' ---")
    
    # Initialize BloodHound manager
    bloodhound_manager = BloodhoundManager(
        env_config.tenant_domain,
        env_config.token_id,
        env_config.token_key,
        logger=logging
    )
    bloodhound_manager.set_azure_monitor_config(
        azure_config.tenant_id,
        azure_config.app_id,
        azure_config.app_secret,
        azure_config.dce_uri,
        azure_config.dcr_immutable_id,
        azure_config.table_name
    )

    # Test connection
    if not bloodhound_manager.test_connection():
        logging.error(f"BloodHound API connection test failed for '{env_config.tenant_domain}'")
        return 0, 0, None

    # Fetch audit logs
    audit_logs = bloodhound_manager.get_audit_logs(last_timestamp)
    if not audit_logs:
        logging.warning(f"No new audit logs found for environment '{env_config.tenant_domain}'")
        return 0, 0, None

    logging.info(f"Retrieved {len(audit_logs)} audit logs from BloodHound for '{env_config.tenant_domain}'")

    # Get Azure Monitor token
    azure_monitor_token = bloodhound_manager.get_bearer_token()
    if not azure_monitor_token:
        logging.error("Failed to obtain Bearer token for Azure Monitor")
        return 0, 0, None

    # Process logs
    successful, failed = send_audit_logs_to_azure_monitor(
        audit_logs,
        bloodhound_manager,
        azure_monitor_token,
        env_config.tenant_domain
    )

    new_last_timestamp = None
    if successful > 0:
        new_last_timestamp = max(log["created_at"] for log in audit_logs if "created_at" in log)
        logging.info(f"Updated last processed timestamp for '{env_config.tenant_domain}' to {new_last_timestamp}")

    return successful, failed, new_last_timestamp

def bloodhound_audit_logs_collector_main_function(
    last_audit_logs_timestamp: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Azure Function Timer Trigger to collect BloodHound audit logs and send them to Azure Monitor.
    This version processes multiple BloodHound environments.
    
    Args:
        last_audit_logs_timestamp: Dictionary mapping tenant domains to their last processed timestamps
    
    Returns:
        Updated dictionary of last processed timestamps per tenant domain
    
    Raises:
        KeyError: If required environment variables are missing
        ValueError: If configuration is invalid
        Exception: For any other unexpected errors
    """
    logging.info("Python timer trigger function 'bloodhound_audit_logs_collector' executed.")
    last_audit_logs_timestamp = last_audit_logs_timestamp or {}

    # Load configurations with audit logs table
    env_configs, azure_config = load_environment_configs("AUDIT_LOGS_TABLE_NAME")
    logging.info(f"Config loaded. Key Vault URL: {azure_config.key_vault_url}")
    logging.info(f"Identified {len(env_configs)} BloodHound environments to process.")

    # Process each environment
    for env_config in env_configs:
        successful, failed, new_timestamp = process_environment(
            env_config,
            azure_config,
            last_audit_logs_timestamp.get(env_config.tenant_domain, "")
        )

        logging.info(f"Environment '{env_config.tenant_domain}': Successful submissions: {successful}, Failed submissions: {failed}")

        if successful > 0 and new_timestamp:
            last_audit_logs_timestamp[env_config.tenant_domain] = new_timestamp
            logging.info(f"Updated timestamp for '{env_config.tenant_domain}' to {new_timestamp}")
        else:
            logging.info(f"No successful submissions for '{env_config.tenant_domain}'. Timestamp unchanged.")

        logging.info(f"--- Finished audit log collection for environment '{env_config.tenant_domain}' ---\n")

    logging.info("All environments processed successfully.")
    return last_audit_logs_timestamp

def send_audit_logs_to_azure_monitor(
    audit_logs: List[Dict[str, Any]],
    bloodhound_manager: BloodhoundManager,
    azure_monitor_token: str,
    current_tenant_domain: str
) -> Tuple[int, int]:
    """
    Sends audit logs to Azure Monitor in batches of 100.
    
    Args:
        audit_logs: List of audit log entries to process
        bloodhound_manager: Instance of BloodHoundManager
        azure_monitor_token: Azure Monitor bearer token
        current_tenant_domain: Current tenant domain being processed
    
    Returns:
        Tuple of (successful_submissions, failed_submissions)
    
    Raises:
        Exception: If there's an error sending logs to Azure Monitor
    """
    successful_submissions = failed_submissions = 0
    batch_size = get_azure_batch_size()
    logging.info(f"Processing {len(audit_logs)} audit logs for '{current_tenant_domain}' in batches of {batch_size}")
    
    # Process in batches
    for batch_start in range(0, len(audit_logs), batch_size):
        batch_end = min(batch_start + batch_size, len(audit_logs))
        batch = audit_logs[batch_start:batch_end]
        
        # Transform batch entries to the expected schema for Azure Monitor
        log_entries = []
        for data in batch:
            log_entry = {
                "action": data.get("action", ""),
                "actor_email": data.get("actor_email", ""),
                "actor_id": data.get("actor_id", ""),
                "actor_name": data.get("actor_name", ""),
                "commit_id": data.get("commit_id", ""),
                "created_at": data.get("created_at", ""),
                "fields": json.dumps(data.get("fields", {})),  # fields should be a string in Log Analytics
                "id": data.get("id", ""),
                "request_id": data.get("request_id", ""),
                "source_ip_address": data.get("source_ip_address", ""),
                "status": data.get("status", ""),
                "tenant_url": current_tenant_domain,
            }
            log_entries.append(log_entry)
        
        logging.info(f"Sending batch {batch_start//batch_size + 1} ({len(log_entries)} entries): IDs {[log.get('id', 'unknown') for log in log_entries[:5]]}...")
        
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
            logging.info(f"Successfully sent batch of {entries_sent} audit logs")
        else:
            failed_submissions += len(log_entries)
            logging.error(f"Failed to send batch: {result.get('message', 'Unknown error') if result else 'No response'}")
        
        # Rate limiting is handled automatically by azure_monitor_rate_limiter in _send_to_azure_monitor()

    logging.info(
        f"Audit log processing for '{current_tenant_domain}' complete. "
        f"Successful: {successful_submissions}, Failed: {failed_submissions}"
    )
    return successful_submissions, failed_submissions