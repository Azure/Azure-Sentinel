import json
import logging

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

from models.feed import FeedConfig
from services.azure_clients import get_blob_service_client

CHECKPOINT_CONTAINER = "checkpoints"


def get_blob_client(storage_account_name: str, feed: FeedConfig):
    blob_service_client = get_blob_service_client(storage_account_name)

    container_client = blob_service_client.get_container_client(CHECKPOINT_CONTAINER)

    blob_client = container_client.get_blob_client(feed.checkpoint_blob_name())

    return container_client, blob_client


def ensure_checkpoint_container(storage_account_name: str) -> None:
    blob_service_client = get_blob_service_client(storage_account_name)

    container_client = blob_service_client.get_container_client(CHECKPOINT_CONTAINER)

    try:
        container_client.get_container_properties()
    except ResourceNotFoundError:
        try:
            container_client.create_container()
        except ResourceExistsError:
            # Ignored: Safe race condition if another worker created the container concurrently.
            pass

        logging.info(
            "Created checkpoint container: %s",
            CHECKPOINT_CONTAINER,
        )


def get_checkpoint(
    storage_account_name: str,
    feed: FeedConfig,
) -> dict | None:
    _, blob_client = get_blob_client(storage_account_name, feed)

    try:
        data = blob_client.download_blob().readall()

        checkpoint = json.loads(data.decode("utf-8"))

        logging.info(
            "Checkpoint loaded: feed=%s date=%s offset=%s status=%s",
            feed.name,
            checkpoint.get("feed_date"),
            checkpoint.get("offset"),
            checkpoint.get("status"),
        )

        return checkpoint

    except ResourceNotFoundError:
        logging.info(
            "No checkpoint found for feed=%s. Starting from offset=0.",
            feed.name,
        )

        return None


def save_checkpoint(
    storage_account_name: str,
    feed: FeedConfig,
    feed_date: str,
    offset: int,
    status: str,
) -> None:

    ensure_checkpoint_container(storage_account_name)

    _, blob_client = get_blob_client(storage_account_name, feed)

    checkpoint = {
        "feed": feed.name,
        "feed_date": feed_date,
        "offset": offset,
        "status": status,
    }

    blob_client.upload_blob(
        json.dumps(checkpoint),
        overwrite=True,
    )

    logging.info(
        "Checkpoint saved: feed=%s date=%s offset=%s status=%s",
        feed.name,
        feed_date,
        offset,
        status,
    )
