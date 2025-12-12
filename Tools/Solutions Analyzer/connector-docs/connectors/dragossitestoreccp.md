#  Dragos Notifications via Cloud Sitestore

| | |
|----------|-------|
| **Connector ID** | `DragosSitestoreCCP` |
| **Publisher** | Dragos |
| **Tables Ingested** | [`DragosAlerts_CL`](../tables-index.md#dragosalerts_cl) |
| **Used in Solutions** | [Dragos](../solutions/dragos.md) |
| **Connector Definition Files** | [dragosSitestoreDataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos/Data%20Connectors/DragosSiteStore_CCP/dragosSitestoreDataConnectorDefinition.json) |

The [Dragos Platform](https://www.dragos.com/) is the leading Industrial Cyber Security platform it offers a comprehensive Operational Technology (OT) cyber threat detection built by unrivaled industrial cybersecurity expertise. This solution enables Dragos Platform notification data to be viewed in Microsoft Sentinel so that security analysts are able to triage potential cyber security events occurring in their industrial environments.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Dragos Sitestore API access**: A Sitestore user account that has the `notification:read` permission. This account also needs to have an API key that can be provided to Sentinel.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Please provide the following information to allow Microsoft Sentinel to connect to your Dragos Sitestore.
- **Dragos Sitestore Hostname**: dragossitestore.example.com
- **Dragos Sitestore API Key ID**: Enter the API key ID.
- **Dragos Sitestore API Key Secret**: (password field)
- **Minimum Notification Severity. Valid values are 0-5 inclusive. Ensure less than or equal to maximum severity.**: Enter the min severity (recommend 0 for all notifications)
- **Maximum Notification Severity. Valid values are 0-5 inclusive. Ensure greater than or equal to minimum severity.**: Enter the max severity (recommend 5 for all notifications)
- Click 'Connect to Sitestore' to establish connection

[← Back to Connectors Index](../connectors-index.md)
