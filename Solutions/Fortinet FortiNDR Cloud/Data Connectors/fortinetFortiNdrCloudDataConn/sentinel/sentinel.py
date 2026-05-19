import json
import logging
import os

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient

# New Environment Variables matching ARM output
AZURE_TENANT_ID = (os.environ.get("TENANT_ID") or "").strip()
AZURE_CLIENT_ID = (os.environ.get("CLIENT_ID") or "").strip()
AZURE_CLIENT_SECRET = (os.environ.get("CLIENT_SECRET") or "").strip()
AZURE_ENDPOINT = (os.environ.get("DceUri") or "").strip()
DCR_ID = (os.environ.get("DcrImmutableId") or "").strip()


def post_data(events: list[dict], log_type_suffix: str):
    """
    Post data using the official Azure Monitor Ingestion SDK.
    """
    if not events:
        return

    try:
        logging.info("Creating the Client Secret Credential object.")
        creds = ClientSecretCredential(
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_CLIENT_SECRET,
            tenant_id=AZURE_TENANT_ID,
        )

        logging.info("Creating the Log Ingestion Client object.")
        client = LogsIngestionClient(
            endpoint=AZURE_ENDPOINT,
            credential=creds
        )

    except Exception as e:
        logging.error(
            f"{log_type_suffix.title()}: Failed to create Azure credential/client. "
            f"Check TENANT_ID, CLIENT_ID, CLIENT_SECRET, DceUri. Error: {e}"
        )
        raise

    try:
        # The stream name must match your DCR definition exactly: "Custom-<TableName>_CL"
        stream_name = f"Custom-FncEvents{log_type_suffix.title()}_CL"

        logging.info(
            f"Uploading {len(events)} events to stream {stream_name} via Log Ingestion Client.")

        client.upload(
            rule_id=DCR_ID,
            stream_name=stream_name,
            logs=events
        )

        logging.info(
            f"SentinelClient: Successfully uploaded {len(events)} events.")

    except ClientAuthenticationError as exc:
        logging.error(
            f"{log_type_suffix} : Authentication failed — verify CLIENT_ID, "
            f"CLIENT_SECRET, TENANT_ID, and that the App Registration has "
            f"'Monitoring Metrics Publisher' role assigned on the DCR. Error: {exc}"
        )
        raise
    except HttpResponseError as e:
        logging.error(f"SentinelClient: HTTP error during upload: {e}")
        raise
    except Exception as e:
        logging.error(
            f"SentinelClient: Unexpected error during data upload: {e}")
        raise
