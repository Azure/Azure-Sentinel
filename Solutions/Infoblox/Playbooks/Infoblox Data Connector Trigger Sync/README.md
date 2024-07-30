# Infoblox Data Connectors Trigger Sync

* [Summary](#Summary)
* [Prerequisites](#Prerequisites)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)
        

## Summary<a name="Summary"></a>

Playbook to sync timer trigger of all Infoblox data connectors.

### Prerequisites<a name="Prerequisites"></a>

* Users must have a below Microsoft Azure credentials:
    * Tenant ID
    * Client ID
    * Client Secret 
    * Resource Group Name
    * Subscription ID

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Subscription : Select Subscription in which you want to deploy the Logic App.
    * Resource Group: Select Resource Group name in which you want to deploy the Logic App.
    * Playbook Name: Enter the playbook name
    * Tenant ID : Enter the Azure Tenant ID.
    * Client ID : Enter the Azure Client ID.
    * Client Secret : Enter the Azure Client Secret.
    * Resource Group Name : Enter the Azure Resource Group Name in which your Infoblox data connectors are available.
    * Subscription ID : Enter the Azure Subscription ID in which your Infoblox data connectors are available.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20Data%20Connector%20Trigger%20Sync%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https%3A%2F%2Fportal.azure.us%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20Data%20Connectors%20Trigger%20Sync%2Fazuredeploy.json)

### Post-Deployment instructions<a name="Post-Deployment-instructions"></a>

a. Run the playbook to sync timer trigger of all Infoblox Data connectors
