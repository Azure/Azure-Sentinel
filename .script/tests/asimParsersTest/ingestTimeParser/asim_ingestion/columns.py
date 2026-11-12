"""Shared column contracts for ASIM ingestion validation."""

from __future__ import annotations


PLATFORM_MANAGED_COLUMNS = frozenset(
    {
        "_BilledSize",
        "_IsBillable",
        "_ItemId",
        "_ResourceId",
        "_ResourceId_s",
        "_SubscriptionId",
        "_TimeReceived",
        "id",
        "MG",
        "TenantId",
        "Title",
        "Type",
        "UniqueId",
        "verbose",
        "verbose_b",
    }
)


def is_platform_managed_column(name: object) -> bool:
    normalized_name = str(name).casefold()
    return any(
        normalized_name == column.casefold()
        for column in PLATFORM_MANAGED_COLUMNS
    )
