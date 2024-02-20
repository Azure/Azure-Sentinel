# Varonis SaaS

### In this article
[Connector Attributes](#connector-attributes)\
[Connector Attributes](#query-samples)\
[Prerequisites](#prerequisites)\
[Vendor Installation Instructions](#vendor-installation-instructions)\
[Next Steps](#next-steps)

Varonis SaaS provides the capability to ingest [Varonis Alerts](https://www.varonis.com/products/datalert) into Microsoft Sentinel.

## Connector Attributes
| Connector attribute           | Description                                   |
| ----------------------------- | --------------------------------------------- |
| Azure function app code       | https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/VaronisSaaS/Data%20Connectors/VaronisSaaSFunction |
| Log Analytics table(s)        | VaronisAlerts_CL                              |
| Data collection rules support | Not currently supported                       |
| Supported by                  | Varonis Corporation                           |

## Query samples
#### All Varonis Data Alerts logs

```kusto
VaronisAlerts_CL
| sort by TimeGenerated desc
```

## Prerequisites
To integrate with Varonis SaaS (using Azure Functions) make sure you have the following:
- Microsoft.Web/sites permissions: Read and write permissions to Azure Functions to create a Function App is required. See the [documentation](https://learn.microsoft.com/azure/azure-functions/) to learn more about Azure Functions.
- Varonis API credentials: Varonis API credentials with permission read log is required for Varonis DatAlert API. See the documentation to learn more about creating Varonis DatAlert API credentials.

## Vendor installation instructions
>This connector uses Azure Functions to connect to the Varonis DatAlert Endpoint API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

STEP 1 - Obtain the Varonis DatAlert Endpoint API credentials.

To generate the Client ID and API key:

1. Launch the Varonis Web Interface.
2. Navigate to Configuration -> API Keys. The API Keys page is displayed.
3. Click Create API Key. The Add New API Key settings are displayed on the right.
4. Fill in the name and description.
5. Click the Generate Key button.
6. Copy the API key secret and  save it in a handy location. You won’t be able to copy it again.


STEP 2 - Choose ONE from the following deployment options to deploy the connector and the associated Azure Function.

Option 1 - Azure Resource Manager (ARM) Template

Use this method for automated deployment of the data connector using an ARM Template.

1. Click the Deploy to Azure button.\
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVaronisSaaS%2FData%2520Connectors%2Fazuredeploy.json)
2. Select the preferred Subscription, Resource Group and Location, Function App plan SKU.
3. Enter Log Analytics Workspace Name, DatAlert Host Name, Dat Alert API Key.
4. Click Review + Create, Create.

Option 2 - Manual Deployment of Azure Functions

Use the following step-by-step instructions to deploy the data connector manually with Azure Functions (Deployment via Visual Studio Code).

1. Deploy a Function App

    >NOTE: You will need to prepare VS code for Azure function development.

    1. Download the [Azure Function App file](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/VaronisSaaS/Data%20Connectors/Varonis.Sentinel.Functions.zip). Extract archive to your local development computer.
    2. Start VS Code. Choose File in the main menu and select Open Folder.
    3. Select the top-level folder from the extracted files.
    4. Click the Azure icon in the Activity bar, then in the Azure: Functions area, choose the Deploy to function app button. If you aren't already signed in, click the Azure icon in the Activity bar, then in the Azure: Functions area, choose Sign in to Azure. If you're already signed in, go to the next step.
    5. Provide the following information at the prompts:
        - Select folder: Choose a folder from your workspace or browse to one that contains your function app.
        - Select Subscription: Choose the subscription to use.
        - Select Create new Function App in Azure (Don't choose the Advanced option)
        - Enter a globally unique name for the function app: Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions.
        - Select a runtime: Choose DOTNET 6.0.
        - Select a location for new resources. For better performance and lower costs, choose the same region where Microsoft Sentinel is located.
    6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
    7. Go to Azure Portal for the Function App configuration.

2. Configure the Function App

    1. In the Function App, select the Function App Name and select Configuration.
    2. In the Application settings tab, select + New application setting.
    3. Add each of the following application settings individually, with their respective string values (case-sensitive): DatAlertHostName, DatAlertApiKey, LogAnalyticsKey, LogAnalyticsWorkspace, FirstFetchTime, Severities, ThreatModelNameList and Statuses.
    4. Once all application settings have been entered, click Save.

## Next
For more information, go to the related solution in the Azure Marketplace.