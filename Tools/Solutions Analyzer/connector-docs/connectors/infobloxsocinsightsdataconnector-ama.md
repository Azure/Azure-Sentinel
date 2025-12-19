# [Recommended] Infoblox SOC Insight Data Connector via AMA

| | |
|----------|-------|
| **Connector ID** | `InfobloxSOCInsightsDataConnector_AMA` |
| **Publisher** | Infoblox |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Infoblox](../solutions/infoblox.md), [Infoblox SOC Insights](../solutions/infoblox-soc-insights.md) |
| **Connector Definition Files** | [InfobloxSOCInsightsDataConnector_AMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_AMA.json) |

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. 



This data connector ingests Infoblox SOC Insight CDC logs into your Log Analytics Workspace using the new Azure Monitor Agent. Learn more about ingesting using the new Azure Monitor Agent [here](https://learn.microsoft.com/azure/sentinel/connect-cef-ama). **Microsoft recommends using this Data Connector.**

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Workspace Keys**

In order to use the playbooks as part of this solution, find your **Workspace ID** and **Workspace Primary Key** below for your convenience.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Workspace Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**2. Parsers**

>This data connector depends on a parser based on a Kusto Function to work as expected called [**InfobloxCDC_SOCInsights**](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Parsers/InfobloxCDC_SOCInsights.yaml) which is deployed with the Microsoft Sentinel Solution.

**3. SOC Insights**

>This data connector assumes you have access to Infoblox BloxOne Threat Defense SOC Insights. You can find more information about SOC Insights [**here**](https://docs.infoblox.com/space/BloxOneThreatDefense/501514252/SOC+Insights).

**4. Infoblox Cloud Data Connector**

>This data connector assumes an Infoblox Data Connector host has already been created and configured in the Infoblox Cloud Services Portal (CSP). As the [**Infoblox Data Connector**](https://docs.infoblox.com/display/BloxOneThreatDefense/Deploying+the+Data+Connector+Solution) is a feature of BloxOne Threat Defense, access to an appropriate BloxOne Threat Defense subscription is required. See this [**quick-start guide**](https://www.infoblox.com/wp-content/uploads/infoblox-deployment-guide-data-connector.pdf) for more information and licensing requirements.
**Follow the steps below to configure this data connector**

**A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note: CEF logs are collected only from Linux Agents_

1. Navigate to your **Microsoft Sentinel workspace > Data connectors** blade.

2. Search for the **Common Event Format (CEF) via AMA** data connector and open it.

3. Ensure there is no existing DCR configured to collect required facility of logs as it may cause log duplication. Create a new **DCR (Data Collection Rule)**.

	_Note: It is recommended to install the AMA agent v1.27 at minimum. [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplication._

4. Run the command provided in the **Common Event Format (CEF) via AMA** data connector page to configure the CEF collector on the machine.

  **B. Within the Infoblox Cloud Services Portal, configure Infoblox BloxOne to send CEF Syslog data to the Infoblox Cloud Data Connector to forward to the Syslog agent**

  Follow the steps below to configure the Infoblox CDC to send BloxOne data to Microsoft Sentinel via the Linux Syslog agent.
1. Navigate to **Manage > Data Connector**.
2. Click the **Destination Configuration** tab at the top.
3. Click **Create > Syslog**. 
 - **Name**: Give the new Destination a meaningful **name**, such as **Microsoft-Sentinel-Destination**.
 - **Description**: Optionally give it a meaningful **description**.
 - **State**: Set the state to **Enabled**.
 - **Format**: Set the format to **CEF**.
 - **FQDN/IP**: Enter the IP address of the Linux device on which the Linux agent is installed.
 - **Port**: Leave the port number at **514**.
 - **Protocol**: Select desired protocol and CA certificate if applicable.
 - Click **Save & Close**.
4. Click the **Traffic Flow Configuration** tab at the top.
5. Click **Create**.
 - **Name**: Give the new Traffic Flow a meaningful **name**, such as **Microsoft-Sentinel-Flow**.
 - **Description**: Optionally give it a meaningful **description**. 
 - **State**: Set the state to **Enabled**. 
 - Expand the **Service Instance** section. 
    - **Service Instance**: Select your desired Service Instance for which the Data Connector service is enabled. 
 - Expand the **Source Configuration** section.  
    - **Source**: Select **BloxOne Cloud Source**. 
    - Select the **Internal Notifications** Log Type.
 - Expand the **Destination Configuration** section.  
    - Select the **Destination** you just created. 
 - Click **Save & Close**. 
6. Allow the configuration some time to activate.

  **C. Validate connection**

  Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

 1. Make sure that you have Python on your machine using the following command: python -version

2. You must have elevated permissions (sudo) on your machine
  - **Run the following command to validate your connectivity:**: `sudo wget -O Sentinel_AMA_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/Syslog/Sentinel_AMA_troubleshoot.py&&sudo python Sentinel_AMA_troubleshoot.py --cef`

**2. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

[← Back to Connectors Index](../connectors-index.md)
