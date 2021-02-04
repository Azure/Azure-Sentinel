# PaloAlto-PAN-OS-GetURLCategoryInfo Playbook
 ## Summary
 When a new sentinal incident is created, this playbook gets triggered and performs below actions:
 1. Fetches the address group details and URL filtering category information from PAN-OS
 2. Updates all the collected information in incident


![PaloAlto-PAN-OS-GetURLCategoryInfo](./designerScreenshot.PNG)<br>
### Prerequisites 
1. PAN-OS Custom Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Generate an API key. [Refer this link on how to generate the API Key](https://paloaltolactest.trafficmanager.net/restapi-doc/#tag/key-generation)

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here (e.g. PAN-OS Playbook)
    
### Post-Deployment instructions 
####a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for PAN-OS API Connection (For authorizing the PAN-OS API connection, API Key needs to be provided)

####b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky user account 
2. Configure the automation rules to trigger this playbook

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fdev.azure.com/SentinelAccenture/Sentinel-Accenture%20Logic%20Apps%20connectors/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FPlaybooks%2FPaloAlto-PAN-OS-GetURLCategoryInfo%2Fazuredeploy.json&version=GBPaloAlto-PAN-OS) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)

## Playbook steps explained

### When Azure Sentinel incident creation rule is triggered

Azure Sentinel incident is created. The playbook receives the incident as the input.

### Entities - Get URLs

Get the list of risky/malicious URLs as entities from the Incident

### List-address objects

Playbook uses "List address objects" action to get address object details from PAN-OS

### List URL filtering category information

Playbook uses "List URL filtering category information" action to get URL filtering category details from PAN-OS
### For each-risky URL received from the incident
Iterates on the URLs found in this incident (probably one) and performs the following:

1. For the risky URL, Filter URL from list of address objects action to get specific address object details from PAN-OS

   a. Compose body of address object where URL is a member for updating incident with address object details

 2. Create HTML table for URL category information such as name, location and description

 3. Add a comment to the incident with the information below:

     a. User information collected by "List address obects" action from PAN-OS such as

    *  name, location, description and URL
    
     
     b. URL filtering category information collected by "List URL filtering category information" action from PAN-OS such as

    * name, location and description

