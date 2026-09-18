"""
Microsoft SaaS Fulfillment API v2 Client
Handles subscription lifecycle for QCrypton PQC Scanner - Azure Marketplace transactable offer.
Reference: https://learn.microsoft.com/en-us/partner-center/marketplace-offers/partner-center-portal/pc-saas-fulfillment-subscription-api
"""

import logging
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

FULFILLMENT_API_BASE = "https://marketplaceapi.microsoft.com/api/saas"
API_VERSION = "2018-08-31"


@dataclass
class Subscription:
    subscription_id: str
    subscription_name: str
    offer_id: str
    plan_id: str
    quantity: int
    status: str
    beneficiary_tenant_id: str
    beneficiary_email: str
    purchaser_tenant_id: str
    purchaser_email: str
    term_start: str
    term_end: str
    is_free_trial: bool


class MarketplaceClient:
    """Client for Microsoft SaaS Fulfillment API v2."""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._token_expiry = None

    def _get_access_token(self) -> str:
        if self._token and self._token_expiry and datetime.utcnow() < self._token_expiry:
            return self._token

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        response = requests.post(token_url, data={
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "20e940b3-4c77-4b0b-9a53-9e16a1b010a7/.default"
        })
        response.raise_for_status()
        token_data = response.json()
        self._token = token_data["access_token"]
        self._token_expiry = datetime.utcnow() + timedelta(seconds=token_data["expires_in"] - 60)
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
            "x-ms-requestid": "",
            "x-ms-correlationid": "",
        }

    def _url(self, path: str) -> str:
        return f"{FULFILLMENT_API_BASE}/{path}?api-version={API_VERSION}"

    # ── Resolve ──────────────────────────────────────────────
    def resolve_token(self, marketplace_token: str) -> dict:
        """Resolve a marketplace purchase token to subscription details.
        Called from the landing page after customer clicks 'Buy' in Azure Marketplace.
        """
        response = requests.post(
            self._url("subscriptions/resolve"),
            headers={
                **self._headers(),
                "x-ms-marketplace-token": marketplace_token,
            },
        )
        response.raise_for_status()
        return response.json()

    # ── Activate ─────────────────────────────────────────────
    def activate_subscription(self, subscription_id: str, plan_id: str, quantity: int = None) -> None:
        """Activate a subscription after the customer completes onboarding on the landing page."""
        body = {"planId": plan_id}
        if quantity is not None:
            body["quantity"] = quantity

        response = requests.post(
            self._url(f"subscriptions/{subscription_id}/activate"),
            headers=self._headers(),
            json=body,
        )
        response.raise_for_status()
        logger.info("Activated subscription %s on plan %s", subscription_id, plan_id)

    # ── Get Subscription ─────────────────────────────────────
    def get_subscription(self, subscription_id: str) -> Subscription:
        """Get details for a specific subscription."""
        response = requests.get(
            self._url(f"subscriptions/{subscription_id}"),
            headers=self._headers(),
        )
        response.raise_for_status()
        data = response.json()
        return self._parse_subscription(data)

    # ── List Subscriptions ───────────────────────────────────
    def list_subscriptions(self) -> list[Subscription]:
        """List all SaaS subscriptions for this publisher."""
        subscriptions = []
        url = self._url("subscriptions")

        while url:
            response = requests.get(url, headers=self._headers())
            response.raise_for_status()
            data = response.json()
            for sub in data.get("subscriptions", []):
                subscriptions.append(self._parse_subscription(sub))
            url = data.get("@nextLink")

        return subscriptions

    # ── Update Operation Status ──────────────────────────────
    def update_operation_status(self, subscription_id: str, operation_id: str, plan_id: str,
                                quantity: int, status: str) -> None:
        """Update the status of a pending operation (webhook acknowledgment).
        status must be 'Success' or 'Failure'.
        """
        response = requests.patch(
            self._url(f"subscriptions/{subscription_id}/operations/{operation_id}"),
            headers=self._headers(),
            json={
                "planId": plan_id,
                "quantity": quantity,
                "status": status,
            },
        )
        response.raise_for_status()
        logger.info("Updated operation %s to %s for subscription %s",
                     operation_id, status, subscription_id)

    # ── List Operations ──────────────────────────────────────
    def list_operations(self, subscription_id: str) -> list[dict]:
        """List pending operations for a subscription."""
        response = requests.get(
            self._url(f"subscriptions/{subscription_id}/operations"),
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json().get("operations", [])

    # ── Get Operation ────────────────────────────────────────
    def get_operation(self, subscription_id: str, operation_id: str) -> dict:
        """Get details of a specific operation."""
        response = requests.get(
            self._url(f"subscriptions/{subscription_id}/operations/{operation_id}"),
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    # ── Change Plan ──────────────────────────────────────────
    def change_plan(self, subscription_id: str, plan_id: str) -> dict:
        """Initiate a plan change for a subscription."""
        response = requests.patch(
            self._url(f"subscriptions/{subscription_id}"),
            headers=self._headers(),
            json={"planId": plan_id},
        )
        response.raise_for_status()
        return response.json()

    # ── Change Quantity ──────────────────────────────────────
    def change_quantity(self, subscription_id: str, quantity: int) -> dict:
        """Change the seat quantity for a subscription."""
        response = requests.patch(
            self._url(f"subscriptions/{subscription_id}"),
            headers=self._headers(),
            json={"quantity": quantity},
        )
        response.raise_for_status()
        return response.json()

    # ── Delete (Unsubscribe) ─────────────────────────────────
    def delete_subscription(self, subscription_id: str) -> None:
        """Unsubscribe / cancel a subscription."""
        response = requests.delete(
            self._url(f"subscriptions/{subscription_id}"),
            headers=self._headers(),
        )
        response.raise_for_status()
        logger.info("Deleted subscription %s", subscription_id)

    # ── Helpers ──────────────────────────────────────────────
    @staticmethod
    def _parse_subscription(data: dict) -> Subscription:
        beneficiary = data.get("beneficiary", {})
        purchaser = data.get("purchaser", {})
        term = data.get("term", {})
        return Subscription(
            subscription_id=data.get("id", ""),
            subscription_name=data.get("name", ""),
            offer_id=data.get("offerId", ""),
            plan_id=data.get("planId", ""),
            quantity=data.get("quantity", 0),
            status=data.get("saasSubscriptionStatus", ""),
            beneficiary_tenant_id=beneficiary.get("tenantId", ""),
            beneficiary_email=beneficiary.get("emailId", ""),
            purchaser_tenant_id=purchaser.get("tenantId", ""),
            purchaser_email=purchaser.get("emailId", ""),
            term_start=term.get("startDate", ""),
            term_end=term.get("endDate", ""),
            is_free_trial=data.get("isFreeTrial", False),
        )
