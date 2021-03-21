# Crowdstrike_ContainHost
 ## Summary
 When a new Azure Sentinel incident is created, this playbook gets triggered and performs below actions:
 1. Fetches the device information from Crowdstrike
 2. Contain host if it is not already contained
 3. Enrich the incident with device information from Crowdstrike
 4. Close the incident if contained the host

![Crowdstrike_ContainHost](./ContainHost.png)
### Prerequisites 
1. Azure Key vault is required for storing the Crowdstrike ClientID and Secrets, create key vault if not exists [learn how](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2F201-key-vault-secret-create%2Fazuredeploy.json)
2. Add Crowdstrike Client ID and Client Secret in Key vault secrets and capture the keys which are required during the template deployment
3. CrowdStrike_Base playbook needs to be deployed prior to the deployment of this playbook under the same subscription and under the same resource group.
4. CrowdStrike_Base playbook needs to be added in the access policy of the Key Vault [learn how](https://docs.microsoft.com/en-us/azure/key-vault/general/assign-access-policy-portal)


### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:
    * Playbook_Name: Enter the playbook name here (Ex:Crowdstrike_ContainHost)
    * CrowdStrike_Base_Playbook_Name : Enter the base playbook name here (Ex:CrowdStrike_Base)
    
### Post-Deployment instructions 
####a. Authorize connections
Once deployment is complete, you will need to authorize connections.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save

####b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky device 
2. Configure the automation rules to trigger this playbook

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https://dev.azure.com/SentinelAccenture/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FPlaybooks%2FCrowdstrike_ContainHost%2Fazuredeploy.json&version=GBCrowdstrike) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)

## Playbook steps explained

###When Azure Sentinel incident creation rule is triggered
Azure Sentinel incident is created. The playbook receives the incident as the input.

###Entities - Get Hosts
Get the list of risky devices as entities from the Incident

###Initialize variable comment
Initialize a string variable to hold comments to update in the incident

###Initialize variable success from crowdstrike
Initialize a string variable to hold the success or failure information from crowdstrike api actions

###CrowdStrike Base
Call the base logic App to get access token and Falcon Host URL

###HTTP - Get device id
This gets the device id from crowdstrike filtered by hostname

###Parse JSON Get device id response
This prepares Json message for the device id response

 ###Condition to check if device is present in crowdstrike
1. If device is present, get the device information from crowdstrike API and prepares HTML table with required information
2. Checks the device status, if not contained/normal the playbook will contain the device

 ###Compose image to add in the incident
This action will compose the Crowdstrike image to add to the incident comments

###Add a comment to the incident with the information
This action will enrich the incident with the constructed HTML table with device information

###Condition to check if playbook contained the device
If playbook contained the device, then close the incident with proper closure comments

