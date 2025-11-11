# Infoblox TIDE Lookup

* [Summary](#Summary)
* [Prerequisites](#Prerequisites)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)

## Summary<a name="Summary"></a>

The playbook fetches TIDE lookup data for the provided entity type and value.

### Prerequisites<a name="Prerequisites"></a>

1. User must have a valid Infoblox API Key.

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here
    * Infoblox Base Url: Enter baseurl for your Infoblox instance.(e.g. https://csp.infoblox.com)
    * Infoblox API Key: Enter valid value for API Key
    * Workspace Name: Enter name of Log Analytics Workspace

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20TIDE%20Lookup%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https%3A%2F%2Fportal.azure.us%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20TIDE%20Lookup%2Fazuredeploy.json)

### Post-Deployment instructions<a name="Post-Deployment-instructions"></a>

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Go to your logic app -> API connections -> Select azuremonitorlogs connection resource
2. Go to General -> edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections