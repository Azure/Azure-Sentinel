# NetskopeDataConnectorsTriggerSync

* [Summary](#Summary)
* [Prerequisites](#Prerequisites)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)


## Summary<a name="Summary"></a>

Playbook to sync timer trigger of all Netskope data connectors.

### Prerequisites<a name="Prerequisites"></a>

* Users must have a below Microsoft Azure credentials:
    * 1.Tenant ID
    * 2.Client ID
    * 3.Client Secret 
    * 4.Resource Group Name
    * 5.Subscription ID

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Subscription : Select Subscription in which you want to deploy the Logic App.
    * Resource Group: Select Resource Group name in which you want to deploy the Logic App.
    * Playbook Name: Enter the playbook name
    * Tenant ID : Enter the Azure Tenant ID.
    * Client ID : Enter the Azure Client ID.
    * Client Secret : Enter the Azure Client Secret.
    * Resource Group Name : Enter the Azure Resource Group Name in which your Netskope data connectors are available.
    * Subscription ID : Enter the Azure Subscription ID in which your Netskope data connectors are available.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FNetskopev2%2FPlaybooks%2FNetskopeDataConnectorsTriggerSync%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FNetskopev2%2FPlaybooks%2FNetskopeDataConnectorsTriggerSync%2Fazuredeploy.json)

### Post-Deployment instructions<a name="Post-Deployment-instructions"></a>

##### a. Run the playbook to sync timer trigger of all Netskope Data connectors
