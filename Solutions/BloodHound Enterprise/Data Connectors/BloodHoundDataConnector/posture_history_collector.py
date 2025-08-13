import logging
import os
import time

# Import Azure SDKs for Key Vault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

# Import BloodhoundManager from the same directory
from bloodhound_manager import (
    BloodhoundManager,
)


def run_posture_history_collection_process() -> None:
    """
    Orchestrates the entire BloodHound posture history collection and Azure Monitor submission process.
    """
    logging.info("Starting BloodHound posture history collection process.")

    try:
        tenant_domain = os.environ["BLOODHOUND_TENANT_DOMAIN"]
        tenant_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_TENANT_ID"]
        app_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_ID"]
        app_secret = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_SECRET"]
        dce_uri = os.environ["DCE_URI"]
        dcr_immutable_id = os.environ["DCR_IMMUTABLE_ID"]  # Use POSTURE DCR ID
        table_name = os.environ["POSTURE_HISTORY_TABLE_NAME"]  # Use POSTURE Table Name
        token_id_secret_name = os.environ["BLOODHOUND_TOKEN_ID_SECRET_NAME"]
        token_key_secret_name = os.environ["BLOODHOUND_TOKEN_KEY_SECRET_NAME"]
        key_vault_url = os.environ["KEY_VAULT_URL"]

        logging.info(
            f"Config loaded for posture history. Key Vault URL: {key_vault_url}"
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
            "Successfully retrieved token ID and token key from Azure Key Vault."
        )

    except ResourceNotFoundError as e:
        logging.error(
            f"One or both secrets not found in Azure Key Vault for posture history. Ensure '{token_id_secret_name}' and '{token_key_secret_name}' exist. Error: {e}. Exiting process."
        )
        return
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while retrieving secrets from Azure Key Vault for posture history: {e}. Exiting process."
        )
        return

    logging.info(f"Tokens retrieved for posture history. Token ID: {token_id}")

    # 3. Initialize BloodhoundManager for posture history
    bloodhound_manager = BloodhoundManager(
        tenant_domain, token_id, token_key, logger=logging
    )
    # Configure manager for the specific Azure Monitor table for posture history
    bloodhound_manager.set_azure_monitor_config(
        tenant_id, app_id, app_secret, dce_uri, dcr_immutable_id, table_name
    )

    # 4. Test BloodHound API connection
    connection_response = bloodhound_manager.test_connection()
    if not connection_response:
        logging.error(
            "BloodHound API connection test failed for posture history. Aborting collection."
        )
        return

    logging.info(
        "BloodHound API connection test passed for posture history. Starting collection..."
    )

    # 5. Get available domains from BloodHound
    res_domains = bloodhound_manager.get_available_domains()
    if not res_domains:
        logging.error(
            "Failed to fetch available domains. Cannot proceed with posture history."
        )
        return

    domains_data = res_domains.get("data", [])
    logging.info(f"Found {len(domains_data)} domains from BloodHound API.")

    # Filter domains
    filtered_domains = [
        domain for domain in domains_data if domain.get("collected") is True
    ]

    environment_ids = [domain["id"] for domain in filtered_domains if domain.get("id")]
    logging.info(f"Processing Posture History for Environment IDs: {environment_ids}")

    if not environment_ids:
        logging.info(
            "No collected or selected environment IDs found to query posture history. Exiting."
        )
        return

    # 6. Get Bearer Token for Azure Monitor
    azure_monitor_token = bloodhound_manager.get_bearer_token()
    if not azure_monitor_token:
        logging.error(
            "Failed to obtain Bearer token for Azure Monitor for posture history. Aborting submission."
        )
        return

    # 7. Fetch and send posture history
    data_types_to_fetch = [
        "findings",
        "exposure",
        "assets",
    ]  # Your specified data types
    all_collected_data = []

    for env_id in environment_ids:
        logging.info(f"--- Processing Environment ID: {env_id} for Posture History ---")
        for data_type in data_types_to_fetch:
            logging.info(f"Fetching {data_type} for environment ID: {env_id}")
            posture_history_response = bloodhound_manager.get_posture_history(
                data_type, environment_id=env_id
            )

            if posture_history_response and "data" in posture_history_response:
                type_specific_data = []
                response_data = posture_history_response["data"]

                # Logic to select first, middle, last (if at least 3 elements)
                if len(response_data) >= 3:
                    first_element = response_data[0]
                    middle_element = response_data[len(response_data) // 2]
                    last_element = response_data[-1]
                    type_specific_data = [
                        first_element,
                        middle_element,
                        last_element,
                    ]
                elif len(response_data) > 0:  # If less than 3 but more than 0, take all
                    type_specific_data = response_data

                logging.info(
                    f"Found {len(type_specific_data)} {data_type} entries for environment ID {env_id}"
                )

                for data_item in type_specific_data:
                    # Add additional fields from the response top level and fixed values
                    data_item["start_date"] = posture_history_response.get("start", "")
                    data_item["end_date"] = posture_history_response.get("end", "")
                    # Ensure 'environments' list is not empty before accessing index 0
                    data_item["domain_id"] = posture_history_response.get(
                        "environments", [None]
                    )[0]
                    data_item["type"] = data_type  # Add the data_type itself
                    all_collected_data.append(data_item)
            else:
                logging.warning(
                    f"No {data_type} data found or an error occurred for environment ID {env_id}. Response: {posture_history_response}"
                )

    successful_submissions = 0
    failed_submissions = 0

    if all_collected_data:
        logging.info(
            f"Sending {len(all_collected_data)} collected posture history data points to Azure Monitor."
        )
        for i, data_item in enumerate(all_collected_data, 1):
            try:
                result = bloodhound_manager.send_posture_history_logs(
                    data_item,
                    azure_monitor_token,
                    tenant_domain,
                    domains_data,  # Pass domains_data for lookup
                )
                if result.get("status") == "success":
                    successful_submissions += 1
                else:
                    failed_submissions += 1
                    logging.error(
                        f"Failed to send posture history log for '{data_item.get('type')}' in domain '{data_item.get('domain_id')}': {result.get('message', 'Unknown error')}"
                    )
            except Exception as e:
                failed_submissions += 1
                logging.error(
                    f"Exception while sending posture history log for '{data_item.get('type')}' in domain '{data_item.get('domain_id')}': {e}"
                )
            time.sleep(0.1)  # Small delay to avoid hitting potential rate limits

        logging.info(
            f"Posture history processing complete. Successful submissions: {successful_submissions}, Failed submissions: {failed_submissions}."
        )
    else:
        logging.info("No posture history data was collected to send to Azure Monitor.")

    logging.info("BloodHound posture history collection process finished.")
