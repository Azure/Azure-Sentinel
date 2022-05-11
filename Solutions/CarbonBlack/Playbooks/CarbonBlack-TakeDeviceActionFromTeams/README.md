# CarbonBlack-TakeDeviceActionFromTeams playbook
 
## Summary

 When a new Microsoft Sentinel incident is created, this playbook is triggered and performs the following actions:

 1. Retrieves the device information from Carbon Black.
 2. Sends an adaptive card to the SOC Teams channel, let the analyst decide on action:
    - Quarantine the device or Update the policy based on SOC action.

    ![card example](./images/adaptiveCard.png)

 3. Add a comment to the incident with the information collected from the Carbon Black, summary of the actions taken and close the incident.
     
     ![Comment example](./images/IncidentComment.png)

### Prerequisites

1. Carbon Black Custom Connector needs to be deployed prior to the deployment of this playbook in the same subscription.
2. Generate an API key. Refer this link [how to generate the API Key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)
3. Find the organization key by referring this link. [Determine the Carbon Black organization key.](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)

### Deployment instructions

1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:
   - Playbook Name: Enter the playbook name here (Ex:CarbonBlack-TakeDeviceActionFromTeams)
   - OrganizationKey: Enter the Carbon Back organization key.
   - PolicyId: Enter the Carbon Black policy Id to move devices.
   - Teams GroupId: Enter the Microsoft Teams group Id.
   - Teams ChannelId: Enter the Microsoft Teams channel Id.
  
      [How to find the Microsoft Teams channel and group ids](https://docs.microsoft.com/powershell/module/teams/get-teamchannel?view=teams-ps)
  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FPlaybooks%2FCarbonBlack-TakeDeviceActionFromTeams%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2FPlaybooks%2FCarbonBlack-TakeDeviceActionFromTeams%2Fazuredeploy.json)

### Post-deployment instructions

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

1. Sentinel analytics rule should be configured to trigger an incident with risky device.
2. Configure the automation rules to trigger this playbook

## Playbook steps explained

### When Microsoft Sentinel incident creation rule is triggered

Microsoft Sentinel incident is created. The playbook receives the incident as the input.

### Entities - Get Hosts

Get the list of risky devices as entities from the Incident

### Initialize the following variables:

- PolicyId - Assign the pre-configured policy Id value
- OrganizationId - Assign the Organization Id
- Information - SOC will take the action based on the note
- ActionSummary - Assign the summary of the actions taken by SOC
- AdaptiveCardColumnsList - Assign the dynamically prepared columns list to show in the adaptive card [Each device information returned from Carbon Black]
- DeviceActions - Choice list contains actions information [Quarantine, Update_Policy and Ignore]
- AdaptiveCardColumnsList - Assign the dynamically prepared columns list to show in the adaptive card [Each device information returned from Carbon Black]
- AdaptiveCardBody - Assing the dynamically prepared adaptive card body
- Hosts - Assign the Hosts information 
- CarbonBlackDeviceInformation - Assign the Carbon Black device information
- DevicesActionsNeeded - Assign the devices information that needs SOC action
- ComposeProductname - Compose the product name

### For each host

This action will perform the following actions:

- Makes a call to Carbon Black API [Contains device name]
- Verifies the Carbon Black API response_mode
- Checks if the device is quarantined or assigned to predefined policy
- Prepares choice lists based on the response returned by API [Quarantine, Update_Policy and Ignore]

### Compose Incident information

This action will compose the Incident information to show it on the adaptive card

### Compose Adaptive card

This action will compose the dynamically collected devices info [ actions] and choice list

### Post an adaptive card and wait for the SOC action

This action will send an adaptive card to the SOC with the dynamically collected information

### For each host information

This action make a call to the Carbon Black cloud API endpoint to take the necessary actions based on SOC [ Quarantine, Update_Policy and Ignore ]

### Construct HTML table - Quarantined devices through playbook

This action will construct the HTML table with Quarantined devices through playbook

### Add a comment to the incident with the information

This action will enrich the incident with the constructed HTML table with devices information

### Close the comment

This action will close the incident if there is no exceptions occurred while quarantining the devices
