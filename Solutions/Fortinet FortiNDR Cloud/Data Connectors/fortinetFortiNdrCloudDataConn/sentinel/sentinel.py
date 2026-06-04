import json
import logging
import os
from datetime import datetime, timezone

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient


def post_data(events: list[dict], log_type_suffix: str):
    """
    Post data using the official Azure Monitor Ingestion SDK.
    """
    if not events:
        return

    AZURE_TENANT_ID = (os.environ.get("TENANT_ID") or "").strip()
    AZURE_CLIENT_ID = (os.environ.get("CLIENT_ID") or "").strip()
    AZURE_CLIENT_SECRET = (os.environ.get("CLIENT_SECRET") or "").strip()
    AZURE_ENDPOINT = (os.environ.get("DceUri") or "").strip()
    DCR_ID = (os.environ.get("DcrImmutableId") or "").strip()

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
            credential=creds,
            api_version="2023-01-01"
        )

    except Exception as e:
        logging.error(
            f"{log_type_suffix.title()}: Failed to create Azure credential/client. "
            f"Check TENANT_ID, CLIENT_ID, CLIENT_SECRET, DceUri. Error: {e}"
        )
        raise

    stream_name = "Custom-FortinetFortiNdrCloudRaw_CL"

    logging.info("Wrapping events to be uploaded:")

    wrapped_events = []
    for event in events:
        event_time = event.get('timestamp')
        if not event_time:
            event_time = datetime.now(
                timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        wrapped_events.append({
            "TimeGenerated": event_time,
            "LogTypeSuffix": log_type_suffix.lower(),
            "RawData": json.dumps(event),
        })

    try:
        logging.info(
            f"Uploading {len(wrapped_events)} packaged events to stream {stream_name} via Log Ingestion Client."
        )

        clean_dcr_id = DCR_ID.split('/')[-1] if '/' in DCR_ID else DCR_ID

        client.upload(
            rule_id=clean_dcr_id,
            stream_name=stream_name,
            logs=wrapped_events
        )

        logging.info(
            f"SentinelClient: Successfully uploaded {len(events)} events."
        )

    except ClientAuthenticationError as exc:
        logging.error(
            f"{log_type_suffix} : Authentication failed - verify CLIENT_ID, "
            f"CLIENT_SECRET, TENANT_ID, and that the App Registration has "
            f"'Monitoring Metrics Publisher' role assigned on the DCR. Error: {exc}"
        )
        raise
    except HttpResponseError as e:
        error_details = "No inner error details provided by Azure."
        if hasattr(e, 'response') and e.response:
            try:
                # Unpack the raw text response body containing the structural validation breakdown
                error_details = e.response.text()
            except Exception:
                pass

        logging.error(
            f"SentinelClient: HTTP error during upload (Status {e.status_code}): {e.message}")
        logging.error(f"Azure API Schema Validation Details: {error_details}")
        raise
    except Exception as e:
        logging.error(
            f"SentinelClient: Unexpected error during data upload: {e}"
        )
        raise
