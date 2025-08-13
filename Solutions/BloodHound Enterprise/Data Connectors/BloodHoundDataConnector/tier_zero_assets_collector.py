import logging
import os
import time
import json

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

from bloodhound_manager import BloodhoundManager


def run_tier_zero_assets_collection_process() -> None:
    """
    Orchestrates the entire BloodHound Tier Zero Assets collection and Azure Monitor submission process.
    """
    logging.info("Starting BloodHound Tier Zero Assets collection process.")

    try:
        tenant_domain = os.environ["BLOODHOUND_TENANT_DOMAIN"]
        tenant_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_TENANT_ID"]
        app_id = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_ID"]
        app_secret = os.environ["MICROSOFT_ENTRA_ID_APPLICATION_APP_SECRET"]
        dce_uri = os.environ["DCE_URI"]
        dcr_immutable_id = os.environ["DCR_IMMUTABLE_ID"]
        table_name = os.environ["TIER_ZERO_ASSETS_TABLE_NAME"]
        token_id_secret_name = os.environ["BLOODHOUND_TOKEN_ID_SECRET_NAME"]
        token_key_secret_name = os.environ["BLOODHOUND_TOKEN_KEY_SECRET_NAME"]
        key_vault_url = os.environ["KEY_VAULT_URL"]

        logging.info(
            f"Configuration loaded for Tier Zero Assets. Key Vault URL: {key_vault_url}"
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
            "Successfully retrieved token ID and token key from Azure Key Vault for Tier Zero Assets."
        )

    except ResourceNotFoundError as e:
        logging.error(
            f"One or both secrets not found in Azure Key Vault for Tier Zero Assets. Ensure '{token_id_secret_name}' and '{token_key_secret_name}' exist. Error: {e}. Exiting process."
        )
        return
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while retrieving secrets from Azure Key Vault for Tier Zero Assets: {e}. Exiting process."
        )
        return

    logging.info(f"Tokens retrieved for Tier Zero Assets.")

    # 3. Initialize BloodhoundManager
    bloodhound_manager = BloodhoundManager(
        tenant_domain, token_id, token_key, logger=logging
    )
    # Configure manager for the specific Azure Monitor table
    bloodhound_manager.set_azure_monitor_config(
        tenant_id, app_id, app_secret, dce_uri, dcr_immutable_id, table_name
    )

    # 4. Test BloodHound API connection
    connection_response = bloodhound_manager.test_connection()
    if not connection_response:
        logging.error(
            f"BloodHound API connection test failed for Tier Zero Assets (Status: {connection_response.status_code if connection_response else 'N/A'}). Aborting collection."
        )
        return
    logging.info(
        "BloodHound API connection test passed for Tier Zero Assets. Starting collection..."
    )

    # 5. Get available domains from BloodHound and apply environment filter
    res_domains = bloodhound_manager.get_available_domains()
    if not res_domains:
        logging.error(
            "Failed to fetch available domains. Cannot proceed with Tier Zero Assets collection."
        )
        return

    all_domains_data = res_domains.get("data", [])
    logging.info(f"Found {len(all_domains_data)} domains from BloodHound API.")

    filtered_domains_by_env = [
        domain for domain in all_domains_data if domain.get("collected") is True
    ]

    if not filtered_domains_by_env:
        logging.info(
            "No collected or selected environments found to query Tier Zero Assets. Exiting."
        )
        return

    logging.info(
        f"Filtered {len(filtered_domains_by_env)} domains for Tier Zero Assets collection."
    )

    domains_for_name_lookup = {d["id"]: d["name"] for d in filtered_domains_by_env}

    # 6. Fetch Tier Zero Assets using Cypher query
    cypher_response = bloodhound_manager.fetch_tier_zero_assets()

    if (
        not cypher_response
        or "data" not in cypher_response
        or "nodes" not in cypher_response["data"]
    ):
        logging.error(
            "Failed to fetch Tier Zero assets or received unexpected response structure. Aborting."
        )
        return

    nodes_array = []
    for node_id, node_data in cypher_response["data"]["nodes"].items():
        # Exclude 'Meta' kind nodes as per original script's filtering
        if node_data.get("kind") == "Meta":
            continue

        properties = node_data.get("properties", {})
        name = bloodhound_manager.extract_name(node_data, properties, node_id)
        domain_name = bloodhound_manager.extract_domain_name(
            node_data, properties, name, filtered_domains_by_env
        )

        # Create a combined dictionary including 'nodeId', 'domain_name', 'name', and all other node_data
        combined_node_data = {
            "nodeId": node_id,
            "domain_name": domain_name,
            "name": name,
            **node_data,  # This will include 'label', 'kind', 'objectId', 'properties', etc.
        }
        nodes_array.append(combined_node_data)

    logging.info(f"Found {len(nodes_array)} Tier Zero Assets to process.")

    # 7. Get Bearer Token for Azure Monitor
    token = bloodhound_manager.get_bearer_token()
    if not token:
        logging.error(
            "Failed to obtain Bearer token for Azure Monitor. Aborting data submission."
        )
        return

    logging.info("Bearer token obtained successfully for Azure Monitor.")

    # 8. Send Tier Zero Assets data to Azure Monitor
    submission_results = []
    if not nodes_array:
        logging.info("No Tier Zero Assets data to send to Azure Monitor. Exiting.")
        return

    for i, data in enumerate(nodes_array, 1):
        logging.info(
            f"Sending Tier Zero Asset data {i}/{len(nodes_array)}: ID {data.get('nodeId')} ({data.get('name')})"
        )
        try:
            res = bloodhound_manager.send_tier_zero_assets_data(
                data,
                token,
                filtered_domains_by_env,  # Pass filtered domains for name lookup
            )
            submission_results.append(
                {"nodeId": data.get("nodeId"), "status": "success", "response": res}
            )
        except Exception as e:
            logging.error(
                f"Error sending Tier Zero Asset data ID {data.get('nodeId')}: {e}"
            )
            submission_results.append(
                {"nodeId": data.get("nodeId"), "status": "error", "message": str(e)}
            )
        time.sleep(0.1)  # Small delay to avoid hammering the API

    logging.info(
        f"All Tier Zero Asset data submission results: {json.dumps(submission_results, indent=2)}"
    )
    logging.info("BloodHound Tier Zero Assets collection process completed.")
