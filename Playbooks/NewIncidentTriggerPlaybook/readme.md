# Alert trigger empty playbook
Use this template to quickly create a new playbook which starts with an Azure Sentinel alert.<br>
The playbook is deployed with Managed Identity enabled.

## prerequisites
* This playbook is configured to work with Managed Identity for the Azure Sentinel Logic Apps connector steps. After playbook is deployed, assign permissions for this playbook to Azure Sentinel workspace. [Learn more](https://docs.microsoft.com/connectors/azuresentinel/#authentication)

## screenshots
![screenshot1](./images/designerScreenshotDark.png)<br>
![screenshot2](./images/designerScreenshotLight.png)


## deploy to Azure
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FNewAlertTriggerPlaybookk%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FNewAlertTriggerPlaybookk%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>