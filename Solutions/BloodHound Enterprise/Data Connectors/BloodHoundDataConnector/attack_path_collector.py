import logging
import os
import time
import json

# Import Azure SDKs for Key Vault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

# Import BloodhoundManager from the same directory
from bloodhound_manager import (
    BloodhoundManager,
)


def run_attack_paths_collection_process() -> None:
    """
    Orchestrates the entire BloodHound attack paths collection and Azure Monitor submission process.
    """
    logging.info("Starting BloodHound attack paths collection process.")

    try:

        tenant_domain = os.environ["BLOODHOUND_TENANT_DOMAIN"]
        tenant_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_TENANT_ID"]
        app_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_ID"]
        app_secret = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_SECRET"]
        dce_uri = os.environ["DCE_URI"]
        dcr_immutable_id = os.environ["DCR_IMMUTABLE_ID"]  # Use ATTACK PATHS DCR ID
        table_name = os.environ[
            "ATTACK_PATHS_TABLE_NAME"
        ]  # Use ATTACK PATHS Table Name
        token_id_secret_name = os.environ["BLOODHOUND_TOKEN_ID_SECRET_NAME"]
        token_key_secret_name = os.environ["BLOODHOUND_TOKEN_KEY_SECRET_NAME"]
        key_vault_url = os.environ["KEY_VAULT_URL"]
        selected_bhe_environments = os.environ["SELECTED_BLOODHOUND_ENVIRONMENTS"]
        selected_finding_types = os.environ["SELECTED_FINDING_TYPES"]

        logging.info(f"Config loaded for attack paths. Key Vault URL: {key_vault_url}")
    except KeyError as e:
        logging.error(
            f"Missing one or more required environment variables for posture stats: {e}. Exiting process."
        )
        return
    except Exception as ex:
        logging.error(f"Unexpected Error occured. {ex}")
        return

    # 2. Fetch API tokens from Azure Key Vault
    try:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

        token_id = secret_client.get_secret(token_id_secret_name).value
        token_key = secret_client.get_secret(token_key_secret_name).value
        logging.info(
            "Successfully retrieved token ID and token key from Azure Key Vault for attack paths."
        )

    except ResourceNotFoundError as e:
        logging.error(
            f"One or both secrets not found in Azure Key Vault for attack paths. Ensure '{token_id_secret_name}' and '{token_key_secret_name}' exist. Error: {e}. Exiting process."
        )
        return
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while retrieving secrets from Azure Key Vault for attack paths: {e}. Exiting process."
        )
        return

    logging.info(f"Tokens retrieved for attack paths. Token ID: {token_id}")

    # 3. Initialize BloodhoundManager for attack paths
    bloodhound_manager = BloodhoundManager(
        tenant_domain, token_id, token_key, logger=logging
    )
    # Configure manager for the specific Azure Monitor table for attack paths
    bloodhound_manager.set_azure_monitor_config(
        tenant_id, app_id, app_secret, dce_uri, dcr_immutable_id, table_name
    )

    # 4. Test BloodHound API connection
    connection_response = bloodhound_manager.test_connection()
    if not connection_response:
        logging.error(
            "BloodHound API connection test failed for attack paths. Aborting collection."
        )
        return

    logging.info(
        "BloodHound API connection test passed for attack paths. Starting collection..."
    )

    # 5. Get available domains from BloodHound and apply environment filter
    res_domains = bloodhound_manager.get_available_domains()
    if not res_domains:
        logging.error(
            "Failed to fetch available domains. Cannot proceed with attack paths."
        )
        return

    all_domains_data = res_domains.get("data", [])
    logging.info(f"Found {len(all_domains_data)} domains from BloodHound API.")

    # Apply Selected_BloodHound_Environment filter
    filtered_domains_by_env = []
    if selected_bhe_environments.strip().lower() == "all":
        filtered_domains_by_env = [
            domain for domain in all_domains_data if domain.get("collected") is True
        ]
    else:
        domain_names_to_include = [
            name.strip() for name in selected_bhe_environments.split(",")
        ]
        filtered_domains_by_env = [
            domain
            for domain in all_domains_data
            if domain.get("collected") is True
            and domain.get("name").strip() in domain_names_to_include
        ]

    if not filtered_domains_by_env:
        logging.info(
            "No collected or selected environments found to query attack paths. Exiting."
        )
        return

    logging.info(
        f"Filtered {len(filtered_domains_by_env)} domains for attack path collection."
    )

    # 6. Fetch available finding types for each filtered domain
    # And apply Selected_Finding_Types filter
    final_domains_to_process = []
    selected_finding_types_list = (
        [t.strip() for t in selected_finding_types.split(",")]
        if selected_finding_types.strip().lower() != "all"
        else []
    )

    for domain in filtered_domains_by_env:
        domain_id = domain.get("id")
        domain_name = domain.get("name")

        available_types = bloodhound_manager.get_available_types_for_domain(domain_id)

        if selected_finding_types_list:
            # Filter available types based on user selection
            filtered_domain_types = [
                _type
                for _type in available_types
                if _type in selected_finding_types_list
            ]
        else:
            filtered_domain_types = (
                available_types  # If 'All', take all available types
            )

        if filtered_domain_types:
            domain["available_types"] = filtered_domain_types
            final_domains_to_process.append(domain)
            logging.info(
                f"Domain '{domain_name}' has {len(filtered_domain_types)} relevant finding types."
            )
        else:
            logging.info(
                f"Domain '{domain_name}' has no relevant finding types after filtering. Skipping."
            )

    if not final_domains_to_process:
        logging.info(
            "No domains or finding types remain after filtering for attack path collection. Exiting."
        )
        return

    # 7. Get unique finding types text details (titles, descriptions, remediations)
    unique_finding_types_data = (
        bloodhound_manager.get_all_path_asset_details_for_finding_types(
            final_domains_to_process
        )
    )
    logging.info(
        f"Fetched asset text details for {len(unique_finding_types_data)} unique finding types/details combinations."
    )

    # 8. Get Bearer Token for Azure Monitor
    azure_monitor_token = bloodhound_manager.get_bearer_token()
    if not azure_monitor_token:
        logging.error(
            "Failed to obtain Bearer token for Azure Monitor for attack paths. Aborting submission."
        )
        return

    # 9. Fetch and send attack path details
    all_collected_attack_paths = []

    for domain_entry in final_domains_to_process:
        domain_id = domain_entry.get("id")
        domain_name = domain_entry.get("name")
        available_types_for_domain = domain_entry.get("available_types", [])

        if not available_types_for_domain:
            logging.info(
                f"[SKIPPED] No available types to fetch for domain {domain_name}."
            )
            continue

        for attack_type in available_types_for_domain:
            logging.info(
                f"Fetching attack path details for domain: {domain_name}, type: {attack_type}"
            )
            attack_details_for_type = bloodhound_manager.get_attack_path_details(
                domain_id, attack_type
            )

            if attack_details_for_type:
                all_collected_attack_paths.extend(attack_details_for_type)
                logging.info(
                    f"Fetched {len(attack_details_for_type)} findings for {attack_type} in {domain_name}."
                )
            else:
                logging.warning(
                    f"No attack path details found for {attack_type} in domain {domain_name}."
                )

    successful_submissions = 0
    failed_submissions = 0

    if all_collected_attack_paths:
        logging.info(
            f"Sending {len(all_collected_attack_paths)} collected attack path details to Azure Monitor."
        )
        for i, data_item in enumerate(all_collected_attack_paths, 1):
            try:
                result = bloodhound_manager.send_attack_data(
                    data_item,
                    azure_monitor_token,
                    unique_finding_types_data,  # Pass pre-fetched asset details
                    tenant_domain,  # Pass tenant_domain for the log entry
                    all_domains_data,  # Pass all_domains_data for domain name lookup
                )
                if result.get("status") == "success":
                    successful_submissions += 1
                else:
                    failed_submissions += 1
                    logging.error(
                        f"Failed to send attack path log for ID '{data_item.get('id')}' (Finding: {data_item.get('Finding')}, Domain SID: {data_item.get('DomainSID')}): {result.get('message', 'Unknown error')}"
                    )
            except Exception as e:
                failed_submissions += 1
                logging.error(
                    f"Exception while sending attack path log for ID '{data_item.get('id')}' (Finding: {data_item.get('Finding')}, Domain SID: {data_item.get('DomainSID')}): {e}"
                )
            time.sleep(0.1)  # Small delay to avoid hitting potential rate limits

        logging.info(
            f"Attack paths processing complete. Successful submissions: {successful_submissions}, Failed submissions: {failed_submissions}."
        )
    else:
        logging.info(
            "No attack path details data was collected to send to Azure Monitor."
        )

    logging.info("BloodHound attack paths collection process finished.")
