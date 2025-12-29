# Infoblox

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Infoblox |
| **Support Tier** | Partner |
| **Support Link** | [https://support.infoblox.com/](https://support.infoblox.com/) |
| **Categories** | domains |
| **First Published** | 2024-07-15 |
| **Last Updated** | 2024-07-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox) |

## Data Connectors

This solution provides **4 data connector(s)**.

### [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md)

**Publisher:** Infoblox

### [[Recommended] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md)

**Publisher:** Infoblox

### [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md)

**Publisher:** Infoblox

### [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md)

**Publisher:** Infoblox

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. 



This data connector ingests Infoblox SOC Insight CDC logs into your Log Analytics Workspace using the legacy Log Analytics agent.



**Microsoft recommends installation of Infoblox SOC Insight Data Connector via AMA Connector.** The legacy connector uses the Log Analytics agent which is about to be deprecated by **Aug 31, 2024,** and should only be installed where AMA is not supported.



 Using MMA and AMA on the same machine can cause log duplication and extra ingestion cost. [More details](https://learn.microsoft.com/en-us/azure/sentinel/ama-migrate).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

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

**1. Linux Syslog agent configuration**

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1.1 Select or create a Linux machine**

  Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your security solution and Microsoft Sentinel this machine can be on your on-prem environment, Azure or other clouds.

  **1.2 Install the CEF collector on the Linux machine**

  Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python -version.

> 2. You must have elevated permissions (sudo) on your machine.
  - **Run the following command to install and apply the CEF collector:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2. Within the Infoblox Cloud Services Portal, configure Infoblox BloxOne to send CEF Syslog data to the Infoblox Cloud Data Connector to forward to the Syslog agent**

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

**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python -version

>2. You must have elevated permissions (sudo) on your machine
- **Run the following command to validate your connectivity:**: `sudo wget  -O cef_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  {0}`

**4. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [InfobloxSOCInsightsDataConnector_Legacy.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_Legacy.json) |

[→ View full connector details](../connectors/infobloxsocinsightsdataconnector-legacy.md)

## Tables Reference

This solution ingests data into **20 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md), [[Recommended] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md) |
| `Failed_Range_To_Ingest_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `InfobloxInsight_CL` | [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md) |
| `Infoblox_Failed_Indicators_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_atp_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_atp_threat_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_dns_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_geo_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_infoblox_web_cat_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_inforank_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_malware_analysis_v3_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_nameserver_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_nameserver_matches_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_ptr_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_rpz_feeds_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_rpz_feeds_records_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_threat_actor_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_tld_risk_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_whitelist_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_whois_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
