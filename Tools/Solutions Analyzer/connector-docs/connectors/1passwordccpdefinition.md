# 1Password (Serverless)

| | |
|----------|-------|
| **Connector ID** | `1PasswordCCPDefinition` |
| **Publisher** | 1Password |
| **Tables Ingested** | [`OnePasswordEventLogs_CL`](../tables-index.md#onepasswordeventlogs_cl) |
| **Used in Solutions** | [1Password](../solutions/1password.md) |
| **Connector Definition Files** | [1Password_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Data%20Connectors/1Password_ccpv2/1Password_DataConnectorDefinition.json) |

The 1Password CCP connector allows the user to ingest 1Password Audit, Signin & ItemUsage events into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **1Password API token**: A 1Password API Token is required. See the [1Password documentation](https://support.1password.com/events-reporting/#appendix-issue-or-revoke-bearer-tokens) on how to create an API token.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. STEP 1 - Create a 1Password API token:**

Follow the [1Password documentation](https://support.1password.com/events-reporting/#appendix-issue-or-revoke-bearer-tokens) for guidance on this step.

**2. STEP 2 - Choose the correct base URL:**

There are multiple 1Password servers which might host your events. The correct server depends on your license and region. Follow the [1Password documentation](https://developer.1password.com/docs/events-api/reference/#servers) to choose the correct server. Input the base URL as displayed by the documentation (including 'https://' and without a trailing '/').

**3. STEP 3 - Enter your 1Password Details:**

Enter the 1Password base URL & API Token below:
- **Base Url**: Enter your Base Url
- **API Token**: (password field)
- Click 'connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
