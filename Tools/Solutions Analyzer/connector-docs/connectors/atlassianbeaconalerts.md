# Atlassian Beacon Alerts

| | |
|----------|-------|
| **Connector ID** | `AtlassianBeaconAlerts` |
| **Publisher** | DEFEND Ltd. |
| **Tables Ingested** | [`atlassian_beacon_alerts_CL`](../tables-index.md#atlassian_beacon_alerts_cl) |
| **Used in Solutions** | [Integration for Atlassian Beacon](../solutions/integration-for-atlassian-beacon.md) |
| **Connector Definition Files** | [AtlassianBeacon_DataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Integration%20for%20Atlassian%20Beacon/Data%20Connectors/AtlassianBeacon_DataConnector.json) |

Atlassian Beacon is a cloud product that is built for Intelligent threat detection across the Atlassian platforms (Jira, Confluence, and Atlassian Admin). This can help users detect, investigate and respond to risky user activity for the Atlassian suite of products. The solution is  a custom data connector from DEFEND Ltd. that is used to visualize the alerts ingested from Atlassian Beacon to Microsoft Sentinel via a Logic App.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Microsoft Sentinel**

>1. Navigate to the newly installed Logic App 'Atlassian Beacon Integration'

>2. Navigate to 'Logic app designer'

>3. Expand the 'When a HTTP request is received'

>4. Copy the 'HTTP POST URL'

**2. Atlassian Beacon**

>1. Login to Atlassian Beacon using an admin account

>2. Navigate to 'SIEM forwarding' under SETTINGS

> 3. Paste the copied URL from Logic App in the text box

> 4. Click the 'Save' button

**3. Testing and Validation**

>1. Login to Atlassian Beacon using an admin account

>2. Navigate to 'SIEM forwarding' under SETTINGS

> 3. Click the 'Test' button right next to the newly configured webhook

> 4. Navigate to Microsoft Sentinel

> 5. Navigate to the newly installed Logic App

> 6. Check for the Logic App Run under 'Runs history'

> 7. Check for logs under the table name 'atlassian_beacon_alerts_CL' in 'Logs'

> 8. If the analytic rule has been enabled, the above Test alert should have created an incident in Microsoft Sentinel

[← Back to Connectors Index](../connectors-index.md)
