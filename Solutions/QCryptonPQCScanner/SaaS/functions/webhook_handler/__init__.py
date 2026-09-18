"""
Azure Function: Marketplace Webhook Handler
Receives subscription lifecycle events from Microsoft Azure Marketplace.

Events handled:
  - ChangePlan: Customer changed their subscription plan
  - ChangeQuantity: Customer changed seat count
  - Suspend: Microsoft suspended the subscription (e.g., payment failure)
  - Unsubscribe: Customer cancelled the subscription
  - Reinstate: Subscription reinstated after suspension
  - Renew: Subscription auto-renewed

Partner Center configuration:
  Webhook URL: https://<your-function-app>.azurewebsites.net/api/webhook
"""

import json
import logging
import os
import azure.functions as func
from shared.marketplace_client import MarketplaceClient
from shared.api_key_manager import ApiKeyManager

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body", status_code=400)

    action = body.get("action", "").lower()
    subscription_id = body.get("subscriptionId", "")
    operation_id = body.get("id", "")
    plan_id = body.get("planId", "")
    quantity = body.get("quantity", 0)
    publisher_id = body.get("publisherId", "")

    logger.info("Webhook received: action=%s subscription=%s operation=%s",
                action, subscription_id, operation_id)

    if publisher_id != os.environ.get("PUBLISHER_ID", "qcryptoninc1788706847984"):
        logger.warning("Publisher ID mismatch: %s", publisher_id)
        return func.HttpResponse("Publisher mismatch", status_code=403)

    client = _get_marketplace_client()
    api_key_mgr = _get_api_key_manager()

    # Verify the operation is legitimate by fetching it from Microsoft
    try:
        operation = client.get_operation(subscription_id, operation_id)
        if operation.get("status") != "InProgress":
            logger.warning("Operation %s is not InProgress, ignoring", operation_id)
            return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        logger.error("Failed to verify operation: %s", e)
        return func.HttpResponse("Operation verification failed", status_code=400)

    handler = HANDLERS.get(action)
    if not handler:
        logger.warning("Unknown action: %s", action)
        return func.HttpResponse("Unknown action", status_code=400)

    try:
        handler(client, api_key_mgr, subscription_id, operation_id, plan_id, quantity)
        return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        logger.error("Webhook handler failed for action=%s subscription=%s: %s",
                     action, subscription_id, e)
        # Notify Microsoft of failure
        try:
            client.update_operation_status(subscription_id, operation_id, plan_id, quantity, "Failure")
        except Exception:
            pass
        return func.HttpResponse("Handler failed", status_code=500)


# ── Action Handlers ──────────────────────────────────────────

def _handle_change_plan(client, api_key_mgr, subscription_id, operation_id, plan_id, quantity):
    """Customer changed their subscription plan (e.g., Basic → Professional)."""
    logger.info("ChangePlan: subscription=%s new_plan=%s", subscription_id, plan_id)

    # Update API key tier/quota based on new plan
    api_key_mgr.update_plan(subscription_id, plan_id)

    # Acknowledge success to Microsoft
    client.update_operation_status(subscription_id, operation_id, plan_id, quantity, "Success")


def _handle_change_quantity(client, api_key_mgr, subscription_id, operation_id, plan_id, quantity):
    """Customer changed seat count."""
    logger.info("ChangeQuantity: subscription=%s quantity=%d", subscription_id, quantity)

    api_key_mgr.update_quantity(subscription_id, quantity)
    client.update_operation_status(subscription_id, operation_id, plan_id, quantity, "Success")


def _handle_suspend(client, api_key_mgr, subscription_id, operation_id, plan_id, quantity):
    """Microsoft suspended the subscription (payment failure, policy violation)."""
    logger.info("Suspend: subscription=%s", subscription_id)

    # Disable the API key — stop data flow but don't delete data
    api_key_mgr.suspend(subscription_id)
    client.update_operation_status(subscription_id, operation_id, plan_id, quantity, "Success")


def _handle_unsubscribe(client, api_key_mgr, subscription_id, operation_id, plan_id, quantity):
    """Customer cancelled the subscription."""
    logger.info("Unsubscribe: subscription=%s", subscription_id)

    # Revoke API key — customer will need to remove the connector manually
    api_key_mgr.revoke(subscription_id)
    client.update_operation_status(subscription_id, operation_id, plan_id, quantity, "Success")


def _handle_reinstate(client, api_key_mgr, subscription_id, operation_id, plan_id, quantity):
    """Subscription reinstated after suspension."""
    logger.info("Reinstate: subscription=%s", subscription_id)

    api_key_mgr.reinstate(subscription_id)
    client.update_operation_status(subscription_id, operation_id, plan_id, quantity, "Success")


def _handle_renew(client, api_key_mgr, subscription_id, operation_id, plan_id, quantity):
    """Subscription auto-renewed."""
    logger.info("Renew: subscription=%s plan=%s", subscription_id, plan_id)

    api_key_mgr.renew(subscription_id, plan_id)
    client.update_operation_status(subscription_id, operation_id, plan_id, quantity, "Success")


HANDLERS = {
    "changeplan": _handle_change_plan,
    "changequantity": _handle_change_quantity,
    "suspend": _handle_suspend,
    "unsubscribe": _handle_unsubscribe,
    "reinstate": _handle_reinstate,
    "renew": _handle_renew,
}


# ── Initialization ───────────────────────────────────────────

def _get_marketplace_client() -> MarketplaceClient:
    return MarketplaceClient(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )


def _get_api_key_manager() -> ApiKeyManager:
    return ApiKeyManager(
        keyvault_url=os.environ["KEYVAULT_URL"],
    )
