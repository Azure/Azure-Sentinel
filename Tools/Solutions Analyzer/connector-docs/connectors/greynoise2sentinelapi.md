# GreyNoise Threat Intelligence

| | |
|----------|-------|
| **Connector ID** | `GreyNoise2SentinelAPI` |
| **Publisher** | GreyNoise, Inc. and BlueCycle LLC |
| **Tables Ingested** | [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md) |
| **Connector Definition Files** | [GreyNoiseConnector_UploadIndicatorsAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Data%20Connectors/GreyNoiseConnector_UploadIndicatorsAPI.json) |

This Data Connector installs an Azure Function app to download GreyNoise indicators once per day and inserts them into the ThreatIntelligenceIndicator table in Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permissions are required.
- **Workspace** (Workspace): read and write permissions on the workspace are required.

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **GreyNoise API Key**: Retrieve your GreyNoise API Key [here](https://viz.greynoise.io/account/api-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. You can connect GreyNoise Threat Intelligence to Microsoft Sentinel by following the below steps:**

> The following steps create an Azure AAD application, retrieves a GreyNoise API key, and saves the values in an Azure Function App Configuration.

**1. Retrieve your API Key from GreyNoise Visualizer.**

Generate an API key from GreyNoise Visualizer https://docs.greynoise.io/docs/using-the-greynoise-api

**2. In your Azure AD tenant, create an Azure Active Directory (AAD) application and acquire Tenant ID and Client ID. Also, get the Log Analytics Workspace ID associated with your Microsoft Sentinel instance (it should display below).**

Follow the instructions here to create your Azure AAD app and save your Client ID and Tenant ID: https://learn.microsoft.com/en-us/azure/sentinel/connect-threat-intelligence-upload-api#instructions
 NOTE: Wait until step 5 to generate your client secret.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Assign the AAD application the Microsoft Sentinel Contributor Role.**

Follow the instructions here to add the Microsoft Sentinel Contributor Role: https://learn.microsoft.com/en-us/azure/sentinel/connect-threat-intelligence-upload-api#assign-a-role-to-the-application

**4. Specify the AAD permissions to enable MS Graph API access to the upload-indicators API.**

Follow this section here to add **'ThreatIndicators.ReadWrite.OwnedBy'** permission to the AAD App: https://learn.microsoft.com/en-us/azure/sentinel/connect-threat-intelligence-tip#specify-the-permissions-required-by-the-application. 
 Back in your AAD App, ensure you grant admin consent for the permissions you just added. 
 Finally, in the 'Tokens and APIs' section, generate a client secret and save it. You will need it in Step 6.

**5. Deploy the Threat Intelligence (Preview) Solution, which includes the Threat Intelligence Upload Indicators API (Preview)**

See Microsoft Sentinel Content Hub for this Solution, and install it in the Microsoft Sentinel instance.

**6. Deploy the Azure Function**

Click the Deploy to Azure button.

  [![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-GreyNoise-azuredeploy)

 Fill in the appropriate values for each parameter. **Be aware** that the only valid values for the **GREYNOISE_CLASSIFICATIONS** parameter are **benign**, **malicious** and/or **unknown**, which must be comma-separated.

**7. Send indicators to Sentinel**

The function app installed in Step 6 queries the GreyNoise GNQL API once per day, and submits each indicator found in STIX 2.1 format to the [Microsoft Upload Threat Intelligence Indicators API](https://learn.microsoft.com/en-us/azure/sentinel/upload-indicators-api). 
 Each indicator expires in ~24 hours from creation unless found on the next day's query. In this case the TI Indicator's **Valid Until** time is extended for another 24 hours, which keeps it active in Microsoft Sentinel.  

 For more information on the GreyNoise API and the GreyNoise Query Language (GNQL), [click here](https://developer.greynoise.io/docs/using-the-greynoise-api).

[← Back to Connectors Index](../connectors-index.md)
