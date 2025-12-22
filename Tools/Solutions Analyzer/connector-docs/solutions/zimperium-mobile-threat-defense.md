# Zimperium Mobile Threat Defense

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Zimperium |
| **Support Tier** | Partner |
| **Support Link** | [https://www.zimperium.com/support/](https://www.zimperium.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zimperium%20Mobile%20Threat%20Defense](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zimperium%20Mobile%20Threat%20Defense) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Zimperium Mobile Threat Defense](../connectors/zimperiummtdalerts.md)

**Publisher:** Zimperium

Zimperium Mobile Threat Defense connector gives you the ability to connect the Zimperium threat log with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's mobile threat landscape and enhances your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure and connect Zimperium MTD**

1. In zConsole, click **Manage** on the navigation bar.
2. Click the **Integrations** tab.
3. Click the **Threat Reporting** button and then the **Add Integrations** button.
4. Create the Integration:
  - From the available integrations, select Microsoft Sentinel.
  - Enter your workspace id and primary key from the fields below, click **Next**.
  - Fill in a name for your Microsoft Sentinel integration.
  - Select a Filter Level for the threat data you wish to push to Microsoft Sentinel.
  - Click **Finish**
5. For additional instructions, please refer to the [Zimperium customer support portal](https://support.zimperium.com).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `ZimperiumMitigationLog_CL` |
| | `ZimperiumThreatLog_CL` |
| **Connector Definition Files** | [Zimperium%20MTD%20Alerts.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zimperium%20Mobile%20Threat%20Defense/Data%20Connectors/Zimperium%20MTD%20Alerts.json) |

[→ View full connector details](../connectors/zimperiummtdalerts.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ZimperiumMitigationLog_CL` | [Zimperium Mobile Threat Defense](../connectors/zimperiummtdalerts.md) |
| `ZimperiumThreatLog_CL` | [Zimperium Mobile Threat Defense](../connectors/zimperiummtdalerts.md) |

[← Back to Solutions Index](../solutions-index.md)
