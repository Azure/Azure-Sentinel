from __future__ import annotations

from typing import Any

# Native Defender tables expose Timestamp in Advanced Hunting even when their
# Log Analytics connector copy exposes TimeGenerated.
NATIVE_XDR_TABLES = frozenset(
    {
        "AlertEvidence",
        "AlertInfo",
        "CloudAppEvents",
        "DeviceEvents",
        "DeviceFileCertificateInfo",
        "DeviceFileEvents",
        "DeviceImageLoadEvents",
        "DeviceInfo",
        "DeviceLogonEvents",
        "DeviceNetworkEvents",
        "DeviceNetworkInfo",
        "DeviceProcessEvents",
        "DeviceRegistryEvents",
        "DeviceTvmSecureConfigurationAssessment",
        "DeviceTvmSoftwareInventory",
        "DeviceTvmSoftwareVulnerabilities",
        "EmailAttachmentInfo",
        "EmailEvents",
        "EmailPostDeliveryEvents",
        "EmailUrlInfo",
        "IdentityDirectoryEvents",
        "IdentityLogonEvents",
        "IdentityQueryEvents",
        "UrlClickEvents",
    }
)

# These tables were verified to resolve in Advanced Hunting with their Sentinel
# name and time-column conventions. The catalog is intentionally extensible;
# runtime validation remains the final authority.
PASSTHROUGH_TABLES: dict[str, dict[str, Any]] = {
    "AzureActivity": {
        "columnRenames": {},
        "notes": "Sentinel workload table; preserve TimeGenerated and source schema.",
    },
    "IdentityInfo": {
        "columnRenames": {
            "AccountUPN": "AccountUpn",
            "AccountCreationTime": "CreatedDateTime",
            "UserType": "TenantMembershipType",
        },
        "notes": "Identity profile table with verified Sentinel-to-AH field names.",
    },
    "Event": {
        "columnRenames": {},
        "notes": "Sentinel workload table; availability depends on the unified tenant.",
    },
    "SecurityEvent": {
        "columnRenames": {},
        "notes": "Sentinel workload table; preserve TimeGenerated and source schema.",
    },
    "WindowsEvent": {
        "columnRenames": {},
        "notes": "Sentinel workload table; preserve TimeGenerated and source schema.",
    },
}


def referenced_catalog_tables(query: str) -> set[str]:
    import re

    known = NATIVE_XDR_TABLES | PASSTHROUGH_TABLES.keys()
    return {
        table
        for table in known
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(table)}(?![A-Za-z0-9_])", query)
    }


def referenced_custom_tables(query: str) -> set[str]:
    import re

    return set(
        re.findall(r"(?<![A-Za-z0-9_])([A-Za-z][A-Za-z0-9_]*_CL)(?![A-Za-z0-9_])", query)
    )


def query_requires_timestamp(query: str) -> bool:
    tables = referenced_catalog_tables(query)
    return bool(tables & NATIVE_XDR_TABLES) and not bool(
        tables & PASSTHROUGH_TABLES.keys()
    )


def query_has_mixed_time_semantics(query: str) -> bool:
    tables = referenced_catalog_tables(query)
    return bool(tables & NATIVE_XDR_TABLES) and bool(
        tables & PASSTHROUGH_TABLES.keys()
    )


def query_column_renames(query: str) -> dict[str, str]:
    renames: dict[str, str] = {}
    tables = referenced_catalog_tables(query)
    if tables & NATIVE_XDR_TABLES and not tables & PASSTHROUGH_TABLES.keys():
        renames["TimeGenerated"] = "Timestamp"
    for table in tables & PASSTHROUGH_TABLES.keys():
        renames.update(PASSTHROUGH_TABLES[table]["columnRenames"])
    return renames
