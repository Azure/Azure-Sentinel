# Crowdstrike-ResponsefromTeams playbook
 ## Summary
 When a new Azure Sentinel incident is created, this playbook gets triggered and performs below actions:
 1. Fetches the device information from Crowdstrike
 1. Contain the device or run a script based on SOC action
 1. Add a comment to the incident with the information collected from the Crowdstrike, summary of the actions taken and close the incident

**Adaptive card that will be sent in the Teams SOC Channel:**
![Crowdstrike-ResponsefromTeams](./adaptivecardcrowdstrike.png)

**Summary card that will be sent in the Teams SOC Channel to indicate actions success:**
![Crowdstrike-ResponsefromTeams](./SummarizedAdaptiveCard.PNG)

**Playbook overview:**
![Crowdstrike-ResponsefromTeams](./ResponsefromTeams.png)


### Prerequisites 

1. Azure Key vault is required for storing the Crowdstrike ClientID and Secrets, create key vault if not exists [learn how](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2F201-key-vault-secret-create%2Fazuredeploy.json)
2. Add Crowdstrike Client ID and Client Secret in Key vault secrets and capture the keys which are required during the template deployment
3. The base playbook should be added in the access policies of Key vault [learn how](https://docs.microsoft.com/en-us/azure/key-vault/general/assign-access-policy-portal)
4. There should be a list of prewritten scripts in Crowdstrike.[learn how](https://falcon.crowdstrike.com/support/documentation/71/real-time-response-and-network-containment#rtr_custom_scripts) our playbook does not provide an option to create a script.
5. To run a script user needs to be an RTR Active Responder and RTR Administrator in the falcon console.[Understand and assign Real Time Responder roles](https://falcon.crowdstrike.com/support/documentation/71/real-time-response-and-network-containment#rtr_roles)
6. The following needs to be done on the host to run a script:
   *  Configure [Response Policies](https://falcon.crowdstrike.com/support/documentation/71/real-time-response-and-network-containment#rtr-policy-config) - create policies and assign host groups to them
   * 	Enable the toggle real time functionality and enable custom scripts toggle to run them in [Real time resonse policy settings](https://falcon.crowdstrike.com/support/documentation/71/real-time-response-and-network-containment#rtr-policy-config)


### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:
    * Playbook_Name: Enter the playbook name here (Ex:Crowdstrike_ContainHost)
    * CrowdStrike_Base_Playbook_Name : Enter the base playbook name here (Ex:CrowdStrike_Base)
    * Teams GroupId : Enter the Teams GroupId
    * Teams ChannelId : Enter the Teams ChannelId
      [Refer the below link to get the channel id and group id](https://docs.microsoft.com/en-us/powershell/module/teams/get-teamchannel?view=teams-ps)
    
### Post-Deployment instructions 
####a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for Teams connection as well
####b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky device 
2. Configure the automation rules to trigger this playbook

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https://dev.azure.com/SentinelAccenture/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FPlaybooks%2FCrowdstrike_ResponsefromTeams%2Fazuredeploy.json&version=GBCrowdstrike&version=GBCrowdstrike) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)

## Playbook steps explained

###When Azure Sentinel incident creation rule is triggered
Azure Sentinel incident is created. The playbook receives the incident as the input.

###Entities - Get Hosts
Get the list of risky devices as entities from the Incident

###Initialize the below variables
  a. Adaptivecardbody - Assing the dynamically prepared adaptive card body

  b. ActionSummary - Assign the summary of the actions taken by SOC
  
  C. DeviceActions - Choice list contains actions information [ Contain/LiftContainment, RunScript and Ignore ]

  b. DeviceInfo - Assign the Crowdstrike device information

  d. Scriptoptions - Assign the list of script names present in crowdstrike to display in the choice list of adaptive card

  e. ActionTaken - Assign the action taken on host by SOC on device
  

###CrowdStrike Base
Call the base logic App to get access token and Falcon Host URL

###HTTP - Get device id
This gets the device id from crowdstrike by filtering on hostname

###Parse JSON Get device id response
This prepares Json message for the device id response

 ###Condition to check if device is present in crowdstrike
1. If device is present, get the device information from crowdstrike API and prepares HTML table with required information
2. Check if the device status or assigned to predefined policy or contains any predefined scripts 
3. Prepare choice lists based on the response returned by API [ Contain/Lift Containment, Run Script and Ignore ]

 ###Compose Adaptive card
This action will compose the dynamically collected devices info [device actions] and choice list

###Post an adaptive card and wait for the SOC action
This action will send an adaptive card to the SOC with the dynamically collected information

###CrowdStrike Base
Again Call the base logic App to get access token and Falcon Host URL

###Switch to take action on the device
This action make a call to the CrowdStrike cloud API endpoint to take the necessary actions based on SOC [ Contain/LiftContainment/Run Script and Ignore ]

###Post a summarized adaptive card 
This action will send an adaptive card with the summary of actions taken

 ###Compose image to add in the incident
This action will compose the Crowdstrike image to add to the incident comments

###Add a comment to the incident with the information
This action will enrich the incident with the constructed HTML table with device information and action taken

###Close the Incident
This action will close the incident if there are no exceptions occurred while acting on the devices