# Infoblox Data Connector via REST API

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `InfobloxDataConnector` |
| **Publisher** | Infoblox |
| **Used in Solutions** | [Infoblox](../solutions/infoblox.md) |
| **Collection Method** | Azure Function |
| **Connector Definition Files** | [Infoblox_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxCloudDataConnector/Infoblox_API_FunctionApp.json) |

The Infoblox Data Connector allows you to easily connect your Infoblox TIDE data and Dossier data with Microsoft Sentinel. By connecting your data to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`Failed_Range_To_Ingest_CL`](../tables/failed-range-to-ingest-cl.md) | — | — |
| [`Infoblox_Failed_Indicators_CL`](../tables/infoblox-failed-indicators-cl.md) | — | — |
| [`dossier_atp_CL`](../tables/dossier-atp-cl.md) | — | — |
| [`dossier_atp_threat_CL`](../tables/dossier-atp-threat-cl.md) | — | — |
| [`dossier_dns_CL`](../tables/dossier-dns-cl.md) | — | — |
| [`dossier_geo_CL`](../tables/dossier-geo-cl.md) | — | — |
| [`dossier_infoblox_web_cat_CL`](../tables/dossier-infoblox-web-cat-cl.md) | — | — |
| [`dossier_inforank_CL`](../tables/dossier-inforank-cl.md) | — | — |
| [`dossier_malware_analysis_v3_CL`](../tables/dossier-malware-analysis-v3-cl.md) | — | — |
| [`dossier_nameserver_CL`](../tables/dossier-nameserver-cl.md) | — | — |
| [`dossier_nameserver_matches_CL`](../tables/dossier-nameserver-matches-cl.md) | — | — |
| [`dossier_ptr_CL`](../tables/dossier-ptr-cl.md) | — | — |
| [`dossier_rpz_feeds_CL`](../tables/dossier-rpz-feeds-cl.md) | — | — |
| [`dossier_rpz_feeds_records_CL`](../tables/dossier-rpz-feeds-records-cl.md) | — | — |
| [`dossier_threat_actor_CL`](../tables/dossier-threat-actor-cl.md) | — | — |
| [`dossier_tld_risk_CL`](../tables/dossier-tld-risk-cl.md) | — | — |
| [`dossier_whitelist_CL`](../tables/dossier-whitelist-cl.md) | — | — |
| [`dossier_whois_CL`](../tables/dossier-whois-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Subscription**: Azure Subscription with owner role is required to register an application in Microsoft Entra ID and assign role of contributor to app in resource group.
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **Infoblox API Key** is required.  See the documentation to learn more about API on the [Rest API reference](https://csp.infoblox.com/apidoc?url=https://csp.infoblox.com/apidoc/docs/Infrastructure#/Services/ServicesRead)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Infoblox API to create Threat Indicators for TIDE and pull Dossier data into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - App Registration steps for the Application in Microsoft Entra ID**

 This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:
 1. Sign in to the [Azure portal](https://portal.azure.com/).
 2. Search for and select **Microsoft Entra ID**.
 3. Under **Manage**, select **App registrations > New registration**.
 4. Enter a display **Name** for your application.
 5. Select **Register** to complete the initial app registration.
 6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of the TriggersSync playbook. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

**STEP 2 - Add a client secret for application in Microsoft Entra ID**

 Sometimes called an application password, a client secret is a string value required for the execution of TriggersSync playbook. Follow the steps in this section to create a new Client Secret:
 1. In the Azure portal, in **App registrations**, select your application.
 2. Select **Certificates & secrets > Client secrets > New client secret**.
 3. Add a description for your client secret.
 4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
 5. Select **Add**. 
 6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of TriggersSync playbook. 

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret)

**STEP 3 - Assign role of Contributor to application in Microsoft Entra ID**

 Follow the steps in this section to assign the role:
 1. In the Azure portal, Go to **Resource Group** and select your resource group.
 2. Go to **Access control (IAM)** from left panel.
 3. Click on **Add**, and then select **Add role assignment**.
 4. Select **Contributor** as role and click on next.
 5. In **Assign access to**, select `User, group, or service principal`.
 6. Click on **add members** and type **your app name** that you have created and select it.
 7. Now click on **Review + assign** and then again click on **Review + assign**. 

> **Reference link:** [https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal)

**STEP 4 - Steps to generate the Infoblox API Credentials**

 Follow these instructions to generate Infoblox API Key.
 In the [Infoblox Cloud Services Portal](https://csp.infoblox.com/atlas/app/welcome), generate an API Key and copy it somewhere safe to use in the next step. You can find instructions on how to create API keys [**here**](https://docs.infoblox.com/space/BloxOneThreatDefense/230394187/How+Do+I+Create+an+API+Key%3F).

**STEP 5 - Steps to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Infoblox data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following) readily available.., as well as the Infoblox API Authorization Credentials
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**6. Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Infoblox Data connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-infoblox-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the below information : 
		Azure Tenant Id 
		Azure Client Id 
		Azure Client Secret 
		Infoblox API Token 
		Infoblox Base URL 
		Workspace ID 
		Workspace Key 
		Log Level (Default: INFO) 
		Confidence 
		Threat Level 
		App Insights Workspace Resource ID 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

[← Back to Connectors Index](../connectors-index.md)
