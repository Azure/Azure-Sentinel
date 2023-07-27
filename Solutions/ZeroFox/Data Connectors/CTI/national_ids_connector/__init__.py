import datetime
import logging
import os

import azure.functions as func

from connections.sentinel import SentinelConnector
from connections.zerofox import ZeroFoxClient


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    if mytimer.past_due:
        logging.info("The timer is past due!")

    # Update the customer ID to your Log Analytics workspace ID
    customer_id = os.environ.get("WorkspaceID")

    # For the shared key, use either the primary or the secondary Connected Sources client authentication key
    shared_key = os.environ.get("WorkspaceKey")

    query_from = mytimer.schedule_status["Last"]
    query_to = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)

    zf_client = get_zf_client()

    results = get_cti_national_ids(
        zf_client, created_after=query_from, created_before=query_to
    )

    logging.debug("Trigger function retrieved results")

    # The log type is the name of the event that is being submitted
    log_type = "ZeroFox_CTI_national_ids"

    sentinel_client = SentinelConnector(
        customer_id=customer_id, shared_key=shared_key, log_type=log_type
    )

    for result in results:
        sentinel_client.send(result)

    logging.info(f"Python timer trigger function ran at {utc_timestamp}")


def get_zf_client():
    user = os.environ.get("zf_username")
    token = os.environ.get("token")
    return ZeroFoxClient(user, token)


def get_cti_national_ids(
    client: ZeroFoxClient, created_after: str, created_before: str
):
    url_suffix = "national-ids/"
    params = dict(created_after=created_after, created_before=created_before)
    return client.cti_request(
        "GET",
        url_suffix,
        params=params,
    )
