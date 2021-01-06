# Okta-Response From Teams Playbook
 ## Summary

When a new sentinal incident is created,this playbook gets triggered and performs below actions
1.  An adaptvie card is sent to the SOC Teams channel with information collected from the incident and the risky user information from Okta. 
2.  The SOC is allowed to take action on risky user based on the information provided in the adaptive card.

![Okta-Response From Teams](https://dev.azure.com/SentinelAccenture/a94836bc-ff1d-480a-af0f-79be76a3c9e4/_apis/git/repositories/d1bebabf-1feb-4577-8c0b-7d41b70f49df/items?path=%2FOktaPlaybooks%2FOkta-ResponseFromTeams%2FOkta-ResponseFromTeams.PNG&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=Okta&resolveLfs=true&%24format=octetStream&api-version=5.0)
### Prerequisites 
1. Okta Custom Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Generate an API key.Refer this link [ how to generate the API Key](https://developer.okta.com/docs/guides/create-an-api-token/overview/)

### Deployment instructions 
1. Deploy the playbook by clicking on "Deply to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Playbook Name : Enter the playbook name here (ex:Oktaplaybook)
    * Teams GroupId : Enter the Teams channel id to send the adaptive card
    * Teams ChannelId : Enter the Teams Group id to send the adaptive card
     [Refer the below link to get the channel id and group id](https://docs.microsoft.com/en-us/powershell/module/teams/get-teamchannel?view=teams-ps)
    
### Post-Deployment instructions 
####a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Teams connection and Okta Api  Connection (For authorizing the Okta API connection, API Key needs to be provided)
####b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky user account 
2. Configure the automation rules to trigger this playbook

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fdev.azure.com/SentinelAccenture/Sentinel-Accenture%20Logic%20Apps%20connectors/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?version=GBOkta&path=%2FOktaPlaybooks%2FOkta-ResponseFromTeams%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)


## Playbook steps explained
###When Azure Sentinel incident creation rule is triggered

Azure Sentinel incident is created. The playbook receives the incident as the input.
###Entities - Get Accounts

Get the list of risky/malicious accounts as entities from the Incident
###List groups
Playbook uses "List Groups" action to get all the group details present in the particular Okta domain
This groups list will be used later in the adaptive card dropdown when SOC wants to add user to a group
###For each group
 Select groups-preparing the group name and id from the list of groups to display in the adaptive card for user choice
###Compose group information
Compose the choice set dropdown for adaptive card for group names
###For each-risky account received from the incident
Iterates on the accounts found in this incident (probably one) and performs the following:
 1. For the risky user account, playbook uses "Get User" action to get user details from Okta
 2. Post an Adaptive Card to a SOC admin on teams channel with the incident information and risky user information and admin has a list of choices to perform different user actions on Okta
 3. Switch case to perform action choices on the user in Okta 

     a. Case - Add user to group: When Soc admin chooses to add user to a group in Okta, playbook uses "Add user to group" action to add user to group in okta.SOC admin needs to select a group from the adaptive card

     b. Case - Expire Password: When Soc admin chooses to expire password of the user in Okta, playbook uses "Expire Password" action.

     c. Case - Reset Password : When Soc admin chooses to reset password of the user in Okta,playbook uses "Reset Password" action.

     d. Case - Suspend User: When Soc admin chooses to suspend the user in Okta,playbook uses "Suspend User" action.

     e. Case - Unsuspend User :When Soc admin chooses to unsuspend the user in Okta,playbook uses "UnSuspend User" action.

     f. Ignore

 4. Update incident to change severity and status according to choice of SOC admin through adaptive card  
 5. Add a comment to the incident with the below details:
    * With all the user information collected by "Get User" action from Okta 
       * User id, User name, User login, User email, User status, User created, User activated, User statusChanged, User lastLogin, User lastUpdated, User passwordChanged
    * Actions taken on Sentinel : Incident close reason and action taken on user


