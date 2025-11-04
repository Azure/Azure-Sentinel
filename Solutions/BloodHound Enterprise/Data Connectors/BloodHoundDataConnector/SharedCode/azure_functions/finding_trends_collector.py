import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from ..utility.utils import (
    EnvironmentConfig,
    AzureConfig,
    load_environment_configs
)
from ..utility.bloodhound_manager import BloodhoundManager

@dataclass
class FindingTrend:
    """Represents a finding trend data point to be sent to Azure Monitor."""
    finding: Dict[str, Any]
    period: str
    environment_id: str
    start_date: str
    end_date: str

def send_finding_trends_to_azure_monitor(
    findings: List[Dict[str, Any]],
    bloodhound_manager: BloodhoundManager, 
    azure_monitor_token: str,
    current_tenant_domain: str,
    domains_data: List[Dict[str, Any]]
) -> Tuple[int, int]:
    """
    Sends finding trends data to Azure Monitor.

    Args:
        findings: List of finding trends to send (dictionaries)
        bloodhound_manager: The configured BloodHound manager instance
        azure_monitor_token: Valid Azure Monitor bearer token
        current_tenant_domain: The current tenant domain being processed
        domains_data: List of filtered domain data

    Returns:
        Tuple of (successful_submissions, failed_submissions)
    """
    successful_submissions = 0
    failed_submissions = 0

    if not findings:
        logging.info("No finding trends to send to Azure Monitor for this environment")
        return successful_submissions, failed_submissions

    # Convert dictionaries to FindingTrend objects
    finding_trends = [
        FindingTrend(
            finding=item["finding"],
            period=item["period"],
            environment_id=item["environment_id"],
            start_date=item["start_date"],
            end_date=item["end_date"]
        ) 
        for item in findings
    ]

    logging.info(f"Sending {len(finding_trends)} collected finding trends to Azure Monitor.")
    for idx, item in enumerate(finding_trends, 1):
        logging.info(f"Processing finding trends log entry {idx}/{len(finding_trends)}: {item.finding.get('finding')} in environment ID {item.environment_id}")
        
        result = bloodhound_manager.send_finding_trends_logs(
            item.finding, 
            azure_monitor_token, 
            current_tenant_domain, 
            domains_data,
            environment_id=item.environment_id,
            start_date=item.start_date,
            end_date=item.end_date,
            period=item.period
        )

        if result and result.get("status") == "success":
            successful_submissions += 1
            logging.info(f"Successfully sent finding trends for '{item.finding.get('finding')}'")
        else:
            failed_submissions += 1
            error_msg = result.get("message", "Unknown error") if result else "No response"
            logging.error(f"Failed to send finding trends for '{item.finding.get('finding')}': {error_msg}")
        
        time.sleep(0.1)  # Rate limiting between requests

    logging.info(
        f"Finding trends processing for '{current_tenant_domain}' complete. Successful: {successful_submissions}, Failed: {failed_submissions}."
    )
    return successful_submissions, failed_submissions


