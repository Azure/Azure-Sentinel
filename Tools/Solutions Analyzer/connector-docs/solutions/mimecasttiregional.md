# MimecastTIRegional

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2023-08-23 |
| **Last Updated** | 2023-09-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md)

**Publisher:** Mimecast

The data connector for Mimecast Intelligence for Microsoft provides regional threat intelligence curated from Mimecast’s email inspection technologies with pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times.  

Mimecast products and features required: 

- Mimecast Secure Email Gateway 

- Mimecast Threat Intelligence



**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Mimecast API credentials**: You need to have the following pieces of information to configure the integration:
- mimecastEmail: Email address of a dedicated Mimecast admin user
- mimecastPassword: Password for the dedicated Mimecast admin user
- mimecastAppId: API Application Id of the Mimecast Microsoft Sentinel app registered with Mimecast
- mimecastAppKey: API Application Key of the Mimecast Microsoft Sentinel app registered with Mimecast
- mimecastAccessKey: Access Key for the dedicated Mimecast admin user
- mimecastSecretKey: Secret Key for the dedicated Mimecast admin user
- mimecastBaseURL: Mimecast Regional API Base URL

> The Mimecast Application Id, Application Key, along with the Access Key and Secret keys for the dedicated Mimecast admin user are obtainable via the Mimecast Administration Console: Administration | Services | API and Platform Integrations.

> The Mimecast API Base URL for each region is documented here: https://integrations.mimecast.com/documentation/api-overview/global-base-urls/
- **Resource group**: You need to have a resource group created with a subscription you are going to use.
- **Functions app**: You need to have an Azure App registered for this connector to use
1. Application Id
2. Tenant Id
3. Client Id
4. Client Secret

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to a Mimecast API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**1. Configuration:**

**STEP 1 - Configuration steps for the Mimecast API**

Go to ***Azure portal ---> App registrations ---> [your_app] ---> Certificates & secrets ---> New client secret*** and create a new secret (save the Value somewhere safe right away because you will not be able to preview it later)

**STEP 2 - Deploy Mimecast API Connector**

>**IMPORTANT:** Before deploying the Mimecast API connector, have the Workspace ID  and Workspace Primary Key (can be copied from the following), as well as the Mimecast API authorization key(s) or Token, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Enable Mimecast Intelligence for Microsoft - Microsoft Sentinel Connector:**

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-MimecastTIRegional-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the following fields:
 - appName: Unique string that will be used as id for the app in Azure platform
 - objectId: Azure portal ---> Azure Active Directory ---> more info ---> Profile -----> Object ID
 - appInsightsLocation(default): westeurope
 - mimecastEmail: Email address of dedicated user for this integraion
 - mimecastPassword: Password for dedicated user
 - mimecastAppId: Application Id from the Microsoft Sentinel app registered with Mimecast
 - mimecastAppKey: Application Key from the Microsoft Sentinel app registered with Mimecast
 - mimecastAccessKey: Access Key for the dedicated Mimecast user
 - mimecastSecretKey: Secret Key for dedicated Mimecast user
 - mimecastBaseURL: Regional Mimecast API Base URL
 - activeDirectoryAppId: Azure portal ---> App registrations ---> [your_app] ---> Application ID
 - activeDirectoryAppSecret: Azure portal ---> App registrations ---> [your_app] ---> Certificates & secrets ---> [your_app_secret]
 - workspaceId: Azure portal ---> Log Analytics Workspaces ---> [Your workspace] ---> Agents ---> Workspace ID (or you can copy workspaceId from above) 
 - workspaceKey:  Azure portal ---> Log Analytics Workspaces ---> [Your workspace] ---> Agents ---> Primary Key (or you can copy workspaceKey from above) 
 - AppInsightsWorkspaceResourceID : Azure portal ---> Log Analytics Workspaces ---> [Your workspace] ---> Properties ---> Resource ID 

 >Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details.

4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

6. Go to ***Azure portal ---> Resource groups ---> [your_resource_group] --->  [appName](type: Storage account) ---> Storage Explorer ---> BLOB CONTAINERS ---> TIR checkpoints ---> Upload*** and create empty file on your machine named checkpoint.txt and select it for upload (this is done so that date_range for TIR logs is stored in consistent state)

**4. Additional configuration:**

>Connect to a **Threat Intelligence Platforms** Data Connector. Follow instructions on the connector page and then click connect button.

| | |
|--------------------------|---|
| **Tables Ingested** | `Event` |
| | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [MimecastTIRegional_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional/Data%20Connectors/MimecastTIRegional_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/mimecasttiregionalconnectorazurefunctions.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Event` | [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md) |
| `ThreatIntelligenceIndicator` | [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md) |

[← Back to Solutions Index](../solutions-index.md)
