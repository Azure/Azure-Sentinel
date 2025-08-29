# posture_stats_processor.py
import os
import logging
import json
import time

# Import the BloodhoundManager class
from bloodhound_manager import BloodhoundManager

# For Azure Key Vault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

# Configure logging for the Azure Function
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_posture_stats_collection_process():
    """
    Orchestrates the entire BloodHound posture stats collection and Azure Monitor submission process.
    """
    logging.info("Starting BloodHound posture stats collection process.")

    try:
        tenant_domain = os.environ["BLOODHOUND_TENANT_DOMAIN"]
        tenant_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_TENANT_ID"]
        app_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_ID"]
        app_secret = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_SECRET"]
        dce_uri = os.environ["DCE_URI"]
        dcr_immutable_id = os.environ["DCR_IMMUTABLE_ID"]  # Use POSTURE DCR ID
        table_name = os.environ["POSTURE_STATS_TABLE_NAME"]  # Use POSTURE Table Name
        token_id_secret_name = os.environ["BLOODHOUND_TOKEN_ID_SECRET_NAME"]
        token_key_secret_name = os.environ["BLOODHOUND_TOKEN_KEY_SECRET_NAME"]
        key_vault_url = os.environ["KEY_VAULT_URL"]

        logging.info(f"Config loaded for posture stats. Key Vault URL: {key_vault_url}")
    except KeyError as e:
        logging.error(
            f"Missing one or more required environment variables for posture stats: {e}. Exiting process."
        )
        return
    except Exception as ex:
        logging.error(f"Unexpected Error occured. {ex}")
        return

    logger.info("Starting posture stats processing...")

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
            f"One or both secrets not found in Azure Key Vault for posture stats. Ensure '{token_id_secret_name}' and '{token_key_secret_name}' exist. Error: {e}. Exiting process."
        )
        return
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while retrieving secrets from Azure Key Vault for posture stats: {e}. Exiting process."
        )
        return

    logging.info(f"Tokens retrieved for posture stats. Token ID: {token_id}")

    # 3. Initialize BloodhoundManager for posture stats
    bloodhound_manager = BloodhoundManager(
        tenant_domain, token_id, token_key, logger=logging
    )
    # Configure manager for the specific Azure Monitor table for posture stats
    bloodhound_manager.set_azure_monitor_config(
        tenant_id, app_id, app_secret, dce_uri, dcr_immutable_id, table_name
    )

    # 4. Test BloodHound API connection
    response = bloodhound_manager.test_connection()
    if not response:
        logger.error("Connection test to BloodHound Enterprise failed. Exiting.")
        return

    logger.info("Connection test to BloodHound Enterprise successful!")
    try:
        # res_domains = response.json()
        domains_data = response.get("data", [])
        logger.info(f"Found {len(domains_data)} domains.")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode domains response: {e}")
        return

    # 5. Get available domains from BloodHound and modify according to our need
    filtered_domains = [
        domain for domain in domains_data if domain.get("collected") == True
    ]

    if not filtered_domains:
        logger.info("No collected domains found based on filters. Exiting.")
        return
    logger.info(
        f"Processing collected domains: {[d.get('name') for d in filtered_domains]}"
    )

    posture_stats = bloodhound_manager.get_posture_stats()

    posture_stats_data = posture_stats.get("data")
    for data_entry in posture_stats_data:
        data_entry["domain_name"] = next(
            (
                item["name"].strip()
                for item in filtered_domains
                if item["id"] == data_entry.get("domain_sid")
            ),
            None,
        )

    logger.info(f"Total consolidated posture entries: {len(posture_stats_data)}")

    # 6. Get Bearer Token for Azure Monitor
    monitor_bearer_token = bloodhound_manager.get_bearer_token()
    if not monitor_bearer_token:
        logger.error("Failed to obtain Bearer token for Azure Monitor. Exiting.")
        return
    logger.info("Bearer token for Azure Monitor obtained successfully.")

    # 7. Fetch and send posture stats
    results = []
    for i, data_entry in enumerate(posture_stats_data, 1):

        logger.info(
            f"Sending posture data {i}/{len(posture_stats_data)}: ID {data_entry.get('id')}"
        )
        try:
            res = bloodhound_manager.send_posture_stat_data(
                data_entry,
                monitor_bearer_token,
                dce_uri,
                dcr_immutable_id,
                table_name,
                tenant_domain,
            )
            results.append(
                {"id": data_entry.get("id"), "status": "success", "response": res}
            )
        except Exception as e:
            logger.error(f"Error sending posture data ID {data_entry.get('id')}: {e}")
            results.append(
                {"id": data_entry.get("id"), "status": "error", "message": str(e)}
            )
        time.sleep(0.1)  # Avoid rate limiting

    logger.info(f"Azure Monitor ingestion results: {results}")
    logger.info("Posture stats processing completed.")
