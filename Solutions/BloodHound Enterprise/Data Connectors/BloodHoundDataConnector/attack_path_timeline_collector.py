import logging
import os
import time
import json

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

from bloodhound_manager import BloodhoundManager


def run_attack_paths_timeline_collection_process() -> None:
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
        dcr_immutable_id = os.environ["DCR_IMMUTABLE_ID"]
        table_name = os.environ["ATTACK_PATHS_TIMELINE_TABLE_NAME"]
        token_id_secret_name = os.environ["BLOODHOUND_TOKEN_ID_SECRET_NAME"]
        token_key_secret_name = os.environ["BLOODHOUND_TOKEN_KEY_SECRET_NAME"]
        key_vault_url = os.environ["KEY_VAULT_URL"]
        selected_bhe_environments = os.environ["SELECTED_BLOODHOUND_ENVIRONMENTS"]
        selected_finding_types = os.environ["SELECTED_FINDING_TYPES"]

        logging.info(
            f"Configuration loaded for attack paths. Key Vault URL: {key_vault_url}"
        )
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

    logging.info(f"Tokens retrieved for attack paths.")

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
        f"Filtered {len(filtered_domains_by_env)} domains for attack path collection based on environments."
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
            filtered_domain_types = available_types

        if filtered_domain_types:
            domain["available_types"] = filtered_domain_types
            final_domains_to_process.append(domain)
            logging.info(
                f"Domain '{domain_name}' has {len(filtered_domain_types)} relevant finding types after filtering."
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

    consolidated_attack_paths_timeline = []

    for domain in final_domains_to_process:
        domain_id = domain.get("id")
        domain_name = domain.get("name")
        available_types = domain.get("available_types", [])

        if not available_types:
            logging.warning(
                f"No available types for domain {domain_name} after filtering. Skipping."
            )
            continue

        for attack_type in available_types:
            logging.info(
                f"Fetching attack path timeline for {domain_name} [{attack_type}]..."
            )

            attack_path_timeline = (
                bloodhound_manager.get_attack_path_sparkline_timeline(
                    domain_id, attack_type
                )
            )

            if attack_path_timeline:
                consolidated_attack_paths_timeline.extend(
                    attack_path_timeline
                )  # Use extend instead of append
                logging.info(
                    f"Fetched {len(attack_path_timeline)} attack path timeline entries for {attack_type} in domain {domain_name}."
                )
            else:
                logging.warning(
                    f"Failed to fetch attack path timeline for {attack_type} in domain {domain_name} or no data returned."
                )

    logging.info(
        f"Total consolidated attack path timeline entries: {len(consolidated_attack_paths_timeline)}"
    )

    # 8. Get Bearer Token for Azure Monitor (re-calling here to ensure freshness)
    token = bloodhound_manager.get_bearer_token()
    if not token:
        logging.error(
            "Failed to obtain Bearer token for Azure Monitor. Aborting data submission."
        )
        return

    logging.info("Bearer token obtained successfully for Azure Monitor.")

    # 9. Fetch and send posture stats (attack path timeline data)
    submission_results = []
    if not consolidated_attack_paths_timeline:
        logging.info("No attack path timeline data to send to Azure Monitor. Exiting.")
        return

    for i, attack in enumerate(consolidated_attack_paths_timeline, 1):
        logging.info(
            f"Sending attack data {i}/{len(consolidated_attack_paths_timeline)}: ID {attack.get('id')}"
        )
        try:
            res = bloodhound_manager.send_attack_path_timeline_data(
                attack,
                token,
                unique_finding_types_data,
                final_domains_to_process,
            )
            submission_results.append(
                {"id": attack.get("id"), "status": "success", "response": res}
            )
        except Exception as e:
            logging.error(f"Error sending attack data ID {attack.get('id')}: {e}")
            submission_results.append(
                {"id": attack.get("id"), "status": "error", "message": str(e)}
            )
        time.sleep(0.1)  # Small delay to avoid hammering the API

    logging.info(
        f"All attack path timeline data submission results: {json.dumps(submission_results, indent=2)}"
    )
    logging.info("BloodHound attack paths collection process completed.")
