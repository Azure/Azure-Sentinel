"""
API Key Manager for QCrypton PQC Scanner SaaS subscriptions.
Maps Azure Marketplace subscriptions to QCrypton API keys stored in Azure Key Vault.

Each subscription gets:
  - An API key (stored in Key Vault)
  - A plan tier (determines scan quotas and features)
  - A status (active, suspended, revoked)
"""

import logging
import secrets
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

logger = logging.getLogger(__name__)

# Plan-to-quota mapping — matches Partner Center plan IDs
PLAN_QUOTAS = {
    "basic": {
        "max_resources": 100,
        "scan_interval_hours": 24,
        "features": ["key_vault_scan", "tls_cert_scan"],
    },
    "professional": {
        "max_resources": 1000,
        "scan_interval_hours": 6,
        "features": ["key_vault_scan", "tls_cert_scan", "app_service_scan", "storage_scan"],
    },
    "enterprise": {
        "max_resources": -1,  # unlimited
        "scan_interval_hours": 1,
        "features": ["key_vault_scan", "tls_cert_scan", "app_service_scan", "storage_scan",
                      "cmk_scan", "custom_scan", "api_access", "priority_support"],
    },
}


class ApiKeyManager:
    """Manages QCrypton API keys tied to Marketplace subscriptions."""

    def __init__(self, keyvault_url: str):
        credential = DefaultAzureCredential()
        self.secret_client = SecretClient(vault_url=keyvault_url, credential=credential)

    def _secret_name(self, subscription_id: str) -> str:
        """Key Vault secret name for a subscription's API key."""
        return f"qcrypton-apikey-{subscription_id}"

    def _meta_name(self, subscription_id: str) -> str:
        """Key Vault secret name for a subscription's metadata."""
        return f"qcrypton-meta-{subscription_id}"

    # ── Provision ────────────────────────────────────────────
    def provision(self, subscription_id: str, plan_id: str, tenant_id: str, email: str) -> str:
        """Create a new API key for a marketplace subscription.
        Returns the generated API key.
        """
        api_key = f"qpqc_{secrets.token_urlsafe(32)}"

        # Store the API key
        self.secret_client.set_secret(
            self._secret_name(subscription_id),
            api_key,
            tags={
                "subscription_id": subscription_id,
                "plan_id": plan_id,
                "tenant_id": tenant_id,
                "email": email,
                "status": "active",
            },
        )

        # Store subscription metadata
        import json
        meta = {
            "plan_id": plan_id,
            "tenant_id": tenant_id,
            "email": email,
            "status": "active",
            "quotas": PLAN_QUOTAS.get(plan_id, PLAN_QUOTAS["basic"]),
        }
        self.secret_client.set_secret(
            self._meta_name(subscription_id),
            json.dumps(meta),
            tags={"subscription_id": subscription_id, "type": "metadata"},
        )

        logger.info("Provisioned API key for subscription %s on plan %s", subscription_id, plan_id)
        return api_key

    # ── Update Plan ──────────────────────────────────────────
    def update_plan(self, subscription_id: str, new_plan_id: str) -> None:
        """Update the plan tier for a subscription (upgrades/downgrades)."""
        import json
        meta_secret = self.secret_client.get_secret(self._meta_name(subscription_id))
        meta = json.loads(meta_secret.value)
        meta["plan_id"] = new_plan_id
        meta["quotas"] = PLAN_QUOTAS.get(new_plan_id, PLAN_QUOTAS["basic"])

        self.secret_client.set_secret(
            self._meta_name(subscription_id),
            json.dumps(meta),
            tags={**meta_secret.properties.tags, "plan_id": new_plan_id},
        )

        # Update API key tags
        api_secret = self.secret_client.get_secret(self._secret_name(subscription_id))
        self.secret_client.set_secret(
            self._secret_name(subscription_id),
            api_secret.value,
            tags={**api_secret.properties.tags, "plan_id": new_plan_id},
        )
        logger.info("Updated plan to %s for subscription %s", new_plan_id, subscription_id)

    # ── Update Quantity ──────────────────────────────────────
    def update_quantity(self, subscription_id: str, quantity: int) -> None:
        """Update the seat quantity for a subscription."""
        import json
        meta_secret = self.secret_client.get_secret(self._meta_name(subscription_id))
        meta = json.loads(meta_secret.value)
        meta["quantity"] = quantity

        self.secret_client.set_secret(
            self._meta_name(subscription_id),
            json.dumps(meta),
            tags=meta_secret.properties.tags,
        )
        logger.info("Updated quantity to %d for subscription %s", quantity, subscription_id)

    # ── Suspend ──────────────────────────────────────────────
    def suspend(self, subscription_id: str) -> None:
        """Suspend an API key — key remains but is marked inactive."""
        self._set_status(subscription_id, "suspended")
        logger.info("Suspended subscription %s", subscription_id)

    # ── Reinstate ────────────────────────────────────────────
    def reinstate(self, subscription_id: str) -> None:
        """Reinstate a suspended subscription."""
        self._set_status(subscription_id, "active")
        logger.info("Reinstated subscription %s", subscription_id)

    # ── Revoke ───────────────────────────────────────────────
    def revoke(self, subscription_id: str) -> None:
        """Permanently revoke an API key (unsubscribe)."""
        self._set_status(subscription_id, "revoked")
        logger.info("Revoked subscription %s", subscription_id)

    # ── Renew ────────────────────────────────────────────────
    def renew(self, subscription_id: str, plan_id: str) -> None:
        """Mark subscription as renewed."""
        self._set_status(subscription_id, "active")
        logger.info("Renewed subscription %s on plan %s", subscription_id, plan_id)

    # ── Validate ─────────────────────────────────────────────
    def validate_key(self, api_key: str) -> dict | None:
        """Validate an API key and return its subscription metadata.
        Used by the QCrypton API to authorize requests.
        Returns None if key is invalid or not active.
        """
        import json
        # List all API key secrets and find matching one
        for secret_props in self.secret_client.list_properties_of_secrets():
            if not secret_props.name.startswith("qcrypton-apikey-"):
                continue
            if secret_props.tags.get("status") != "active":
                continue

            secret = self.secret_client.get_secret(secret_props.name)
            if secret.value == api_key:
                subscription_id = secret_props.tags.get("subscription_id", "")
                meta_secret = self.secret_client.get_secret(self._meta_name(subscription_id))
                return json.loads(meta_secret.value)

        return None

    # ── Helpers ──────────────────────────────────────────────
    def _set_status(self, subscription_id: str, status: str) -> None:
        import json
        # Update API key tags
        api_secret = self.secret_client.get_secret(self._secret_name(subscription_id))
        self.secret_client.set_secret(
            self._secret_name(subscription_id),
            api_secret.value,
            tags={**api_secret.properties.tags, "status": status},
        )

        # Update metadata
        meta_secret = self.secret_client.get_secret(self._meta_name(subscription_id))
        meta = json.loads(meta_secret.value)
        meta["status"] = status
        self.secret_client.set_secret(
            self._meta_name(subscription_id),
            json.dumps(meta),
            tags={**meta_secret.properties.tags, "status": status},
        )
