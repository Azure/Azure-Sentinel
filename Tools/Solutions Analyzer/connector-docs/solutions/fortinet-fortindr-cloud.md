# Fortinet FortiNDR Cloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Fortinet |
| **Support Tier** | Partner |
| **Support Link** | [https://www.fortinet.com/support](https://www.fortinet.com/support) |
| **Categories** | domains |
| **First Published** | 2024-01-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md)

**Publisher:** Fortinet

The Fortinet FortiNDR Cloud data connector provides the capability to ingest [Fortinet FortiNDR Cloud](https://docs.fortinet.com/product/fortindr-cloud) data into Microsoft Sentinel using the FortiNDR Cloud API

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **MetaStream Credentials**: **AWS Access Key Id**, **AWS Secret Access Key**, **FortiNDR Cloud Account Code** are required to retrieve event data.
- **API Credentials**: **FortiNDR Cloud API Token**, **FortiNDR Cloud Account UUID** are required to retrieve detection data.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the FortiNDR Cloud API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**NOTE:** This connector uses a parser based on a Kusto Function to normalize fields. [Follow these steps](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Fortinet%20FortiNDR%20Cloud/Parsers/Fortinet_FortiNDR_Cloud.md) to create the Kusto function alias **Fortinet_FortiNDR_Cloud**.

**STEP 1 - Configuration steps for the Fortinet FortiNDR Cloud Logs Collection**

The provider should provide or link to detailed steps to configure the 'PROVIDER NAME APPLICATION NAME' API endpoint so that the Azure Function can authenticate to it successfully, get its authorization key or token, and pull the appliance's logs into Microsoft Sentinel.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Fortinet FortiNDR Cloud connector, have the Workspace ID  and Workspace Primary Key (can be copied from the following), as well as the as well as the FortiNDR Cloud API credentials (available in FortiNDR Cloud account management), readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Fortinet FortiNDR Cloud connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-FortinetFortiNDR-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**(Make sure using the same location as your Resource Group, and got the location supports Flex Consumption. 
3. Enter the **Workspace ID**, **Workspace Key**, **AwsAccessKeyId**, **AwsSecretAccessKey**, and/or Other required fields. 
4. Click **Create** to deploy.

| | |
|--------------------------|---|
| **Tables Ingested** | `FncEventsDetections_CL` |
| | `FncEventsObservation_CL` |
| | `FncEventsSuricata_CL` |
| **Connector Definition Files** | [FortinetFortiNdrCloud_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud/Data%20Connectors/FortinetFortiNdrCloud_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/fortinetfortindrclouddataconnector.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `FncEventsDetections_CL` | [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md) |
| `FncEventsObservation_CL` | [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md) |
| `FncEventsSuricata_CL` | [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
