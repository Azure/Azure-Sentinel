# Cynerio Security Events

| | |
|----------|-------|
| **Connector ID** | `CynerioSecurityEvents` |
| **Publisher** | Cynerio |
| **Tables Ingested** | [`CynerioEvent_CL`](../tables-index.md#cynerioevent_cl) |
| **Used in Solutions** | [Cynerio](../solutions/cynerio.md) |
| **Connector Definition Files** | [Cynerio_Connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Data%20Connectors/Cynerio_Connector.json) |

The [Cynerio](https://www.cynerio.com/) connector allows you to easily connect your Cynerio Security Events with Microsoft Sentinel, to view IDS Events. This gives you more insight into your organization network security posture and improves your security operation capabilities. 

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure and connect Cynerio**

Cynerio can integrate with and export events directly to Microsoft Sentinel via Azure Server. Follow these steps to establish integration:

1. In the Cynerio console, go to Settings > Integrations tab (default), and click on the **+Add Integration** button at the top right.

2. Scroll down to the **SIEM** section.

3. On the Microsoft Sentinel card, click the Connect button.

4. The Integration Details window opens. Use the parameters below to fill out the form and set up the connection.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
