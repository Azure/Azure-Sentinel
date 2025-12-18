# WithSecureElementsViaFunction

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | WithSecure |
| **Support Tier** | Partner |
| **Support Link** | [https://www.withsecure.com/en/support](https://www.withsecure.com/en/support) |
| **Categories** | domains |
| **First Published** | 2024-02-22 |
| **Last Updated** | 2025-04-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaFunction](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaFunction) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [WithSecure Elements API (Azure Function)](../connectors/withsecureelementsviafunction.md)

**Publisher:** WithSecure

WithSecure Elements is the unified cloud-based cyber security platform designed to reduce risk, complexity, and inefficiency.



Elevate your security from your endpoints to your cloud applications. Arm yourself against every type of cyber threat, from targeted attacks to zero-day ransomware.



WithSecure Elements combines powerful predictive, preventive, and responsive security capabilities - all managed and monitored through a single security center. Our modular structure and flexible pricing models give you the freedom to evolve. With our expertise and insight, you'll always be empowered - and you'll never be alone.



With Microsoft Sentinel integration, you can correlate [security events](https://connect.withsecure.com/api-reference/security-events#overview) data from the WithSecure Elements solution with data from other sources, enabling a rich overview of your entire environment and faster reaction to threats.



With this solution Azure Function is deployed to your tenant, polling periodically for the WithSecure Elements security events.



For more information visit our website at: [https://www.withsecure.com](https://www.withsecure.com).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **WithSecure Elements API client credentials**: Client credentials are required. [See the documentation to learn more.](https://connect.withsecure.com/getting-started/elements#getting-client-credentials)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Create WithSecure Elements API credentials**

Follow the [user guide](https://connect.withsecure.com/getting-started/elements#getting-client-credentials) to create Elements API credentials. Save credentials in a safe place.

**2. Create Microsoft Entra application**

Create new Microsoft Entra application and credentials. Follow [the instructions](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#create-microsoft-entra-application) and store values of **Directory (tenant) ID**, **Object ID**, **Application (client) ID** and **Client Secret** (from client credentials field). Remember to store Client Secret in a safe place.

**3. Deploy Function App**

>**NOTE:** This connector uses Azure Functions to pull logs from WithSecure Elements. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store Microsoft Entra client credentials and WithSecure Elements API client credentials in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

>**IMPORTANT:** Before deploying the WithSecure Elements connector, have the Workspace Name (can be copied from the following), data from Microsoft Entra (Directory (tenant) ID, Object ID, Application (client) ID and Client Secret), as well as the WithSecure Elements client credentials, readily available.
- **Workspace Name**: `workspaceName`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**1. Deploy all the resources related to the connector**

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-WithSecureElementsViaFunction-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Entra Client ID**, **Entra Client Secret**, **Entra Tenant ID**, **Elements API Client ID**, **Elements API Client Secret**.
>Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. You can also fill in optional fields: **Elements API url**, **Engine**, **Engine Group**. Use default value of **Elements API url** unless you have some special case. **Engine** and **Engine Group** map to [security events request parameters](https://connect.withsecure.com/api-reference/elements#post-/security-events/v1/security-events), fill in those parameters if you are interested only in events from specific engine or engine group, in case you want to receive all security events leave the fields with default values.
5. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
6. Click **Purchase** to deploy.

| | |
|--------------------------|---|
| **Tables Ingested** | `WsSecurityEvents_CL` |
| **Connector Definition Files** | [WithSecureElementsViaFunction.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaFunction/Data%20Connectors/WithSecureElementsViaFunction.json) |

[→ View full connector details](../connectors/withsecureelementsviafunction.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `WsSecurityEvents_CL` | [WithSecure Elements API (Azure Function)](../connectors/withsecureelementsviafunction.md) |

[← Back to Solutions Index](../solutions-index.md)
