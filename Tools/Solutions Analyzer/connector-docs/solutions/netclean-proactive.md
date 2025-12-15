# NetClean ProActive

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | NetClean |
| **Support Tier** | Partner |
| **Support Link** | [https://www.netclean.com/contact](https://www.netclean.com/contact) |
| **Categories** | domains |
| **First Published** | 2022-06-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Netclean ProActive Incidents](../connectors/netclean-proactive-incidents.md)

**Publisher:** NetClean Technologies

This connector uses the Netclean Webhook (required) and Logic Apps to push data into Microsoft Sentinel Log Analytics

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** NetClean ProActive uses a Webhook to expose incident data, Azure Logic Apps is used to receive and push data to Log Analytics This might result in additional data ingestion costs.
 It's possible to test this without Logic Apps or NetClean Proactive see option 2
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**1. Option 1: Logic app**

1. Create a new logic app
 Use When a HTTP request is recived as the Trigger and save it. It will now have generated a URL that can be used in the ProActive webconsole configuration.
 Add an action:
 Select the Azure Log Analytics Data Collector and choose Send Data
 Enter Connection Name, Workspace ID and Workspace Key, you will find the information needed in your Log Analytics workspace under Settings-->Agents-->Log Analytics agent instructions.
 In JSON Request body add @triggerBody(). in Custom Log Name add Netclean_Incidents.

**2. Option 2 (Testing only)**

Ingest data using a api function. please use the script found on
 https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-collector-api?tabs=powershell 
Replace the CustomerId and SharedKey values with your values
Replace the content in $json variable to the sample data found here: https://github.com/Azure/Azure-Sentinel/blob/master/Sample%20Data/Custom/Netclean_Incidents_CL.json .
Set the LogType varible to **Netclean_Incidents_CL**
Run the script

| | |
|--------------------------|---|
| **Tables Ingested** | `Netclean_Incidents_CL` |
| **Connector Definition Files** | [Connector_NetClean.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NetClean%20ProActive/Data%20Connectors/Connector_NetClean.json) |

[→ View full connector details](../connectors/netclean-proactive-incidents.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Netclean_Incidents_CL` | [Netclean ProActive Incidents](../connectors/netclean-proactive-incidents.md) |

[← Back to Solutions Index](../solutions-index.md)
