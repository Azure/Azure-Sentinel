# CarbonBlack-QuarantineDevice Enrich Incident With device information
 ## Summary

When a new Sentinel incident is created, this playbook gets triggered and performs following actions:

1. Retrieves the device information from Carbon Black Cloud.
2. Quarantines the device.
3. Enriches the incident with device information from Carbon Black Cloud.

    ![CarbonBlack-Enrich Incident With devices information](./images/IncidentComment.png)
    ![CarbonBlack-Enrich Incident With device information](./images/designerOverviewLight1.png)<br>
    ![CarbonBlack-Enrich Incident With device information](./images/designerOverviewLight2.png)

### Prerequisites

1. The Carbon Black custom connector must be already be deployed in same subscription as this playbook.
2. Generate an API key. Refer to this link [how to generate the API Key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)
3. [Determine the Carbon Black organization key.](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)

### Deployment instructions 

1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here (Ex:CarbonBlack-QuarantineDevice)
    * OrganizationKey : Carbon Black organization key

### Post-Deployment instructions

#### Authorize connections

Once deployment is complete, you will need to authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps two and three for the Carbon Black connector connection.

Note: To authorize the Carbon Black API connection, the API Key needs to be provided as a combination of the API Key and API ID.

#### Configurations in Sentinel

1. In Microsoft Sentinel analytical rules should be configured to trigger an incident with risky device.
2. Configure the automation rules to trigger this playbook.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FPlaybooks%2FCarbonBlack-QuarantineDevice%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FPlaybooks%2FCarbonBlack-QuarantineDevice%2Fazuredeploy.json)

## Playbook steps explained

### When Microsoft Sentinel incident creation rule is triggered

Microsoft Sentinel incident is created. The playbook receives the incident as the input.

### Entities - Get Hosts

Gets list of risky devices as entities from the incident.

### Initialize variable to assign the Organization Id

Initializes an string variable to assign the Organization Id provided by Client while deploying the playbook and used a parameter while calling the search devices with organization API action.

### Initialize variable to assign the Carbon Black devices information

Initializes an array variable to assign the Carbon Black devices used as source to format the HTML with the device information.

### Initialize variable to assign the quarantined devices information

Initializes an array variable to assign the quarantined devices information used as source to format the HTML with the action takened device information.

### For each-hosts

This action performs the following actions:

  a. Make a call to Carbon Black API with the parameters [Contains device name].
  b. Verify Carbon Black returned the results and verify the device is quarantined.
  c. If the device is not quarantined then isolate it.

### Construct HTML table - Carbon Black devices information

This action constructs the HTML table with devices information.

### Construct HTML table - Quarantined devices through playbook

This action constructs the HTML table with Quarantined devices through playbook.

### Add a comment to the incident with the information

This action enriches the incident with the constructed HTML table with devices information.

### Close the comment

This action closes the incident if there is no exceptions occurred while quarantining the devices.
