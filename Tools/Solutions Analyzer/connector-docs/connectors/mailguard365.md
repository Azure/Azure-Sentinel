# MailGuard 365

| | |
|----------|-------|
| **Connector ID** | `MailGuard365` |
| **Publisher** | MailGuard365 |
| **Tables Ingested** | [`MailGuard365_Threats_CL`](../tables-index.md#mailguard365_threats_cl) |
| **Used in Solutions** | [MailGuard 365](../solutions/mailguard-365.md) |
| **Connector Definition Files** | [MailGuard365.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365/Data%20Connectors/MailGuard365.json) |

MailGuard 365 Enhanced Email Security for Microsoft 365. Exclusive to the Microsoft marketplace, MailGuard 365 is integrated with Microsoft 365 security (incl. Defender) for enhanced protection against advanced email threats like phishing, ransomware and sophisticated BEC attacks.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

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

[← Back to Connectors Index](../connectors-index.md)
