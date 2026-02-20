import logging
import os
import json
import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError, AzureError
from azure.storage.blob import BlobServiceClient

from ..SharedCode.azure_functions.attack_path_collector import run_attack_paths_collection_process

# Azure Blob Storage configuration
STORAGE_CONNECTION_STRING = os.environ.get("AzureWebJobsStorage")
CONTAINER_NAME = "attack-path-function-state"
BLOB_NAME = "attack_path_collector_state.json"

def get_connection_string():
    """
    Get the storage connection string from environment variable.
    For local development, provide a full connection string in local.settings.json.
    For production, AzureWebJobsStorage will contain the connection string.
    """
    connection_string = STORAGE_CONNECTION_STRING
    
    if not connection_string:
        raise ValueError("AzureWebJobsStorage connection string is not configured")
    
    return connection_string

def read_state():
    """
    Read the state from Azure Blob Storage. Return {} if blob does not exist or is empty.
    
    Note: This function does not handle exceptions. The caller is responsible for
    catching and logging any errors that occur during blob I/O or JSON decoding.
    """
    if not STORAGE_CONNECTION_STRING:
        logging.error("AzureWebJobsStorage connection string is not configured")
        return {}
    
    try:
        blob_service_client = BlobServiceClient.from_connection_string(get_connection_string())
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)
        
        # Check if blob exists
        if not blob_client.exists():
            logging.info("State blob does not exist. Initializing with empty state.")
            # Create container if it doesn't exist
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)
            if not container_client.exists():
                container_client.create_container()
            # Write empty state
            blob_client.upload_blob(json.dumps({}), overwrite=True)
            return {}
        
        # Download and parse blob content
        blob_data = blob_client.download_blob()
        content = blob_data.readall().decode('utf-8').strip()
        
        if not content:
            logging.warning("State blob is empty. Initializing with {}.")
            return {}
        
        return json.loads(content)
    except AzureError as e:
        logging.error(f"Azure Blob Storage error while reading state: {e}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error while reading state: {e}")
        return {}

def write_state(state):
    """Write updated state to Azure Blob Storage"""
    if not STORAGE_CONNECTION_STRING:
        logging.error("AzureWebJobsStorage connection string is not configured")
        return
    
    try:
        blob_service_client = BlobServiceClient.from_connection_string(get_connection_string())
        
        # Ensure container exists
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        if not container_client.exists():
            container_client.create_container()
        
        # Upload state to blob
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)
        blob_client.upload_blob(json.dumps(state, indent=2), overwrite=True)
        logging.info(f"State successfully written to blob: {CONTAINER_NAME}/{BLOB_NAME}")
    except AzureError as e:
        logging.error(f"Azure Blob Storage error while writing state: {e}")
        raise

def main(myTimer: func.TimerRequest) -> None:
    """Main function for the attack path collector Azure Function."""
    logging.info("Timer triggered: attack path collector executed.")

    try:
        if myTimer.past_due:
            logging.info('The timer is past due!')

        logging.info("Starting attack path collector function")

        # Read previous state
        state = read_state()
        logging.info(f"State: {state}")
        last_attack_path_timestamp = state.get("last_attack_path_timestamp", {})
        logging.info(f"Last attack path timestamp from Azure Blob Storage: {last_attack_path_timestamp}")

        # Call main function with last value
        new_attack_path_timestamp = run_attack_paths_collection_process(last_attack_path_timestamp)

        # If the function does not return a value, keep the old timestamp
        if new_attack_path_timestamp is None:
            logging.warning("Collection process did not return new timestamps. Keeping old values.")
            new_attack_path_timestamp = last_attack_path_timestamp

        logging.info(f"New attack path timestamp: {new_attack_path_timestamp}")

        # Update state in Azure Blob Storage
        state["last_attack_path_timestamp"] = new_attack_path_timestamp
        write_state(state)
        logging.info(f"State updated in Azure Blob Storage: {new_attack_path_timestamp}")

    except KeyError as e:
        logging.error(f"Missing one or more required environment variables: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Error reading or writing state blob: {e}")
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
    except ResourceNotFoundError as e:
        logging.error(f"Azure Key Vault secret not found: {e}")
    except AzureError as e:
        logging.error(f"Azure Blob Storage error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
    finally:
        logging.info("Attack path collector execution finished.")
