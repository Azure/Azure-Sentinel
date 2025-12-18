# Veeam Data Connector (using Azure Functions)

| | |
|----------|-------|
| **Connector ID** | `VeeamCustomTablesDataConnector` |
| **Publisher** | Veeam |
| **Tables Ingested** | [`VeeamAuthorizationEvents_CL`](../tables-index.md#veeamauthorizationevents_cl), [`VeeamCovewareFindings_CL`](../tables-index.md#veeamcovewarefindings_cl), [`VeeamMalwareEvents_CL`](../tables-index.md#veeammalwareevents_cl), [`VeeamOneTriggeredAlarms_CL`](../tables-index.md#veeamonetriggeredalarms_cl), [`VeeamSecurityComplianceAnalyzer_CL`](../tables-index.md#veeamsecuritycomplianceanalyzer_cl), [`VeeamSessions_CL`](../tables-index.md#veeamsessions_cl) |
| **Used in Solutions** | [Veeam](../solutions/veeam.md) |
| **Connector Definition Files** | [Veeam_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Data%20Connectors/Veeam_API_FunctionApp.json) |

Veeam Data Connector allows you to ingest Veeam telemetry data from multiple custom tables into Microsoft Sentinel.



The connector supports integration with Veeam Backup & Replication, Veeam ONE and Coveware platforms to provide comprehensive monitoring and security analytics. The data is collected through Azure Functions and stored in custom Log Analytics tables with dedicated Data Collection Rules (DCR) and Data Collection Endpoints (DCE).



**Custom Tables Included:**

- **VeeamMalwareEvents_CL**: Malware detection events from Veeam Backup & Replication

- **VeeamSecurityComplianceAnalyzer_CL**: Security & Compliance Analyzer results collected from Veeam backup infrastructure components

- **VeeamAuthorizationEvents_CL**: Authorization and authentication events

- **VeeamOneTriggeredAlarms_CL**: Triggered alarms from Veeam ONE servers

- **VeeamCovewareFindings_CL**: Security findings from Coveware solution

- **VeeamSessions_CL**: Veeam sessions

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Veeam Infrastructure Access**: Access to Veeam Backup & Replication REST API and Veeam ONE monitoring platform is required. This includes proper authentication credentials and network connectivity.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to Veeam APIs and pull data into Microsoft Sentinel custom tables. This may result in additional data ingestion costs. See the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

**STEP 1 - Select the deployment option for Veeam Data Connector and associated Azure Functions**

>**IMPORTANT:** Before you deploy Veeam Data Connector, prepare Workspace Name (can be copied from the following).
- **Workspace Name**: `WorkspaceName`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**2. Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Veeam data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVeeam%2FData%2520Connectors%2Fazuredeploy_Veeam_API_FunctionApp.json)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Microsoft Sentinel Workspace Name**. 
4. Click **Review + Create**, **Create**.

[← Back to Connectors Index](../connectors-index.md)
