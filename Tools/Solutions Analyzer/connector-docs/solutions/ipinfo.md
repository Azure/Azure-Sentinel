# IPinfo

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | IPinfo |
| **Support Tier** | Partner |
| **Support Link** | [https://www.ipinfo.io/](https://www.ipinfo.io/) |
| **Categories** | domains |
| **First Published** | 2024-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IPinfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IPinfo) |

## Data Connectors

This solution provides **17 data connector(s)**.

### [IPinfo ASN Data Connector](../connectors/ipinfoasndataconnector.md)

**Publisher:** IPinfo

### [IPinfo Abuse Data Connector](../connectors/ipinfoabusedataconnector.md)

**Publisher:** IPinfo

### [IPinfo Carrier Data Connector](../connectors/ipinfocarrierdataconnector.md)

**Publisher:** IPinfo

### [IPinfo Company Data Connector](../connectors/ipinfocompanydataconnector.md)

**Publisher:** IPinfo

### [IPinfo Country ASN Data Connector](../connectors/ipinfocountrydataconnector.md)

**Publisher:** IPinfo

### [IPinfo Domain Data Connector](../connectors/ipinfodomaindataconnector.md)

**Publisher:** IPinfo

### [IPinfo Iplocation Data Connector](../connectors/ipinfoiplocationdataconnector.md)

**Publisher:** IPinfo

### [IPinfo Iplocation Extended Data Connector](../connectors/ipinfoiplocationextendeddataconnector.md)

**Publisher:** IPinfo

### [IPinfo Privacy Data Connector](../connectors/ipinfoprivacydataconnector.md)

**Publisher:** IPinfo

### [IPinfo Privacy Extended Data Connector](../connectors/ipinfoprivacyextendeddataconnector.md)

**Publisher:** IPinfo

### [IPinfo RIRWHOIS Data Connector](../connectors/ipinforirwhoisdataconnector.md)

**Publisher:** IPinfo

### [IPinfo RWHOIS Data Connector](../connectors/ipinforwhoisdataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS ASN Data Connector](../connectors/ipinfowhoisasndataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS MNT Data Connector](../connectors/ipinfowhoismntdataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS NET Data Connector](../connectors/ipinfowhoisnetdataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS ORG Data Connector](../connectors/ipinfowhoisorgdataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS POC Data Connector](../connectors/ipinfowhoispocdataconnector.md)

**Publisher:** IPinfo

This IPinfo data connector installs an Azure Function app to download WHOIS_POC datasets and insert it into custom log table in Microsoft Sentinel

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **IPinfo API Token**: Retrieve your IPinfo API Token [here](https://ipinfo.io/).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Retrieve API Token**

Retrieve your IPinfo API Token [here](https://ipinfo.io/).

**2. In your Azure AD tenant, create an Azure Active Directory (AAD) application**

In your Azure AD tenant, create an Azure Active Directory (AAD) application and acquire Tenant ID, Client ID, and Client Secret: Use this Link.

**3. Assign the AAD application the Microsoft Sentinel Contributor Role.**

Assign the AAD application you just created to the Contributor(Privileged administrator roles) and Monitoring Metrics Publisher(Job function roles) in the same “Resource Group” you use for “Log Analytic Workspace” on which “Microsoft Sentinel” is added: Use this Link.

**4. Get Workspace Resource ID**

Use the Log Analytic Workspace -> Properties blade having the 'Resource ID' property value. This is a fully qualified resourceId which is in the format '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}'

**5. Deploy the Azure Function**

Use this for automated deployment of the IPinfo data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-IPinfo-WHOIS-POC-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **RESOURCE_ID**, **IPINFO_TOKEN**, **TENANT_ID**, **CLIENT_ID**, **CLIENT_SECRET**.

**1. Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the IPinfo data connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

  1. Download the Azure Function App file. Extract the archive to your local development computer [Azure Function App](https://aka.ms/sentinel-Ipinfo-WHOIS-POC-functionapp). 
2. Create Function App using Hosting Functions Premium or App service plan using advanced option using VSCode. 
3. Follow the function app manual deployment instructions to deploy the Azure Functions app using VSCode. 
4. After successful deployment of the function app, follow the next steps for configuring it.

  **Step 2 - Configure the Function App**

  1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Settings** -> **Configuration** or **Environment variables**. 
3. In the **Application settings** tab, select **+ New application setting**.
4. Add each of the following application settings individually, with their respective string values (case-sensitive):
		RESOURCE_ID
		IPINFO_TOKEN
		TENANT_ID
		CLIENT_ID
		CLIENT_SECRET
		RETENTION_IN_DAYS
		TOTAL_RETENTION_IN_DAYS
		SCHEDULE
		LOCATION 
5. Once all application settings have been entered, click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `Ipinfo_WHOIS_POC_CL` |
| **Connector Definition Files** | [IPinfo_WHOIS_POC_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IPinfo/Data%20Connectors/WHOIS%20POC/IPinfo_WHOIS_POC_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/ipinfowhoispocdataconnector.md)

## Tables Reference

This solution ingests data into **17 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Ipinfo_ASN_CL` | [IPinfo ASN Data Connector](../connectors/ipinfoasndataconnector.md) |
| `Ipinfo_Abuse_CL` | [IPinfo Abuse Data Connector](../connectors/ipinfoabusedataconnector.md) |
| `Ipinfo_Carrier_CL` | [IPinfo Carrier Data Connector](../connectors/ipinfocarrierdataconnector.md) |
| `Ipinfo_Company_CL` | [IPinfo Company Data Connector](../connectors/ipinfocompanydataconnector.md) |
| `Ipinfo_Country_CL` | [IPinfo Country ASN Data Connector](../connectors/ipinfocountrydataconnector.md) |
| `Ipinfo_Domain_CL` | [IPinfo Domain Data Connector](../connectors/ipinfodomaindataconnector.md) |
| `Ipinfo_Location_CL` | [IPinfo Iplocation Data Connector](../connectors/ipinfoiplocationdataconnector.md) |
| `Ipinfo_Location_extended_CL` | [IPinfo Iplocation Extended Data Connector](../connectors/ipinfoiplocationextendeddataconnector.md) |
| `Ipinfo_Privacy_CL` | [IPinfo Privacy Data Connector](../connectors/ipinfoprivacydataconnector.md) |
| `Ipinfo_Privacy_extended_CL` | [IPinfo Privacy Extended Data Connector](../connectors/ipinfoprivacyextendeddataconnector.md) |
| `Ipinfo_RIRWHOIS_CL` | [IPinfo RIRWHOIS Data Connector](../connectors/ipinforirwhoisdataconnector.md) |
| `Ipinfo_RWHOIS_CL` | [IPinfo RWHOIS Data Connector](../connectors/ipinforwhoisdataconnector.md) |
| `Ipinfo_WHOIS_ASN_CL` | [IPinfo WHOIS ASN Data Connector](../connectors/ipinfowhoisasndataconnector.md) |
| `Ipinfo_WHOIS_MNT_CL` | [IPinfo WHOIS MNT Data Connector](../connectors/ipinfowhoismntdataconnector.md) |
| `Ipinfo_WHOIS_NET_CL` | [IPinfo WHOIS NET Data Connector](../connectors/ipinfowhoisnetdataconnector.md) |
| `Ipinfo_WHOIS_ORG_CL` | [IPinfo WHOIS ORG Data Connector](../connectors/ipinfowhoisorgdataconnector.md) |
| `Ipinfo_WHOIS_POC_CL` | [IPinfo WHOIS POC Data Connector](../connectors/ipinfowhoispocdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