def filter_domains_by_environment(
    domains_data: List[Dict[str, Any]],
    selected_environments: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter domains based on collection status and selected environments.
    
    Args:
        domains_data: List of domains from BloodHound API
        selected_environments: Selected environments string from config, if None or "all" all collected domains are included
    
    Returns:
        List of filtered domain data
    """
    # Default to including all collected domains if selected_environments is None or "all"
    if not selected_environments or selected_environments.strip().lower() == "all":
        filtered_domains = [
            domain for domain in domains_data if domain.get("collected") is True
        ]
    else:
        domain_names_to_include = [
            name.strip() for name in selected_environments.split(",")
        ]
        filtered_domains = [
            domain
            for domain in domains_data
            if domain.get("collected") is True
            and domain.get("name", "").strip() in domain_names_to_include
        ]
    
    return filtered_domains


def collect_finding_trends_for_timeframe(
    bloodhound_manager: BloodhoundManager,
    environment_ids: List[str],
    time_frames_in_days: List[int],
    time_period_map: Dict[int, str]
) -> List[Dict[str, Any]]:
    """
    Collect finding trends for the specified timeframes and environments.
    
    Args:
        bloodhound_manager: The configured BloodHound manager instance
        environment_ids: List of environment IDs to collect from
        time_frames_in_days: List of timeframes in days to collect
        time_period_map: Mapping of days to period names
    
    Returns:
        List of findings to send to Azure Monitor
    """
    all_findings_to_send = []
    
    for days in time_frames_in_days:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        for env_id in environment_ids:
            logging.info(f"Fetching finding trends for environment ID: {env_id} for period of {days} days")
            finding_trends_response = bloodhound_manager.get_finding_trends(
                environment_id=env_id, start_date=start_date
            )

            if finding_trends_response and finding_trends_response.get("data", {}).get("findings"):
                start_date_from_api = finding_trends_response.get("start", "")
                end_date = finding_trends_response.get("end", "")
                finding_trends_findings = finding_trends_response.get("data").get("findings", [])
                
                logging.info(f"Found {len(finding_trends_findings)} findings for {env_id} in {days} days period")
                for finding in finding_trends_findings:
                    all_findings_to_send.append({
                        "finding": finding,
                        "environment_id": env_id,
                        "start_date": start_date_from_api,
                        "end_date": end_date,
                        "period": time_period_map.get(days, f"{days} days"),
                    })
            else:
                logging.warning(f"No finding trends found for environment ID: {env_id} for {days} days period.")
    
    return all_findings_to_send


def process_environment(
    env_config: EnvironmentConfig,
    azure_config: AzureConfig,
) -> bool:
    """
    Process finding trends for a single environment configuration.
    
    Args:
        env_config: Configuration for the environment
        azure_config: Azure configuration settings
        selected_environments: Selected environments string from config
    
    Returns:
        True if processing was successful
    """
    logging.info(f"\n--- Starting finding trends collection for environment '{env_config.tenant_domain}' ---")

    # Initialize BloodhoundManager
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
        logging.error(f"BloodHound API connection test failed for '{env_config.tenant_domain}'. Aborting.")
        return False

    logging.info(f"BloodHound API connection test passed for '{env_config.tenant_domain}'. Starting collection...")

    # Get available domains
    res_domains = bloodhound_manager.get_available_domains()
    if not res_domains:
        logging.error("Failed to fetch available domains. Cannot proceed with finding trends.")
        return False

    domains_data = res_domains.get("data", [])
    logging.info(f"Found {len(domains_data)} domains from BloodHound API.")

    # Filter domains
    filtered_domains = filter_domains_by_environment(domains_data, env_config.selected_environments)
    if not filtered_domains:
        logging.info("No collected or selected environments found. Skipping.")
        return True

    environment_ids = [domain["id"] for domain in filtered_domains if domain.get("id")]
    if not environment_ids:
        logging.info("No environment IDs found. Skipping this environment.")
        return True

    # Get Bearer Token for Azure Monitor
    azure_monitor_token = bloodhound_manager.get_bearer_token()
    if not azure_monitor_token:
        logging.error("Failed to obtain Bearer token for Azure Monitor. Aborting submission.")
        return False

    # Define timeframes
    time_frames_in_days = [365, 180, 90, 30, 7]
    time_period_map = {
        365: "1 year",
        180: "6 months",
        90: "3 months",
        30: "1 month",
        7: "1 week"
    }

    # Collect findings
    all_findings_to_send = collect_finding_trends_for_timeframe(
        bloodhound_manager,
        environment_ids,
        time_frames_in_days,
        time_period_map
    )

    if all_findings_to_send:
        successful_submissions, failed_submissions = send_finding_trends_to_azure_monitor(
            all_findings_to_send,
            bloodhound_manager,
            azure_monitor_token,
            env_config.tenant_domain,
            domains_data
        )
        logging.info(f"Successful submissions: {successful_submissions} & Failed submissions: {failed_submissions}")
        return successful_submissions > 0

    return True


def run_finding_trends_collection_process() -> bool:
    """
    Orchestrates the entire BloodHound Finding Trends collection process.
    Returns True if successful, False otherwise.
    """
    logging.info("Starting BloodHound Finding Trends collection process.")

    # Load configurations
    env_configs, azure_config = load_environment_configs("FINDING_TRENDS_TABLE_NAME")
    
    # Process each environment
    success = True
    for env_config in env_configs:
        if not process_environment(env_config, azure_config):
            success = False

    logging.info("BloodHound Finding Trends collection process completed for all environments")
    return success