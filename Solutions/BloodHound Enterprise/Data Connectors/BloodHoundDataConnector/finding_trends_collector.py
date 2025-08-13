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


def run_finding_trends_collection_process() -> None:
    """
    Orchestrates the entire BloodHound finding trends collection and Azure Monitor submission process.
    """
    logging.info("Starting BloodHound finding trends collection process.")
    try:
        tenant_domain = os.environ["BLOODHOUND_TENANT_DOMAIN"]
        tenant_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_TENANT_ID"]
        app_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_ID"]
        app_secret = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_SECRET"]
        dce_uri = os.environ["DCE_URI"]
        dcr_immutable_id = os.environ["DCR_IMMUTABLE_ID"]
        table_name = os.environ["FINDING_TRENDS_TABLE_NAME"]
        token_id_secret_name = os.environ["BLOODHOUND_TOKEN_ID_SECRET_NAME"]
        token_key_secret_name = os.environ["BLOODHOUND_TOKEN_KEY_SECRET_NAME"]
        key_vault_url = os.environ["KEY_VAULT_URL"]

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
            f"One or both secrets not found in Azure Key Vault for finding trends. Ensure '{token_id_secret_name}' and '{token_key_secret_name}' exist. Error: {e}. Exiting process."
        )
        return
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while retrieving secrets from Azure Key Vault for finding trends: {e}. Exiting process."
        )
        return

    logging.info(f"Tokens retrieved for finding trends. Token ID: {token_id}")

    # 3. Initialize BloodhoundManager for finding trends
    bloodhound_manager = BloodhoundManager(
        tenant_domain, token_id, token_key, logger=logging
    )
    bloodhound_manager.set_azure_monitor_config(
        tenant_id, app_id, app_secret, dce_uri, dcr_immutable_id, table_name
    )

    # 4. Test BloodHound API connection
    connection_response = bloodhound_manager.test_connection()
    if not connection_response:
        logging.error(
            "BloodHound API connection test failed for finding trends. Aborting collection."
        )
        return

    logging.info(
        "BloodHound API connection test passed for finding trends. Starting collection..."
    )

    # 5. Get available domains from BloodHound
    res_domains = bloodhound_manager.get_available_domains()
    if not res_domains:
        logging.error(
            "Failed to fetch available domains. Cannot proceed with finding trends."
        )
        return

    domains_data = res_domains.get("data", [])
    logging.info(f"Found {len(domains_data)} domains from BloodHound API.")

    # Filter domains
    filtered_domains = [
        domain for domain in domains_data if domain.get("collected") is True
    ]

    environment_ids = [domain["id"] for domain in filtered_domains if domain.get("id")]
    logging.info(f"Processing Finding Trends for Environment IDs: {environment_ids}")

    if not environment_ids:
        logging.info(
            "No collected or selected environment IDs found to query finding trends. Exiting."
        )
        return

    # 6. Get Bearer Token for Azure Monitor
    azure_monitor_token = bloodhound_manager.get_bearer_token()
    if not azure_monitor_token:
        logging.error(
            "Failed to obtain Bearer token for Azure Monitor for finding trends. Aborting submission."
        )
        return

    # 7. Fetch and send finding trends
    all_findings_to_send = []
    for env_id in environment_ids:
        logging.info(f"Fetching finding trends for environment ID: {env_id}")
        finding_trends_response = bloodhound_manager.get_finding_trends(
            environment_id=env_id
        )

        if finding_trends_response:
            start_date = finding_trends_response.get("start", "")
            end_date = finding_trends_response.get("end", "")
            finding_trends_data = finding_trends_response.get("data", {})
            finding_trends_findings = finding_trends_data.get("findings", [])

            if finding_trends_findings:
                logging.info(
                    f"Found {len(finding_trends_findings)} findings for {env_id}"
                )
                for finding in finding_trends_findings:
                    all_findings_to_send.append(
                        {
                            "finding": finding,
                            "environment_id": env_id,
                            "start_date": start_date,
                            "end_date": end_date,
                        }
                    )
            else:
                logging.info(f"No findings found for environment ID: {env_id}")
        else:
            logging.warning(
                f"Failed to fetch finding trends for environment ID: {env_id}"
            )

    successful_submissions = 0
    failed_submissions = 0

    if all_findings_to_send:
        logging.info(
            f"Sending {len(all_findings_to_send)} collected finding trends to Azure Monitor."
        )
        for i, item in enumerate(all_findings_to_send, 1):
            data = item["finding"]
            env_id_for_log = item["environment_id"]

            try:
                result = bloodhound_manager.send_finding_trends_logs(
                    data,
                    azure_monitor_token,
                    tenant_domain,  # Pass tenant_domain as it's part of the log entry
                    domains_data,  # Pass domains_data for lookup
                    environment_id=env_id_for_log,
                    start_date=item["start_date"],
                    end_date=item["end_date"],
                )
                if result.get("status") == "success":
                    successful_submissions += 1
                else:
                    failed_submissions += 1
                    logging.error(
                        f"Failed to send finding trends log for '{data.get('finding')}': {result.get('message', 'Unknown error')}"
                    )
            except Exception as e:
                failed_submissions += 1
                logging.error(
                    f"Exception while sending finding trends log for '{data.get('finding')}': {e}"
                )
            time.sleep(0.1)  # Small delay to avoid hitting potential rate limits

        logging.info(
            f"Finding trends processing complete. Successful submissions: {successful_submissions}, Failed submissions: {failed_submissions}."
        )
    else:
        logging.info("No finding trends were collected to send to Azure Monitor.")

    logging.info("BloodHound finding trends collection process finished.")
