# Ermes Browser Security Events

| | |
|----------|-------|
| **Connector ID** | `ErmesBrowserSecurityEvents` |
| **Publisher** | Ermes Cyber Security S.p.A. |
| **Tables Ingested** | [`ErmesBrowserSecurityEvents_CL`](../tables-index.md#ermesbrowsersecurityevents_cl) |
| **Used in Solutions** | [Ermes Browser Security](../solutions/ermes-browser-security.md) |
| **Connector Definition Files** | [ErmesBrowserSecurityEvents_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ermes%20Browser%20Security/Data%20Connectors/ErmesBrowserSecurityEvents_CCF/ErmesBrowserSecurityEvents_ConnectorDefinition.json) |

Ermes Browser Security Events

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Ermes Client Id and Client Secret**: Enable API access in Ermes. Please contact [Ermes Cyber Security](https://www.ermes.company) support for more information.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Ermes Browser Security Events to Microsoft Sentinel**

Connect using OAuth2 credentials
- **API URL (optional)**: https://api.shield.ermessecurity.com
- **OAuth Configuration**:
  - Client ID
  - Client Secret
  - Click 'Connect' to authenticate

[← Back to Connectors Index](../connectors-index.md)
