import logging
import os
import time

# Import Azure SDKs for Key Vault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

from bloodhound_manager import (
    BloodhoundManager,
)  # This also often works in Azure Functions


def bloodhound_audit_logs_collector_main_function() -> None:
    """
    Azure Function Timer Trigger to collect BloodHound audit logs and send them to Azure Monitor.
    """
    logging.info(
        "Python timer trigger function 'bloodhound_audit_logs_collector' executed."
    )
    try:
        tenant_domain = os.environ["BLOODHOUND_TENANT_DOMAIN"]
        tenant_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_TENANT_ID"]
        app_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_ID"]
        app_secret = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_SECRET"]
        dce_uri = os.environ["DCE_URI"]
        dcr_immutable_id = os.environ["DCR_IMMUTABLE_ID"]  # Use POSTURE DCR ID
        table_name = os.environ["AUDIT_LOGS_TABLE_NAME"]  # Use POSTURE Table Name
        token_id_secret_name = os.environ["BLOODHOUND_TOKEN_ID_SECRET_NAME"]
        token_key_secret_name = os.environ["BLOODHOUND_TOKEN_KEY_SECRET_NAME"]
        key_vault_url = os.environ["KEY_VAULT_URL"]

        logging.info(
            f"Config loaded. Tenant Domain: {tenant_domain}, Key Vault URL: {key_vault_url}"
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
            f"One or both secrets not found in Azure Key Vault. Ensure '{token_id_secret_name}' and '{token_key_secret_name}' exist. Error: {e}"
        )
        return
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while retrieving secrets from Azure Key Vault: {e}"
        )
        return

    logging.info(f"Tokens are: Token ID: {token_id}, Token Key: {token_key}")

    # 3. Initialize BloodhoundManager
    bloodhound_manager = BloodhoundManager(
        tenant_domain, token_id, token_key, logger=logging
    )
    bloodhound_manager.set_azure_monitor_config(
        tenant_id, app_id, app_secret, dce_uri, dcr_immutable_id, table_name
    )

    # 4. Test BloodHound API connection
    connection_response = bloodhound_manager.test_connection()
    if not connection_response:
        logging.error("BloodHound API connection test failed. Aborting log collection.")
        return

    logging.info(
        f"BloodHound API connection test passed. Starting log collection...with response: {connection_response}"
    )

    # 5. Fetch Audit Logs from BloodHound
    audit_logs = bloodhound_manager.get_audit_logs()
    if not audit_logs:
        logging.error(
            "Failed to fetch audit logs from BloodHound. Aborting log submission."
        )
        return

    logging.info(f"Retrieved {len(audit_logs)} audit logs from BloodHound.")

    if not audit_logs:
        logging.info("No new audit logs found to process.")
        return

    # 6. Get Bearer Token for Azure Monitor
    azure_monitor_token = bloodhound_manager.get_bearer_token()
    if not azure_monitor_token:
        logging.error(
            "Failed to obtain Bearer token for Azure Monitor. Aborting log submission."
        )
        return

    # 7. Send Audit Logs to Azure Monitor
    successful_submissions = 0
    failed_submissions = 0
    for log_entry in audit_logs[:100]:
        try:
            result = bloodhound_manager.send_audit_logs_data(
                log_entry, azure_monitor_token
            )
            if result.get("status") == "success":
                successful_submissions += 1
            else:
                failed_submissions += 1
                logging.error(
                    f"Failed to send audit log ID {log_entry.get('id')}: {result.get('message', 'Unknown error')}"
                )
            time.sleep(0.1)
        except Exception as e:
            failed_submissions += 1
            logging.error(
                f"Exception while sending audit log ID {log_entry.get('id')}: {e}"
            )

    logging.info(
        f"Audit log processing complete. Successful submissions: {successful_submissions}, Failed submissions: {failed_submissions}."
    )
    logging.info(
        "Python timer trigger function 'bloodhound_audit_logs_collector' finished execution."
    )
