# JoeSandbox Threat Intelligence Feed and Enrichment Integration - Microsoft Sentinel

**Latest Version:** **1.0.0** - **Release Date:** **15/09/2025**

## Overview


## Requirements
- Microsoft Sentinel.
- JoeSandbox API Key.
- Microsoft Azure
  1. Azure functions with Flex Consumption plan.
     Reference: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
     
	 **Note:** Flex Consumption plans are not available in all regions, please check if the region you are deploying the function is supported, if not we suggest you to deploy the function app with premium plan.
	 Reference: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-how-to?tabs=azure-cli%2Cvs-code-publish&pivots=programming-language-python#view-currently-supported-regions
  3. Azure functions Premium plan.
	 Reference: https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan
  4. Azure Logic App with Consumption plan.
     Reference: https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-pricing#consumption-multitenant
  5. Azure storage with Standard general-purpose v2.
     
## Microsoft Sentinel

### Creating Application for API Access

- Open [https://portal.azure.com/](https://portal.azure.com) and search `Microsoft Entra ID` service.

![01](Images/01.png)

- Click `Add->App registration`.

![02a](Images/02a.png)

- Enter the name of application and select supported account types and click on `Register`.

![02](Images/02.png)

- In the application overview you can see `Application Name`, `Application ID` and `Tenant ID`.
 
![03](Images/03.png)

- After creating the application, we need to set API permissions for connector. For this purpose,
  - Click `Manage->API permissions` tab
  - Click `Microsoft Graph` button
  - Search `indicator` and click on the `ThreatIndicators.ReadWrite.OwnedBy`, click `Add permissions` button below.
  - Click on `Grant admin consent`

 ![app_per](Images/app_per.png) 

- We need secrets to access programmatically. For creating secrets
  - Click `Manage->Certificates & secrets` tab
  - Click `Client secrets` tab
  - Click `New client secret` button
  - Enter description and set expiration date for secret

![10](Images/10.png)

- Use Secret `Value` to configure connector.
  
 ![11](Images/11.png)

## Provide Permission To App Created Above

- Open [https://portal.azure.com/](https://portal.azure.com) and search `Microsoft Sentinel` service.
- Goto `Settings` -> `Workspace Setting`

![04](Images/04.png)

- Goto `Access Control(IAM)` -> `Add`

![05](Images/05.png)

- Search for `Microsoft Sentinel Contributor` and click `Next`

![06](Images/06.png)

- Select `User,group or service principle` and click on `select members`.
- Search for the app name created above and click on `select`.
- Click on `Next`

![07](Images/07.png)

- Click on `Review + assign`

![08](Images/08.png)

# Deploy JoeSandbox Threat Intelligence Feed Function App Connector

### Flex Consumption Plan 
- Click on below button to deploy with Flex Consumption plan:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FJoeSandbox%2FData%20Connectors%2Fazuredeploy_JoeSandboxThreatIntelligenceFuncApp_AzureFunction_flex.json)
### Premium Plan
- Click on below button to deploy with Premium plan:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FJoeSandbox%2FData%20Connectors%2Fazuredeploy_JoeSandboxThreatIntelligenceFuncApp_AzureFunction_premium.json)

- It will redirect to feed Configuration page.
  ![09](Images/09.png)
- Please provide the values accordingly.
  
| Fields                                                | Description                                                                                                       |
|:------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------
| Subscription		                                        | Select the appropriate Azure Subscription                                                                         | 
| Resource Group 	                                      | Select the appropriate Resource Group                                                                             |
| Region			                                             | Based on Resource Group this will be uto populated                                                                |
| Function Name		                                       | Please provide a function name if needed to change the default value                                              |
| Joe Sandbox Base URL                                  | Joe Sandbox Base URL                                                                                              |
| Joe Sandbox API Key                                   | Joe Sandbox API Key                                                                                               |
| Azure Client ID                                       | Enter the Azure Client ID created in the App Registration Step                                                    |
| Azure Client Secret                                   | Enter the Azure Client Secret created in the App Registration Step                                                |
| Azure Tenant ID                                       | Enter the Azure Tenant ID of the App Registration                                                                 |
| Azure Workspacse ID                                   | Enter the Azure Workspacse ID. Go to  `Log Analytics workspace -> Overview`, Copy `Workspace ID`                  |
| App Insights Workspace Resource ID                    | Go to `Log Analytics workspace` -> `Settings` -> `Properties`, Copy `Resource ID` and paste here                  |


- Once you provide the above values, please click on `Review + create` button.

- Once the threat intelligence function app connector is successfully deployed, the connector saves the IOCS into the Microsoft Sentinel Threat Intelligence.

