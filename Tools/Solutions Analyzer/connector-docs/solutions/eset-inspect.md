# ESET Inspect

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | ESET Enterprise |
| **Support Tier** | Partner |
| **Support Link** | [https://www.eset.com/int/business/solutions/endpoint-detection-and-response/](https://www.eset.com/int/business/solutions/endpoint-detection-and-response/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Inspect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Inspect) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [ESET Inspect](../connectors/esetinspect.md)

**Publisher:** ESET Netherlands

This connector will ingest detections from [ESET Inspect](https://www.eset.com/int/business/solutions/xdr-extended-detection-and-response/) using the provided [REST API](https://help.eset.com/ei_navigate/latest/en-US/api.html). This API is present in ESET Inspect version 1.4 and later.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Access to the ESET PROTECT console**: Permissions to add users

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to ESET Inspect to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**1. Step 1 -  Create an API user**

1. Log into the ESET PROTECT console with an administrator account, select the **More** tab and the **Users** subtab. 
2. Click on the **ADD NEW** button and add a **native user**.
3. Create a new user for the API account. **Optional:** Select a **Home group** other than **All** to limit what detections are ingested. 
4. Under the **Permission Sets** tab, assign the **Inspect reviewer permission set**.
4. Log out of the administrator account and log into the console with the new API credentials for validation, then log out of the API account. 
5.

**2. Step 2 - Copy Workspace ID and Key**

>**IMPORTANT:** Before deploying the ESET Inspect connector, have the Workspace ID and Workspace Primary Key (can be copied from the following) readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Step 3 - Deploy the Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the ESET Inspect connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESETInspect-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **API Username**, **API Password** , enter the **Inspect base URL** and the **first ID** to start ingesting detections from.
 - The defailt starting ID is **0**. This means that all detections will be ingested. 
 - Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labelled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

| | |
|--------------------------|---|
| **Tables Ingested** | `ESETInspect_CL` |
| **Connector Definition Files** | [ESETInspect_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Inspect/Data%20Connectors/ESETInspect_API_FunctionApp.json) |

[→ View full connector details](../connectors/esetinspect.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ESETInspect_CL` | [ESET Inspect](../connectors/esetinspect.md) |

[← Back to Solutions Index](../solutions-index.md)
