# MailGuard 365

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | MailGuard 365 |
| **Support Tier** | Partner |
| **Support Link** | [https://www.mailguard365.com/support/](https://www.mailguard365.com/support/) |
| **Categories** | domains |
| **First Published** | 2023-05-09 |
| **Last Updated** | 2023-06-08 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [MailGuard 365](../connectors/mailguard365.md)

**Publisher:** MailGuard365

MailGuard 365 Enhanced Email Security for Microsoft 365. Exclusive to the Microsoft marketplace, MailGuard 365 is integrated with Microsoft 365 security (incl. Defender) for enhanced protection against advanced email threats like phishing, ransomware and sophisticated BEC attacks.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure and connect MailGuard 365**

1. In the MailGuard 365 Console, click **Settings** on the navigation bar.
2. Click the **Integrations** tab.
3. Click the **Enable Microsoft Sentinel**.
4. Enter your workspace id and primary key from the fields below, click **Finish**.
5. For additional instructions, please contact MailGuard 365 support.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `MailGuard365_Threats_CL` |
| **Connector Definition Files** | [MailGuard365.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365/Data%20Connectors/MailGuard365.json) |

[→ View full connector details](../connectors/mailguard365.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MailGuard365_Threats_CL` | [MailGuard 365](../connectors/mailguard365.md) |

[← Back to Solutions Index](../solutions-index.md)