![ti_feed](Images/ti_feed.png)

## Deploy JoeSandbox Enrichment Function App Connector

- Click on below button to deploy 

  [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2raw.githubusercontent.com%2Azure%2Azure-Sentinel%2refs%2heads%2master%2Solutions%2JoeSandbox%2Playbooks%2CustomConnector%2JoeSandboxEnrichment_FunctionAppConnector%2azuredeploy.json)
  
- It will redirect to feed Configuration page.

![13](Images/13.png)

- Please provide the values accordingly
  
| Fields                             | Description                                                                                      |
|:-----------------------------------|:-------------------------------------------------------------------------------------------------
| Subscription		                     | Select the appropriate Azure Subscription                                                        | 
| Resource Group 	                   | Select the appropriate Resource Group                                                            |
| Region			                          | Based on Resource Group this will be uto populated                                               |
| Function Name		                    | Please provide a function name if needed to change the default value                             |
| Joe Sandbox Base URL               | Joe Sandbox Base URL                                                                             |
| Joe Sandbox API Key                | Joe Sandbox API Key                                                                              |
| Resubmit                           | If true file will be resubmitted to JoeSandbox                                                   |
| App Insights Workspace Resource ID | Go to `Log Analytics workspace` -> `Settings` -> `Properties`, Copy `Resource ID` and paste here |

- Once you provide the above values, please click on `Review + create` button.


## Deploy JoeSandbox Enrichment Logic Apps

### `JoeSandbox-Submit-Url-Sentinel-Incident` Logic App

- This playbook can be used to enrich sentinel incidents, this playbook when configured to trigger on seninel incidents, the playbook will collect all the `URL` entities from the Incident and submits them to JoeSandbox, once the submission is completed, it will add the JoeSandbox Analysis report to the Incident and creates the IOCs in the microsoft seninel threat intelligence.

- Click on below button to deploy
  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2raw.githubusercontent.com%2Azure%2Azure-Sentinel%2refs%2heads%2master%2Solutions%2JoeSandbox%2Playbooks%2JoeSandbox-Submit-Url-Sentinel-Incident%2azuredeploy.json)

- It will redirect to configuration page

![url_playbook](Images/url_playbook.png)

- Please provide the values accordingly

|       Fields       | Description                                                |
|:---------------------|:-----------------------------------------------------------
| Subscription		| Select the appropriate Azure Subscription                  | 
| Resource Group 	| Select the appropriate Resource Group                      |
| Region			| Based on Resource Group this will be uto populated         |
| Playbook Name		| Please provide a playbook name, if needed                  |
| Workspace ID		| Please provide Log Analytics Workspace ID                  |
| Function App Name		| Please provide the JoeSandbox enrichment function app name |

- Once you provide the above values, please click on `Review + create` button.


### `JoeSandbox-Submit-File-Outlook-Attachment` Logic App

- This playbook can be used to enrich outlook attachments, this playbook when configured will collect all the `attachements` from the email and submits them to JoeSandbox, once the submission is completed, it will add the JoeSandbox Analysis report by creating an Incident and creates the IOCs in the microsoft seninel threat intelligence.


- Click on below button to deploy
  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2raw.githubusercontent.com%2Azure%2Azure-Sentinel%2refs%2heads%2master%2Solutions%2JoeSandbox%2Playbooks%2JoeSandbox-Submit-File-Outlook-Attachment%2azuredeploy.json)

- It will redirect to configuration page

![email_playbook](Images/email_playbook.png)

- Please provide the values accordingly

|       Fields       | Description                                                |
|:---------------------|:-----------------------------------------------------------
| Subscription		| Select the appropriate Azure Subscription                  | 
| Resource Group 	| Select the appropriate Resource Group                      |
| Region			| Based on Resource Group this will be uto populated         |
| Playbook Name		| Please provide a playbook name, if needed                  |
| Workspace Name		| Please provide Log Analytics Workspace Name                |
| Workspace ID		| Please provide Log Analytics Workspace ID                  |
| Function App Name		| Please provide the JoeSandbox enrichment function app name |

- Once you provide the above values, please click on `Review + create` button.

## Provide Permission to Logic app

- Open [https://portal.azure.com/](https://portal.azure.com) and search `Microsoft Sentinel` service.
- Goto `Settings` -> `Workspace Setting`

![04](Images/04.png)

- Goto `Access Control(IAM)` -> `Add`

![05](Images/05.png)

- Search for `Microsoft Sentinel Contributor` and click `Next`

![06](Images/06.png)

- Select `Managed Identity` and click on `select members` .
- Search for the Logic app name deployed above and click on `select`.
- Click on `Next` 

![38](Images/38.png)

- Click on `Review + assign`

