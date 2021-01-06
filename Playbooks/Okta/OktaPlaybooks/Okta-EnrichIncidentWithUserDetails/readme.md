# Okta-Enrich Incident With User Details Playbook
 ## Summary
 When a new sentinal incident is created,this playbook gets triggered and performs below actions
 1. Fetches the user details and user group details from Okta
 2. Updates all the collected information in incident


![Okta-Enrich Incident With User Details](https://dev.azure.com/SentinelAccenture/a94836bc-ff1d-480a-af0f-79be76a3c9e4/_apis/git/repositories/d1bebabf-1feb-4577-8c0b-7d41b70f49df/items?path=%2FOktaPlaybooks%2FOkta-EnrichIncidentWithUserDetails%2FOkta-EnrichIncidentwithuserdetails.PNG&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=Okta&resolveLfs=true&%24format=octetStream&api-version=5.0)
### Prerequisites 
1. Okta Custom Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Generate an API key.Refer this link [ how to generate the API Key](https://developer.okta.com/docs/guides/create-an-api-token/overview/)

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here (Ex:OktaPlaybook)
    
### Post-Deployment instructions 
####a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for Okta Api  Connection (For authorizing the Okta API connection, API Key needs to be provided)
####b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky user account 
2. Configure the automation rules to trigger this playbook

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fdev.azure.com/SentinelAccenture/Sentinel-Accenture%20Logic%20Apps%20connectors/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FOktaPlaybooks%2FOkta-EnrichIncidentWithUserDetails%2Fazuredeploy.json&version=GBOkta) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)

## Playbook steps explained
###When Azure Sentinel incident creation rule is triggered

Azure Sentinel incident is created. The playbook receives the incident as the input.
###Entities - Get Accounts

Get the list of risky/malicious accounts as entities from the Incident

###Initialize variable to collect group details
Initialize an array variable to compose user group details to use it later while updating the incident

###For each-risky account received from the incident
Iterates on the accounts found in this incident (probably one) and performs the following:

1. For the risky user account, playbook uses "Get User" action to get user details from Okta
2. For each user, playbook uses "Get User Groups" action to get user  group details from Okta

   a. Compose array of groups for updating incident with group details

   b. Append groups to group array variable

3. Create HTML table format of user group details such as group id,group name and group description

4. Add a comment to the incident with the information below:

     a. User information collected by "Get User" action from Okta such as

     * User id, User name, User login, User email, User status, User created, User activated, User statusChanged, User lastLogin, User lastUpdated, User passwordChanged


     
     b. User groups information collected by "Get User Groups" action from Okta such as

     * Group id,Group name and Group description

