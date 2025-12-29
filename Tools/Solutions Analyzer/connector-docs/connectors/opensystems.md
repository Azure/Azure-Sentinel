# Open Systems Data Connector

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `OpenSystems` |
| **Publisher** | Open Systems |
| **Used in Solutions** | [Open Systems](../solutions/open-systems.md) |
| **Collection Method** | Azure Function |
| **Connector Definition Files** | [OpenSystems.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Open%20Systems/Data%20Connectors/OpenSystems.json) |

The Open Systems Logs API Microsoft Sentinel Connector provides the capability to ingest Open Systems logs into Microsoft Sentinel using Open Systems Logs API.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`OpenSystemsAuthenticationLogs_CL`](../tables/opensystemsauthenticationlogs-cl.md) | — | — |
| [`OpenSystemsFirewallLogs_CL`](../tables/opensystemsfirewalllogs-cl.md) | — | — |
| [`OpenSystemsImAuthentication`](../tables/opensystemsimauthentication.md) | — | — |
| [`OpenSystemsImNetworkSessionFirewall`](../tables/opensystemsimnetworksessionfirewall.md) | — | — |
| [`OpenSystemsImNetworkSessionProxy`](../tables/opensystemsimnetworksessionproxy.md) | — | — |
| [`OpenSystemsImZTNA`](../tables/opensystemsimztna.md) | — | — |
| [`OpenSystemsProxyLogs_CL`](../tables/opensystemsproxylogs-cl.md) | — | — |
| [`OpenSystemsZtnaLogs_CL`](../tables/opensystemsztnalogs-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Container Apps, DCRs, and DCEs**: Permissions to deploy Azure Container Apps, Managed Environments, Data Collection Rules (DCRs), and Data Collection Endpoints (DCEs) are required. This is typically covered by having the 'Contributor' role on the subscription or resource group.
- **Role Assignment Permissions**: Permissions to create role assignments (specifically 'Monitoring Metrics Publisher' on DCRs) are required for the deploying user or service principal.
- **Required Credentials for ARM Template**: During deployment, you will need to provide: Open Systems Logs API endpoint and connection string, and Service Principal credentials (Client ID, Client Secret, Object/Principal ID).
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Custom prerequisites if necessary, otherwise delete this customs tag**: Description for any custom pre-requisites

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. STEP 1: Prerequisites**

Ensure you have the following information and permissions before proceeding: 
1. Open Systems Logs API endpoint and connection String. 
2. Service Principal credentials (Client ID, Client Secret, Object/Principal ID). 
3. Permissions to deploy Azure Container Apps, Managed Environments, Data Collection Rules (DCRs), Data Collection Endpoints (DCEs), and create Role Assignments (typically 'Contributor' role on the subscription or resource group).

**2. STEP 2: Deploy the Connector**

Deploy the ARM template to set up the data processing resources, including the data collection rule and associated components.

1. Click the **Deploy to Azure** button below. This will take you to the Azure portal.

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-OpenSystemsLogsAPI-azuredeploy)

2. In the Azure portal, select your desired **Subscription**, **Resource Group**, and **Region**.
3. Provide the required parameters, including those gathered in the prerequisites step (Open Systems Logs API details, Service Principal credentials, etc.), when prompted by the deployment wizard.
4. Review the terms and click **Review + create**, then **Create** to start the deployment.

**3. STEP 3: Post-Deployment Verification**

After successful deployment: 
1. Verify that the Azure Container App running the processor is in a 'Running' state. 
2. Check the `OpenSystemsZtnaLogs_CL`, `OpenSystemsFirewallLogs_CL`, `OpenSystemsAuthenticationLogs_CL`, and `OpenSystemsProxyLogs_CL` tables in your Log Analytics workspace for incoming data. It may take some time for logs to appear after initial setup. 
3. Use the sample queries provided in the 'Next Steps' tab of this data connector page to view and analyze your logs.

[← Back to Connectors Index](../connectors-index.md)
