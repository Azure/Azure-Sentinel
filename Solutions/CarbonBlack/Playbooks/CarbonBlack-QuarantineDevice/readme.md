# CarbonBlack-QuarantineDevice Enrich Incident With device information
 ## Summary

 When a new Sentinel incident is created,this playbook gets triggered and performs following actions:
 
 1. Retrieves the device information from Carbon Black.
 2. Quarantine the device
 3. Enrich the incident with device information by fetching from Carbon Black<br>
    ![CarbonBlack-Enrich Incident With devices information](./images/Incident_Comment.png)

![CarbonBlack-Enrich Incident With device information](./images/designerOverviewLight1.png)<br>
![CarbonBlack-Enrich Incident With device information](./images/designerOverviewLight2.png)

### Prerequisites 

1. Carbon Black Custom Connector needs to be deployed prior to the deployment of this playbook in the same subscription.
2. Generate an API key. Refer this link [how to generate the API Key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)
3. Find the organization key by refering this link [ Find Organization key by refering this link ](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)
   
### Deployment instructions 

1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here (Ex:CarbonBlack-QuarantineDevice)
    * OrganizationKey : Enter the Organization key

### Post-Deployment instructions

#### Authorize connections

Once deployment is complete, you will need to authorize each connection.

1. Click the Microsoft Sentinel connection resource.
2. Click edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps 2 & 3 for the Carbon Black connector Connection to authorize connector API of the playbook (For authorizing the Carbon Black API connection, the API Key needs to be provided. API Key Value is the combination of API Key / API ID).

#### Configurations in Sentinel

1. In Microsoft Sentinel analytical rules should be configured to trigger an incident with risky device.
2. Configure the automation rules to trigger this playbook.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FPlaybooks%2FCarbonBlack-QuarantineDevice%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FPlaybooks%2FCarbonBlack-QuarantineDevice%2Fazuredeploy.json)

## Playbook steps explained

### When Microsoft Sentinel incident creation rule is triggered

Microsoft Sentinel incident is created. The playbook receives the incident as the input.

### Entities - Get Hosts

Get the list of risky devices as entities from the Incident

### Initialize variable to assign the Organization Id

Initialize an string variable to assign the Organization Id provided by Client while deploying the playbook and used a parameter while calling the search devices with organization API action.

### Initialize variable to assign the Carbon Black devices information

Initialize an array variable to assign the Carbon Black devices used as source to format the HTML with the devices information

### Initialize variable to assign the quarantined devices information

Initialize an array variable to assign the quarantined devices information used as source to format the HTML with the action takened devices information

### For each-hosts

This action will perform the following actions:

  a. Make a call to Carbon Black API with the parameters [ Contains device name ]
  b. Verify the Carbon Black returned the results and Check the device is quarantined
  c. If the device is not quarantined then isolate it.

### Construct HTML table - Carbon Black devices information

This action will construct the HTML table with devices information

### Construct HTML table - Quarantined devices through playbook

This action will construct the HTML table with Quarantined devices through playbook

### Add a comment to the incident with the information

This action will enrich the incident with the constructed HTML table with devices information

### Close the comment

This action will close the incident if there is no exceptions occurred while quarantining the devices
