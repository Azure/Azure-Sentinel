# ZeroFox

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | ZeroFox |
| **Support Tier** | Partner |
| **Support Link** | [https://www.zerofox.com/contact-us/](https://www.zerofox.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2023-07-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroFox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroFox) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [ZeroFox Enterprise - Alerts (Polling CCF)](../connectors/zerofoxalertsdefinition.md)

**Publisher:** ZeroFox Enterprise

### [ZeroFox CTI](../connectors/zerofoxctidataconnector.md)

**Publisher:** ZeroFox

The ZeroFox CTI data connectors provide the capability to ingest the different [ZeroFox](https://www.zerofox.com/threat-intelligence/) cyber threat intelligence alerts into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **ZeroFox API Credentials/permissions**: **ZeroFox Username**, **ZeroFox Personal Access Token** are required for ZeroFox CTI REST API.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the ZeroFox CTI REST API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Retrieval of ZeroFox credentials:**

 Follow these instructions for set up logging and obtain credentials. 
1. [Log into ZeroFox's website.](https://cloud.zerofox.com/login) using your username and password 
2 - Click into the Settings button and go to the Data Connectors Section. 
3 - Select the API DATA FEEDS tab and head to the bottom of the page, select <<Reset>> in the API Information box, to obtain a Personal Access Token to be used along with your username.

**STEP 2 - Deploy the Azure Function data connectors using the Azure Resource Manager template: **

>**IMPORTANT:** Before deploying the ZeroFox CTI data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Preparing resources for deployment.**

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-zerofox-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group**, Log analytics Workspace and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **ZeroFox Username**, **ZeroFox Personal Access Token**
4.
5. Click **Review + Create** to deploy.

| | |
|--------------------------|---|
| **Tables Ingested** | `ZeroFox_CTI_C2_CL` |
| | `ZeroFox_CTI_advanced_dark_web_CL` |
| | `ZeroFox_CTI_botnet_CL` |
| | `ZeroFox_CTI_breaches_CL` |
| | `ZeroFox_CTI_compromised_credentials_CL` |
| | `ZeroFox_CTI_credit_cards_CL` |
| | `ZeroFox_CTI_dark_web_CL` |
| | `ZeroFox_CTI_discord_CL` |
| | `ZeroFox_CTI_disruption_CL` |
| | `ZeroFox_CTI_email_addresses_CL` |
| | `ZeroFox_CTI_exploits_CL` |
| | `ZeroFox_CTI_irc_CL` |
| | `ZeroFox_CTI_malware_CL` |
| | `ZeroFox_CTI_national_ids_CL` |
| | `ZeroFox_CTI_phishing_CL` |
| | `ZeroFox_CTI_phone_numbers_CL` |
| | `ZeroFox_CTI_ransomware_CL` |
| | `ZeroFox_CTI_telegram_CL` |
| | `ZeroFox_CTI_threat_actors_CL` |
| | `ZeroFox_CTI_vulnerabilities_CL` |
| **Connector Definition Files** | [ZeroFoxCTI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroFox/Data%20Connectors/CTI/ZeroFoxCTI.json) |

[→ View full connector details](../connectors/zerofoxctidataconnector.md)

## Tables Reference

This solution ingests data into **21 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ZeroFoxAlertPoller_CL` | [ZeroFox Enterprise - Alerts (Polling CCF)](../connectors/zerofoxalertsdefinition.md) |
| `ZeroFox_CTI_C2_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_advanced_dark_web_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_botnet_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_breaches_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_compromised_credentials_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_credit_cards_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_dark_web_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_discord_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_disruption_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_email_addresses_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_exploits_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_irc_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_malware_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_national_ids_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_phishing_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_phone_numbers_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_ransomware_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_telegram_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_threat_actors_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_vulnerabilities_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
