# Microsoft Purview Information Protection

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-01-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview%20Information%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview%20Information%20Protection) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Purview Information Protection](../connectors/microsoftpurviewinformationprotection.md)

**Publisher:** Microsoft

Microsoft Purview Information Protection helps you discover, classify, protect, and govern sensitive information wherever it lives or travels. Using these capabilities enable you to know your data, identify items that are sensitive and gain visibility into how they are being used to better protect your data. Sensitivity labels are the foundational capability that provide protection actions, applying encryption, access restrictions and visual markings.

    Integrate Microsoft Purview Information Protection logs with Microsoft Sentinel to view dashboards, create custom alerts and improve investigation. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223811&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **License**: Enterprise Mobility + Security E5/A5 or Microsoft 365 E5/A5 or P2

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Purview Information Protection audit logs to Microsoft Sentinel**

| | |
|--------------------------|---|
| **Tables Ingested** | `MicrosoftPurviewInformationProtection` |
| **Connector Definition Files** | [MicrosoftPurviewInformationProtection.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview%20Information%20Protection/Data%20Connectors/MicrosoftPurviewInformationProtection.json) |

[→ View full connector details](../connectors/microsoftpurviewinformationprotection.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MicrosoftPurviewInformationProtection` | [Microsoft Purview Information Protection](../connectors/microsoftpurviewinformationprotection.md) |

[← Back to Solutions Index](../solutions-index.md)
