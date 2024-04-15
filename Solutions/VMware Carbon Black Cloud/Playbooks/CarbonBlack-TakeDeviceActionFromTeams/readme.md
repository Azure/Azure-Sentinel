# CarbonBlack-TakeDeviceActionFromTeams playbook
 ## Summary
 When a new Sentinel incident is created,this playbook gets triggered and performs below actions
 1. Fetches the devices information from CarbonBlack
 2. Sends an adaptive card to the SOC Teams channel, let the analyst decide on action:
    Quarantine the device or Update the policy based on SOC action

    ![card example](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/VMware%20Carbon%20Black%20Cloud/Playbooks/CarbonBlack-TakeDeviceActionFromTeams/images/adaptiveCard.png)

 3. Add a comment to the incident with the information collected from the carbon black, summary of the actions taken and close the incident
     ![Comment example](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/VMware%20Carbon%20Black%20Cloud/Playbooks/CarbonBlack-TakeDeviceActionFromTeams/images/Incident_Comment.png)

### Prerequisites 
1. CarbonBlack Custom Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Generate an API key.Refer this link [ how to generate the API Key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)
3. Find Organization key by referring this link [ Find Organization key by referring this link ](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)
### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here (Ex:CarbonBlack-TakeDeviceActionFromTeams)
    * OrganizationKey: Enter the Organization key
    * PolicyId: Enter the PolicyId
    * Teams GroupId: Enter the Teams GroupId
    * Teams ChannelId: Enter the Teams ChannelId
      [Refer the below link to get the channel id and group id](https://docs.microsoft.com/powershell/module/teams/get-teamchannel?view=teams-ps)
  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVMware%2520Carbon%2520Black%2520Cloud%2FPlaybooks%2FCarbonBlack-TakeDeviceActionFromTeams%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVMware%2520Carbon%2520Black%2520Cloud%2FPlaybooks%2FCarbonBlack-TakeDeviceActionFromTeams%2Fazuredeploy.json)


### Post-Deployment instructions 
#### Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Microsoft Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat step 2&3 while for CarbonBlack connector Connection to authorize connector API of the playbook (For authorizing the CarbonBlack API connection, API Key needs to be provided. API Key Value is the combination of API Key / API ID)
#### Configurations in Sentinel
1. In Microsoft sentinel analytical rules should be configured to trigger an incident with risky device 
2. Configure the automation rules to trigger this playbook



## Playbook steps explained

### When Azure Sentinel incident creation rule is triggered
Azure Sentinel incident is created. The playbook receives the incident as the input.

### Entities - Get Hosts
Get the list of risky devices as entities from the Incident

### Initialize the below variables
  a. PolicyId - Assign the pre-configured policyId value

  b. OrganizationId - Assign the OrganizationId

  c. Information - SOC will take the action based on the note

  d. ActionSummary - Assign the summary of the actions taken by SOC

  e. AdaptiveCardColumnsList - Assign the dynamically prepared columns list to show in the adaptive card [ Each device information returned from CarbonBlack ]

  f. DeviceActions - Choice list contains actions information [ Quarantine, Update_Policy and Ignore ]

  g. AdaptiveCardColumnsList - Assign the dynamically prepared columns list to show in the adaptive card [ Each device information returned from CarbonBlack ]

  h. AdaptiveCardBody - Accessing the dynamically prepared adaptive card body

  i. Hosts - Assign the Hosts information 

  j. CarbonBlackDeviceInformation - Assign the CarbonBlack device information

  k. DevicesActionsNeeded - Assign the devices information that needs SOC action

  l. ComposeProductname - Compose the product name

### For each-Hosts
This action will perform the below actions
 a. Make a call to CarbonBlack API with the parameters such as Organization Key and Query [ Contains device name ]

 b. Verify the CarbonBlack API response_mode

 c. Check if the device is quarantined or assigned to predefined policy

 d. Prepare choice lists based on the response returned by API [ Quarantine, Update_Policy and Ignore ]

### Compose Incident information
This action will compose the Incident information to show it on the adaptive card

### Compose Adaptive card
This action will compose the dynamically collected devices info [ actions] and choice list

### Post an adaptive card and wait for the SOC action
This action will send an adaptive card to the SOC with the dynamically collected information

### For each hosts information
This action make a call to the CarbonBlack cloud API endpoint to take the necessary actions based on SOC [ Quarantine, Update_Policy and Ignore ]

### Construct HTML table - Quarantined devices through playbook
This action will construct the HTML table with Quarantined devices through playbook

### Add a comment to the incident with the information
This action will enrich the incident with the constructed HTML table with devices information

### Close the comment
This action will close the incident if there is no exceptions occurred while quarantining the devices
