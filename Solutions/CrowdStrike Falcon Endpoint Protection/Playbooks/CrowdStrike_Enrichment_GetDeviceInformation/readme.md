# Crowdstrike_Enrichment_GetDeviceInformation
 ## Summary
 When a new Microsoft Sentinel incident is created, this playbook gets triggered and performs below actions:
 1. Fetches the device information from Crowdstrike
 2. Enrich the incident with device information from Crowdstrike

![comment](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Playbooks/CrowdStrike_Enrichment_GetDeviceInformation/images/comment.png)

![Crowdstrike_Enrichment_GetDeviceInformation](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Playbooks/CrowdStrike_Enrichment_GetDeviceInformation/images/designerOverviewCollapsedLight.png)

### Prerequisites 
1. Azure Key vault is required for storing the Crowdstrike ClientID and Secrets, create key vault if not exists [learn how](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2Fquickstarts%2Fmicrosoft.keyvault%2Fkey-vault-secret-create%2Fazuredeploy.json)
2. Add Crowdstrike Client ID and Client Secret in Key vault secrets and capture the keys which are required during the template deployment
3. CrowdStrike_Base playbook needs to be deployed prior to the deployment of this playbook under the same subscription and under the same resource group.
4. CrowdStrike_Base playbook needs to be added in the access policy of the Key Vault [learn how](https://docs.microsoft.com/azure/key-vault/general/assign-access-policy-portal)

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:
    * Playbook_Name: Enter the playbook name here (Ex:Crowdstrike_ContainHost)
    * CrowdStrike_Base_Playbook_Name : Enter the base playbook name here (Ex:CrowdStrike_Base)
    
### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize connections.
1.	Click the Microsoft Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
#### b. Configurations in Sentinel
1. In Microsoft sentinel analytical rules should be configured to trigger an incident with risky device 
2. Configure the automation rules to trigger this playbook


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCrowdStrike%2520Falcon%2520Endpoint%2520Protection%2FPlaybooks%2FCrowdStrike_Enrichment_GetDeviceInformation%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCrowdStrike%2520Falcon%2520Endpoint%2520Protection%2FPlaybooks%2FCrowdStrike_Enrichment_GetDeviceInformation%2Fazuredeploy.json)

## Playbook steps explained

### When Microsoft Sentinel incident creation rule is triggered
Microsoft Sentinel incident is created. The playbook receives the incident as the input.

### Entities - Get Hosts
Get the list of risky devices as entities from the Incident

### Initialize_variable_comment
Initialize a string variable to store comments to update in the incident

### Initialize variable timestamp
Initialize timestamp variable to hold the timestamp for the past 3 days

### CrowdStrike Base
Call the base logic App to get access token and Falcon Host URL

### HTTP-Get device id
This gets the device id from crowdstrike by filtering on hostname

### Parse JSON Get device id response
This prepares Json message for the device id response

 ### Condition to check if device is present in crowdstrike

1. If device is present, get the device information from crowdstrike API and prepares HTML table with required information
2. Set the timestamp for past 3 days and search for detections on the host and get the detection information
3. check if detection information is present create HTML table for detection information

 ### Compose image to add in the incident
This action will compose the Crowdstrike image to add to the incident comments

### Add a comment to the incident with the information
This action will enrich the incident with the constructed HTML table with device information
