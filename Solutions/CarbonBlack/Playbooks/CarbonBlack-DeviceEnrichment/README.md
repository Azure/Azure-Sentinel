# CarbonBlack-DeviceEnrichment Incident With devices information

## Summary

 When a new Microsoft Sentinel incident is created, this playbook is triggered and performs the following actions:

 1. Retrieves the devices information from Carbon Black.
 2. Enrich the incident with device information by adding a comment to the incident.

    ![Comment example](./images/IncidentComment.png)

    ![CarbonBlack-Enrich Incident With devices information](./images/designerOverviewLight.png)

### Prerequisites

1. The Carbon Black custom connector must be deployed prior to the deployment of this playbook under the same subscription.
2. Generate an API key.Refer this link [how to generate the API Key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)
3. [Find the Carbon Black organization key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)

### Deployment instructions

1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here (Ex:CarbonBlack-DeviceEnrichment)
    * OrganizationKey : Enter the Carbon Black organization key

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FPlaybooks%2FCarbonBlack-DeviceEnrichment%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FPlaybooks%2FCarbonBlack-DeviceEnrichment%2Fazuredeploy.json)

### Post-Deployment instructions

#### Authorize connections

Once deployment is complete, you will need to authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps two and three for the Carbon Black connector Connection.

Note: To authorize the Carbon Black API connection, the API Key needs to be provided as a combination of the API Key and API ID.

#### Sentinel configuration

1. In Microsoft Sentinel analytics rules should be configured to trigger an incident with risky device.
2. Configure the automation rules to trigger this playbook

## Playbook steps explained

### When Microsoft Sentinel incident creation rule is triggered

Microsoft Sentinel incident is created. The playbook receives the incident as the input.

### Entities - Get Hosts

Get the list of risky devices as entities from the Incident

### Initialize variable to compose the devices information

Initialize an array variable to format the license query and used as parameter while calling the search devices with organization API action

### Initialize variable to assign the Organization Id

Initialize an string variable to assign the Organization Id provided by Client while deploying the playbook and used a parameter while calling the search devices with organization API action.

### For each host

This action will append each host to array variable called Hosts

### Join OR to the hosts

This action will append logical OR operator to collected Hosts

### Search devices in your organization

This action call API to search the devices in the organization by taking two parameters such as organization key and query [Query contains names of the devices]

### Construct HTML table

This action will construct the HTML table with devices information

### Add a comment to the incident with the information

This action will enrich the incident with the constructed HTML table with device information
